import json
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


def test_run_warn_skips_empty_genome_unit_and_processes_other_units(tmp_path, monkeypatch):
    manifest_data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    manifest_data["units"]["u1"]["genome_ids_q001"] = []
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest_data), encoding="utf-8")
    peptide_path = tmp_path / "peptides.tsv"
    peptide_path.write_text(
        "Sequence\ts1\ts2\nPEP1\t1\t0\nPEP2\t0\t1\n",
        encoding="utf-8",
    )
    taxafunc_db = tmp_path / "taxafunc.db"
    peptide_db = tmp_path / "peptide.db"
    taxafunc_db.touch()
    peptide_db.touch()

    class FakeMapper:
        def __init__(self, *, peptide_df, genome_list, **kwargs):
            self.peptide_table = peptide_df
            self.peptides_after_mapping = len(peptide_df)
            self.final_peptide_table = peptide_df
            self.selected_genomes_num = len(genome_list)

        def all_in_one(self, **kwargs):
            return pd.DataFrame(
                {
                    "Sequence": self.peptide_table["Sequence"],
                    "Taxon": ["t__test"] * len(self.peptide_table),
                    "Intensity_s2": self.peptide_table["Intensity_s2"],
                }
            )

    monkeypatch.setattr(backend, "peptideProteinsMapper", FakeMapper)
    annotator = backend.ManifestOTFAnnotator(
        peptide_table_path=str(peptide_path),
        metaumbra_manifest_path=str(manifest_path),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "output.tsv"),
        db_path=str(peptide_db),
        genome_threshold="q0.01",
        on_empty_unit="warn-skip",
    )

    with pytest.warns(UserWarning, match="Unit 'u1' has no genomes"):
        result = annotator.run()

    assert result.completed_units == 1
    assert result.skipped_units == 1
    summary = pd.read_csv(result.summary_path, sep="\t")
    skipped = summary.loc[summary["analysis_unit_id"] == "u1"].iloc[0]
    assert skipped["status"] == "skipped"
    assert skipped["n_genomes_from_manifest"] == 0
    assert "no genomes at selected threshold q0.01" in skipped["message"]


def test_run_errors_on_empty_genome_unit_when_configured(tmp_path):
    manifest_data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    manifest_data["units"]["u1"]["genome_ids_q001"] = []
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest_data), encoding="utf-8")
    peptide_path = tmp_path / "peptides.tsv"
    peptide_path.write_text("Sequence\ts1\ts2\nPEP\t1\t1\n", encoding="utf-8")
    taxafunc_db = tmp_path / "taxafunc.db"
    peptide_db = tmp_path / "peptide.db"
    taxafunc_db.touch()
    peptide_db.touch()
    annotator = backend.ManifestOTFAnnotator(
        peptide_table_path=str(peptide_path),
        metaumbra_manifest_path=str(manifest_path),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "output.tsv"),
        db_path=str(peptide_db),
        genome_threshold="q0.01",
        on_empty_unit="error",
    )

    with pytest.raises(ValueError, match="Unit 'u1' has no genomes at selected threshold q0.01"):
        annotator.run()


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
