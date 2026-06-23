from __future__ import annotations

import json
import re
import tempfile
import warnings
from pathlib import Path
from typing import Iterable

import pandas as pd

from metax.peptide_annotator.pep_table_to_otf import peptideProteinsMapper
from metax.peptide_annotator.unit_aware_manifest import (
    UnitAwareManifest,
    load_unit_aware_manifest,
    resolve_manifest_sample_columns,
    write_unit_sample_column_mapping,
)


def _safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", str(value)).strip("._") or "unit"


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
    ):
        if (db_path is None) == (digested_genome_folders is None):
            raise ValueError("Exactly one of db_path or digested_genome_folders must be provided")
        if on_missing_sample not in {"error", "warn-skip"}:
            raise ValueError("on_missing_sample must be 'error' or 'warn-skip'")
        if on_empty_unit not in {"error", "warn-skip"}:
            raise ValueError("on_empty_unit must be 'error' or 'warn-skip'")
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
        unit_df[canonical_cols] = unit_df[canonical_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
        unit_df = unit_df.loc[unit_df[canonical_cols].sum(axis=1) > 0].copy()
        return unit_df, canonical_cols

    def _unit_output_path(self, analysis_unit_id: str, tmpdir: Path) -> Path:
        if self.save_per_unit_outputs:
            per_unit_dir = self.artifacts_dir / "per_unit"
            per_unit_dir.mkdir(parents=True, exist_ok=True)
            return per_unit_dir / f"{_safe_filename(analysis_unit_id)}_OTF.tsv"
        return tmpdir / f"{_safe_filename(analysis_unit_id)}_OTF.tsv"

    def _write_manifest_used(self) -> None:
        target = self.artifacts_dir / "unit_aware_manifest_used.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.unit_aware_manifest_path.read_text(encoding="utf-8"), encoding="utf-8")

    def _read_peptide_table(self) -> pd.DataFrame:
        suffix = self.peptide_table_path.suffix.lower()
        if suffix in {".parquet", ".pq"}:
            df = pd.read_parquet(self.peptide_table_path)
            if {"Run", "Precursor.Quantity"}.issubset(df.columns) and self.peptide_col in df.columns:
                print(
                    "Detected long-format DIA-NN parquet; pivoting "
                    f"{self.peptide_col} x Run using Precursor.Quantity"
                )
                wide = (
                    df.pivot_table(
                        index=self.peptide_col,
                        columns="Run",
                        values="Precursor.Quantity",
                        aggfunc="sum",
                        fill_value=0,
                    )
                    .reset_index()
                    .rename_axis(None, axis=1)
                )
                wide.columns = [str(col) for col in wide.columns]
                return wide
            return df
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

    def _merge_unit_outputs(self, unit_otf_dfs: list[pd.DataFrame], canonical_sample_cols: list[str]) -> pd.DataFrame:
        if not unit_otf_dfs:
            raise ValueError("No unit-aware OTF rows were produced")

        aligned = []
        for df in unit_otf_dfs:
            df = df.copy()
            for col in canonical_sample_cols:
                if col not in df.columns:
                    df[col] = 0
            aligned.append(df)

        merged = pd.concat(aligned, ignore_index=True, sort=False)
        leading_cols = [
            "analysis_unit_id",
            "Sequence",
            "Proteins",
            "LCA_level",
            "Taxon",
            "Taxon_prop",
        ]
        middle_cols = [
            col
            for col in merged.columns
            if col not in leading_cols and col not in canonical_sample_cols
        ]
        ordered_cols = [col for col in leading_cols if col in merged.columns] + middle_cols + canonical_sample_cols
        return merged.loc[:, ordered_cols]

    def run(self) -> pd.DataFrame:
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
        print(
            f"[Unit-aware] Sample mapping complete: {len(sample_mapping)} of "
            f"{len(manifest_samples)} manifest samples mapped.",
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
        unit_otf_dfs: list[pd.DataFrame] = []
        summary_rows: list[dict] = []

        with tempfile.TemporaryDirectory(prefix="metax_unit_aware_") as tmp:
            tmpdir = Path(tmp)
            for unit_index, unit in enumerate(manifest.units.values(), start=1):
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

                unit_output_path = self._unit_output_path(unit.analysis_unit_id, tmpdir)
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
                    continue_base_on_annotaied_peptide_table=False,
                    protein_genome_separator=self.protein_genome_separator,
                    duplicate_peptide_handling_mode=self.duplicate_peptide_handling_mode,
                    n_jobs=self.n_jobs,
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
                    },
                )

                unit_otf_df = unit_otf_df.copy()
                unit_otf_df.insert(0, "analysis_unit_id", unit.analysis_unit_id)
                if self.include_unit_aware_sequence:
                    sequence_values = unit_otf_df["Sequence"].astype(str)
                    unit_otf_df.insert(1, "UnitAwareSequence", unit.analysis_unit_id + "||" + sequence_values)
                unit_otf_dfs.append(unit_otf_df)
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
                print(
                    f"{progress_prefix} completed "
                    f"({len(unit_df)} peptides, {len(unit_otf_df)} OTF rows).",
                    flush=True,
                )

        merged = self._merge_unit_outputs(unit_otf_dfs, canonical_sample_cols)
        merged.to_csv(self.output_path, sep="\t", index=False)

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
        summary_df.to_csv(self.artifacts_dir / "unit_annotation_summary.tsv", sep="\t", index=False)
        completed_units = int((summary_df["status"] == "ok").sum()) if not summary_df.empty else 0
        skipped_units = int((summary_df["status"] == "skipped").sum()) if not summary_df.empty else 0
        print(
            f"[Unit-aware] Annotation complete: {total_units} units total, "
            f"{completed_units} completed, {skipped_units} skipped, "
            f"{len(merged)} merged OTF rows.",
            flush=True,
        )

        manifest_summary = {
            "unit_aware_manifest_path": str(self.unit_aware_manifest_path),
            "selected_genome_threshold": manifest.selected_genome_threshold,
            "n_units": len(manifest.units),
            "n_manifest_samples": len(manifest_samples),
            "output_path": str(self.output_path),
        }
        (self.artifacts_dir / "run_summary.json").write_text(
            json.dumps(manifest_summary, indent=2),
            encoding="utf-8",
        )
        return merged
