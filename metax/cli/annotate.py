from __future__ import annotations

import argparse
import sys

from metax.peptide_annotator.peptide_table_prepare import (
    DIANN_INTENSITY_CANDIDATES,
)
from metax.peptide_annotator.unit_specific_otf import UnitSpecificOTFAnnotator


def _decode_separator(value: str) -> str:
    if value == r"\t":
        return "\t"
    if value == r"\n":
        return "\n"
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="metax-annotate",
        description="Run MetaX backend peptide annotation workflows.",
    )
    parser.add_argument(
        "--unit-specific",
        action="store_true",
        help="Use MetaUmbra unit-specific manifest mode",
    )
    parser.add_argument("--peptide-table", help="Input peptide intensity table")
    parser.add_argument(
        "--unit-specific-manifest",
        help="MetaUmbra unit_specific_manifest.json",
    )
    parser.add_argument("--taxafunc-db", help="MetaX taxa-function annotation SQLite database")
    parser.add_argument("--output", help="Output merged OTF TSV")
    parser.add_argument("--peptide-db", help="SQLite peptide-to-protein database")
    parser.add_argument(
        "--digested-genome-folders",
        nargs="+",
        help="One or more folders containing digested genome TSV files",
    )
    parser.add_argument("--genome-threshold", default="auto", help="q0.05, q0.01, or auto")
    parser.add_argument("--peptide-col", default="Sequence")
    parser.add_argument(
        "--output-sample-col-prefix",
        default="Intensity_",
        choices=["Intensity_"],
        help=(
            "Prefix for output OTF sample columns. Must be 'Intensity_' for unit-specific output. "
            "Use --input-sample-col-prefix to match non-standard input columns."
        ),
    )
    parser.add_argument(
        "--input-sample-col-prefix",
        help="Optional prefix to strip when matching manifest sample_columns to peptide table columns",
    )
    parser.add_argument("--table-separator", default=r"\t")
    parser.add_argument("--lca-threshold", type=float, default=1.0)
    parser.add_argument(
        "--genome-mode",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable genome-mode taxa-function annotation",
    )
    parser.add_argument(
        "--distinct-genome-threshold",
        type=int,
        default=0,
        help=(
            "Minimum distinct peptides required to keep a genome after peptide-to-protein annotation. "
            "Unit-specific mode defaults to 0 to trust the MetaUmbra manifest genome list; set >0 for an additional filter."
        ),
    )
    parser.add_argument("--exclude-protein-startwith")
    parser.add_argument("--protein-separator", default=";")
    parser.add_argument("--protein-genome-separator", default="_")
    parser.add_argument("--save-per-unit-outputs", action="store_true")
    parser.add_argument("--include-unit-specific-sequence", action="store_true")
    parser.add_argument(
        "--duplicate-peptide-handling-mode",
        choices=["sum", "max", "min", "mean", "first", "keep"],
        default="sum",
    )
    parser.add_argument("--on-missing-sample", choices=["error", "warn-skip"], default="error")
    parser.add_argument("--on-empty-unit", choices=["error", "warn-skip"], default="warn-skip")
    parser.add_argument("--n-jobs", type=int)
    parser.add_argument(
        "--merge-chunksize",
        type=int,
        default=100_000,
        help="Rows per chunk when merging unit OTF files.",
    )
    parser.add_argument(
        "--collect-unique-stats",
        action="store_true",
        help=(
            "Collect unique sequence/protein-group counts during streaming merge. "
            "May use extra memory for large outputs."
        ),
    )
    parser.add_argument(
        "--diann-intensity-col",
        choices=DIANN_INTENSITY_CANDIDATES,
        help=(
            "DIA-NN parquet intensity column. Defaults to Precursor.Normalised "
            "when both supported columns are present."
        ),
    )
    return parser


def _require_unit_specific_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    missing = [
        flag
        for flag, value in [
            ("--peptide-table", args.peptide_table),
            ("--unit-specific-manifest", args.unit_specific_manifest),
            ("--taxafunc-db", args.taxafunc_db),
            ("--output", args.output),
        ]
        if not value
    ]
    if missing:
        parser.error(f"--unit-specific requires: {', '.join(missing)}")
    if bool(args.peptide_db) == bool(args.digested_genome_folders):
        parser.error("--unit-specific requires exactly one of --peptide-db or --digested-genome-folders")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.unit_specific:
        parser.error("Global/non-unit-specific CLI annotation is not implemented yet; use the GUI or pass --unit-specific")

    _require_unit_specific_args(args, parser)
    digested_folders = args.digested_genome_folders
    if digested_folders is not None and len(digested_folders) == 1:
        digested_folders = digested_folders[0]

    annotator = UnitSpecificOTFAnnotator(
        peptide_table_path=args.peptide_table,
        unit_specific_manifest_path=args.unit_specific_manifest,
        taxafunc_anno_db_path=args.taxafunc_db,
        output_path=args.output,
        db_path=args.peptide_db,
        digested_genome_folders=digested_folders,
        genome_threshold=args.genome_threshold,
        peptide_col=args.peptide_col,
        input_sample_col_prefix=args.input_sample_col_prefix,
        output_sample_col_prefix=args.output_sample_col_prefix,
        table_separator=_decode_separator(args.table_separator),
        lca_threshold=args.lca_threshold,
        genome_mode=args.genome_mode,
        distinct_genome_threshold=args.distinct_genome_threshold,
        exclude_protein_startwith=args.exclude_protein_startwith,
        protein_separator=args.protein_separator,
        protein_genome_separator=args.protein_genome_separator,
        save_per_unit_outputs=args.save_per_unit_outputs,
        include_unit_specific_sequence=args.include_unit_specific_sequence,
        duplicate_peptide_handling_mode=args.duplicate_peptide_handling_mode,
        on_missing_sample=args.on_missing_sample,
        on_empty_unit=args.on_empty_unit,
        n_jobs=args.n_jobs,
        merge_chunksize=args.merge_chunksize,
        collect_unique_stats=args.collect_unique_stats,
        diann_intensity_col=args.diann_intensity_col,
    )
    annotator.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
