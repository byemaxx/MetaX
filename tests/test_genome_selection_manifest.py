import json
from pathlib import Path

import pytest

from metax.peptide_annotator.genome_selection_manifest import (
    SCHEMA_VERSION,
    load_genome_selection_manifest,
    resolve_manifest_sample_columns,
)


FIXTURE = Path(__file__).parent / "fixtures" / "genome_selection_manifest.v1.json"


def test_load_unified_manifest_and_thresholds():
    manifest = load_genome_selection_manifest(FIXTURE)
    assert manifest.schema_version == SCHEMA_VERSION
    assert manifest.unit_definition["mode"] == "metadata"
    assert manifest.selected_genome_threshold == "q0.05"
    assert manifest.units["u1"].sample_ids == ["s1"]
    assert manifest.units["u1"].genome_ids == ["g1", "g2"]
    strict = load_genome_selection_manifest(FIXTURE, genome_threshold="q0.01")
    assert strict.units["u1"].genome_ids == ["g1"]


def test_manifest_rejects_old_schema(tmp_path):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["schema_version"] = "metaumbra.unit_specific_manifest.v1"
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported genome selection"):
        load_genome_selection_manifest(path)


def test_manifest_rejects_duplicate_sample_assignments(tmp_path):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["units"]["u2"]["sample_ids"] = ["s1"]
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="multiple units"):
        load_genome_selection_manifest(path)


def test_manifest_rejects_empty_unit_and_genome_threshold_contract(tmp_path):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["units"]["u1"]["sample_ids"] = []
    data["units"]["u1"]["n_samples"] = 0
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="sample_ids must contain at least one item"):
        load_genome_selection_manifest(path)

    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["units"]["u1"]["genome_ids_q005"] = []
    data["units"]["u1"]["genome_ids_q001"] = []
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="no genomes at selected threshold q0.05"):
        load_genome_selection_manifest(path, genome_threshold="q0.05", strict=True)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("sample_ids", "s1"),
        ("genome_ids_q005", "g1"),
        ("genome_ids_q001", "g1"),
    ],
)
def test_manifest_rejects_string_values_for_array_fields(tmp_path, field, value):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["units"]["u1"][field] = value
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="must be an array of strings"):
        load_genome_selection_manifest(path)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("sample_ids", ["s1", "s1"]),
        ("genome_ids_q005", ["g1", "g1"]),
        ("genome_ids_q001", ["g1", "g1"]),
    ],
)
def test_manifest_rejects_duplicate_array_items(tmp_path, field, value):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["units"]["u1"][field] = value
    if field == "sample_ids":
        data["units"]["u1"]["n_samples"] = len(value)
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="must contain unique items"):
        load_genome_selection_manifest(path)


def test_manifest_rejects_missing_required_provenance(tmp_path):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["generated_by"].pop("run_id")
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="generated_by.run_id must be a string"):
        load_genome_selection_manifest(path)


def test_manifest_subset_violation_respects_strict_mode(tmp_path):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["units"]["u1"]["genome_ids_q001"].append("g3")
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="q0.01 genomes not present"):
        load_genome_selection_manifest(path, strict=True)
    with pytest.warns(UserWarning, match="q0.01 genomes not present"):
        manifest = load_genome_selection_manifest(path, strict=False)
    assert manifest.units["u1"].genome_ids == ["g1", "g2"]


def test_sample_mapping_is_one_to_one():
    mapping = resolve_manifest_sample_columns(
        ["Intensity_s1", "Intensity_s2"], ["s1", "s2"]
    )
    assert mapping == {"s1": "Intensity_s1", "s2": "Intensity_s2"}
    with pytest.raises(ValueError, match="distinct"):
        resolve_manifest_sample_columns(["s1"], ["s1", "s1.raw"])
