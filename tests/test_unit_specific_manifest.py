import json

import pytest

from metax.peptide_annotator.unit_specific_manifest import (
    load_unit_specific_manifest,
    resolve_manifest_sample_columns,
)


def _write_manifest(tmp_path, units):
    path = tmp_path / "unit_specific_manifest.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "metaumbra.unit_specific_manifest.v1",
                "generated_by": {"tool": "MetaUmbra", "version": "1.3.5"},
                "default_genome_threshold": "q0.05",
                "files": {
                    "sample_unit_mapping": "sample_unit_mapping.tsv",
                    "unit_call_counts": "unit_call_counts.tsv",
                    "unit_specific_genome_list_q005": "unit_specific_genome_list_q005.tsv",
                    "unit_specific_genome_list_q001": "unit_specific_genome_list_q001.tsv",
                },
                "units": units,
            }
        ),
        encoding="utf-8",
    )
    return path


def test_load_manifest_default_and_switch_thresholds(tmp_path):
    path = _write_manifest(
        tmp_path,
        {
            "u1": {
                "sample_columns": ["s1"],
                "n_samples": 1,
                "genome_ids_q005": ["MGYG000001456.1", "g2"],
                "genome_ids_q001": ["MGYG000001456.1"],
            }
        },
    )

    manifest = load_unit_specific_manifest(path)
    assert manifest.selected_genome_threshold == "q0.05"
    assert manifest.units["u1"].genome_ids == ["MGYG000001456.1", "g2"]

    manifest = load_unit_specific_manifest(path, genome_threshold="q001")
    assert manifest.selected_genome_threshold == "q0.01"
    assert manifest.units["u1"].genome_ids == ["MGYG000001456.1"]


def test_manifest_rejects_duplicate_samples(tmp_path):
    path = _write_manifest(
        tmp_path,
        {
            "u1": {"sample_columns": ["s1"], "n_samples": 1, "genome_ids_q005": ["g1"], "genome_ids_q001": ["g1"]},
            "u2": {"sample_columns": ["s1"], "n_samples": 1, "genome_ids_q005": ["g2"], "genome_ids_q001": ["g2"]},
        },
    )
    with pytest.raises(ValueError, match="multiple units"):
        load_unit_specific_manifest(path)


def test_manifest_subset_warning_or_error(tmp_path):
    path = _write_manifest(
        tmp_path,
        {
            "u1": {
                "sample_columns": ["s1"],
                "n_samples": 1,
                "genome_ids_q005": ["g1"],
                "genome_ids_q001": ["g1", "g2"],
            }
        },
    )
    with pytest.raises(ValueError, match="not present"):
        load_unit_specific_manifest(path, strict=True)
    with pytest.warns(UserWarning, match="not present"):
        load_unit_specific_manifest(path, strict=False)


def test_resolve_manifest_sample_columns_auto_modes():
    peptide_columns = [
        "s_exact",
        "Intensity_s_prefixed",
        "Intensity_strip",
        "_leading",
        r"C:\data\basename.raw",
    ]
    mapping = resolve_manifest_sample_columns(
        peptide_columns=peptide_columns,
        manifest_sample_columns=["s_exact", "s_prefixed", "strip", "leading", "basename"],
    )
    assert mapping["s_exact"] == "s_exact"
    assert mapping["s_prefixed"] == "Intensity_s_prefixed"
    assert mapping["strip"] == "Intensity_strip"
    assert mapping["leading"] == "_leading"
    assert mapping["basename"] == r"C:\data\basename.raw"


def test_resolve_manifest_sample_columns_input_sample_prefix():
    mapping = resolve_manifest_sample_columns(
        peptide_columns=["LFQ intensity s1", "LFQ intensity s2"],
        manifest_sample_columns=["s1", "s2"],
        input_sample_col_prefix="LFQ intensity ",
    )
    assert mapping == {
        "s1": "LFQ intensity s1",
        "s2": "LFQ intensity s2",
    }


def test_resolve_manifest_sample_columns_missing_and_ambiguous():
    with pytest.raises(ValueError, match="not found"):
        resolve_manifest_sample_columns(["Intensity_a"], ["missing"])

    with pytest.raises(ValueError, match="ambiguous"):
        resolve_manifest_sample_columns([r"C:\a\s.raw", r"D:\b\s.mzML"], ["s"])
