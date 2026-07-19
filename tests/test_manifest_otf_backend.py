from pathlib import Path

import pandas as pd
import pytest

from metax.peptide_annotator.genome_selection_manifest import load_genome_selection_manifest
from metax.peptide_annotator import unit_specific_otf as backend


FIXTURE = Path(__file__).parent / "fixtures" / "genome_selection_manifest.v1.json"


def test_digest_union_is_scanned_once(monkeypatch):
    manifest = load_genome_selection_manifest(FIXTURE)
    calls = []

    def fake_scan(**kwargs):
        calls.append(kwargs)
        return {}

    monkeypatch.setattr(
        backend, "query_peptide_proteins_from_digested_genome_folders_nested", fake_scan
    )
    backend.build_manifest_peptide_protein_map(
        pd.DataFrame({"Sequence": ["PEP1", "PEP2"]}),
        "Sequence",
        manifest,
        "digests",
    )
    assert len(calls) == 1
    assert calls[0]["selected_genomes_set"] == {"g1", "g2"}


def test_merged_column_order_always_contains_analysis_unit_id(tmp_path):
    # This invariant is independent of unit count and is enforced before streaming merge.
    method = backend.ManifestOTFAnnotator._merged_column_order
    instance = object.__new__(backend.ManifestOTFAnnotator)
    instance.output_sample_col_prefix = "Intensity_"
    columns = method(
        instance,
        [{"columns": ["analysis_unit_id", "Sequence", "Taxon", "Intensity_s1"]}],
        ["Intensity_s1"],
    )
    assert columns[0] == "analysis_unit_id"


def test_nested_digest_scan_rejects_missing_manifest_genome(tmp_path):
    digests = tmp_path / "digests"
    digests.mkdir()
    (digests / "g1.tsv").write_text(
        "Peptide\tProtein\nPEP\tg1_p1\n",
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError, match=r"1 selected manifest genomes: g2"):
        backend.query_peptide_proteins_from_digested_genome_folders_nested(
            digested_genome_folders=str(digests),
            peptide_list=["PEP"],
            selected_genomes_set={"g1", "g2"},
            digested_peptide_col="Peptide",
            digested_protein_col="Protein",
            parallel_backend="thread",
            n_jobs=1,
        )


def test_nested_digest_scan_rejects_duplicate_genome_files(tmp_path):
    digest_a = tmp_path / "digest-a"
    digest_b = tmp_path / "digest-b"
    digest_a.mkdir()
    digest_b.mkdir()
    for folder in (digest_a, digest_b):
        (folder / "g1.tsv").write_text(
            "Peptide\tProtein\nPEP\tg1_p1\n",
            encoding="utf-8",
        )

    with pytest.raises(ValueError, match=r"duplicates found for 1 genomes: g1"):
        backend.query_peptide_proteins_from_digested_genome_folders_nested(
            digested_genome_folders=[str(digest_a), str(digest_b)],
            peptide_list=["PEP"],
            selected_genomes_set={"g1"},
            digested_peptide_col="Peptide",
            digested_protein_col="Protein",
            parallel_backend="thread",
            n_jobs=1,
        )


def test_nested_digest_scan_uses_validated_genome_file_once(tmp_path):
    digests = tmp_path / "digests"
    digests.mkdir()
    (digests / "g1.tsv").write_text(
        "Peptide\tProtein\nPEP\tg1_p1\n",
        encoding="utf-8",
    )

    mapping = backend.query_peptide_proteins_from_digested_genome_folders_nested(
        digested_genome_folders=str(digests),
        peptide_list=["PEP"],
        selected_genomes_set={"g1"},
        digested_peptide_col="Peptide",
        digested_protein_col="Protein",
        parallel_backend="thread",
        n_jobs=1,
    )

    assert mapping == {"PEP": {"g1": {"g1_p1"}}}
