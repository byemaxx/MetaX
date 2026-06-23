from __future__ import annotations

import json
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


SCHEMA_VERSION = "metaumbra.unit_aware_manifest.v1"


@dataclass
class UnitAwareUnitSpec:
    analysis_unit_id: str
    sample_columns: list[str]
    genome_ids: list[str]
    n_samples: int


@dataclass
class UnitAwareManifest:
    schema_version: str
    generated_by: dict
    default_genome_threshold: str
    files: dict
    units: dict[str, UnitAwareUnitSpec]
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


def load_unit_aware_manifest(
    manifest_path: str | Path,
    genome_threshold: str | None = None,
    strict: bool = True,
) -> UnitAwareManifest:
    manifest_path = Path(manifest_path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    schema_version = data.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        raise ValueError(f"Unsupported unit-aware manifest schema_version: {schema_version!r}")

    default_threshold = str(data.get("default_genome_threshold", "")).strip()
    selected_threshold, selected_genome_key = _normalize_threshold_alias(genome_threshold, default_threshold)

    raw_units = data.get("units")
    if not isinstance(raw_units, dict) or not raw_units:
        raise ValueError("unit-aware manifest must contain at least one unit")

    seen_samples: dict[str, str] = {}
    units: dict[str, UnitAwareUnitSpec] = {}
    for analysis_unit_id, raw_unit in raw_units.items():
        if not isinstance(raw_unit, dict):
            raise ValueError(f"Unit {analysis_unit_id!r} must be an object")

        sample_columns = [str(sample) for sample in raw_unit.get("sample_columns", [])]
        if not sample_columns:
            raise ValueError(f"Unit {analysis_unit_id!r} has no sample_columns")

        for sample in sample_columns:
            previous_unit = seen_samples.get(sample)
            if previous_unit is not None and previous_unit != analysis_unit_id:
                raise ValueError(
                    f"Sample column {sample!r} is assigned to multiple units: "
                    f"{previous_unit!r} and {analysis_unit_id!r}"
                )
            seen_samples[sample] = str(analysis_unit_id)

        if selected_genome_key not in raw_unit:
            raise ValueError(f"Unit {analysis_unit_id!r} is missing {selected_genome_key}")
        genome_ids = [str(genome) for genome in raw_unit.get(selected_genome_key, [])]

        n_samples_value = raw_unit.get("n_samples", len(sample_columns))
        try:
            n_samples = int(n_samples_value)
        except Exception as exc:
            raise ValueError(f"Unit {analysis_unit_id!r} has invalid n_samples: {n_samples_value!r}") from exc
        if n_samples != len(sample_columns):
            raise ValueError(
                f"Unit {analysis_unit_id!r} declares n_samples={n_samples}, "
                f"but has {len(sample_columns)} sample_columns"
            )

        q005 = raw_unit.get("genome_ids_q005")
        q001 = raw_unit.get("genome_ids_q001")
        if q005 is not None and q001 is not None:
            q005_set = {str(genome) for genome in q005}
            q001_set = {str(genome) for genome in q001}
            missing = q001_set - q005_set
            if missing:
                preview = ", ".join(sorted(missing)[:10])
                _warn_or_raise(
                    f"Unit {analysis_unit_id!r} has q0.01 genomes not present in q0.05: {preview}",
                    strict=strict,
                )

        units[str(analysis_unit_id)] = UnitAwareUnitSpec(
            analysis_unit_id=str(analysis_unit_id),
            sample_columns=sample_columns,
            genome_ids=genome_ids,
            n_samples=n_samples,
        )

    return UnitAwareManifest(
        schema_version=schema_version,
        generated_by=dict(data.get("generated_by") or {}),
        default_genome_threshold=default_threshold,
        files=dict(data.get("files") or {}),
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
    return mapping


def write_unit_sample_column_mapping(
    manifest: UnitAwareManifest,
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
