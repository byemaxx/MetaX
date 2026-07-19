from __future__ import annotations

import json
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


SCHEMA_VERSION = "metaumbra.genome_selection_manifest.v1"
_TOP_LEVEL_FIELDS = {
    "schema_version",
    "generated_by",
    "unit_definition",
    "selection",
    "inputs",
    "units",
    "artifacts",
    "warnings",
}
_GENOME_THRESHOLDS = {"q0.05", "q0.01"}


@dataclass
class GenomeSelectionUnitSpec:
    analysis_unit_id: str
    sample_ids: list[str]
    genome_ids: list[str]
    n_samples: int

    @property
    def sample_columns(self) -> list[str]:
        """Prepared-table mapping uses the manifest's canonical sample IDs."""
        return self.sample_ids


@dataclass
class GenomeSelectionManifest:
    schema_version: str
    generated_by: dict
    unit_definition: dict
    selection: dict
    inputs: dict
    artifacts: dict
    warnings: list[str]
    units: dict[str, GenomeSelectionUnitSpec]
    selected_genome_threshold: str


def _normalize_threshold_alias(genome_threshold: str | None, default_threshold: str) -> tuple[str, str]:
    threshold = default_threshold if genome_threshold in (None, "", "auto") else str(genome_threshold)
    cleaned = threshold.strip().lower()
    aliases = {
        "q0.05": ("q0.05", "genome_ids_q005"),
        "q005": ("q0.05", "genome_ids_q005"),
        "0.05": ("q0.05", "genome_ids_q005"),
        "q0.01": ("q0.01", "genome_ids_q001"),
        "q001": ("q0.01", "genome_ids_q001"),
        "0.01": ("q0.01", "genome_ids_q001"),
    }
    if cleaned not in aliases:
        raise ValueError(
            "genome_threshold must be one of q0.05, q005, 0.05, q0.01, q001, 0.01, or auto"
        )
    return aliases[cleaned]


def _warn_or_raise(message: str, strict: bool) -> None:
    if strict:
        raise ValueError(message)
    warnings.warn(message, stacklevel=2)


def _require_mapping(value: object, label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _require_string(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    return value


def _require_integer(value: object, label: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be greater than or equal to {minimum}")
    return value


def _require_unique_string_list(
    value: object,
    label: str,
    *,
    allow_empty: bool,
    unique: bool = True,
) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array of strings")
    if not allow_empty and not value:
        raise ValueError(f"{label} must contain at least one item")
    if any(not isinstance(item, str) for item in value):
        raise ValueError(f"{label} must contain only strings")
    if unique and len(set(value)) != len(value):
        raise ValueError(f"{label} must contain unique items")
    return list(value)


def _validate_manifest_structure(data: object) -> dict:
    manifest = _require_mapping(data, "genome selection manifest")
    missing_fields = sorted(_TOP_LEVEL_FIELDS - set(manifest))
    if missing_fields:
        raise ValueError(
            "genome selection manifest is missing required fields: "
            + ", ".join(missing_fields)
        )
    unknown_fields = sorted(set(manifest) - _TOP_LEVEL_FIELDS)
    if unknown_fields:
        raise ValueError(
            "genome selection manifest contains unsupported fields: "
            + ", ".join(unknown_fields)
        )

    generated_by = _require_mapping(manifest["generated_by"], "generated_by")
    if generated_by.get("software") != "MetaUmbra":
        raise ValueError("generated_by.software must be 'MetaUmbra'")
    for field in ("version", "run_id", "generated_at"):
        _require_string(generated_by.get(field), f"generated_by.{field}")

    unit_definition = _require_mapping(
        manifest["unit_definition"],
        "unit_definition",
    )
    mode = _require_string(unit_definition.get("mode"), "unit_definition.mode")
    if mode not in {"all-samples", "per-sample", "metadata"}:
        raise ValueError(
            "unit_definition.mode must be 'all-samples', 'per-sample', or 'metadata'"
        )
    _require_string(
        unit_definition.get("sample_id_column"),
        "unit_definition.sample_id_column",
    )
    analysis_unit_column = unit_definition.get("analysis_unit_column")
    if analysis_unit_column is not None:
        _require_string(
            analysis_unit_column,
            "unit_definition.analysis_unit_column",
        )
    _require_integer(
        unit_definition.get("n_units"),
        "unit_definition.n_units",
        minimum=1,
    )

    selection = _require_mapping(manifest["selection"], "selection")
    default_threshold = _require_string(
        selection.get("default_genome_threshold"),
        "selection.default_genome_threshold",
    )
    if default_threshold not in _GENOME_THRESHOLDS:
        raise ValueError(
            "selection.default_genome_threshold must be 'q0.05' or 'q0.01'"
        )
    if selection.get("available_genome_thresholds") != ["q0.05", "q0.01"]:
        raise ValueError(
            "selection.available_genome_thresholds must be ['q0.05', 'q0.01']"
        )
    _require_string(selection.get("scoring_method"), "selection.scoring_method")

    _require_mapping(manifest["inputs"], "inputs")
    _require_mapping(manifest["artifacts"], "artifacts")
    _require_unique_string_list(
        manifest["warnings"],
        "warnings",
        allow_empty=True,
        unique=False,
    )
    return manifest


def load_genome_selection_manifest(
    manifest_path: str | Path,
    genome_threshold: str | None = None,
    strict: bool = True,
) -> GenomeSelectionManifest:
    manifest_path = Path(manifest_path)
    data = _validate_manifest_structure(
        json.loads(manifest_path.read_text(encoding="utf-8"))
    )

    schema_version = data.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        raise ValueError(f"Unsupported genome selection manifest schema_version: {schema_version!r}")

    unit_definition = data["unit_definition"]
    selection = data["selection"]
    default_threshold = str(selection.get("default_genome_threshold", "")).strip()
    selected_threshold, selected_genome_key = _normalize_threshold_alias(genome_threshold, default_threshold)

    raw_units = data["units"]
    if not isinstance(raw_units, dict) or not raw_units:
        raise ValueError("genome selection manifest must contain at least one unit")
    if unit_definition["n_units"] != len(raw_units):
        raise ValueError("unit_definition.n_units does not match units")

    seen_samples: dict[str, str] = {}
    units: dict[str, GenomeSelectionUnitSpec] = {}
    for analysis_unit_id, raw_unit in raw_units.items():
        if not isinstance(raw_unit, dict):
            raise ValueError(f"Unit {analysis_unit_id!r} must be an object")

        sample_columns = _require_unique_string_list(
            raw_unit.get("sample_ids"),
            f"Unit {analysis_unit_id!r}.sample_ids",
            allow_empty=False,
        )

        for sample in sample_columns:
            previous_unit = seen_samples.get(sample)
            if previous_unit is not None and previous_unit != analysis_unit_id:
                raise ValueError(
                    f"Sample {sample!r} is assigned to multiple units: "
                    f"{previous_unit!r} and {analysis_unit_id!r}"
                )
            seen_samples[sample] = str(analysis_unit_id)

        if selected_genome_key not in raw_unit:
            raise ValueError(f"Unit {analysis_unit_id!r} is missing {selected_genome_key}")
        q005 = _require_unique_string_list(
            raw_unit.get("genome_ids_q005"),
            f"Unit {analysis_unit_id!r}.genome_ids_q005",
            allow_empty=True,
        )
        q001 = _require_unique_string_list(
            raw_unit.get("genome_ids_q001"),
            f"Unit {analysis_unit_id!r}.genome_ids_q001",
            allow_empty=True,
        )
        genome_ids = q005 if selected_genome_key == "genome_ids_q005" else q001
        if not genome_ids:
            raise ValueError(
                f"Unit {analysis_unit_id!r} has no genomes at selected threshold {selected_threshold}"
            )

        n_samples = _require_integer(
            raw_unit.get("n_samples"),
            f"Unit {analysis_unit_id!r}.n_samples",
            minimum=1,
        )
        if n_samples != len(sample_columns):
            raise ValueError(
                f"Unit {analysis_unit_id!r} declares n_samples={n_samples}, "
                f"but has {len(sample_columns)} sample_ids"
            )

        missing = set(q001) - set(q005)
        if missing:
            preview = ", ".join(sorted(missing)[:10])
            _warn_or_raise(
                f"Unit {analysis_unit_id!r} has q0.01 genomes not present in q0.05: {preview}",
                strict=strict,
            )

        units[str(analysis_unit_id)] = GenomeSelectionUnitSpec(
            analysis_unit_id=str(analysis_unit_id),
            sample_ids=sample_columns,
            genome_ids=genome_ids,
            n_samples=n_samples,
        )

    generated_by = data["generated_by"]
    return GenomeSelectionManifest(
        schema_version=schema_version,
        generated_by=dict(generated_by),
        unit_definition=dict(unit_definition),
        selection=dict(selection),
        inputs=dict(data.get("inputs") or {}),
        artifacts=dict(data.get("artifacts") or {}),
        warnings=[str(item) for item in data.get("warnings", [])],
        units=units,
        selected_genome_threshold=selected_threshold,
    )


def _strip_intensity_prefix(value: str) -> str:
    if value.startswith("Intensity_"):
        return value[len("Intensity_") :]
    if value.startswith("Intensity "):
        return value[len("Intensity ") :]
    return value


def _strip_prefix(value: str, prefix: str | None) -> str:
    if prefix and value.startswith(prefix):
        return value[len(prefix) :]
    return value


def _strip_leading_underscores(value: str) -> str:
    return value.lstrip("_")


def _basename_without_raw_suffix(value: str) -> str:
    basename = Path(str(value).replace("\\", "/")).name
    lower = basename.lower()
    for suffix in (".raw", ".mzml", ".mzxml"):
        if lower.endswith(suffix):
            return basename[: -len(suffix)]
    return basename


def _candidate_matches(
    manifest_sample: str,
    peptide_columns: Iterable[str],
    output_sample_col_prefix: str,
    input_sample_col_prefix: str | None = None,
) -> dict[int, set[str]]:
    matches: dict[int, set[str]] = {i: set() for i in range(1, 10)}
    manifest_sample = str(manifest_sample)
    for column in peptide_columns:
        column = str(column)
        if column == manifest_sample:
            matches[1].add(column)
        if column == f"Intensity_{manifest_sample}":
            matches[2].add(column)
        if column == f"{output_sample_col_prefix}{manifest_sample}":
            matches[3].add(column)
        if input_sample_col_prefix and column == f"{input_sample_col_prefix}{manifest_sample}":
            matches[4].add(column)
        if _strip_intensity_prefix(column) == manifest_sample:
            matches[5].add(column)
        if _strip_prefix(column, output_sample_col_prefix) == manifest_sample:
            matches[6].add(column)
        if _strip_prefix(column, input_sample_col_prefix) == manifest_sample:
            matches[7].add(column)
        if _strip_leading_underscores(column) == _strip_leading_underscores(manifest_sample):
            matches[8].add(column)
        if _basename_without_raw_suffix(column) == _basename_without_raw_suffix(manifest_sample):
            matches[9].add(column)
    return matches


def resolve_manifest_sample_columns(
    peptide_columns: list[str],
    manifest_sample_columns: list[str],
    output_sample_col_prefix: str = "Intensity_",
    input_sample_col_prefix: str | None = None,
    match_mode: str = "auto",
    on_missing: str = "error",
) -> dict[str, str]:
    if match_mode != "auto":
        raise ValueError("Only match_mode='auto' is currently supported")
    if on_missing not in {"error", "warn-skip"}:
        raise ValueError("on_missing must be 'error' or 'warn-skip'")

    mapping: dict[str, str] = {}
    for sample in manifest_sample_columns:
        matches = _candidate_matches(
            sample,
            peptide_columns,
            output_sample_col_prefix,
            input_sample_col_prefix=input_sample_col_prefix,
        )
        chosen: str | None = None
        for priority in sorted(matches):
            candidates = sorted(matches[priority])
            if not candidates:
                continue
            if len(candidates) > 1:
                raise ValueError(
                    f"Manifest sample {sample!r} is ambiguous; matched peptide columns: {candidates}"
                )
            chosen = candidates[0]
            break

        if chosen is None:
            message = f"Manifest sample {sample!r} was not found in peptide table columns"
            if on_missing == "error":
                raise ValueError(message)
            warnings.warn(message, stacklevel=2)
            continue
        mapping[str(sample)] = chosen
    column_to_samples: dict[str, list[str]] = {}
    for sample, column in mapping.items():
        column_to_samples.setdefault(column, []).append(sample)
    duplicate_matches = {
        column: samples
        for column, samples in column_to_samples.items()
        if len(samples) > 1
    }
    if duplicate_matches:
        details = "; ".join(
            f"{column!r}: {samples}"
            for column, samples in sorted(duplicate_matches.items())
        )
        raise ValueError(
            "Manifest sample columns must map to distinct peptide table columns; "
            f"duplicate matches: {details}"
        )
    return mapping


def write_unit_sample_column_mapping(
    manifest: GenomeSelectionManifest,
    sample_column_mapping: dict[str, str],
    output_path: str | Path,
    output_sample_col_prefix: str = "Intensity_",
) -> pd.DataFrame:
    rows = []
    for unit in manifest.units.values():
        for sample in unit.sample_columns:
            peptide_col = sample_column_mapping.get(sample, "")
            rows.append(
                {
                    "analysis_unit_id": unit.analysis_unit_id,
                    "manifest_sample_column": sample,
                    "peptide_table_column": peptide_col,
                    "canonical_output_column": f"{output_sample_col_prefix}{sample}",
                    "match_status": "matched" if peptide_col else "missing",
                }
            )
    df = pd.DataFrame(
        rows,
        columns=[
            "analysis_unit_id",
            "manifest_sample_column",
            "peptide_table_column",
            "canonical_output_column",
            "match_status",
        ],
    )
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, sep="\t", index=False)
    return df
