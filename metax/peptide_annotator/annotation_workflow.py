from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

from metax.peptide_annotator.pep_table_to_otf import peptideProteinsMapper
from metax.peptide_annotator.peptide_table_prepare import (
    is_diann_parquet,
    is_parquet_path,
    prepare_diann_parquet_for_direct_otf,
    read_parquet_columns,
)


ANNOTATION_WORKFLOW_API_VERSION = "1.0"
METAUMBRA_MINIMUM_VERSION = "1.3.6"
GLOBAL_SELECTION_MODES = {
    "metaumbra",
    "provided",
    "automatic",
    "metaumbra-only",
}


class AnnotationConfigurationError(ValueError):
    """Raised when an annotation workflow configuration is invalid."""


class OptionalDependencyUnavailable(RuntimeError):
    """Raised when an explicitly requested optional runtime is unavailable."""


@dataclass(frozen=True)
class GlobalOTFRunResult:
    output_path: str
    info_path: str | None
    annotation_summary_path: str | None
    inputs: dict[str, object]
    parameters: dict[str, object]
    stages: dict[str, object]
    genome_selection: dict[str, object]
    metrics: dict[str, object]
    outputs: dict[str, object]
    software: dict[str, str]
    warnings: list[str] = field(default_factory=list)
    rows: int | None = None
    column_count: int | None = None


def parse_genome_text(text: str) -> list[str]:
    genomes: list[str] = []
    seen: set[str] = set()
    for item in re.split(r"[\r\n,;，；]+", text or ""):
        genome = item.strip()
        if genome and genome not in seen:
            seen.add(genome)
            genomes.append(genome)
    return genomes


def read_genome_list_file(
    file_path: str | Path,
    *,
    qvalue_cutoff: float = 0.05,
) -> list[str]:
    """Read a plain genome list or a MetaUmbra genome-presence table."""
    file_path = Path(file_path)
    with file_path.open("r", encoding="utf-8-sig") as handle:
        text = handle.read()

    first_line = next((line for line in text.splitlines() if line.strip()), "")
    delimiter = "\t" if "\t" in first_line else ","
    columns = [column.strip() for column in first_line.split(delimiter)]
    if "genome_id" not in columns:
        return parse_genome_text(text)

    dataframe = pd.read_csv(file_path, sep=delimiter)
    if "qvalue" in dataframe.columns:
        qvalues = pd.to_numeric(dataframe["qvalue"], errors="coerce")
        dataframe = dataframe[qvalues <= qvalue_cutoff]
    return parse_genome_text("\n".join(dataframe["genome_id"].dropna().astype(str)))


def _parse_version(version_text: str) -> tuple[int, int, int] | None:
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", version_text)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def _normalise_paths(values: str | Path | Iterable[str | Path] | None) -> list[str]:
    if values is None:
        return []
    if isinstance(values, (str, Path)):
        values = [values]
    return [str(Path(value)) for value in values if str(value).strip()]


def _normalise_genomes(values: str | Iterable[str] | None) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        values = parse_genome_text(values)
    seen: set[str] = set()
    genomes: list[str] = []
    for value in values:
        genome = str(value).strip()
        if genome and genome not in seen:
            seen.add(genome)
            genomes.append(genome)
    return genomes


def _file_descriptor(path: str | Path, *, format_name: str | None = None) -> dict[str, object]:
    file_path = Path(path)
    descriptor: dict[str, object] = {"path": str(file_path)}
    if format_name:
        descriptor["format"] = format_name
    if file_path.is_file():
        stat = file_path.stat()
        descriptor["size_bytes"] = int(stat.st_size)
        descriptor["modified_at"] = datetime.fromtimestamp(
            stat.st_mtime
        ).astimezone().isoformat(timespec="seconds")
    return descriptor


def _elapsed(started: float) -> float:
    return round(time.perf_counter() - started, 6)


def _sample_metrics(dataframe: pd.DataFrame, sample_columns: Iterable[str]) -> dict[str, object]:
    row_count = int(dataframe.shape[0])
    metrics: dict[str, object] = {}
    for column in sample_columns:
        values = pd.to_numeric(dataframe[column], errors="coerce").fillna(0)
        positive = values[values > 0]
        detected = int(positive.shape[0])
        metrics[str(column)] = {
            "detected_peptides": detected,
            "zero_or_missing_peptides": row_count - detected,
            "zero_or_missing_fraction": (
                round((row_count - detected) / row_count, 6) if row_count else None
            ),
            "total_intensity": float(values.sum()),
            "median_nonzero_intensity": (
                float(positive.median()) if not positive.empty else None
            ),
        }
    return metrics


def _metaumbra_environment() -> tuple[Path, dict[str, str]]:
    project_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root) + os.pathsep + env.get("PYTHONPATH", "")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return project_root, env


def ensure_metaumbra_available(
    *,
    minimum_version: str = METAUMBRA_MINIMUM_VERSION,
    env: dict[str, str] | None = None,
) -> str:
    if env is None:
        _, env = _metaumbra_environment()
    process = subprocess.run(
        [sys.executable, "-m", "metaumbra", "--version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    version_output = (process.stdout or "").strip()
    if process.returncode != 0:
        if "No module named" in version_output and "metaumbra" in version_output.lower():
            raise OptionalDependencyUnavailable(
                "MetaUmbra is required for global genome scoring. Install or update "
                "the annotation dependencies in this Python environment."
            )
        raise RuntimeError(
            f"Unable to launch MetaUmbra with {sys.executable}:\n{version_output}"
        )

    actual = _parse_version(version_output)
    required = _parse_version(minimum_version)
    if actual is None or required is None or actual < required:
        raise OptionalDependencyUnavailable(
            f"MetaX global annotation requires MetaUmbra >= {minimum_version}, but "
            f"the active Python resolves {version_output or 'an unknown version'}. "
            f"Python executable: {sys.executable}"
        )
    return ".".join(map(str, actual))


def run_metaumbra_scoring(
    *,
    peptide_table_path: str,
    digested_genome_folders: str | Iterable[str],
    output_path: str,
    peptide_col: str,
    peptide_score_col: str = "Evidence",
    peptide_error_col: str = "Q.Value",
    single_peptide_error_rate_upper_bound: float = 0.3,
) -> dict[str, object]:
    digest_dirs = _normalise_paths(digested_genome_folders)
    command = [
        sys.executable,
        "-m",
        "metaumbra",
        "score",
        "--peptide-table",
        peptide_table_path,
        "--genome-digest-dirs",
        *digest_dirs,
        "--output",
        output_path,
        "--peptide-seq-col",
        peptide_col,
        "--peptide-score-col",
        peptide_score_col,
        "--peptide-error-col",
        peptide_error_col,
        "--single-peptide-error-rate-upper-bound",
        str(single_peptide_error_rate_upper_bound),
    ]

    print("Launching MetaUmbra scoring in an isolated process:")
    print(" ".join(f'"{part}"' if " " in str(part) else str(part) for part in command))
    project_root, env = _metaumbra_environment()
    metaumbra_version = ensure_metaumbra_available(env=env)

    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    process = subprocess.Popen(
        command,
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        env=env,
        creationflags=creationflags,
    )
    last_lines: list[str] = []
    assert process.stdout is not None
    for line in process.stdout:
        print(line.rstrip("\n"))
        last_lines.append(line)
        if len(last_lines) > 80:
            last_lines = last_lines[-80:]

    return_code = process.wait()
    if return_code != 0:
        tail = "".join(last_lines[-30:])
        raise RuntimeError(
            f"MetaUmbra scoring failed (exit={return_code}). Last output:\n{tail}"
        )
    if not Path(output_path).is_file():
        raise RuntimeError(
            f"MetaUmbra scoring finished but output file was not found: {output_path}"
        )
    return {
        "output": output_path,
        "metaumbra_peptide_score_col": peptide_score_col,
        "metaumbra_peptide_error_col": peptide_error_col,
        "metaumbra_single_peptide_error_rate_upper_bound": (
            single_peptide_error_rate_upper_bound
        ),
        "metaumbra_version": metaumbra_version,
    }


class GlobalOTFAnnotator:
    """Shared backend for GUI and CLI global peptide-to-OTF annotation."""

    def __init__(
        self,
        *,
        peptide_table_path: str,
        output_path: str,
        taxafunc_anno_db_path: str | None = None,
        db_path: str | None = None,
        digested_genome_folders: str | Iterable[str] | None = None,
        selection_mode: str | None = None,
        selected_genomes: str | Iterable[str] | None = None,
        genome_list_path: str | None = None,
        peptide_col: str = "Sequence",
        intensity_col_prefix: str = "Intensity",
        table_separator: str = "\t",
        protein_peptide_coverage_cutoff: float = 1.0,
        lca_threshold: float = 1.0,
        genome_mode: bool = True,
        distinct_genome_threshold: int = 0,
        exclude_protein_startwith: str | None = None,
        protein_separator: str = ";",
        protein_genome_separator: str = "_",
        duplicate_peptide_handling_mode: str = "sum",
        n_jobs: int | None = None,
        diann_intensity_col: str | None = None,
        metaumbra_peptide_score_col: str = "Evidence",
        metaumbra_peptide_error_col: str = "Q.Value",
        metaumbra_single_peptide_error_rate_upper_bound: float = 0.3,
        metaumbra_genome_qvalue_cutoff: float = 0.05,
        selected_genome_source: str | None = None,
    ) -> None:
        self.peptide_table_path = Path(peptide_table_path)
        self.output_path = Path(output_path)
        self.taxafunc_anno_db_path = (
            Path(taxafunc_anno_db_path) if taxafunc_anno_db_path else None
        )
        self.db_path = Path(db_path) if db_path else None
        self.digested_genome_folders = _normalise_paths(digested_genome_folders)
        self.selection_mode = selection_mode or (
            "metaumbra" if self.digested_genome_folders else "automatic"
        )
        self.selected_genomes = _normalise_genomes(selected_genomes)
        self.genome_list_path = Path(genome_list_path) if genome_list_path else None
        self.peptide_col = peptide_col
        self.intensity_col_prefix = intensity_col_prefix
        self.table_separator = table_separator
        self.protein_peptide_coverage_cutoff = protein_peptide_coverage_cutoff
        self.lca_threshold = lca_threshold
        self.genome_mode = genome_mode
        self.distinct_genome_threshold = distinct_genome_threshold
        self.exclude_protein_startwith = exclude_protein_startwith
        self.protein_separator = protein_separator
        self.protein_genome_separator = protein_genome_separator
        self.duplicate_peptide_handling_mode = duplicate_peptide_handling_mode
        self.n_jobs = n_jobs
        self.diann_intensity_col = diann_intensity_col
        self.metaumbra_peptide_score_col = metaumbra_peptide_score_col
        self.metaumbra_peptide_error_col = metaumbra_peptide_error_col
        self.metaumbra_single_peptide_error_rate_upper_bound = (
            metaumbra_single_peptide_error_rate_upper_bound
        )
        self.metaumbra_genome_qvalue_cutoff = metaumbra_genome_qvalue_cutoff
        self.selected_genome_source = selected_genome_source
        self.warnings: list[str] = []

    @property
    def temp_dir(self) -> Path:
        path = self.output_path.parent / "metax_temp"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def metaumbra_output_path(self) -> Path:
        stem = self.output_path.stem or "OTF"
        return self.temp_dir / f"{stem}_metaumbra_genome_presence.tsv"

    @property
    def info_path(self) -> Path:
        return self.output_path.with_name(f"{self.output_path.stem}_info.txt")

    def _validate(self) -> None:
        if self.selection_mode not in GLOBAL_SELECTION_MODES:
            raise AnnotationConfigurationError(
                f"selection_mode must be one of {sorted(GLOBAL_SELECTION_MODES)}"
            )
        if not self.peptide_table_path.is_file():
            raise FileNotFoundError(f"Peptide table not found: {self.peptide_table_path}")
        if not self.output_path.parent.is_dir():
            raise FileNotFoundError(
                f"Output directory not found: {self.output_path.parent}"
            )
        if self.selection_mode != "metaumbra-only":
            if self.taxafunc_anno_db_path is None:
                raise AnnotationConfigurationError(
                    "taxafunc_anno_db_path is required for global OTF annotation"
                )
            if not self.taxafunc_anno_db_path.is_file():
                raise FileNotFoundError(
                    f"Taxa-function database not found: {self.taxafunc_anno_db_path}"
                )
            if (self.db_path is None) == (not self.digested_genome_folders):
                raise AnnotationConfigurationError(
                    "Exactly one of db_path or digested_genome_folders is required"
                )
        if self.db_path is not None and not self.db_path.is_file():
            raise FileNotFoundError(f"Peptide database not found: {self.db_path}")
        for digest_dir in self.digested_genome_folders:
            if not Path(digest_dir).is_dir():
                raise FileNotFoundError(f"Digested genome directory not found: {digest_dir}")
        if self.selection_mode in {"metaumbra", "metaumbra-only"} and not self.digested_genome_folders:
            raise AnnotationConfigurationError(
                f"selection_mode={self.selection_mode!r} requires digested_genome_folders"
            )
        if self.genome_list_path is not None and not self.genome_list_path.is_file():
            raise FileNotFoundError(f"Genome list not found: {self.genome_list_path}")
        if not 0 <= self.lca_threshold <= 1:
            raise AnnotationConfigurationError("lca_threshold must be between 0 and 1")
        if not 0 < self.protein_peptide_coverage_cutoff <= 1:
            raise AnnotationConfigurationError(
                "protein_peptide_coverage_cutoff must be greater than 0 and at most 1"
            )
        if self.distinct_genome_threshold < 0:
            raise AnnotationConfigurationError(
                "distinct_genome_threshold must be greater than or equal to 0"
            )
        if self.n_jobs is not None and self.n_jobs < 1:
            raise AnnotationConfigurationError("n_jobs must be greater than or equal to 1")
        if not 0 < self.metaumbra_single_peptide_error_rate_upper_bound <= 1:
            raise AnnotationConfigurationError(
                "metaumbra_single_peptide_error_rate_upper_bound must be greater than 0 "
                "and at most 1"
            )
        if not 0 < self.metaumbra_genome_qvalue_cutoff <= 1:
            raise AnnotationConfigurationError(
                "metaumbra_genome_qvalue_cutoff must be greater than 0 and at most 1"
            )
        if self.duplicate_peptide_handling_mode not in {
            "sum", "max", "min", "mean", "first", "keep"
        }:
            raise AnnotationConfigurationError(
                "duplicate_peptide_handling_mode must be one of "
                "sum, max, min, mean, first, keep"
            )

    def _prepare_input(self) -> tuple[str, str, str, str, dict[str, object]]:
        input_path = str(self.peptide_table_path)
        separator = self.table_separator
        peptide_col = self.peptide_col
        intensity_prefix = self.intensity_col_prefix
        metadata: dict[str, object] = {}
        if not is_parquet_path(self.peptide_table_path):
            return input_path, separator, peptide_col, intensity_prefix, metadata

        parquet_columns = read_parquet_columns(self.peptide_table_path)
        if not is_diann_parquet(parquet_columns):
            if self.selection_mode in {"metaumbra", "metaumbra-only"}:
                raise AnnotationConfigurationError(
                    "MetaUmbra scoring accepts tabular peptide input or long-format "
                    "DIA-NN parquet; this parquet does not contain the DIA-NN core columns."
                )
            return input_path, separator, peptide_col, intensity_prefix, metadata

        print(f"Preparing DIA-NN parquet peptide table: {self.peptide_table_path}")
        prepared = prepare_diann_parquet_for_direct_otf(
            self.peptide_table_path,
            require_score_columns=self.selection_mode in {"metaumbra", "metaumbra-only"},
            intensity_col=self.diann_intensity_col,
        )
        prepared_path = self.temp_dir / (
            f"{self.output_path.stem or 'pep_direct_to_otf'}_diann_parquet_peptide_table.tsv"
        )
        prepared.dataframe.to_csv(prepared_path, sep="\t", index=False)
        metadata = {**prepared.metadata, "prepared_peptide_table_path": str(prepared_path)}
        return (
            str(prepared_path),
            "\t",
            prepared.peptide_col,
            prepared.intensity_col_prefix,
            metadata,
        )

    def _resolve_selected_genomes(self) -> list[str]:
        genomes = list(self.selected_genomes)
        if self.genome_list_path is not None:
            genomes.extend(
                read_genome_list_file(
                    self.genome_list_path,
                    qvalue_cutoff=self.metaumbra_genome_qvalue_cutoff,
                )
            )
        return _normalise_genomes(genomes)

    def run(self) -> GlobalOTFRunResult:
        stages: dict[str, object] = {}
        stage_started = time.perf_counter()
        self._validate()
        stages["validation"] = {
            "status": "success",
            "duration_seconds": _elapsed(stage_started),
        }

        stage_started = time.perf_counter()
        (
            peptide_table_path,
            table_separator,
            peptide_col,
            intensity_col_prefix,
            input_metadata,
        ) = self._prepare_input()
        stages["input_preparation"] = {
            "status": "success",
            "duration_seconds": _elapsed(stage_started),
        }

        input_format = str(
            input_metadata.get(
                "input_peptide_table_format",
                "parquet" if is_parquet_path(self.peptide_table_path) else "delimited_text",
            )
        )
        peptide_input = _file_descriptor(
            self.peptide_table_path,
            format_name=input_format,
        )
        if "diann_intensity_column" in input_metadata:
            peptide_input["diann"] = {
                "intensity_column": input_metadata["diann_intensity_column"],
                "run_to_sample_column": input_metadata["diann_run_to_sample_column"],
            }
        inputs: dict[str, object] = {"peptide_table": peptide_input}
        if self.taxafunc_anno_db_path is not None:
            inputs["taxafunc_database"] = _file_descriptor(
                self.taxafunc_anno_db_path,
                format_name="sqlite",
            )
        if self.db_path is not None:
            inputs["peptide_mapping"] = {
                "type": "sqlite",
                "database": _file_descriptor(self.db_path, format_name="sqlite"),
            }
        elif self.digested_genome_folders:
            inputs["peptide_mapping"] = {
                "type": "digested_genome_directories",
                "directories": [{"path": path} for path in self.digested_genome_folders],
            }
        if self.genome_list_path is not None:
            inputs["genome_list"] = _file_descriptor(self.genome_list_path)

        parameters: dict[str, object] = {
            "selection_mode": self.selection_mode,
            "peptide_column": peptide_col,
            "intensity_column_prefix": intensity_col_prefix,
            "table_separator": table_separator,
            "protein_peptide_coverage_cutoff": self.protein_peptide_coverage_cutoff,
            "lca_threshold": self.lca_threshold,
            "genome_mode": self.genome_mode,
            "distinct_genome_threshold": self.distinct_genome_threshold,
            "exclude_protein_startswith": self.exclude_protein_startwith,
            "protein_separator": self.protein_separator,
            "protein_genome_separator": self.protein_genome_separator,
            "duplicate_peptide_handling_mode": self.duplicate_peptide_handling_mode,
            "n_jobs": self.n_jobs,
        }
        parameters = {key: value for key, value in parameters.items() if value is not None}
        if self.selection_mode in {"metaumbra", "metaumbra-only"}:
            parameters["metaumbra"] = {
                "peptide_score_column": self.metaumbra_peptide_score_col,
                "peptide_error_column": self.metaumbra_peptide_error_col,
                "single_peptide_error_rate_upper_bound": (
                    self.metaumbra_single_peptide_error_rate_upper_bound
                ),
                "genome_qvalue_cutoff": self.metaumbra_genome_qvalue_cutoff,
            }

        outputs: dict[str, object] = {}
        prepared_path = input_metadata.get("prepared_peptide_table_path")
        if prepared_path:
            outputs["prepared_peptide_table"] = _file_descriptor(
                str(prepared_path), format_name="tsv"
            )

        input_metric_keys = {
            "input_rows": "rows",
            "input_columns": "columns",
            "input_rows_with_required_values": "rows_with_required_values",
            "input_runs": "runs",
            "input_unique_peptides": "unique_peptides",
            "aggregated_run_peptide_rows": "aggregated_run_peptide_rows",
            "prepared_peptide_rows": "prepared_peptides",
            "prepared_sample_columns": "sample_columns",
        }
        input_metrics = {
            output_key: input_metadata[input_key]
            for input_key, output_key in input_metric_keys.items()
            if input_key in input_metadata
        }
        metrics: dict[str, object] = {"input": input_metrics}
        software: dict[str, str] = {}
        metaumbra_metadata: dict[str, object] = {}

        stage_started = time.perf_counter()
        selected_genomes = self._resolve_selected_genomes()
        stages["genome_selection_input"] = {
            "status": "success",
            "duration_seconds": _elapsed(stage_started),
        }
        if self.selection_mode == "provided" and not selected_genomes:
            raise AnnotationConfigurationError(
                "selection_mode='provided' requires selected_genomes or genome_list_path"
            )

        genome_selection: dict[str, object] = {"method": self.selection_mode}
        selection_source = self.selected_genome_source or (
            str(self.genome_list_path) if self.genome_list_path else None
        )
        if selection_source:
            genome_selection["source"] = selection_source
        if self.selection_mode in {"metaumbra", "metaumbra-only"} or self.genome_list_path:
            genome_selection["qvalue_cutoff"] = self.metaumbra_genome_qvalue_cutoff

        if self.selection_mode in {"metaumbra", "metaumbra-only"}:
            scoring_output = (
                self.output_path
                if self.selection_mode == "metaumbra-only"
                else self.metaumbra_output_path
            )
            stage_started = time.perf_counter()
            scoring_result = run_metaumbra_scoring(
                peptide_table_path=peptide_table_path,
                digested_genome_folders=self.digested_genome_folders,
                output_path=str(scoring_output),
                peptide_col=peptide_col,
                peptide_score_col=self.metaumbra_peptide_score_col,
                peptide_error_col=self.metaumbra_peptide_error_col,
                single_peptide_error_rate_upper_bound=(
                    self.metaumbra_single_peptide_error_rate_upper_bound
                ),
            )
            stages["metaumbra_scoring"] = {
                "status": "success",
                "duration_seconds": _elapsed(stage_started),
            }
            outputs["genome_presence"] = _file_descriptor(
                scoring_output, format_name="tsv"
            )
            software["metaumbra_version"] = str(scoring_result["metaumbra_version"])
            metaumbra_metadata = {
                "metaumbra_genome_presence_path": str(scoring_output),
                "metaumbra_version": str(scoring_result["metaumbra_version"]),
                "metaumbra_peptide_score_col": self.metaumbra_peptide_score_col,
                "metaumbra_peptide_error_col": self.metaumbra_peptide_error_col,
                "metaumbra_single_peptide_error_rate_upper_bound": (
                    self.metaumbra_single_peptide_error_rate_upper_bound
                ),
                "metaumbra_genome_qvalue_cutoff": self.metaumbra_genome_qvalue_cutoff,
            }
            genome_presence = pd.read_csv(scoring_output, sep="\t")
            genome_selection["genomes_evaluated"] = int(genome_presence.shape[0])
            if self.selection_mode == "metaumbra-only":
                rows, columns = genome_presence.shape
                genome_selection["genomes_selected"] = None
                outputs["genome_presence"].update(
                    {"rows": int(rows), "columns": int(columns)}
                )
                metrics["output"] = {"rows": int(rows), "columns": int(columns)}
                return GlobalOTFRunResult(
                    output_path=str(scoring_output),
                    info_path=None,
                    annotation_summary_path=None,
                    inputs=inputs,
                    parameters=parameters,
                    stages=stages,
                    genome_selection=genome_selection,
                    metrics=metrics,
                    outputs=outputs,
                    software=software,
                    warnings=list(self.warnings),
                    rows=int(rows),
                    column_count=int(columns),
                )
            selected_genomes = read_genome_list_file(
                scoring_output,
                qvalue_cutoff=self.metaumbra_genome_qvalue_cutoff,
            )
            if not selected_genomes:
                raise RuntimeError(
                    "MetaUmbra scoring did not select any genomes with the current q-value cutoff."
                )
            metaumbra_metadata["selected_genomes_from_metaumbra_count"] = len(
                selected_genomes
            )

        genome_selection["genomes_selected"] = len(selected_genomes)
        if selected_genomes:
            genome_selection["selected_genome_ids"] = selected_genomes

        genome_list = selected_genomes or None
        selected_set = set(selected_genomes) if selected_genomes else None
        if selected_genomes:
            print(f"Selected genomes for peptide mapping: {len(selected_genomes)}")

        selection_metadata = {
            "workflow": "Peptide Direct to OTFs (MetaUmbra)",
            "genome_selection_method": self.selection_mode,
            "metaumbra_scoring_run": self.selection_mode == "metaumbra",
            "selected_genomes_input_count": len(selected_genomes),
            **metaumbra_metadata,
            **input_metadata,
        }
        if selection_source:
            selection_metadata["selected_genome_source"] = selection_source
        stage_started = time.perf_counter()
        mapper = peptideProteinsMapper(
            peptide_table_path=peptide_table_path,
            db_path=str(self.db_path) if self.db_path else None,
            digested_genome_folders=self.digested_genome_folders or None,
            table_separator=table_separator,
            peptide_col=peptide_col,
            intensity_col_prefix=intensity_col_prefix,
            protein_peptide_coverage_cutoff=self.protein_peptide_coverage_cutoff,
            output_path=str(self.output_path),
            temp_dir=str(self.temp_dir),
            selected_genomes_set=selected_set,
            genome_list=genome_list,
            continue_base_on_annotaied_peptide_table=False,
            digested_parallel_backend="subprocess",
            duplicate_peptide_handling_mode=self.duplicate_peptide_handling_mode,
            protein_genome_separator=self.protein_genome_separator,
            n_jobs=self.n_jobs,
        )
        dataframe = mapper.all_in_one(
            taxafunc_anno_db_path=str(self.taxafunc_anno_db_path),
            lca_threshold=self.lca_threshold,
            genome_mode=self.genome_mode,
            distinct_genome_threshold=self.distinct_genome_threshold,
            exclude_protein_startwith=self.exclude_protein_startwith,
            protein_separator=self.protein_separator,
            protein_genome_separator=self.protein_genome_separator,
            genome_list=genome_list,
            duplicate_peptide_handling_mode=self.duplicate_peptide_handling_mode,
            genome_selection_metadata=selection_metadata,
        )
        stages["peptide_mapping_and_annotation"] = {
            "status": "success",
            "duration_seconds": _elapsed(stage_started),
        }
        if not self.output_path.is_file():
            raise RuntimeError(
                f"Annotation finished but output file was not found: {self.output_path}"
            )
        info_path = str(self.info_path) if self.info_path.is_file() else None

        peptides_before = int(getattr(mapper, "original_peptides_before_mapping", 0))
        peptides_after = int(getattr(mapper, "peptides_after_mapping", 0))
        mapping_metrics = {
            "peptides_before_mapping": peptides_before,
            "peptides_after_mapping": peptides_after,
            "unmapped_peptides": int(getattr(mapper, "removed_peptides_no_matched", 0)),
            "mapping_rate": (
                round(peptides_after / peptides_before, 6) if peptides_before else None
            ),
            "total_proteins_found": (
                int(len(mapper.protein_ranked_table))
                if getattr(mapper, "protein_ranked_table", None) is not None
                else None
            ),
            "selected_proteins": int(getattr(mapper, "selected_proteins_num", 0)),
        }
        metrics["mapping"] = mapping_metrics

        annotation_stats = dict(getattr(mapper, "annotation_run_stats", {}))
        output_metrics = dict(getattr(mapper, "annotation_output_metrics", {}))
        sample_columns = list(output_metrics.get("sample_columns", []))
        output_metrics["samples"] = _sample_metrics(dataframe, sample_columns)
        output_metrics["filters"] = {
            "empty_protein_rows_removed": int(
                annotation_stats.get("removed_empty_protein", 0)
            ),
            "all_zero_sample_rows_removed": int(
                annotation_stats.get("removed_zero_intensity", 0)
            ),
            "duplicate_rows_removed": int(annotation_stats.get("duplicate_removed", 0)),
            "excluded_protein_rows_removed": int(
                annotation_stats.get("excluded_proteins_removed", 0)
            ),
            "genome_filter_rows_removed": int(
                annotation_stats.get("genome_filtered_removed", 0)
            ),
        }
        metrics["output"] = output_metrics

        if self.selection_mode == "automatic":
            genome_selection["genomes_selected"] = int(
                getattr(mapper, "selected_genomes_num", 0)
            )

        outputs["otf"] = _file_descriptor(self.output_path, format_name="tsv")
        outputs["otf"].update(
            {"rows": int(dataframe.shape[0]), "columns": int(dataframe.shape[1])}
        )
        if info_path:
            outputs["annotation_summary"] = _file_descriptor(
                info_path, format_name="text"
            )
        return GlobalOTFRunResult(
            output_path=str(self.output_path),
            info_path=info_path,
            annotation_summary_path=info_path,
            inputs=inputs,
            parameters=parameters,
            stages=stages,
            genome_selection=genome_selection,
            metrics=metrics,
            outputs=outputs,
            software=software,
            warnings=list(self.warnings),
            rows=int(dataframe.shape[0]),
            column_count=int(dataframe.shape[1]),
        )
