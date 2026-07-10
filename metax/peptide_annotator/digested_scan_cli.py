"""CLI helper to scan digested genome TSVs in an isolated process.

This exists primarily to support the GUI on Windows:
- The GUI process loads Qt/Matplotlib.
- Using multiprocessing directly from the GUI can cause spawned workers to re-import
  the GUI entry module, triggering repeated backend initialization and crashes.

By running the scan inside a separate Python process (this module), we ensure the
multiprocessing workers only import lightweight code.

Output:
- A mapping TSV with columns: Peptide, Proteins
- With --nested-output: a long TSV with columns: Peptide, Genome, Protein
- A small JSON metadata file with resolved column names.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Iterable


def _read_lines(path: str) -> list[str]:
    p = pathlib.Path(path)
    if not p.is_file():
        return []
    out: list[str] = []
    with p.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if s:
                out.append(s)
    return out


def _ensure_repo_root_on_syspath() -> None:
    # When invoked via subprocess from the GUI, ensure we can import `metax`.
    this_file = pathlib.Path(__file__).resolve()
    repo_root = this_file.parents[2]  # .../MetaX
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)


def _parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="metax.peptide_annotator.digested_scan_cli",
        description="Scan digested genome TSV folder(s) and build peptide->proteins mapping.",
    )

    parser.add_argument(
        "--folders",
        nargs="+",
        required=True,
        help="One or more folders containing per-genome *.tsv files.",
    )
    parser.add_argument(
        "--peptides-file",
        required=True,
        help="Text file with one peptide per line.",
    )
    parser.add_argument(
        "--out-mapping-tsv",
        required=True,
        help="Output TSV path (columns: Peptide, Proteins).",
    )
    parser.add_argument(
        "--out-meta-json",
        required=True,
        help="Output JSON path for metadata (resolved columns).",
    )
    parser.add_argument(
        "--nested-output",
        action="store_true",
        help="Write long-form Peptide/Genome/Protein output for unit-specific mapping.",
    )

    parser.add_argument("--sep", default="\t", help="TSV separator (default: tab).")
    parser.add_argument("--n-jobs", type=int, default=0, help="Workers; 0 means auto.")
    parser.add_argument("--protein-genome-separator", default="_", help="Separator between genome and protein id.")

    parser.add_argument("--digested-peptide-col", default="", help="Peptide column name in digested TSV.")
    parser.add_argument("--digested-protein-col", default="", help="Protein column name in digested TSV.")

    parser.add_argument("--removed-genomes-file", default="", help="Optional: text file with genomes to remove.")
    parser.add_argument("--selected-genomes-file", default="", help="Optional: text file with genomes to keep.")

    return parser.parse_args(list(argv))


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    _ensure_repo_root_on_syspath()

    from metax.peptide_annotator.pep_table_to_otf import (
        query_peptide_proteins_from_digested_genome_folders,
        query_peptide_proteins_from_digested_genome_folders_nested,
    )

    peptide_list = _read_lines(args.peptides_file)
    if not peptide_list:
        raise SystemExit(f"No peptides found in: {args.peptides_file}")

    removed_set = set(_read_lines(args.removed_genomes_file)) if args.removed_genomes_file else None
    selected_set = set(_read_lines(args.selected_genomes_file)) if args.selected_genomes_file else None

    n_jobs = None if args.n_jobs <= 0 else int(args.n_jobs)

    pep_col = args.digested_peptide_col.strip() or None
    pro_col = args.digested_protein_col.strip() or None

    out_mapping = pathlib.Path(args.out_mapping_tsv)
    out_mapping.parent.mkdir(parents=True, exist_ok=True)
    if args.nested_output:
        if selected_set is None:
            raise SystemExit("--nested-output requires --selected-genomes-file")
        mapping = query_peptide_proteins_from_digested_genome_folders_nested(
            digested_genome_folders=list(args.folders),
            peptide_list=peptide_list,
            selected_genomes_set=selected_set,
            protein_genome_separator=args.protein_genome_separator,
            sep=args.sep,
            n_jobs=n_jobs,
            digested_peptide_col=pep_col,
            digested_protein_col=pro_col,
            parallel_backend="process",
        )
        with out_mapping.open("w", encoding="utf-8", newline="") as f:
            f.write("Peptide\tGenome\tProtein\n")
            for peptide in peptide_list:
                for genome_id, proteins in mapping.get(str(peptide), {}).items():
                    for protein_id in sorted(proteins):
                        f.write(f"{peptide}\t{genome_id}\t{protein_id}\n")
        resolved_pep_col = pep_col or ""
        resolved_pro_col = pro_col or ""
    else:
        mapping, resolved_pep_col, resolved_pro_col = query_peptide_proteins_from_digested_genome_folders(
            digested_genome_folders=list(args.folders),
            peptide_list=peptide_list,
            removed_genomes_set=removed_set,
            selected_genomes_set=selected_set,
            protein_genome_separator=args.protein_genome_separator,
            sep=args.sep,
            n_jobs=n_jobs,
            digested_peptide_col=pep_col,
            digested_protein_col=pro_col,
            parallel_backend="process",
        )
        with out_mapping.open("w", encoding="utf-8", newline="") as f:
            f.write("Peptide\tProteins\n")
            for pep in peptide_list:
                proteins = mapping.get(str(pep), "")
                proteins = "" if proteins is None else str(proteins)
                f.write(f"{pep}\t{proteins}\n")

    out_meta = pathlib.Path(args.out_meta_json)
    out_meta.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        "resolved_digested_peptide_col": resolved_pep_col,
        "resolved_digested_protein_col": resolved_pro_col,
        "peptides": len(peptide_list),
        "folders": list(args.folders),
        "mapping_format": "nested-long" if args.nested_output else "peptide-proteins",
    }
    out_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
