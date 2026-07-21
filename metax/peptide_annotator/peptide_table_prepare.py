from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


DIANN_PEPTIDE_COLUMN = "Stripped.Sequence"
DIANN_RUN_COLUMN = "Run"
DIANN_SCORE_COLUMN = "Evidence"
DIANN_ERROR_COLUMN = "Q.Value"
DIANN_INTENSITY_CANDIDATES = (
    "Precursor.Normalised",
    "Precursor.Quantity",
)
DIANN_OUTPUT_SAMPLE_COLUMN_PREFIX = "Intensity_"
DIANN_RUN_WRAPPER_SUFFIXES = (".dia",)
DIANN_ACQUISITION_SUFFIXES = (".raw", ".mzml", ".mzxml")


@dataclass(frozen=True)
class PeptideTableSchema:
    peptide_col: str
    intensity_col: str
    intensity_col_prefix: str
    sample_col: str | None = None
    score_col: str | None = None
    error_col: str | None = None


@dataclass(frozen=True)
class PreparedDIANNPeptideTable:
    dataframe: pd.DataFrame
    schema: PeptideTableSchema
    metadata: dict

    @property
    def peptide_col(self) -> str:
        return self.schema.peptide_col

    @property
    def intensity_col(self) -> str:
        return self.schema.intensity_col

    @property
    def intensity_col_prefix(self) -> str:
        return self.schema.intensity_col_prefix


def is_parquet_path(file_path: str | Path) -> bool:
    return Path(file_path).suffix.lower() in {".parquet", ".parq", ".pq"}


def read_parquet_columns(parquet_path: str | Path) -> list[str]:
    try:
        import pyarrow.parquet as pq

        return [str(name) for name in pq.ParquetFile(parquet_path).schema.names]
    except Exception as exc:
        raise RuntimeError(
            "Failed to read parquet metadata. Make sure the file is a valid parquet file."
        ) from exc


def available_diann_intensity_columns(columns: Iterable[str]) -> list[str]:
    available = {str(column) for column in columns}
    return [
        candidate
        for candidate in DIANN_INTENSITY_CANDIDATES
        if candidate in available
    ]


def select_diann_intensity_column(
    columns: Iterable[str],
    intensity_col: str | None = None,
) -> str:
    available = {str(column) for column in columns}
    if intensity_col is not None:
        intensity_col = str(intensity_col).strip()
        if intensity_col not in DIANN_INTENSITY_CANDIDATES:
            raise ValueError(
                f"Unsupported DIA-NN intensity column: {intensity_col!r}. "
                "Expected one of: "
                + ", ".join(DIANN_INTENSITY_CANDIDATES)
            )
        if intensity_col not in available:
            raise ValueError(
                f"Selected DIA-NN intensity column {intensity_col!r} "
                "was not found in the parquet file."
            )
        return intensity_col

    available_candidates = available_diann_intensity_columns(available)
    if available_candidates:
        return available_candidates[0]
    raise ValueError(
        "DIA-NN parquet is missing an intensity column. Expected one of: "
        + ", ".join(DIANN_INTENSITY_CANDIDATES)
    )


def is_diann_parquet(columns: Iterable[str]) -> bool:
    available = {str(column) for column in columns}
    return (
        has_diann_core_columns(available)
        and any(candidate in available for candidate in DIANN_INTENSITY_CANDIDATES)
    )


def has_diann_core_columns(columns: Iterable[str]) -> bool:
    available = {str(column) for column in columns}
    return {DIANN_RUN_COLUMN, DIANN_PEPTIDE_COLUMN}.issubset(available)


def resolve_diann_parquet_schema(
    columns: Iterable[str],
    *,
    require_score_columns: bool = False,
    intensity_col: str | None = None,
) -> PeptideTableSchema:
    available = {str(column) for column in columns}
    required = [DIANN_RUN_COLUMN, DIANN_PEPTIDE_COLUMN]
    if require_score_columns:
        required.extend([DIANN_SCORE_COLUMN, DIANN_ERROR_COLUMN])
    missing = [column for column in required if column not in available]
    if missing:
        raise ValueError(f"DIA-NN parquet is missing required columns: {missing}")

    intensity_col = select_diann_intensity_column(available, intensity_col)
    return PeptideTableSchema(
        peptide_col=DIANN_PEPTIDE_COLUMN,
        intensity_col=intensity_col,
        intensity_col_prefix=diann_parquet_intensity_prefix(intensity_col),
        sample_col=DIANN_RUN_COLUMN,
        score_col=DIANN_SCORE_COLUMN if DIANN_SCORE_COLUMN in available else None,
        error_col=DIANN_ERROR_COLUMN if DIANN_ERROR_COLUMN in available else None,
    )


def diann_parquet_required_columns(
    columns: Iterable[str],
    *,
    require_score_columns: bool = False,
    intensity_col: str | None = None,
) -> list[str]:
    schema = resolve_diann_parquet_schema(
        columns,
        require_score_columns=require_score_columns,
        intensity_col=intensity_col,
    )
    required = [schema.sample_col, schema.peptide_col]
    if require_score_columns:
        required.extend([schema.score_col, schema.error_col])
    return [column for column in required if column is not None] + [schema.intensity_col]


def diann_parquet_intensity_prefix(_intensity_col: str) -> str:
    """Return the canonical OTF sample prefix for any DIA-NN intensity source."""
    return DIANN_OUTPUT_SAMPLE_COLUMN_PREFIX


def normalize_sample_identifier(value: object) -> str:
    """Return a path-free sample ID with known DIA-NN/raw suffixes removed."""
    name = Path(str(value).strip().replace("\\", "/")).name

    # DIA-NN matrix headers may append ``.dia`` to the original acquisition
    # filename (for example, ``sample.raw.dia``). Remove the wrapper first so
    # the underlying acquisition suffix can be recognized next.
    for suffix_group in (DIANN_RUN_WRAPPER_SUFFIXES, DIANN_ACQUISITION_SUFFIXES):
        lower_name = name.lower()
        for suffix in suffix_group:
            if lower_name.endswith(suffix):
                name = name[: -len(suffix)]
                break
    return name


def _safe_sample_name(run: str) -> str:
    run = str(run).strip()
    run_name = normalize_sample_identifier(run) if run else "unknown_run"
    run_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", run_name).strip("_")
    return run_name or "unknown_run"


def build_diann_run_to_sample_column_map(
    runs: Iterable[object],
    sample_column_prefix: str,
) -> dict[str, str]:
    run_to_column: dict[str, str] = {}
    used_columns: set[str] = set()
    for run in sorted({str(run) for run in runs}):
        base_column = f"{sample_column_prefix}{_safe_sample_name(run)}"
        column = base_column
        suffix = 2
        while column in used_columns:
            column = f"{base_column}_{suffix}"
            suffix += 1
        used_columns.add(column)
        run_to_column[run] = column
    return run_to_column


def prepare_diann_parquet_for_direct_otf(
    parquet_path: str | Path,
    *,
    require_score_columns: bool = False,
    sample_column_prefix: str | None = None,
    intensity_col: str | None = None,
) -> PreparedDIANNPeptideTable:
    parquet_path = str(parquet_path)
    available_columns = read_parquet_columns(parquet_path)
    schema = resolve_diann_parquet_schema(
        available_columns,
        require_score_columns=require_score_columns,
        intensity_col=intensity_col,
    )
    required_columns = [schema.sample_col, schema.peptide_col]
    if require_score_columns:
        required_columns.extend([schema.score_col, schema.error_col])
    required_columns = [
        column for column in required_columns if column is not None
    ] + [schema.intensity_col]
    intensity_col = required_columns[-1]
    read_columns = list(required_columns)

    try:
        df = pd.read_parquet(parquet_path, columns=read_columns)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to read DIA-NN parquet columns: {read_columns}"
        ) from exc

    input_rows = int(df.shape[0])
    df = df.dropna(subset=[DIANN_RUN_COLUMN, DIANN_PEPTIDE_COLUMN]).copy()
    if df.empty:
        raise ValueError(
            f"DIA-NN parquet contains no rows with both {DIANN_RUN_COLUMN} "
            f"and {DIANN_PEPTIDE_COLUMN}."
        )

    df[DIANN_RUN_COLUMN] = df[DIANN_RUN_COLUMN].astype(str)
    df[DIANN_PEPTIDE_COLUMN] = df[DIANN_PEPTIDE_COLUMN].astype(str)
    numeric_columns = [intensity_col]
    for optional_col in (DIANN_SCORE_COLUMN, DIANN_ERROR_COLUMN):
        if optional_col in df.columns:
            numeric_columns.append(optional_col)
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    aggregations: dict[str, tuple[str, str]] = {
        intensity_col: (intensity_col, "sum"),
    }
    if DIANN_SCORE_COLUMN in df.columns:
        aggregations[DIANN_SCORE_COLUMN] = (DIANN_SCORE_COLUMN, "max")
    if DIANN_ERROR_COLUMN in df.columns:
        aggregations[DIANN_ERROR_COLUMN] = (DIANN_ERROR_COLUMN, "min")

    grouped = (
        df.groupby([DIANN_RUN_COLUMN, DIANN_PEPTIDE_COLUMN], as_index=False)
        .agg(**aggregations)
    )

    if sample_column_prefix is None:
        sample_column_prefix = schema.intensity_col_prefix
    if sample_column_prefix != schema.intensity_col_prefix:
        schema = PeptideTableSchema(
            peptide_col=schema.peptide_col,
            intensity_col=schema.intensity_col,
            intensity_col_prefix=sample_column_prefix,
            sample_col=schema.sample_col,
            score_col=schema.score_col,
            error_col=schema.error_col,
        )

    run_to_column = build_diann_run_to_sample_column_map(
        grouped[DIANN_RUN_COLUMN].unique(),
        sample_column_prefix,
    )

    grouped["sample_col"] = grouped[DIANN_RUN_COLUMN].map(run_to_column)
    wide = (
        grouped.pivot_table(
            index=DIANN_PEPTIDE_COLUMN,
            columns="sample_col",
            values=intensity_col,
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )

    summary_aggregations: dict[str, tuple[str, object]] = {
        DIANN_RUN_COLUMN: (
            DIANN_RUN_COLUMN,
            lambda values: ";".join(sorted(set(map(str, values)))),
        ),
        intensity_col: (intensity_col, "sum"),
    }
    if DIANN_SCORE_COLUMN in grouped.columns:
        summary_aggregations[DIANN_SCORE_COLUMN] = (DIANN_SCORE_COLUMN, "max")
    if DIANN_ERROR_COLUMN in grouped.columns:
        summary_aggregations[DIANN_ERROR_COLUMN] = (DIANN_ERROR_COLUMN, "min")

    summary = (
        grouped.groupby(DIANN_PEPTIDE_COLUMN, as_index=False)
        .agg(**summary_aggregations)
    )
    prepared_df = summary.merge(wide, on=DIANN_PEPTIDE_COLUMN, how="left")
    leading_columns = [
        DIANN_RUN_COLUMN,
        DIANN_PEPTIDE_COLUMN,
        DIANN_SCORE_COLUMN,
        DIANN_ERROR_COLUMN,
        intensity_col,
    ]
    ordered_columns = [
        column for column in leading_columns if column in prepared_df.columns
    ] + list(run_to_column.values())
    prepared_df = prepared_df.loc[:, ordered_columns]

    metadata = {
        "input_peptide_table_format": "diann_parquet",
        "input_peptide_table_original_path": parquet_path,
        "input_rows": input_rows,
        "input_columns": len(available_columns),
        "input_rows_with_required_values": int(df.shape[0]),
        "input_runs": int(df[DIANN_RUN_COLUMN].nunique(dropna=True)),
        "input_unique_peptides": int(df[DIANN_PEPTIDE_COLUMN].nunique(dropna=True)),
        "aggregated_run_peptide_rows": int(grouped.shape[0]),
        "diann_intensity_column": intensity_col,
        "diann_run_to_sample_column": dict(run_to_column),
        "prepared_peptide_rows": int(prepared_df.shape[0]),
        "prepared_sample_columns": len(run_to_column),
        "prepared_intensity_col_prefix": sample_column_prefix,
    }
    return PreparedDIANNPeptideTable(
        dataframe=prepared_df,
        schema=schema,
        metadata=metadata,
    )
