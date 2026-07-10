from __future__ import annotations

import json
import logging
import shutil
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from metax.taxafunc_analyzer.analyzer import TaxaFuncAnalyzer

from .config import AutoReportConfig
from .html_report import HtmlReportBuilder
from .paths import ReportPaths
from .plot_builder import PlotBuilder
from .registry import ResultRegistry
from .reproducibility import save_reproducibility_artifacts
from .stats_builder import StatsBuilder
from .table_builder import TableBuilder, VALID_TAXA_LEVELS, taxa_level_label


@dataclass
class ReportResult:
    output_dir: Path
    index_html_path: Path
    summary_json_path: Path
    registry: ResultRegistry
    reproducibility_artifacts: dict[str, Path] = field(default_factory=dict)


@dataclass
class ReportContext:
    config: AutoReportConfig
    paths: ReportPaths
    registry: ResultRegistry
    logger: logging.Logger
    tfa: TaxaFuncAnalyzer
    generated_tables: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    generated_stats: list[dict[str, Any]] = field(default_factory=list)
    function_columns: list[str] = field(default_factory=list)
    taxa_levels: list[str] = field(default_factory=list)
    dataset_summary: dict[str, Any] = field(default_factory=dict)


class AutoOTFReport:
    def __init__(self, config: AutoReportConfig):
        self.config = config
        self._validation_warnings: list[dict[str, Any]] = []

    def run(self) -> ReportResult:
        self._validate_input_files()
        paths = ReportPaths(self.config.report.output_dir)
        self._prepare_output_dir(paths)
        logger = self._setup_logging(paths)
        registry = ResultRegistry()
        for warning in self._validation_warnings:
            registry.add_warning(warning["message"], warning["source"], details=warning.get("details"))
        logger.info("Starting MetaX Auto OTF report")
        logger.info("OTF path: %s", self.config.input.otf_path)
        logger.info("Meta path: %s", self.config.input.meta_path)
        logger.info("Output directory: %s", paths.output_dir)
        logger.info("Config: %s", self.config.to_dict())
        reproducibility_artifacts = save_reproducibility_artifacts(self.config, paths.output_dir)
        for artifact_name, artifact_path in reproducibility_artifacts.items():
            logger.info("Saved reproducibility %s: %s", artifact_name, artifact_path)

        try:
            with self._redirect_backend_output(logger):
                tfa = self._init_analyzer()
                context = ReportContext(
                    config=self.config,
                    paths=paths,
                    registry=registry,
                    logger=logger,
                    tfa=tfa,
                )
                self._validate_analyzer_context(context)

                TableBuilder(context).build_all()
                self._ensure_core_tables(context)
                StatsBuilder(context).run_all()
                PlotBuilder(context).plot_all()

            context.dataset_summary = self._dataset_summary(context)
            index_html_path = HtmlReportBuilder(context).render()
            registry.finish()
            summary_json_path = self._save_summary(context)
            logger.info("Report finished: %s", index_html_path)
            return ReportResult(
                output_dir=paths.output_dir,
                index_html_path=index_html_path,
                summary_json_path=summary_json_path,
                registry=registry,
                reproducibility_artifacts=reproducibility_artifacts,
            )
        except Exception as exc:
            registry.add_error(str(exc), "AutoOTFReport")
            logger.exception("Fatal report failure")
            raise

    def _validate_input_files(self) -> None:
        input_config = self.config.input
        diff_method = self.config.statistics.diff_method.lower()
        if diff_method not in {"limma", "dunnett", "gui_dunnett"}:
            raise ValueError(
                f"Unsupported statistics.diff_method [{self.config.statistics.diff_method}]. "
                "Supported methods are: limma, dunnett."
            )
        if not input_config.otf_path:
            raise ValueError("OTF path is required.")
        otf_path = Path(input_config.otf_path)
        if not otf_path.exists():
            raise FileNotFoundError(f"OTF file does not exist: {otf_path}")
        if not otf_path.is_file():
            raise ValueError(f"OTF path is not a file: {otf_path}")

        if input_config.meta_path:
            meta_path = Path(input_config.meta_path)
            if not meta_path.exists():
                raise FileNotFoundError(f"Meta file does not exist: {meta_path}")
            if not meta_path.is_file():
                raise ValueError(f"Meta path is not a file: {meta_path}")
            self._validate_meta_samples_match(otf_path, meta_path)

        taxa_levels = self.config.tables.taxa_levels
        if taxa_levels != ["all"]:
            invalid = [level for level in taxa_levels if level not in VALID_TAXA_LEVELS]
            if invalid:
                raise ValueError(f"Invalid taxa level(s): {invalid}. Valid levels: {sorted(VALID_TAXA_LEVELS)}")
        supported_formats = {"png", "pdf", "svg"}
        invalid_formats = sorted(set(self.config.report.figure_formats) - supported_formats)
        if invalid_formats:
            raise ValueError(
                f"Unsupported report.figure_formats: {invalid_formats}. "
                f"Supported formats: {sorted(supported_formats)}"
            )
        if self.config.report.dpi <= 0:
            raise ValueError("report.dpi must be greater than zero.")

    def _validate_meta_samples_match(self, otf_path: Path, meta_path: Path) -> None:
        otf_samples = set(self._detect_otf_samples(otf_path))
        if not otf_samples:
            raise ValueError(
                f"No sample columns detected in OTF table using prefix [{self.config.input.sample_col_prefix}]."
            )
        meta = pd.read_csv(meta_path, sep="\t", keep_default_na=False, dtype=str)
        if meta.empty:
            raise ValueError(f"Meta table is empty: {meta_path}")
        sample_col = meta.columns[0]
        meta_samples = {
            self._normalize_sample_name(value)
            for value in meta[sample_col].astype(str).tolist()
            if str(value).strip()
        }
        missing_in_meta = sorted(otf_samples - meta_samples)
        missing_in_otf = sorted(meta_samples - otf_samples)
        if missing_in_otf:
            raise ValueError(
                "Samples in OTF and meta table do not match. "
                f"Missing in OTF: {missing_in_otf}"
            )
        if missing_in_meta:
            self._validation_warnings.append(
                {
                    "message": (
                        "OTF table contains samples that are not present in the meta table. "
                        f"These samples will not be used by TaxaFuncAnalyzer: {missing_in_meta}"
                    ),
                    "source": "AutoOTFReport",
                    "details": {
                        "otf_path": str(otf_path),
                        "meta_path": str(meta_path),
                        "sample_col_prefix": self.config.input.sample_col_prefix,
                        "missing_in_meta": missing_in_meta,
                        "n_missing_in_meta": len(missing_in_meta),
                        "n_otf_samples": len(otf_samples),
                        "n_meta_samples": len(meta_samples),
                    },
                }
            )

    def _detect_otf_samples(self, otf_path: Path) -> list[str]:
        header = pd.read_csv(otf_path, sep="\t", nrows=0).columns.tolist()
        prefix = self.config.input.sample_col_prefix.strip()
        if not prefix:
            raise ValueError("sample_col_prefix must be provided for OTF input.")
        normalized_columns = [column.replace(" ", "_") for column in header]
        sample_columns = [
            column for column in normalized_columns if column.startswith(prefix) and column != prefix
        ]
        return [self._normalize_sample_name(column) for column in sample_columns]

    def _normalize_sample_name(self, value: str) -> str:
        prefix = self.config.input.sample_col_prefix.strip()
        sample = str(value).strip().replace(" ", "_")
        if prefix and sample.startswith(prefix):
            sample = sample.replace(prefix, "", 1)
        if sample.startswith("_"):
            sample = sample[1:]
        return sample

    def _output_was_nonempty(self) -> bool:
        output_dir = Path(self.config.report.output_dir)
        return output_dir.exists() and output_dir.is_dir() and any(output_dir.iterdir())

    def _prepare_output_dir(self, paths: ReportPaths) -> None:
        if paths.output_dir.exists() and not paths.output_dir.is_dir():
            raise ValueError(f"Output path exists but is not a directory: {paths.output_dir}")
        if self._output_was_nonempty() and not self.config.report.overwrite:
            raise FileExistsError(
                f"Output directory is not empty: {paths.output_dir}. "
                "Use --overwrite or choose a new output directory."
            )
        if paths.output_dir.exists() and self.config.report.overwrite:
            self._clear_previous_report(paths.output_dir)
        paths.create()
        test_path = paths.output_dir / ".write_test"
        try:
            test_path.write_text("ok", encoding="utf-8")
            test_path.unlink()
        except OSError as exc:
            raise OSError(f"Output directory is not writable: {paths.output_dir}") from exc

    def _clear_previous_report(self, output_dir: Path) -> None:
        for name in ["tables", "stats", "figures", "assets", "logs"]:
            path = output_dir / name
            if path.exists():
                shutil.rmtree(path)
        for name in ["index.html", "config_used.yaml", "summary.json"]:
            path = output_dir / name
            if path.exists():
                path.unlink()

    def _setup_logging(self, paths: ReportPaths) -> logging.Logger:
        logger = logging.getLogger(f"metax.report.auto_otf.{id(self)}")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        logger.handlers.clear()

        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler = logging.FileHandler(paths.logs_dir / "report.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    @contextmanager
    def _redirect_backend_output(self, logger: logging.Logger):
        writer = _LoggerWriter(logger, logging.INFO)
        with redirect_stdout(writer), redirect_stderr(writer):
            yield

    def _init_analyzer(self) -> TaxaFuncAnalyzer:
        config = self.config.input
        tfa = TaxaFuncAnalyzer(
            df_path=config.otf_path,
            meta_path=config.meta_path,
            peptide_col_name=config.peptide_col_name,
            protein_col_name=config.protein_col_name,
            sample_col_prefix=config.sample_col_prefix,
            any_df_mode=config.any_df_mode,
            custom_col_name=config.custom_col_name or "Custom",
        )
        if config.meta_path is None:
            sample_list = list(tfa.sample_list or [])
            tfa.meta_df = pd.DataFrame(
                {
                    "Sample": sample_list,
                    "AutoGroup": ["All"] * len(sample_list),
                    "Sample_Name": sample_list,
                }
            )
        return tfa

    def _validate_analyzer_context(self, context: ReportContext) -> None:
        tfa = context.tfa
        if not tfa.sample_list:
            raise ValueError("No sample columns detected after initializing TaxaFuncAnalyzer.")
        if tfa.meta_df is None or tfa.meta_df.empty:
            raise ValueError("Meta table is empty after initializing TaxaFuncAnalyzer.")

        self._validate_meta_column(context.config.preprocessing.detection_by_group, tfa, "detection_by_group")
        self._validate_meta_column(context.config.preprocessing.handle_by_group, tfa, "handle_by_group")
        self._validate_meta_column(context.config.preprocessing.batch_meta, tfa, "batch_meta")

        group_meta = context.config.analysis.group_meta
        if group_meta:
            if group_meta not in tfa.meta_df.columns:
                raise ValueError(f"group_meta [{group_meta}] is not in meta table columns: {list(tfa.meta_df.columns)}")
            tfa.set_group(group_meta)

            control_group = context.config.analysis.control_group
            if control_group:
                groups = set(tfa.meta_df[group_meta].astype(str))
                if control_group not in groups:
                    raise ValueError(
                        f"control_group [{control_group}] is not present in group_meta [{group_meta}]. "
                        f"Available groups: {sorted(groups)}"
                    )
        elif context.config.analysis.control_group:
            raise ValueError("control_group was provided, but group_meta is not set.")

    def _validate_meta_column(self, column: str | None, tfa: TaxaFuncAnalyzer, field_name: str) -> None:
        if column in [None, "None", ""]:
            return
        if column not in tfa.meta_df.columns:
            raise ValueError(f"{field_name} [{column}] is not in meta table columns: {list(tfa.meta_df.columns)}")

    def _ensure_core_tables(self, context: ReportContext) -> None:
        core_count = sum(
            len(context.generated_tables.get(table_type, []))
            for table_type in ["taxa", "function", "otf", "protein"]
        )
        if core_count == 0:
            raise RuntimeError("No core analysis tables were generated.")

    def _dataset_summary(self, context: ReportContext) -> dict[str, Any]:
        group_meta = context.config.analysis.group_meta
        if group_meta and group_meta in context.tfa.meta_df.columns:
            n_groups = int(context.tfa.meta_df[group_meta].nunique())
        else:
            n_groups = 1

        return {
            "n_samples": len(context.tfa.sample_list or []),
            "n_groups": n_groups,
            "n_peptides": int(context.tfa.original_df.shape[0]),
            "n_taxa": self._main_taxa_table_rows(context),
            "n_functions": self._first_table_rows(context, "function"),
            "n_otfs": self._first_table_rows(context, "otf"),
            "otf_counts": self._otf_table_counts(context),
            "main_taxa_level": taxa_level_label(context.config.analysis.main_taxa_level),
            "selected_taxa_levels": [taxa_level_label(level) for level in context.taxa_levels],
            "main_function": context.config.analysis.main_function
            or (context.function_columns[0] if context.function_columns else "None"),
            "selected_function_columns": list(context.function_columns),
            "statistics_backend": self._statistics_backend_summary(context),
            "unit_aware": self._unit_aware_summary(context),
        }

    def _main_taxa_table_rows(self, context: ReportContext) -> int:
        tables = context.generated_tables.get("taxa", [])
        main_level = context.config.analysis.main_taxa_level
        for artifact in tables:
            if artifact.get("taxa_level") == main_level:
                return int(artifact["df"].shape[0])
        return int(tables[0]["df"].shape[0]) if tables else 0

    def _statistics_backend_summary(self, context: ReportContext) -> str:
        if not context.config.statistics.run_group_vs_control:
            return "Group-vs-control testing disabled"
        if context.config.statistics.diff_method.lower() == "limma":
            return "limma via InMoose on log2(x+1)-transformed abundance"
        return "MetaX GUI Dunnett compatibility workflow"

    def _unit_aware_summary(self, context: ReportContext) -> dict[str, Any]:
        candidates = ["analysis_unit_id", "analysis_unit", "unit_id"]
        original_unit_column = next(
            (name for name in candidates if name in context.tfa.original_df.columns),
            None,
        )
        meta_unit_column = next(
            (name for name in candidates if name in context.tfa.meta_df.columns),
            None,
        )
        unit_column = original_unit_column or meta_unit_column
        if unit_column is None:
            return {
                "detected": False,
                "message": "No unit-aware metadata detected",
                "genome_evidence_source": None,
                "duplicate_peptide_handling": None,
                "unit_specific_assignment_available": False,
            }
        if original_unit_column:
            values = context.tfa.original_df[original_unit_column].dropna().astype(str)
        else:
            values = context.tfa.meta_df[meta_unit_column].dropna().astype(str)
        samples_per_unit: dict[str, int] = {}
        if meta_unit_column and "Sample" in context.tfa.meta_df.columns:
            samples_per_unit = (
                context.tfa.meta_df.dropna(subset=[meta_unit_column])
                .groupby(meta_unit_column)["Sample"]
                .nunique()
                .astype(int)
                .to_dict()
            )
            samples_per_unit = {str(unit): int(count) for unit, count in samples_per_unit.items()}
        elif original_unit_column:
            sample_columns = [
                sample
                for sample in context.tfa.sample_list or []
                if sample in context.tfa.original_df.columns
            ]
            for unit, frame in context.tfa.original_df.dropna(
                subset=[original_unit_column]
            ).groupby(original_unit_column):
                matrix = frame[sample_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
                samples_per_unit[str(unit)] = int((matrix != 0).any(axis=0).sum())
        records_per_unit: dict[str, int] = {}
        if meta_unit_column:
            record_counts = (
                context.tfa.meta_df.dropna(subset=[meta_unit_column])
                .groupby(meta_unit_column)
                .size()
                .astype(int)
                .to_dict()
            )
            records_per_unit = {str(unit): int(count) for unit, count in record_counts.items()}
        features_per_unit: dict[str, int] = {}
        if original_unit_column:
            feature_counts = (
                context.tfa.original_df.dropna(subset=[original_unit_column])
                .groupby(original_unit_column)
                .size()
                .astype(int)
                .to_dict()
            )
            features_per_unit = {str(unit): int(count) for unit, count in feature_counts.items()}
        return {
            "detected": True,
            "unit_column": unit_column,
            "n_analysis_units": int(values.nunique()),
            "samples_per_unit": samples_per_unit,
            "records_per_unit": records_per_unit,
            "features_per_unit": features_per_unit,
            "genome_evidence_source": None,
            "duplicate_peptide_handling": None,
            "unit_specific_assignment_available": original_unit_column == "analysis_unit_id",
        }

    def _first_table_rows(self, context: ReportContext, table_type: str) -> int:
        tables = context.generated_tables.get(table_type, [])
        if not tables:
            return 0
        return int(tables[0]["df"].shape[0])

    def _otf_table_counts(self, context: ReportContext) -> list[dict[str, Any]]:
        counts: list[dict[str, Any]] = []
        for artifact in context.generated_tables.get("otf", []):
            counts.append(
                {
                    "key": artifact.get("key"),
                    "title": artifact.get("title"),
                    "taxa_level": taxa_level_label(str(artifact.get("taxa_level"))),
                    "function_column": artifact.get("function_column"),
                    "n_features": int(artifact["df"].shape[0]),
                }
            )
        return counts

    def _save_summary(self, context: ReportContext) -> Path:
        path = context.paths.output_dir / "summary.json"
        registry_dict = context.registry.to_dict()
        summary = {
            "input": context.config.input.__dict__,
            "config": context.config.to_dict(),
            "dataset_summary": context.dataset_summary,
            "outputs": {
                "tables": registry_dict["tables"],
                "figures": registry_dict["figures"],
                "stats": registry_dict["stats"],
                "html": registry_dict["html"],
            },
            "warnings": registry_dict["warnings"],
            "errors": registry_dict["errors"],
            "runtime": registry_dict["runtime"],
        }
        with path.open("w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2)
        context.logger.info("Saved summary JSON: %s", path)
        return path


class _LoggerWriter:
    def __init__(self, logger: logging.Logger, level: int):
        self.logger = logger
        self.level = level
        self._buffer = ""

    def write(self, message: str) -> int:
        if not message:
            return 0
        self._buffer += message.replace("\r", "\n")
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            line = line.strip()
            if line:
                self.logger.log(self.level, line)
        return len(message)

    def flush(self) -> None:
        line = self._buffer.strip()
        if line:
            self.logger.log(self.level, line)
        self._buffer = ""
