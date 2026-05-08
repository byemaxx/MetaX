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

from .config import AutoReportConfig, save_config_used
from .html_report import HtmlReportBuilder
from .paths import ReportPaths
from .plot_builder import PlotBuilder
from .registry import ResultRegistry
from .stats_builder import StatsBuilder
from .table_builder import TableBuilder, VALID_TAXA_LEVELS


@dataclass
class ReportResult:
    output_dir: Path
    index_html_path: Path
    summary_json_path: Path
    registry: ResultRegistry


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
        output_was_nonempty = self._output_was_nonempty()
        paths = ReportPaths(self.config.report.output_dir)
        self._prepare_output_dir(paths)
        logger = self._setup_logging(paths)
        registry = ResultRegistry()
        for warning in self._validation_warnings:
            registry.add_warning(warning["message"], warning["source"], details=warning.get("details"))
        if output_was_nonempty and not self.config.report.overwrite:
            registry.add_warning(
                "Output directory already contained files. Existing report files may be overwritten.",
                "AutoOTFReport",
                details={
                    "output_dir": self.config.report.output_dir,
                    "overwrite": self.config.report.overwrite,
                },
            )

        logger.info("Starting MetaX Auto OTF report")
        logger.info("OTF path: %s", self.config.input.otf_path)
        logger.info("Meta path: %s", self.config.input.meta_path)
        logger.info("Output directory: %s", paths.output_dir)
        logger.info("Config: %s", self.config.to_dict())
        save_config_used(self.config, paths.output_dir)

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
            )
        except Exception as exc:
            registry.add_error(str(exc), "AutoOTFReport")
            logger.exception("Fatal report failure")
            raise

    def _validate_input_files(self) -> None:
        input_config = self.config.input
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
            "n_taxa": self._first_table_rows(context, "taxa"),
            "n_functions": self._first_table_rows(context, "function"),
            "n_otfs": self._first_table_rows(context, "otf"),
            "otf_counts": self._otf_table_counts(context),
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
                    "taxa_level": artifact.get("taxa_level"),
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
