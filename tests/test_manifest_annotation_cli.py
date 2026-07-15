import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from metax.cli import annotate
from metax.peptide_annotator.manifest_otf import ManifestOTFRunResult
from metax.peptide_annotator.annotation_workflow import read_plain_genome_list_file


def test_cli_has_explicit_input_sources_without_legacy_mode_inference():
    parser = annotate.build_parser()
    destinations = {action.dest for action in parser._actions}
    assert "metaumbra_manifest" in destinations
    assert "input_source" in destinations
    assert "mode" not in destinations
    assert "unit_specific_manifest" not in destinations
    assert "genome_list_file" in destinations
    assert "intensity_col_prefix" in destinations
    source_action = next(action for action in parser._actions if action.dest == "input_source")
    assert source_action.choices == ["metaumbra-manifest", "metax-automatic", "genome-list"]


def test_custom_genome_list_is_not_interpreted_as_metaumbra_qvalue_output(tmp_path):
    genome_list = tmp_path / "genomes.tsv"
    genome_list.write_text("genome_id\tqvalue\ng1\t0.9\ng2\t0.01\n", encoding="utf-8")
    assert read_plain_genome_list_file(genome_list) == ["g1", "g2"]


def test_cli_result_json_contract(monkeypatch, tmp_path):
    peptide = tmp_path / "report.parquet"
    manifest = tmp_path / "genome_selection_manifest.json"
    database = tmp_path / "taxafunc.db"
    digest = tmp_path / "digests"
    output = tmp_path / "OTF.tsv"
    result_json = tmp_path / "result.json"
    for path in (peptide, manifest, database):
        path.write_text("x", encoding="utf-8")
    digest.mkdir()

    class FakeAnnotator:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def run(self):
            output.write_text("analysis_unit_id\tSequence\n__global__\tPEP\n", encoding="utf-8")
            return ManifestOTFRunResult(
                output_path=str(output), info_path="", summary_path="", rows=1,
                column_count=2, column_names=["analysis_unit_id", "Sequence"],
                completed_units=1, skipped_units=0, selected_genome_threshold="q0.05",
                manifest_schema_version="metaumbra.genome_selection_manifest.v1", warnings=[],
            )

    monkeypatch.setattr(annotate, "ManifestOTFAnnotator", FakeAnnotator)
    code = annotate.main([
        "--peptide-table", str(peptide),
        "--metaumbra-manifest", str(manifest),
        "--taxafunc-db", str(database),
        "--digested-genome-folders", str(digest),
        "--output", str(output),
        "--result-json", str(result_json),
    ])
    assert code == 0
    result = json.loads(result_json.read_text(encoding="utf-8"))
    assert result["manifest"]["path"] == str(manifest)
    assert result["number_of_units"] == 1
    assert result["selected_threshold"] == "q0.05"
    assert result["outputs"]["otf"]["path"] == str(output)
    assert result["input_source"] == "metaumbra-manifest"
    assert result["schema_version"] == "metax.annotation_result.v2"


@pytest.mark.parametrize(
    ("source", "extra_args", "expected_mode"),
    [
        ("metax-automatic", [], "automatic"),
        ("genome-list", ["--selected-genomes", "g1", "g2"], "provided"),
    ],
)
def test_cli_retains_non_metaumbra_and_custom_list_annotation(
    monkeypatch, tmp_path, source, extra_args, expected_mode
):
    peptide = tmp_path / "report.tsv"
    database = tmp_path / "taxafunc.db"
    digest = tmp_path / "digests"
    output = tmp_path / f"{source}.tsv"
    result_json = tmp_path / f"{source}.json"
    peptide.write_text("Sequence\tIntensity_s1\nPEP\t1\n", encoding="utf-8")
    database.write_text("x", encoding="utf-8")
    digest.mkdir()
    captured = {}

    class FakeGlobalAnnotator:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def run(self):
            output.write_text("Sequence\nPEP\n", encoding="utf-8")
            return SimpleNamespace(
                output_path=str(output),
                inputs={}, parameters={}, stages={},
                genome_selection={"method": expected_mode}, metrics={},
                outputs={"otf": {"path": str(output)}}, software={}, warnings=[],
            )

    monkeypatch.setattr(annotate, "GlobalOTFAnnotator", FakeGlobalAnnotator)
    code = annotate.main([
        "--input-source", source,
        "--peptide-table", str(peptide),
        "--taxafunc-db", str(database),
        "--digested-genome-folders", str(digest),
        "--output", str(output),
        "--result-json", str(result_json),
        "--intensity-col-prefix", "Abundance",
        *extra_args,
    ])
    assert code == 0
    assert captured["selection_mode"] == expected_mode
    assert captured["intensity_col_prefix"] == "Abundance"
    if expected_mode == "automatic":
        assert captured["selected_genome_source"] is None
    else:
        assert captured["selected_genome_source"] == "CLI --selected-genomes"
    result = json.loads(result_json.read_text(encoding="utf-8"))
    assert result["input_source"] == source
    assert result["manifest"] is None
