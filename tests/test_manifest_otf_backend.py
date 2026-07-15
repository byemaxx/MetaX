from pathlib import Path

import pandas as pd

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
