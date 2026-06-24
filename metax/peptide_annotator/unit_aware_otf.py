from __future__ import annotations

import json
import re
import shutil
import time
import warnings
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

from metax.peptide_annotator.pep_table_to_otf import (
    peptideProteinsMapper,
    query_peptide_proteins_from_digested_genome_folders_nested,
)
from metax.peptide_annotator.peptide_table_prepare import (
    has_diann_core_columns,
    is_parquet_path,
    prepare_diann_parquet_for_direct_otf,
    read_parquet_columns,
)
from metax.peptide_annotator.unit_aware_manifest import (
    UnitAwareManifest,
    load_unit_aware_manifest,
    resolve_manifest_sample_columns,
    write_unit_sample_column_mapping,
)
from metax.utils.version import __version__


@dataclass(frozen=True)
class UnitAwareOTFRunResult:
    output_path: str
    info_path: str
    summary_path: str
    rows: int
    columns: int
    completed_units: int
    skipped_units: int


def _safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", str(value)).strip("._") or "unit"


def _create_temporary_unit_directory(parent: Path, analysis_unit_id: str) -> Path:
    base_name = f"run_{_safe_filename(analysis_unit_id)}"
    run_dir = parent / base_name
    if run_dir.exists():
        run_dir = parent / (
            f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        )
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def build_global_unit_aware_peptide_protein_map(
    peptide_df: pd.DataFrame,
    peptide_col: str,
    manifest: UnitAwareManifest,
    digested_genome_folders: str | list[str],
    protein_genome_separator: str = "_",
    n_jobs: int | None = None,
    digested_peptide_col: str | None = None,
    digested_protein_col: str | None = None,
) -> dict[str, dict[str, set[str]]]:
    """Scan the manifest genome union once into an in-memory nested mapping."""
    global_genome_set = {
        str(genome_id)
        for unit in manifest.units.values()
        for genome_id in unit.genome_ids
    }
    global_peptide_list = (
        peptide_df[peptide_col]
        .dropna()
        .astype(str)
        .loc[lambda values: values.str.len() > 0]
        .drop_duplicates()
        .tolist()
    )
    return query_peptide_proteins_from_digested_genome_folders_nested(
        digested_genome_folders=digested_genome_folders,
        peptide_list=global_peptide_list,
        selected_genomes_set=global_genome_set,
        protein_genome_separator=protein_genome_separator,
        sep="\t",
        n_jobs=n_jobs,
        digested_peptide_col=digested_peptide_col,
        digested_protein_col=digested_protein_col,
    )


class UnitAwareOTFAnnotator:
    def __init__(
        self,
        peptide_table_path: str,
        unit_aware_manifest_path: str,
        taxafunc_anno_db_path: str,
        output_path: str,
        db_path: str | None = None,
        digested_genome_folders: str | list[str] | None = None,
        genome_threshold: str | None = None,
        peptide_col: str = "Sequence",
        input_sample_col_prefix: str | None = None,
        output_sample_col_prefix: str = "Intensity_",
        table_separator: str = "\t",
        lca_threshold: float = 1.0,
        genome_mode: bool = True,
        distinct_genome_threshold: int = 0,
        exclude_protein_startwith: str | None = None,
        protein_separator: str = ";",
        protein_genome_separator: str = "_",
        save_per_unit_outputs: bool = False,
        include_unit_aware_sequence: bool = False,
        duplicate_peptide_handling_mode: str = "sum",
        on_missing_sample: str = "error",
        on_empty_unit: str = "warn-skip",
        n_jobs: int | None = None,
        merge_chunksize: int = 100_000,
        collect_unique_stats: bool = False,
    ):
        if (db_path is None) == (digested_genome_folders is None):
            raise ValueError("Exactly one of db_path or digested_genome_folders must be provided")
        if on_missing_sample not in {"error", "warn-skip"}:
            raise ValueError("on_missing_sample must be 'error' or 'warn-skip'")
        if on_empty_unit not in {"error", "warn-skip"}:
            raise ValueError("on_empty_unit must be 'error' or 'warn-skip'")
        if merge_chunksize <= 0:
            raise ValueError("merge_chunksize must be greater than 0")
        duplicate_peptide_handling_mode = (duplicate_peptide_handling_mode or "sum").strip().lower()
        valid_duplicate_modes = {"sum", "max", "min", "mean", "first", "keep"}
        if duplicate_peptide_handling_mode not in valid_duplicate_modes:
            raise ValueError(
                "duplicate_peptide_handling_mode must be one of "
                f"{sorted(valid_duplicate_modes)}"
            )

        self.peptide_table_path = Path(peptide_table_path)
        self.unit_aware_manifest_path = Path(unit_aware_manifest_path)
        self.taxafunc_anno_db_path = Path(taxafunc_anno_db_path)
        self.output_path = Path(output_path)
        self.db_path = db_path
        self.digested_genome_folders = digested_genome_folders
        self.genome_threshold = genome_threshold
        self.peptide_col = peptide_col
        self.input_sample_col_prefix = input_sample_col_prefix
        self.output_sample_col_prefix = output_sample_col_prefix
        self.table_separator = table_separator
        self.lca_threshold = lca_threshold
        self.genome_mode = genome_mode
        self.distinct_genome_threshold = distinct_genome_threshold
        self.exclude_protein_startwith = exclude_protein_startwith
        self.protein_separator = protein_separator
        self.protein_genome_separator = protein_genome_separator
        self.save_per_unit_outputs = save_per_unit_outputs
        self.include_unit_aware_sequence = include_unit_aware_sequence
        self.duplicate_peptide_handling_mode = duplicate_peptide_handling_mode
        self.on_missing_sample = on_missing_sample
        self.on_empty_unit = on_empty_unit
        self.n_jobs = n_jobs
        self.merge_chunksize = merge_chunksize
        self.collect_unique_stats = collect_unique_stats
        self._last_unique_sequences: int | None = None
        self._last_unique_protein_groups: int | None = None
        self.peptide_table_prepare_metadata: dict = {}

        for path, label in [
            (self.peptide_table_path, "peptide_table_path"),
            (self.unit_aware_manifest_path, "unit_aware_manifest_path"),
            (self.taxafunc_anno_db_path, "taxafunc_anno_db_path"),
        ]:
            if not path.is_file():
                raise FileNotFoundError(f"{label} does not exist: {path}")
        if self.db_path is not None:
            peptide_db_path = Path(self.db_path)
            if not peptide_db_path.is_file():
                raise FileNotFoundError(f"db_path does not exist or is not a file: {peptide_db_path}")
        if self.digested_genome_folders is not None:
            folders = (
                [self.digested_genome_folders]
                if isinstance(self.digested_genome_folders, str)
                else list(self.digested_genome_folders)
            )
            if not folders:
                raise ValueError("digested_genome_folders must contain at least one directory")
            for folder in folders:
                folder_path = Path(folder)
                if not folder_path.is_dir():
                    raise FileNotFoundError(
                        f"digested_genome_folders entry does not exist or is not a directory: {folder_path}"
                    )
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def artifacts_dir(self) -> Path:
        return self.output_path.parent / f"{self.output_path.stem}_artifacts"

    @property
    def temporary_unit_otf_dir(self) -> Path:
        return self.artifacts_dir / "per_unit" / "unit_otf"

    def _all_manifest_samples(self, manifest: UnitAwareManifest) -> list[str]:
        samples: list[str] = []
        for unit in manifest.units.values():
            for sample in unit.sample_columns:
                if sample not in samples:
                    samples.append(sample)
        return samples

    def _build_unit_dataframe(
        self,
        peptide_df: pd.DataFrame,
        unit_samples: list[str],
        sample_mapping: dict[str, str],
    ) -> tuple[pd.DataFrame, list[str]]:
        rename_map = {
            sample_mapping[sample]: f"{self.output_sample_col_prefix}{sample}"
            for sample in unit_samples
            if sample in sample_mapping
        }
        canonical_cols = list(rename_map.values())
        if not canonical_cols:
            raise ValueError("No manifest sample columns were mapped for this unit")

        unit_df = peptide_df[[self.peptide_col] + list(rename_map.keys())].copy()
        unit_df = unit_df.rename(columns=rename_map)
        unit_df = unit_df[[self.peptide_col] + canonical_cols]
        unit_df = unit_df.loc[unit_df[canonical_cols].sum(axis=1) > 0].copy()
        return unit_df, canonical_cols

    def _unit_output_path(self, analysis_unit_id: str, tmpdir: Path) -> Path:
        if self.save_per_unit_outputs:
            per_unit_dir = self.artifacts_dir / "per_unit"
            per_unit_dir.mkdir(parents=True, exist_ok=True)
            return per_unit_dir / f"{_safe_filename(analysis_unit_id)}_OTF.tsv"
        return tmpdir / f"{_safe_filename(analysis_unit_id)}_OTF.tsv"

    def _add_unit_protein_mapping(
        self,
        unit_df: pd.DataFrame,
        global_mapping: dict[str, dict[str, set[str]]],
        unit_genome_ids: Iterable[str],
    ) -> pd.DataFrame:
        unit_genomes = [str(genome_id) for genome_id in unit_genome_ids]

        def unit_candidates(peptide: object) -> tuple[str, str]:
            genome_map = global_mapping.get(str(peptide), {})
            proteins = {
                protein_id
                for genome_id in unit_genomes
                for protein_id in genome_map.get(genome_id, set())
            }
            mapped_genomes = [
                genome_id for genome_id in unit_genomes if genome_map.get(genome_id)
            ]
            return ";".join(sorted(proteins)), ";".join(mapped_genomes)

        result = unit_df.copy()
        candidates = result[self.peptide_col].map(unit_candidates)
        result["Proteins"] = candidates.map(lambda value: value[0])
        result["Genomes"] = candidates.map(lambda value: value[1])
        return result.loc[result["Proteins"].ne("")].copy()

    def _write_manifest_used(self) -> None:
        target = self.artifacts_dir / "unit_aware_manifest_used.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.unit_aware_manifest_path.read_text(encoding="utf-8"), encoding="utf-8")

    def _read_peptide_table(self) -> pd.DataFrame:
        if is_parquet_path(self.peptide_table_path):
            parquet_columns = read_parquet_columns(self.peptide_table_path)
            if not has_diann_core_columns(parquet_columns):
                self.peptide_table_prepare_metadata = {
                    "input_peptide_table_format": "parquet",
                    "input_peptide_table_original_path": str(self.peptide_table_path),
                }
                return pd.read_parquet(self.peptide_table_path)
            prepared = prepare_diann_parquet_for_direct_otf(
                self.peptide_table_path,
                sample_column_prefix="",
            )
            self.peptide_col = prepared.peptide_col
            self.peptide_table_prepare_metadata = dict(prepared.metadata)
            print(
                "Detected long-format DIA-NN parquet; pivoting "
                f"{prepared.peptide_col} x Run using {prepared.intensity_col}"
            )
            return prepared.dataframe
        self.peptide_table_prepare_metadata = {}
        return pd.read_csv(self.peptide_table_path, sep=self.table_separator)

    def _record_summary(
        self,
        rows: list[dict],
        analysis_unit_id: str,
        n_manifest_sample_columns: int,
        n_mapped_sample_columns: int,
        n_input_peptides: int,
        n_peptides_after_unit_filter: int,
        n_genomes_from_manifest: int,
        n_final_otf_rows: int | str,
        status: str,
        message: str,
        mapper: peptideProteinsMapper | None = None,
    ) -> None:
        rows.append(
            {
                "analysis_unit_id": analysis_unit_id,
                "n_manifest_sample_columns": n_manifest_sample_columns,
                "n_mapped_sample_columns": n_mapped_sample_columns,
                "n_input_peptides": n_input_peptides,
                "n_peptides_after_unit_filter": n_peptides_after_unit_filter,
                "n_genomes_from_manifest": n_genomes_from_manifest,
                "n_peptides_mapped_to_proteins": getattr(mapper, "peptides_after_mapping", "NA") if mapper else "NA",
                "n_peptides_after_genome_filter": len(mapper.final_peptide_table)
                if mapper is not None and mapper.final_peptide_table is not None
                else "NA",
                "n_selected_genomes": getattr(mapper, "selected_genomes_num", "NA") if mapper else "NA",
                "n_final_otf_rows": n_final_otf_rows,
                "status": status,
                "message": message,
            }
        )

    def _merged_column_order(
        self,
        unit_output_records: list[dict],
        canonical_sample_cols: list[str],
    ) -> list[str]:
        if not unit_output_records:
            raise ValueError("No unit-aware OTF rows were produced")

        leading_cols = [
            "analysis_unit_id",
            "Sequence",
            "Proteins",
            "LCA_level",
            "Taxon",
            "Taxon_prop",
        ]
        all_columns: list[str] = []
        for record in unit_output_records:
            for column in record["columns"]:
                if column not in all_columns:
                    all_columns.append(column)
        middle_cols = [
            column
            for column in all_columns
            if column not in leading_cols and column not in canonical_sample_cols
        ]
        return (
            [column for column in leading_cols if column in all_columns]
            + middle_cols
            + canonical_sample_cols
        )

    def _stream_merge_unit_outputs(
        self,
        unit_output_records: list[dict],
        canonical_sample_cols: list[str],
        merge_chunksize: int | None = None,
        collect_unique_stats: bool | None = None,
    ) -> tuple[list[str], int]:
        if merge_chunksize is None:
            merge_chunksize = self.merge_chunksize
        if merge_chunksize <= 0:
            raise ValueError("merge_chunksize must be greater than 0")
        if collect_unique_stats is None:
            collect_unique_stats = self.collect_unique_stats
        ordered_columns = self._merged_column_order(
            unit_output_records,
            canonical_sample_cols,
        )
        total_rows = 0
        wrote_header = False
        unique_sequences: set[str] | None = set() if collect_unique_stats else None
        unique_protein_groups: set[str] | None = set() if collect_unique_stats else None
        for record in unit_output_records:
            unit_path = Path(record["path"])
            for chunk in pd.read_csv(unit_path, sep="\t", chunksize=merge_chunksize):
                for column in canonical_sample_cols:
                    if column not in chunk.columns:
                        chunk[column] = 0
                for column in ordered_columns:
                    if column not in chunk.columns:
                        chunk[column] = pd.NA
                chunk = chunk.loc[:, ordered_columns]
                if unique_sequences is not None:
                    sequence_column = "Sequence" if "Sequence" in chunk.columns else self.peptide_col
                    unique_sequences.update(
                        chunk[sequence_column].dropna().astype(str)
                    )
                    if "Proteins" in chunk.columns:
                        unique_protein_groups.update(
                            chunk["Proteins"].dropna().astype(str)
                        )
                chunk.to_csv(
                    self.output_path,
                    sep="\t",
                    index=False,
                    mode="a" if wrote_header else "w",
                    header=not wrote_header,
                )
                wrote_header = True
                total_rows += len(chunk)
                del chunk
            if record.get("temporary", False):
                unit_path.unlink(missing_ok=True)
        self._last_unique_sequences = (
            len(unique_sequences) if unique_sequences is not None else None
        )
        self._last_unique_protein_groups = (
            len(unique_protein_groups) if unique_protein_groups is not None else None
        )
        return ordered_columns, total_rows

    @property
    def info_path(self) -> Path:
        return self.output_path.with_name(f"{self.output_path.stem}_info.txt")

    def _write_merged_info(
        self,
        *,
        manifest: UnitAwareManifest,
        manifest_samples: list[str],
        sample_mapping: dict[str, str],
        summary_df: pd.DataFrame,
        merged_columns: list[str],
        merged_rows: int,
        unique_sequences: int | None,
        unique_protein_groups: int | None,
        started_at: datetime,
    ) -> None:
        completed_at = datetime.now()
        completed_units = int((summary_df["status"] == "ok").sum()) if not summary_df.empty else 0
        skipped_units = int((summary_df["status"] == "skipped").sum()) if not summary_df.empty else 0
        sample_columns = [
            column
            for column in merged_columns
            if column.startswith(self.output_sample_col_prefix)
        ]
        with self.info_path.open("w", encoding="utf-8") as handle:
            handle.write("MetaX PeptideAnnotator Results\n")
            handle.write("=" * 50 + "\n")
            handle.write(f"Software: MetaX (UnitAwareOTFAnnotator) v{__version__}\n")
            handle.write(f"Run time: {started_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
            handle.write("-" * 50 + "\n")
            handle.write("Parameters:\n")
            handle.write(f"  - Threshold: {self.lca_threshold}\n")
            handle.write(f"  - Genome mode: {self.genome_mode}\n")
            handle.write(f"  - Distinct genome threshold: {self.distinct_genome_threshold}\n")
            handle.write(f"  - Exclude proteins: {self.exclude_protein_startwith}\n")
            handle.write(f"  - Protein separator: '{self.protein_separator}'\n")
            handle.write(f"  - Protein-genome separator: '{self.protein_genome_separator}'\n")
            handle.write(f"  - Peptide column: '{self.peptide_col}'\n")
            handle.write(f"  - Sample prefix (output): '{self.output_sample_col_prefix}'\n")
            handle.write(f"  - Duplicate handling mode: {self.duplicate_peptide_handling_mode}\n")
            handle.write("-" * 50 + "\n")
            handle.write("Unit-aware configuration:\n")
            handle.write(f"  - Manifest: {self.unit_aware_manifest_path}\n")
            handle.write(f"  - Selected genome threshold: {manifest.selected_genome_threshold}\n")
            handle.write(f"  - Units: {len(manifest.units)}\n")
            handle.write(f"  - Manifest samples: {len(manifest_samples)}\n")
            handle.write(f"  - Mapped samples: {len(sample_mapping)}\n")
            handle.write(f"  - On missing sample: {self.on_missing_sample}\n")
            handle.write(f"  - On empty unit: {self.on_empty_unit}\n")
            handle.write(f"  - Include UnitAwareSequence: {self.include_unit_aware_sequence}\n")
            handle.write("-" * 50 + "\n")
            handle.write("Input/Output:\n")
            handle.write(f"  - Input: {self.peptide_table_path}\n")
            handle.write(f"  - Database: {self.taxafunc_anno_db_path}\n")
            handle.write(f"  - Output (TSV): {self.output_path}\n")
            handle.write(f"  - Output (info): {self.info_path}\n")
            handle.write("-" * 50 + "\n")
            handle.write("Processing summary:\n")
            handle.write(f"  - Completed units: {completed_units}\n")
            handle.write(f"  - Skipped units: {skipped_units}\n")
            handle.write(f"  - Unit summary: {self.artifacts_dir / 'unit_annotation_summary.tsv'}\n")
            handle.write("-" * 50 + "\n")
            handle.write("Result summary:\n")
            handle.write(f"  - Shape: {merged_rows} rows × {len(merged_columns)} columns\n")
            handle.write(
                f"  - Unique sequences: "
                f"{unique_sequences if unique_sequences is not None else 'NA'}\n"
            )
            handle.write(
                f"  - Unique protein groups: "
                f"{unique_protein_groups if unique_protein_groups is not None else 'NA'}\n"
            )
            handle.write(f"  - Sample columns: {len(sample_columns)}\n")
            if sample_columns:
                shown = sample_columns[:10] + (["..."] if len(sample_columns) > 10 else [])
                handle.write(f"  - Samples: {', '.join(shown)}\n")
            handle.write("-" * 50 + "\n")
            handle.write("Completion:\n")
            handle.write(f"  - Completion time: {completed_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
            handle.write(f"  - Processing duration: {str(completed_at - started_at).split('.')[0]}\n")

    def run(
        self,
        return_dataframe: bool = False,
    ) -> UnitAwareOTFRunResult | pd.DataFrame:
        started_at = datetime.now()
        manifest = load_unit_aware_manifest(
            self.unit_aware_manifest_path,
            genome_threshold=self.genome_threshold,
            strict=True,
        )
        total_units = len(manifest.units)
        print(
            f"[Unit-aware] Preparing annotation for {total_units} units "
            f"(genome threshold: {manifest.selected_genome_threshold}).",
            flush=True,
        )
        peptide_df = self._read_peptide_table()
        if self.peptide_col not in peptide_df.columns:
            raise ValueError(f"Peptide column {self.peptide_col!r} not found in peptide table")

        manifest_samples = self._all_manifest_samples(manifest)
        sample_mapping = resolve_manifest_sample_columns(
            peptide_columns=[str(col) for col in peptide_df.columns],
            manifest_sample_columns=manifest_samples,
            output_sample_col_prefix=self.output_sample_col_prefix,
            input_sample_col_prefix=self.input_sample_col_prefix,
            on_missing=self.on_missing_sample,
        )
        mapped_input_cols = sorted(set(sample_mapping.values()))
        if mapped_input_cols:
            peptide_df[mapped_input_cols] = (
                peptide_df[mapped_input_cols]
                .apply(pd.to_numeric, errors="coerce")
                .fillna(0)
            )
        print(
            f"[Unit-aware] Sample mapping complete: {len(sample_mapping)} of "
            f"{len(manifest_samples)} manifest samples mapped.",
            flush=True,
        )
        global_genome_set = {
            str(genome_id)
            for unit in manifest.units.values()
            for genome_id in unit.genome_ids
        }
        global_peptides = peptide_df[self.peptide_col].dropna().astype(str)
        global_peptide_count = int(global_peptides.loc[global_peptides.str.len() > 0].nunique())
        print(
            f"[Unit-aware] Global candidates: {len(global_genome_set)} unique manifest genomes, "
            f"{global_peptide_count} unique input peptides.",
            flush=True,
        )

        global_mapping: dict[str, dict[str, set[str]]] | None = None
        if self.digested_genome_folders is not None:
            mapping_started = time.perf_counter()
            global_mapping = build_global_unit_aware_peptide_protein_map(
                peptide_df=peptide_df,
                peptide_col=self.peptide_col,
                manifest=manifest,
                digested_genome_folders=self.digested_genome_folders,
                protein_genome_separator=self.protein_genome_separator,
                n_jobs=self.n_jobs,
            )
            mapped_protein_count = sum(
                len(proteins)
                for genome_map in global_mapping.values()
                for proteins in genome_map.values()
            )
            print(
                f"[Unit-aware] Global peptide-protein map built once: "
                f"{len(global_mapping)} mapped peptides, {mapped_protein_count} candidates in "
                f"{time.perf_counter() - mapping_started:.2f}s.",
                flush=True,
            )

        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self._write_manifest_used()
        write_unit_sample_column_mapping(
            manifest,
            sample_mapping,
            self.artifacts_dir / "unit_sample_column_mapping.tsv",
            output_sample_col_prefix=self.output_sample_col_prefix,
        )

        canonical_sample_cols = [f"{self.output_sample_col_prefix}{sample}" for sample in manifest_samples]
        unit_output_records: list[dict] = []
        summary_rows: list[dict] = []

        self.temporary_unit_otf_dir.mkdir(parents=True, exist_ok=True)
        temporary_unit_dirs: list[Path] = []
        try:
            for unit_index, unit in enumerate(manifest.units.values(), start=1):
                tmpdir = _create_temporary_unit_directory(
                    self.temporary_unit_otf_dir,
                    unit.analysis_unit_id,
                )
                temporary_unit_dirs.append(tmpdir)
                progress_prefix = (
                    f"[Unit-aware] Unit {unit_index} of {total_units}: "
                    f"{unit.analysis_unit_id}"
                )
                print(
                    f"{progress_prefix} started "
                    f"({len(unit.sample_columns)} samples, {len(unit.genome_ids)} genomes).",
                    flush=True,
                )
                mapped_samples = [sample for sample in unit.sample_columns if sample in sample_mapping]
                try:
                    unit_df, _ = self._build_unit_dataframe(peptide_df, unit.sample_columns, sample_mapping)
                except ValueError as exc:
                    if self.on_empty_unit == "error":
                        print(f"{progress_prefix} failed: {exc}", flush=True)
                        raise
                    warnings.warn(str(exc), stacklevel=2)
                    self._record_summary(
                        summary_rows,
                        unit.analysis_unit_id,
                        len(unit.sample_columns),
                        len(mapped_samples),
                        len(peptide_df),
                        0,
                        len(unit.genome_ids),
                        0,
                        "skipped",
                        str(exc),
                    )
                    print(f"{progress_prefix} skipped: {exc}", flush=True)
                    continue

                if unit_df.empty:
                    message = "unit has no peptides with non-zero mapped sample intensity"
                    if self.on_empty_unit == "error":
                        print(f"{progress_prefix} failed: {message}", flush=True)
                        raise ValueError(f"{unit.analysis_unit_id}: {message}")
                    warnings.warn(f"{unit.analysis_unit_id}: {message}", stacklevel=2)
                    self._record_summary(
                        summary_rows,
                        unit.analysis_unit_id,
                        len(unit.sample_columns),
                        len(mapped_samples),
                        len(peptide_df),
                        0,
                        len(unit.genome_ids),
                        0,
                        "skipped",
                        message,
                    )
                    print(f"{progress_prefix} skipped: {message}", flush=True)
                    continue

                peptides_before_protein_mapping = len(unit_df)
                if global_mapping is not None:
                    unit_df = self._add_unit_protein_mapping(
                        unit_df,
                        global_mapping=global_mapping,
                        unit_genome_ids=unit.genome_ids,
                    )
                    print(
                        f"{progress_prefix} protein mapping: "
                        f"{peptides_before_protein_mapping} -> {len(unit_df)} peptides.",
                        flush=True,
                    )
                    if unit_df.empty:
                        message = "unit has no peptides mapped to proteins in its manifest genomes"
                        if self.on_empty_unit == "error":
                            print(f"{progress_prefix} failed: {message}", flush=True)
                            raise ValueError(f"{unit.analysis_unit_id}: {message}")
                        warnings.warn(f"{unit.analysis_unit_id}: {message}", stacklevel=2)
                        self._record_summary(
                            summary_rows,
                            unit.analysis_unit_id,
                            len(unit.sample_columns),
                            len(mapped_samples),
                            len(peptide_df),
                            peptides_before_protein_mapping,
                            len(unit.genome_ids),
                            0,
                            "skipped",
                            message,
                        )
                        print(f"{progress_prefix} skipped: {message}", flush=True)
                        continue

                unit_output_path = self._unit_output_path(unit.analysis_unit_id, tmpdir)
                unit_started = time.perf_counter()
                mapper = peptideProteinsMapper(
                    peptide_table_path=str(self.peptide_table_path),
                    peptide_df=unit_df,
                    db_path=self.db_path,
                    digested_genome_folders=self.digested_genome_folders,
                    table_separator=self.table_separator,
                    peptide_col=self.peptide_col,
                    intensity_col_prefix=self.output_sample_col_prefix,
                    output_path=str(unit_output_path),
                    temp_dir=str(tmpdir),
                    selected_genomes_set=set(unit.genome_ids),
                    genome_list=unit.genome_ids,
                    continue_base_on_annotaied_peptide_table=global_mapping is not None,
                    protein_genome_separator=self.protein_genome_separator,
                    duplicate_peptide_handling_mode=self.duplicate_peptide_handling_mode,
                    n_jobs=self.n_jobs,
                )
                if global_mapping is not None:
                    mapper.original_peptides_before_mapping = peptides_before_protein_mapping
                    mapper.peptides_after_mapping = len(mapper.peptide_table)
                    mapper.removed_peptides_no_matched = (
                        peptides_before_protein_mapping - mapper.peptides_after_mapping
                    )
                unit_otf_df = mapper.all_in_one(
                    taxafunc_anno_db_path=str(self.taxafunc_anno_db_path),
                    lca_threshold=self.lca_threshold,
                    genome_mode=self.genome_mode,
                    distinct_genome_threshold=self.distinct_genome_threshold,
                    exclude_protein_startwith=self.exclude_protein_startwith,
                    protein_separator=self.protein_separator,
                    protein_genome_separator=self.protein_genome_separator,
                    genome_list=unit.genome_ids,
                    duplicate_peptide_handling_mode=self.duplicate_peptide_handling_mode,
                    genome_selection_metadata={
                        "genome_selection_method": "metaumbra_unit_aware_manifest",
                        "unit_aware_manifest_path": str(self.unit_aware_manifest_path),
                        "analysis_unit_id": unit.analysis_unit_id,
                        "selected_genome_threshold": manifest.selected_genome_threshold,
                        **self.peptide_table_prepare_metadata,
                    },
                    save_output=False,
                )

                unit_otf_df = unit_otf_df.copy()
                unit_otf_df.insert(0, "analysis_unit_id", unit.analysis_unit_id)
                if self.include_unit_aware_sequence:
                    sequence_values = unit_otf_df["Sequence"].astype(str)
                    unit_otf_df.insert(1, "UnitAwareSequence", unit.analysis_unit_id + "||" + sequence_values)
                final_unit_output_path = self._unit_output_path(
                    unit.analysis_unit_id,
                    tmpdir,
                )
                unit_otf_df.to_csv(final_unit_output_path, sep="\t", index=False)
                self._record_summary(
                    summary_rows,
                    unit.analysis_unit_id,
                    len(unit.sample_columns),
                    len(mapped_samples),
                    len(peptide_df),
                    len(unit_df),
                    len(unit.genome_ids),
                    len(unit_otf_df),
                    "ok",
                    "",
                    mapper=mapper,
                )
                unit_otf_rows = len(unit_otf_df)
                unit_output_records.append(
                    {
                        "analysis_unit_id": unit.analysis_unit_id,
                        "path": str(final_unit_output_path),
                        "columns": unit_otf_df.columns.tolist(),
                        "rows": unit_otf_rows,
                        "summary": dict(summary_rows[-1]),
                        "temporary": not self.save_per_unit_outputs,
                    }
                )
                unit_mapped_peptides = len(unit_df)
                del unit_otf_df
                del mapper
                del unit_df
                print(
                    f"{progress_prefix} completed "
                    f"({unit_mapped_peptides} mapped peptides, {unit_otf_rows} OTF rows, "
                    f"{time.perf_counter() - unit_started:.2f}s downstream).",
                    flush=True,
                )

            summary_df = pd.DataFrame(
                summary_rows,
                columns=[
                    "analysis_unit_id",
                    "n_manifest_sample_columns",
                    "n_mapped_sample_columns",
                    "n_input_peptides",
                    "n_peptides_after_unit_filter",
                    "n_genomes_from_manifest",
                    "n_peptides_mapped_to_proteins",
                    "n_peptides_after_genome_filter",
                    "n_selected_genomes",
                    "n_final_otf_rows",
                    "status",
                    "message",
                ],
            )
            merged_columns, merged_rows = self._stream_merge_unit_outputs(
                unit_output_records,
                canonical_sample_cols,
            )
            unique_sequences = self._last_unique_sequences
            unique_protein_groups = self._last_unique_protein_groups
            summary_path = self.artifacts_dir / "unit_annotation_summary.tsv"
            summary_df.to_csv(
                summary_path,
                sep="\t",
                index=False,
            )
            self._write_merged_info(
                manifest=manifest,
                manifest_samples=manifest_samples,
                sample_mapping=sample_mapping,
                summary_df=summary_df,
                merged_columns=merged_columns,
                merged_rows=merged_rows,
                unique_sequences=unique_sequences,
                unique_protein_groups=unique_protein_groups,
                started_at=started_at,
            )
        finally:
            for temporary_unit_dir in temporary_unit_dirs:
                shutil.rmtree(temporary_unit_dir, ignore_errors=True)

        completed_units = int((summary_df["status"] == "ok").sum()) if not summary_df.empty else 0
        skipped_units = int((summary_df["status"] == "skipped").sum()) if not summary_df.empty else 0
        print(
            f"[Unit-aware] Annotation complete: {total_units} units total, "
            f"{completed_units} completed, {skipped_units} skipped, "
            f"{merged_rows} merged OTF rows.",
            flush=True,
        )

        manifest_summary = {
            "unit_aware_manifest_path": str(self.unit_aware_manifest_path),
            "selected_genome_threshold": manifest.selected_genome_threshold,
            "n_units": len(manifest.units),
            "n_manifest_samples": len(manifest_samples),
            "output_path": str(self.output_path),
            **self.peptide_table_prepare_metadata,
        }
        (self.artifacts_dir / "run_summary.json").write_text(
            json.dumps(manifest_summary, indent=2),
            encoding="utf-8",
        )
        if return_dataframe:
            return pd.read_csv(self.output_path, sep="\t")
        return UnitAwareOTFRunResult(
            output_path=str(self.output_path),
            info_path=str(self.info_path),
            summary_path=str(summary_path),
            rows=merged_rows,
            columns=len(merged_columns),
            completed_units=completed_units,
            skipped_units=skipped_units,
        )
