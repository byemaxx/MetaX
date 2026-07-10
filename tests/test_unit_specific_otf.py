import json
import sqlite3
import inspect
from pathlib import Path

import pandas as pd
import pytest

import metax.cli.annotate as annotate_cli
from metax.cli.annotate import build_parser
from metax.peptide_annotator.unit_specific_otf import (
    UnitSpecificOTFAnnotator,
    UnitSpecificOTFRunResult,
    _create_temporary_unit_directory,
    build_global_unit_specific_peptide_protein_map,
)
from metax.peptide_annotator.pep_table_to_otf import (
    query_peptide_proteins_from_digested_genome_folders,
    query_peptide_proteins_from_digested_genome_folders_nested,
)


def _write_manifest(path):
    path.write_text(
        json.dumps(
            {
                "schema_version": "metaumbra.unit_specific_manifest.v1",
                "generated_by": {"tool": "MetaUmbra", "version": "1.3.5"},
                "default_genome_threshold": "q0.05",
                "files": {},
                "units": {
                    "u1": {
                        "sample_columns": ["s1"],
                        "n_samples": 1,
                        "genome_ids_q005": ["g1"],
                        "genome_ids_q001": ["g1"],
                    },
                    "u2": {
                        "sample_columns": ["s2"],
                        "n_samples": 1,
                        "genome_ids_q005": ["g2"],
                        "genome_ids_q001": ["g2"],
                    },
                },
            }
        ),
        encoding="utf-8",
    )


def _write_peptide_protein_db(path):
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE peptide_proteins (peptide TEXT PRIMARY KEY, proteins TEXT)")
        conn.execute("INSERT INTO peptide_proteins VALUES (?, ?)", ("PEPA", json.dumps(["g1_p1", "g2_p2"])))
        conn.execute("INSERT INTO peptide_proteins VALUES (?, ?)", ("PEPB", json.dumps(["g2_p3"])))
        conn.commit()


def _write_taxafunc_db(path):
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE id2taxa (ID TEXT PRIMARY KEY, Taxa TEXT)")
        conn.execute("CREATE TABLE id2annotation (ID TEXT PRIMARY KEY, KEGG_ko TEXT)")
        conn.executemany(
            "INSERT INTO id2taxa VALUES (?, ?)",
            [
                ("g1", "d__Bacteria;p__P1;c__C1;o__O1;f__F1;g__G1;s__S1"),
                ("g2", "d__Bacteria;p__P2;c__C2;o__O2;f__F2;g__G2;s__S2"),
            ],
        )
        conn.executemany(
            "INSERT INTO id2annotation VALUES (?, ?)",
            [
                ("g1_p1", "K00001"),
                ("g2_p2", "K00002"),
                ("g2_p3", "K00003"),
            ],
        )
        conn.commit()


def test_unit_specific_otf_builds_units_and_artifacts(monkeypatch, tmp_path, capsys):
    calls = []
    numeric_apply_calls = 0
    original_dataframe_apply = pd.DataFrame.apply

    def tracking_dataframe_apply(self, func, *args, **kwargs):
        nonlocal numeric_apply_calls
        if func is pd.to_numeric:
            numeric_apply_calls += 1
        return original_dataframe_apply(self, func, *args, **kwargs)

    monkeypatch.setattr(pd.DataFrame, "apply", tracking_dataframe_apply)

    class FakeMapper:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.peptide_df = kwargs["peptide_df"]
            self.final_peptide_table = self.peptide_df.copy()
            self.peptides_after_mapping = len(self.peptide_df)
            self.selected_genomes_num = len(kwargs["genome_list"])
            assert all(
                Path(previous_call["output_path"]).parent.is_dir()
                for previous_call in calls
            )
            assert all(
                Path(previous_call["output_path"]).is_file()
                for previous_call in calls
            )
            calls.append(kwargs)

        def all_in_one(self, **kwargs):
            assert kwargs["save_output"] is False
            genome = self.kwargs["genome_list"][0]
            sample_cols = [c for c in self.peptide_df.columns if c.startswith("Intensity_")]
            return pd.DataFrame(
                {
                    "Sequence": self.peptide_df["Sequence"],
                    "Proteins": [f"{genome}_p1"] * len(self.peptide_df),
                    "LCA_level": ["genome"] * len(self.peptide_df),
                    "Taxon": [f"d__Bacteria|m__{genome}"] * len(self.peptide_df),
                    "Taxon_prop": [1.0] * len(self.peptide_df),
                    "None_func": ["none_func"] * len(self.peptide_df),
                    "None_func_prop": [1.0] * len(self.peptide_df),
                    **{col: self.peptide_df[col].tolist() for col in sample_cols},
                }
            )

    monkeypatch.setattr("metax.peptide_annotator.unit_specific_otf.peptideProteinsMapper", FakeMapper)

    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame(
        {
            "Sequence": ["PEPA", "PEPB"],
            "s1": [10, 0],
            "s2": [20, 5],
        }
    ).to_csv(peptide_table, sep="\t", index=False)
    manifest = tmp_path / "unit_specific_manifest.json"
    _write_manifest(manifest)
    taxafunc_db = tmp_path / "taxafunc.db"
    taxafunc_db.write_text("", encoding="utf-8")
    peptide_db = tmp_path / "peptide.db"
    peptide_db.write_text("", encoding="utf-8")
    output = tmp_path / "OTF_unit_specific.tsv"

    result = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(output),
        db_path=str(peptide_db),
        peptide_col="Sequence",
        duplicate_peptide_handling_mode="max",
    ).run(return_dataframe=True)

    assert [call["genome_list"] for call in calls] == [["g1"], ["g2"]]
    assert calls[0]["selected_genomes_set"] == {"g1"}
    assert calls[1]["selected_genomes_set"] == {"g2"}
    assert [call["duplicate_peptide_handling_mode"] for call in calls] == ["max", "max"]
    assert numeric_apply_calls == 1
    expected_temp_root = (
        tmp_path / "OTF_unit_specific_artifacts" / "per_unit" / "unit_otf"
    )
    assert all(
        Path(call["output_path"]).parent.parent == expected_temp_root
        for call in calls
    )
    assert [Path(call["output_path"]).parent.name for call in calls] == [
        "run_u1",
        "run_u2",
    ]
    assert expected_temp_root.is_dir()
    assert list(expected_temp_root.iterdir()) == []
    assert "UnitSpecificSequence" not in result.columns
    assert result[["analysis_unit_id", "Sequence"]].drop_duplicates().values.tolist() == [
        ["u1", "PEPA"],
        ["u2", "PEPA"],
        ["u2", "PEPB"],
    ]
    assert result.loc[result["analysis_unit_id"] == "u1", "Intensity_s2"].isna().all()
    assert result.loc[result["analysis_unit_id"] == "u2", "Intensity_s1"].isna().all()
    assert output.is_file()
    info_path = tmp_path / "OTF_unit_specific_info.txt"
    assert info_path.is_file()
    info_text = info_path.read_text(encoding="utf-8")
    assert "MetaX PeptideAnnotator Results" in info_text
    assert "Software: MetaX (UnitSpecificOTFAnnotator)" in info_text
    assert "Completed units: 2" in info_text
    assert "Shape: 3 rows" in info_text
    assert (tmp_path / "OTF_unit_specific_artifacts" / "unit_sample_column_mapping.tsv").is_file()
    assert (tmp_path / "OTF_unit_specific_artifacts" / "unit_annotation_summary.tsv").is_file()
    progress_log = capsys.readouterr().out
    assert "[Unit-specific] Preparing annotation for 2 units" in progress_log
    assert "[Unit-specific] Unit 1 of 2: u1 started" in progress_log
    assert "[Unit-specific] Unit 1 of 2: u1 completed" in progress_log
    assert "[Unit-specific] Unit 2 of 2: u2 started" in progress_log
    assert "[Unit-specific] Unit 2 of 2: u2 completed" in progress_log
    assert "2 units total, 2 completed, 0 skipped" in progress_log


def test_temporary_unit_directory_adds_timestamp_only_on_conflict(tmp_path):
    parent = tmp_path / "unit_otf"
    parent.mkdir()

    run_dir = _create_temporary_unit_directory(parent, "u1")
    assert run_dir.name == "run_u1"
    assert run_dir.is_dir()

    conflicting_run_dir = _create_temporary_unit_directory(parent, "u1")
    assert conflicting_run_dir.name.startswith("run_u1_")
    assert conflicting_run_dir.name != "run_u1"
    assert conflicting_run_dir.is_dir()


def test_default_run_does_not_read_merged_output(monkeypatch, tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame(
        {
            "Sequence": ["PEPA", "PEPB"],
            "Intensity_s1": [10, 0],
            "Intensity_s2": [20, 5],
        }
    ).to_csv(peptide_table, sep="\t", index=False)
    manifest = tmp_path / "unit_specific_manifest.json"
    _write_manifest(manifest)
    peptide_db = tmp_path / "peptide.db"
    _write_peptide_protein_db(peptide_db)
    taxafunc_db = tmp_path / "taxafunc.db"
    _write_taxafunc_db(taxafunc_db)
    output = tmp_path / "OTF_unit_specific.tsv"

    original_read_csv = pd.read_csv

    def guarded_read_csv(path, *args, **kwargs):
        if Path(path) == output:
            raise AssertionError("default run must not read the merged output")
        return original_read_csv(path, *args, **kwargs)

    monkeypatch.setattr(
        "metax.peptide_annotator.unit_specific_otf.pd.read_csv",
        guarded_read_csv,
    )

    result = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(output),
        db_path=str(peptide_db),
    ).run()

    assert isinstance(result, UnitSpecificOTFRunResult)
    assert result.output_path == str(output)
    assert result.rows == 3
    assert result.column_count == len(result.column_names)
    assert result.column_names == original_read_csv(
        output,
        sep="\t",
        nrows=0,
    ).columns.tolist()
    assert result.completed_units == 2
    assert result.skipped_units == 0
    assert "KEGG_ko" in result.column_names
    assert "KEGG_ko_prop" in result.column_names
    info_text = Path(result.info_path).read_text(encoding="utf-8")
    assert "Unique sequences: NA" in info_text
    assert "Unique protein groups: NA" in info_text


def test_return_dataframe_explicitly_reads_merged_output(monkeypatch, tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame(
        {
            "Sequence": ["PEPA"],
            "Intensity_s1": [10],
            "Intensity_s2": [5],
        }
    ).to_csv(peptide_table, sep="\t", index=False)
    manifest = tmp_path / "unit_specific_manifest.json"
    _write_manifest(manifest)
    peptide_db = tmp_path / "peptide.db"
    _write_peptide_protein_db(peptide_db)
    taxafunc_db = tmp_path / "taxafunc.db"
    _write_taxafunc_db(taxafunc_db)
    output = tmp_path / "OTF_unit_specific.tsv"

    output_reads = 0
    original_read_csv = pd.read_csv

    def tracking_read_csv(path, *args, **kwargs):
        nonlocal output_reads
        if Path(path) == output:
            output_reads += 1
        return original_read_csv(path, *args, **kwargs)

    monkeypatch.setattr(
        "metax.peptide_annotator.unit_specific_otf.pd.read_csv",
        tracking_read_csv,
    )

    result = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(output),
        db_path=str(peptide_db),
    ).run(return_dataframe=True)

    assert isinstance(result, pd.DataFrame)
    assert output_reads == 1
    assert result["analysis_unit_id"].tolist() == ["u1", "u2"]


def test_stream_merge_unit_outputs_is_chunked_and_fills_columns(tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    manifest = tmp_path / "manifest.json"
    taxafunc_db = tmp_path / "taxafunc.db"
    peptide_db = tmp_path / "peptide.db"
    for path in [peptide_table, manifest, taxafunc_db, peptide_db]:
        path.write_text("", encoding="utf-8")

    annotator = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "merged.tsv"),
        db_path=str(peptide_db),
    )
    unit1 = tmp_path / "u1.tsv"
    unit2 = tmp_path / "u2.tsv"
    pd.DataFrame(
        {
            "analysis_unit_id": ["u1", "u1"],
            "Sequence": ["PEPA", "PEPB"],
            "Proteins": ["g1_p1", "g1_p2"],
            "Intensity_s1": [10, 20],
        }
    ).to_csv(unit1, sep="\t", index=False)
    pd.DataFrame(
        {
            "analysis_unit_id": ["u2"],
            "Sequence": ["PEPC"],
            "Proteins": ["g2_p1"],
            "Mock_func": ["K00001"],
            "Intensity_s2": [30],
        }
    ).to_csv(unit2, sep="\t", index=False)
    records = [
        {
            "path": str(unit1),
            "columns": pd.read_csv(unit1, sep="\t", nrows=0).columns.tolist(),
            "temporary": False,
        },
        {
            "path": str(unit2),
            "columns": pd.read_csv(unit2, sep="\t", nrows=0).columns.tolist(),
            "temporary": True,
        },
    ]

    columns, rows = annotator._stream_merge_unit_outputs(
        records,
        ["Intensity_s1", "Intensity_s2"],
        merge_chunksize=1,
        collect_unique_stats=True,
    )

    merged = pd.read_csv(annotator.output_path, sep="\t")
    assert rows == 3
    assert annotator._last_unique_sequences == 3
    assert annotator._last_unique_protein_groups == 3
    assert merged.columns.tolist() == columns
    assert columns == [
        "analysis_unit_id",
        "Sequence",
        "Proteins",
        "Mock_func",
        "Intensity_s1",
        "Intensity_s2",
    ]
    assert merged.loc[merged["analysis_unit_id"] == "u1", "Intensity_s2"].isna().all()
    assert merged.loc[merged["analysis_unit_id"] == "u2", "Intensity_s1"].isna().all()
    assert merged.loc[merged["analysis_unit_id"] == "u1", "Mock_func"].isna().all()
    raw_rows = annotator.output_path.read_text(encoding="utf-8").splitlines()
    assert raw_rows[1].endswith("\t10\t")
    assert raw_rows[3].endswith("\t\t30")
    assert (
        annotator.output_path.read_text(encoding="utf-8").count("analysis_unit_id")
        == 1
    )
    assert unit1.is_file()
    assert not unit2.exists()


def test_stream_merge_unit_outputs_supports_temporary_pickle(tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    manifest = tmp_path / "manifest.json"
    taxafunc_db = tmp_path / "taxafunc.db"
    peptide_db = tmp_path / "peptide.db"
    for path in [peptide_table, manifest, taxafunc_db, peptide_db]:
        path.write_text("", encoding="utf-8")

    annotator = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "merged.tsv"),
        db_path=str(peptide_db),
    )
    unit_path = tmp_path / "u1.pkl"
    unit_frame = pd.DataFrame(
        {
            "analysis_unit_id": ["u1", "u1"],
            "Sequence": ["PEPA", "PEPB"],
            "Proteins": ["g1_p1", "g1_p2"],
            "Intensity_s1": [10, 20],
        }
    )
    unit_frame.to_pickle(unit_path)

    columns, rows = annotator._stream_merge_unit_outputs(
        [
            {
                "path": str(unit_path),
                "columns": unit_frame.columns.tolist(),
                "temporary": True,
                "format": "pickle",
            }
        ],
        ["Intensity_s1"],
        merge_chunksize=1,
    )

    merged = pd.read_csv(annotator.output_path, sep="\t")
    assert rows == 2
    assert merged.columns.tolist() == columns
    assert merged["Sequence"].tolist() == ["PEPA", "PEPB"]
    assert not unit_path.exists()


def test_add_unit_protein_mapping_preserves_manifest_genome_order(tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    manifest = tmp_path / "manifest.json"
    taxafunc_db = tmp_path / "taxafunc.db"
    peptide_db = tmp_path / "peptide.db"
    for path in [peptide_table, manifest, taxafunc_db, peptide_db]:
        path.write_text("", encoding="utf-8")
    annotator = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "out.tsv"),
        db_path=str(peptide_db),
    )

    result = annotator._add_unit_protein_mapping(
        pd.DataFrame({"Sequence": ["PEPA"]}),
        {
            "PEPA": {
                "g3": {"g3_p3"},
                "g1": {"g1_p1"},
                "g2": {"g2_p2"},
            }
        },
        ["g2", "g1"],
    )

    assert result["Proteins"].tolist() == ["g1_p1;g2_p2"]
    assert result["Genomes"].tolist() == ["g2;g1"]


def test_saved_per_unit_output_is_final_unit_specific_table(tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame(
        {
            "Sequence": ["PEPA"],
            "Intensity_s1": [10],
            "Intensity_s2": [0],
        }
    ).to_csv(peptide_table, sep="\t", index=False)
    manifest = tmp_path / "unit_specific_manifest.json"
    _write_manifest(manifest)
    peptide_db = tmp_path / "peptide.db"
    _write_peptide_protein_db(peptide_db)
    taxafunc_db = tmp_path / "taxafunc.db"
    _write_taxafunc_db(taxafunc_db)

    UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "out.tsv"),
        db_path=str(peptide_db),
        save_per_unit_outputs=True,
        include_unit_specific_sequence=True,
    ).run()

    per_unit_paths = list((tmp_path / "out_artifacts" / "per_unit").glob("u1_*_OTF.tsv"))
    assert len(per_unit_paths) == 1
    per_unit_path = per_unit_paths[0]
    per_unit = pd.read_csv(per_unit_path, sep="\t")
    assert per_unit["analysis_unit_id"].tolist() == ["u1"]
    assert per_unit["UnitSpecificSequence"].tolist() == ["u1||PEPA"]
    temporary_unit_root = (
        tmp_path / "out_artifacts" / "per_unit" / "unit_otf"
    )
    assert temporary_unit_root.is_dir()
    assert list(temporary_unit_root.iterdir()) == []


@pytest.mark.parametrize("intensity_col", ["Precursor.Normalised", "Precursor.Quantity"])
def test_unit_specific_otf_prepares_diann_parquet_with_shared_alias_rules(
    tmp_path,
    intensity_col,
):
    peptide_table = tmp_path / "report.parquet"
    pd.DataFrame(
        {
            "Run": ["s1.raw", "s2.raw"],
            "Stripped.Sequence": ["PEPA", "PEPA"],
            intensity_col: [10.0, 20.0],
        }
    ).to_parquet(peptide_table)
    manifest = tmp_path / "unit_specific_manifest.json"
    _write_manifest(manifest)
    taxafunc_db = tmp_path / "taxafunc.db"
    taxafunc_db.write_text("", encoding="utf-8")
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()

    annotator = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "OTF.tsv"),
        digested_genome_folders=str(digested_dir),
        peptide_col="Stripped.Sequence",
    )

    prepared = annotator._read_peptide_table(["s1", "s2"])

    assert annotator.peptide_col == "Stripped.Sequence"
    assert prepared.loc[0, "s1"] == 10.0
    assert prepared.loc[0, "s2"] == 20.0
    assert annotator._last_sample_mapping == {"s1": "s1", "s2": "s2"}
    assert annotator.peptide_table_prepare_metadata["diann_intensity_column"] == intensity_col


def test_unit_specific_otf_uses_selected_diann_intensity_column(tmp_path):
    peptide_table = tmp_path / "report.parquet"
    pd.DataFrame(
        {
            "Run": ["s1.raw", "s2.raw"],
            "Stripped.Sequence": ["PEPA", "PEPA"],
            "Precursor.Normalised": [10.0, 20.0],
            "Precursor.Quantity": [100.0, 200.0],
        }
    ).to_parquet(peptide_table)
    manifest = tmp_path / "unit_specific_manifest.json"
    _write_manifest(manifest)
    taxafunc_db = tmp_path / "taxafunc.db"
    taxafunc_db.write_text("", encoding="utf-8")
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()

    annotator = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "OTF.tsv"),
        digested_genome_folders=str(digested_dir),
        peptide_col="Stripped.Sequence",
        diann_intensity_col="Precursor.Quantity",
    )

    prepared = annotator._read_peptide_table(["s1", "s2"])

    assert prepared.loc[0, "s1"] == 100.0
    assert prepared.loc[0, "s2"] == 200.0
    assert (
        annotator.peptide_table_prepare_metadata["diann_intensity_column"]
        == "Precursor.Quantity"
    )


def test_unit_specific_otf_diann_mapping_preserves_duplicate_run_basenames(tmp_path):
    peptide_table = tmp_path / "report.parquet"
    pd.DataFrame(
        {
            "Run": [r"C:\batch1\s1.raw", r"C:\batch2\s1.raw"],
            "Stripped.Sequence": ["PEPA", "PEPA"],
            "Precursor.Quantity": [10.0, 20.0],
        }
    ).to_parquet(peptide_table)
    manifest = tmp_path / "unit_specific_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "metaumbra.unit_specific_manifest.v1",
                "generated_by": {"tool": "MetaUmbra", "version": "1.3.7"},
                "default_genome_threshold": "q0.05",
                "files": {},
                "units": {
                    "u1": {
                        "sample_columns": [r"C:\batch1\s1.raw"],
                        "n_samples": 1,
                        "genome_ids_q005": ["g1"],
                        "genome_ids_q001": ["g1"],
                    },
                    "u2": {
                        "sample_columns": [r"C:\batch2\s1.raw"],
                        "n_samples": 1,
                        "genome_ids_q005": ["g2"],
                        "genome_ids_q001": ["g2"],
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    taxafunc_db = tmp_path / "taxafunc.db"
    taxafunc_db.write_text("", encoding="utf-8")
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()

    annotator = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "OTF.tsv"),
        digested_genome_folders=str(digested_dir),
        peptide_col="Stripped.Sequence",
        diann_intensity_col="Precursor.Quantity",
    )

    prepared = annotator._read_peptide_table([r"C:\batch1\s1.raw", r"C:\batch2\s1.raw"])

    assert prepared.loc[0, "s1"] == 10.0
    assert prepared.loc[0, "s1_2"] == 20.0
    assert annotator._last_sample_mapping == {
        r"C:\batch1\s1.raw": "s1",
        r"C:\batch2\s1.raw": "s1_2",
    }


def test_unit_specific_otf_diann_mapping_prefers_prepared_columns(tmp_path):
    peptide_table = tmp_path / "report.parquet"
    pd.DataFrame(
        {
            "Run": [r"C:\batch1\s1.raw", r"C:\batch2\s1.raw"],
            "Stripped.Sequence": ["PEPA", "PEPA"],
            "Precursor.Quantity": [10.0, 20.0],
        }
    ).to_parquet(peptide_table)
    manifest = tmp_path / "unit_specific_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "metaumbra.unit_specific_manifest.v1",
                "generated_by": {"tool": "MetaUmbra", "version": "1.3.7"},
                "default_genome_threshold": "q0.05",
                "files": {},
                "units": {
                    "u1": {
                        "sample_columns": ["s1"],
                        "n_samples": 1,
                        "genome_ids_q005": ["g1"],
                        "genome_ids_q001": ["g1"],
                    },
                    "u2": {
                        "sample_columns": ["s1_2"],
                        "n_samples": 1,
                        "genome_ids_q005": ["g2"],
                        "genome_ids_q001": ["g2"],
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    taxafunc_db = tmp_path / "taxafunc.db"
    taxafunc_db.write_text("", encoding="utf-8")
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()

    annotator = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "OTF.tsv"),
        digested_genome_folders=str(digested_dir),
        peptide_col="Stripped.Sequence",
        diann_intensity_col="Precursor.Quantity",
    )

    prepared = annotator._read_peptide_table(["s1", "s1_2"])

    assert prepared.loc[0, "s1"] == 10.0
    assert prepared.loc[0, "s1_2"] == 20.0
    assert annotator._last_sample_mapping == {
        "s1": "s1",
        "s1_2": "s1_2",
    }


def test_unit_specific_otf_keeps_wide_parquet_compatible(tmp_path):
    peptide_table = tmp_path / "wide.parquet"
    pd.DataFrame(
        {
            "Sequence": ["PEPA"],
            "Intensity_s1": [10.0],
            "Intensity_s2": [20.0],
        }
    ).to_parquet(peptide_table)
    manifest = tmp_path / "unit_specific_manifest.json"
    _write_manifest(manifest)
    taxafunc_db = tmp_path / "taxafunc.db"
    taxafunc_db.write_text("", encoding="utf-8")
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()

    annotator = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "OTF.tsv"),
        digested_genome_folders=str(digested_dir),
    )

    prepared = annotator._read_peptide_table()

    assert prepared.columns.tolist() == ["Sequence", "Intensity_s1", "Intensity_s2"]
    assert annotator.peptide_table_prepare_metadata["input_peptide_table_format"] == "parquet"


def test_unit_specific_otf_reads_only_required_tsv_columns_with_prefix_aliases(
    monkeypatch,
    tmp_path,
):
    peptide_table = tmp_path / "wide.tsv"
    pd.DataFrame(
        {
            "Sequence": ["PEPA"],
            "Input_s1": [10.0],
            "Input_s2": [20.0],
            "Irrelevant": ["unused"],
        }
    ).to_csv(peptide_table, sep="\t", index=False)
    manifest = tmp_path / "unit_specific_manifest.json"
    _write_manifest(manifest)
    taxafunc_db = tmp_path / "taxafunc.db"
    taxafunc_db.write_text("", encoding="utf-8")
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()
    read_calls = []
    original_read_csv = pd.read_csv

    def tracking_read_csv(path, *args, **kwargs):
        if Path(path) == peptide_table:
            read_calls.append(dict(kwargs))
        return original_read_csv(path, *args, **kwargs)

    monkeypatch.setattr(
        "metax.peptide_annotator.unit_specific_otf.pd.read_csv",
        tracking_read_csv,
    )
    annotator = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "OTF.tsv"),
        digested_genome_folders=str(digested_dir),
        input_sample_col_prefix="Input_",
    )

    prepared = annotator._read_peptide_table(["s1", "s2"])

    assert prepared.columns.tolist() == ["Sequence", "Input_s1", "Input_s2"]
    assert annotator._last_sample_mapping == {
        "s1": "Input_s1",
        "s2": "Input_s2",
    }
    assert read_calls[0]["nrows"] == 0
    assert read_calls[1]["usecols"] == ["Sequence", "Input_s1", "Input_s2"]


def test_unit_specific_otf_reads_only_required_wide_parquet_columns(
    monkeypatch,
    tmp_path,
):
    peptide_table = tmp_path / "wide.parquet"
    pd.DataFrame(
        {
            "Sequence": ["PEPA"],
            "Intensity_s1": [10.0],
            "Intensity_s2": [20.0],
            "Irrelevant": ["unused"],
        }
    ).to_parquet(peptide_table)
    manifest = tmp_path / "unit_specific_manifest.json"
    _write_manifest(manifest)
    taxafunc_db = tmp_path / "taxafunc.db"
    taxafunc_db.write_text("", encoding="utf-8")
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()
    read_calls = []
    original_read_parquet = pd.read_parquet

    def tracking_read_parquet(path, *args, **kwargs):
        if Path(path) == peptide_table:
            read_calls.append(dict(kwargs))
        return original_read_parquet(path, *args, **kwargs)

    monkeypatch.setattr(
        "metax.peptide_annotator.unit_specific_otf.pd.read_parquet",
        tracking_read_parquet,
    )
    annotator = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "OTF.tsv"),
        digested_genome_folders=str(digested_dir),
    )

    prepared = annotator._read_peptide_table(["s1", "s2"])

    assert prepared.columns.tolist() == ["Sequence", "Intensity_s1", "Intensity_s2"]
    assert read_calls == [
        {"columns": ["Sequence", "Intensity_s1", "Intensity_s2"]}
    ]


def test_build_unit_dataframe_filters_before_copy_and_preserves_column_order(tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    manifest = tmp_path / "manifest.json"
    taxafunc_db = tmp_path / "taxafunc.db"
    peptide_db = tmp_path / "peptide.db"
    for path in [peptide_table, manifest, taxafunc_db, peptide_db]:
        path.write_text("", encoding="utf-8")
    annotator = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "out.tsv"),
        db_path=str(peptide_db),
    )
    peptide_df = pd.DataFrame(
        {
            "Sequence": ["ZERO", "S2_ONLY", "BOTH"],
            "input_s1": [0, 0, 2],
            "input_s2": [0, 3, 4],
            "unused": [1, 1, 1],
        }
    )

    unit_df, canonical_cols = annotator._build_unit_dataframe(
        peptide_df,
        ["s2", "s1"],
        {"s1": "input_s1", "s2": "input_s2"},
    )

    assert canonical_cols == ["Intensity_s2", "Intensity_s1"]
    assert unit_df.columns.tolist() == [
        "Sequence",
        "Intensity_s2",
        "Intensity_s1",
    ]
    assert unit_df["Sequence"].tolist() == ["S2_ONLY", "BOTH"]
    assert unit_df[["Intensity_s2", "Intensity_s1"]].values.tolist() == [
        [3, 0],
        [4, 2],
    ]


def test_warn_skip_missing_sample_writes_sparse_canonical_column(tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame(
        {
            "Sequence": ["PEPA"],
            "Intensity_s1": [10],
            "Irrelevant": ["unused"],
        }
    ).to_csv(peptide_table, sep="\t", index=False)
    manifest = tmp_path / "unit_specific_manifest.json"
    _write_manifest(manifest)
    peptide_db = tmp_path / "peptide.db"
    _write_peptide_protein_db(peptide_db)
    taxafunc_db = tmp_path / "taxafunc.db"
    _write_taxafunc_db(taxafunc_db)

    with pytest.warns(UserWarning) as warning_records:
        result = UnitSpecificOTFAnnotator(
            peptide_table_path=str(peptide_table),
            unit_specific_manifest_path=str(manifest),
            taxafunc_anno_db_path=str(taxafunc_db),
            output_path=str(tmp_path / "out.tsv"),
            db_path=str(peptide_db),
            on_missing_sample="warn-skip",
        ).run(return_dataframe=True)

    assert any(
        "Manifest sample 's2' was not found" in str(record.message)
        for record in warning_records
    )
    assert result["analysis_unit_id"].tolist() == ["u1"]
    assert result.columns[-2:].tolist() == ["Intensity_s1", "Intensity_s2"]
    assert result["Intensity_s2"].isna().all()


def test_unit_specific_otf_defaults_and_path_validation(tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame({"Sequence": ["PEPA"], "Intensity_s1": [10]}).to_csv(peptide_table, sep="\t", index=False)
    manifest = tmp_path / "unit_specific_manifest.json"
    _write_manifest(manifest)
    taxafunc_db = tmp_path / "taxafunc.db"
    taxafunc_db.write_text("", encoding="utf-8")
    peptide_db = tmp_path / "peptide.db"
    peptide_db.write_text("", encoding="utf-8")

    annotator = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "out.tsv"),
        db_path=str(peptide_db),
    )
    assert annotator.distinct_genome_threshold == 0

    parser = build_parser()
    args = parser.parse_args(["--unit-specific"])
    assert args.distinct_genome_threshold == 0
    assert args.duplicate_peptide_handling_mode == "sum"
    assert args.include_unit_specific_sequence is False
    assert args.output_sample_col_prefix == "Intensity_"

    with pytest.raises(ValueError, match="duplicate_peptide_handling_mode"):
        UnitSpecificOTFAnnotator(
            peptide_table_path=str(peptide_table),
            unit_specific_manifest_path=str(manifest),
            taxafunc_anno_db_path=str(taxafunc_db),
            output_path=str(tmp_path / "out.tsv"),
            db_path=str(peptide_db),
            duplicate_peptide_handling_mode="bad-mode",
        )

    with pytest.raises(FileNotFoundError, match="db_path"):
        UnitSpecificOTFAnnotator(
            peptide_table_path=str(peptide_table),
            unit_specific_manifest_path=str(manifest),
            taxafunc_anno_db_path=str(taxafunc_db),
            output_path=str(tmp_path / "out.tsv"),
            db_path=str(tmp_path / "missing.db"),
        )

    not_a_dir = tmp_path / "not_a_dir.tsv"
    not_a_dir.write_text("", encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="digested_genome_folders"):
        UnitSpecificOTFAnnotator(
            peptide_table_path=str(peptide_table),
            unit_specific_manifest_path=str(manifest),
            taxafunc_anno_db_path=str(taxafunc_db),
            output_path=str(tmp_path / "out.tsv"),
            digested_genome_folders=[str(not_a_dir)],
        )


def test_unit_specific_otf_real_sqlite_integration(tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame(
        {
            "Sequence": ["PEPA", "PEPB"],
            "Intensity_s1": [10, 0],
            "Intensity_s2": [20, 5],
        }
    ).to_csv(peptide_table, sep="\t", index=False)
    manifest = tmp_path / "unit_specific_manifest.json"
    _write_manifest(manifest)
    peptide_db = tmp_path / "peptide.db"
    _write_peptide_protein_db(peptide_db)
    taxafunc_db = tmp_path / "taxafunc.db"
    _write_taxafunc_db(taxafunc_db)
    output = tmp_path / "OTF_unit_specific.tsv"

    result = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(output),
        db_path=str(peptide_db),
        peptide_col="Sequence",
    ).run(return_dataframe=True)

    assert "UnitSpecificSequence" not in result.columns
    assert result["Sequence"].tolist() == ["PEPA", "PEPA", "PEPB"]
    assert result.loc[result["analysis_unit_id"] == "u1", "Proteins"].tolist() == ["g1_p1"]
    assert result.loc[result["analysis_unit_id"] == "u2", "Proteins"].tolist() == ["g2_p2", "g2_p3"]
    assert output.is_file()


def test_unit_specific_otf_can_include_unit_specific_sequence_for_debug(tmp_path, capsys):
    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame({"Sequence": ["PEPA"], "Intensity_s1": [10], "Intensity_s2": [0]}).to_csv(
        peptide_table,
        sep="\t",
        index=False,
    )
    manifest = tmp_path / "unit_specific_manifest.json"
    _write_manifest(manifest)
    peptide_db = tmp_path / "peptide.db"
    _write_peptide_protein_db(peptide_db)
    taxafunc_db = tmp_path / "taxafunc.db"
    _write_taxafunc_db(taxafunc_db)

    result = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "OTF_unit_specific.tsv"),
        db_path=str(peptide_db),
        include_unit_specific_sequence=True,
    ).run(return_dataframe=True)

    assert "UnitSpecificSequence" in result.columns
    assert result["UnitSpecificSequence"].tolist() == ["u1||PEPA"]
    progress_log = capsys.readouterr().out
    assert "[Unit-specific] Unit 2 of 2: u2 skipped" in progress_log
    assert "2 units total, 1 completed, 1 skipped" in progress_log


def test_unit_specific_run_summary_records_sparse_zero_output(tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame(
        {
            "Sequence": ["PEPA", "PEPB"],
            "Intensity_s1": [10, 0],
            "Intensity_s2": [0, 20],
        }
    ).to_csv(peptide_table, sep="\t", index=False)
    manifest = tmp_path / "unit_specific_manifest.json"
    _write_manifest(manifest)
    peptide_db = tmp_path / "peptide.db"
    _write_peptide_protein_db(peptide_db)
    taxafunc_db = tmp_path / "taxafunc.db"
    _write_taxafunc_db(taxafunc_db)
    output = tmp_path / "OTF_unit_specific.tsv"

    result = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(output),
        db_path=str(peptide_db),
    ).run(return_dataframe=True)

    assert result.loc[result["analysis_unit_id"] == "u1", "Intensity_s2"].isna().all()
    assert result.loc[result["analysis_unit_id"] == "u2", "Intensity_s1"].isna().all()
    summary = json.loads(
        (tmp_path / "OTF_unit_specific_artifacts" / "run_summary.json").read_text(
            encoding="utf-8"
        )
    )
    assert summary["sparse_zero_intensity_output"] is True
    info_text = (tmp_path / "OTF_unit_specific_info.txt").read_text(encoding="utf-8")
    assert "sparse_zero_intensity_output: True" in info_text


def _write_shared_genome_manifest(path):
    path.write_text(
        json.dumps(
            {
                "schema_version": "metaumbra.unit_specific_manifest.v1",
                "generated_by": {"tool": "MetaUmbra", "version": "1.3.5"},
                "default_genome_threshold": "q0.05",
                "files": {},
                "units": {
                    "u1": {
                        "sample_columns": ["s1"],
                        "n_samples": 1,
                        "genome_ids_q005": ["g1", "g2"],
                        "genome_ids_q001": ["g1", "g2"],
                    },
                    "u2": {
                        "sample_columns": ["s2"],
                        "n_samples": 1,
                        "genome_ids_q005": ["g2", "g3"],
                        "genome_ids_q001": ["g2", "g3"],
                    },
                },
            }
        ),
        encoding="utf-8",
    )


def test_global_unit_specific_mapping_scans_shared_genomes_once(monkeypatch, tmp_path):
    manifest_path = tmp_path / "manifest.json"
    _write_shared_genome_manifest(manifest_path)
    from metax.peptide_annotator.unit_specific_manifest import load_unit_specific_manifest

    manifest = load_unit_specific_manifest(manifest_path)
    calls = []

    def fake_query(**kwargs):
        calls.append(kwargs)
        return {
            "PEPA": {
                "g1": {"g1_p1"},
                "g2": {"g2_p2"},
                "g3": {"g3_p3"},
            },
            "PEPB": {"g2": {"g2_p4"}},
        }

    monkeypatch.setattr(
        "metax.peptide_annotator.unit_specific_otf.query_peptide_proteins_from_digested_genome_folders_nested",
        fake_query,
    )
    result = build_global_unit_specific_peptide_protein_map(
        peptide_df=pd.DataFrame(
            {
                "Sequence": ["PEPA", "PEPB", "PEPC"],
                "s1": [1, 0, 0],
                "s2": [0, 1, 0],
            }
        ),
        peptide_col="Sequence",
        manifest=manifest,
        digested_genome_folders=str(tmp_path),
    )

    assert len(calls) == 1
    assert calls[0]["selected_genomes_set"] == {"g1", "g2", "g3"}
    assert calls[0]["peptide_list"] == ["PEPA", "PEPB", "PEPC"]
    assert result == {
        "PEPA": {
            "g1": {"g1_p1"},
            "g2": {"g2_p2"},
            "g3": {"g3_p3"},
        },
        "PEPB": {"g2": {"g2_p4"}},
    }


def test_nested_digested_scanner_reads_each_union_genome_once(monkeypatch, tmp_path):
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()
    for genome_id, rows in {
        "g1": [("p1", "PEPA")],
        "g2": [("p2;p3", "PEPA"), ("p4", "PEPB")],
        "g3": [("g3_p5", "PEPB")],
        "unused": [("p6", "PEPA")],
    }.items():
        pd.DataFrame(rows, columns=["Protein", "Peptide"]).to_csv(
            digested_dir / f"{genome_id}.tsv",
            sep="\t",
            index=False,
        )

    import metax.peptide_annotator.pep_table_to_otf as mapping_module

    original_processor = mapping_module._process_digested_genome_batch_for_nested_mapping
    scanned_files = []

    def recording_processor(file_paths, *args, **kwargs):
        scanned_files.extend(file_paths)
        return original_processor(file_paths, *args, **kwargs)

    monkeypatch.setattr(
        mapping_module,
        "_process_digested_genome_batch_for_nested_mapping",
        recording_processor,
    )
    result = query_peptide_proteins_from_digested_genome_folders_nested(
        digested_genome_folders=str(digested_dir),
        peptide_list=["PEPA", "PEPB", "ABSENT"],
        selected_genomes_set={"g1", "g2", "g3"},
        n_jobs=2,
        parallel_backend="thread",
    )

    assert sorted(Path(path).stem for path in scanned_files) == ["g1", "g2", "g3"]
    assert result == {
        "PEPA": {
            "g1": {"g1_p1"},
            "g2": {"g2_p2", "g2_p3"},
        },
        "PEPB": {
            "g2": {"g2_p4"},
            "g3": {"g3_p5"},
        },
    }


def test_nested_scanner_defaults_to_subprocess(monkeypatch, tmp_path):
    calls = []

    def fake_subprocess(**kwargs):
        calls.append(kwargs)
        return {"PEPA": {"g1": {"g1_p1"}}}

    monkeypatch.setattr(
        "metax.peptide_annotator.pep_table_to_otf._query_peptide_proteins_nested_via_subprocess",
        fake_subprocess,
    )
    result = query_peptide_proteins_from_digested_genome_folders_nested(
        digested_genome_folders=str(tmp_path),
        peptide_list=["PEPA"],
        selected_genomes_set={"g1"},
    )

    assert inspect.signature(
        query_peptide_proteins_from_digested_genome_folders_nested
    ).parameters["parallel_backend"].default == "subprocess"
    assert len(calls) == 1
    assert result == {"PEPA": {"g1": {"g1_p1"}}}


def test_nested_scanner_subprocess_matches_direct_backends(tmp_path):
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()
    pd.DataFrame(
        [("p1;p2", "PEPA"), ("p3", "PEPB")],
        columns=["Protein", "Peptide"],
    ).to_csv(digested_dir / "g1.tsv", sep="\t", index=False)
    expected = {
        "PEPA": {"g1": {"g1_p1", "g1_p2"}},
        "PEPB": {"g1": {"g1_p3"}},
    }

    results = {
        backend: query_peptide_proteins_from_digested_genome_folders_nested(
            digested_genome_folders=str(digested_dir),
            peptide_list=["PEPA", "PEPB"],
            selected_genomes_set={"g1"},
            n_jobs=1,
            parallel_backend=backend,
        )
        for backend in ("thread", "process", "subprocess")
    }

    assert results == {backend: expected for backend in results}


def test_nested_scanner_warns_for_malformed_genome(tmp_path, capsys):
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()
    pd.DataFrame({"Wrong": ["x"]}).to_csv(
        digested_dir / "z_bad.tsv",
        sep="\t",
        index=False,
    )
    pd.DataFrame({"Protein": ["p1"], "Peptide": ["PEPA"]}).to_csv(
        digested_dir / "a_good.tsv",
        sep="\t",
        index=False,
    )

    result = query_peptide_proteins_from_digested_genome_folders_nested(
        digested_genome_folders=str(digested_dir),
        peptide_list=["PEPA"],
        selected_genomes_set={"z_bad", "a_good"},
        digested_peptide_col="Peptide",
        digested_protein_col="Protein",
        n_jobs=1,
        parallel_backend="thread",
    )

    assert result == {"PEPA": {"a_good": {"a_good_p1"}}}
    output = capsys.readouterr().out
    assert "Warning: skipped malformed genome TSV" in output
    assert "z_bad.tsv" in output
    assert "ValueError" in output


def test_digested_scanner_skips_malformed_first_file_without_losing_later_hits(
    tmp_path,
    capsys,
):
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()
    pd.DataFrame({"Unrelated": ["x"]}).to_csv(
        digested_dir / "0_bad.tsv",
        sep="\t",
        index=False,
    )
    pd.DataFrame({"Protein": ["p1"], "Peptide": ["PEPA"]}).to_csv(
        digested_dir / "1_good.tsv",
        sep="\t",
        index=False,
    )

    mapping, peptide_col, protein_col = query_peptide_proteins_from_digested_genome_folders(
        digested_genome_folders=str(digested_dir),
        peptide_list=["PEPA"],
        n_jobs=1,
        parallel_backend="thread",
    )

    assert mapping == {"PEPA": "1_good_p1"}
    assert (peptide_col, protein_col) == ("", "")
    output = capsys.readouterr().out
    assert "0_bad.tsv" in output
    assert "ValueError" in output


def test_nested_digested_scanner_resolves_columns_for_each_header(tmp_path):
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()
    pd.DataFrame({"Protein": ["p1"], "Peptide": ["PEPA"]}).to_csv(
        digested_dir / "g1.tsv",
        sep="\t",
        index=False,
    )
    pd.DataFrame({"protein_id": ["p2"], "Sequence": ["PEPB"]}).to_csv(
        digested_dir / "g2.tsv",
        sep="\t",
        index=False,
    )

    result = query_peptide_proteins_from_digested_genome_folders_nested(
        digested_genome_folders=str(digested_dir),
        peptide_list=["PEPA", "PEPB"],
        selected_genomes_set={"g1", "g2"},
        n_jobs=1,
        parallel_backend="thread",
    )

    assert result == {
        "PEPA": {"g1": {"g1_p1"}},
        "PEPB": {"g2": {"g2_p2"}},
    }


def test_digested_scanner_respects_explicit_columns_per_file(tmp_path):
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()
    pd.DataFrame({"CustomPeptide": ["PEPA"], "CustomProtein": ["p1"]}).to_csv(
        digested_dir / "g1.tsv",
        sep="\t",
        index=False,
    )

    mapping, peptide_col, protein_col = query_peptide_proteins_from_digested_genome_folders(
        digested_genome_folders=str(digested_dir),
        peptide_list=["PEPA"],
        digested_peptide_col="CustomPeptide",
        digested_protein_col="CustomProtein",
        n_jobs=1,
        parallel_backend="thread",
    )

    assert mapping == {"PEPA": "g1_p1"}
    assert (peptide_col, protein_col) == ("CustomPeptide", "CustomProtein")


def test_digested_scanner_falls_back_to_inference_when_explicit_columns_are_missing(
    tmp_path,
):
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()
    pd.DataFrame({"protein_id": ["p1"], "Sequence": ["PEPA"]}).to_csv(
        digested_dir / "g1.tsv",
        sep="\t",
        index=False,
    )

    mapping, _, _ = query_peptide_proteins_from_digested_genome_folders(
        digested_genome_folders=str(digested_dir),
        peptide_list=["PEPA"],
        digested_peptide_col="Peptide",
        digested_protein_col="Protein",
        n_jobs=1,
        parallel_backend="thread",
    )

    assert mapping == {"PEPA": "g1_p1"}


def test_unit_specific_cli_passes_extended_options(monkeypatch, tmp_path):
    captured = {}
    defaults = build_parser().parse_args([])
    assert defaults.merge_chunksize == 100_000
    assert defaults.collect_unique_stats is False

    class FakeAnnotator:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def run(self):
            return pd.DataFrame()

    monkeypatch.setattr(annotate_cli, "UnitSpecificOTFAnnotator", FakeAnnotator)
    result = annotate_cli.main(
        [
            "--unit-specific",
            "--peptide-table",
            str(tmp_path / "peptides.tsv"),
            "--unit-specific-manifest",
            str(tmp_path / "manifest.json"),
            "--taxafunc-db",
            str(tmp_path / "taxafunc.db"),
            "--output",
            str(tmp_path / "out.tsv"),
            "--peptide-db",
            str(tmp_path / "peptide.db"),
            "--duplicate-peptide-handling-mode",
            "max",
            "--include-unit-specific-sequence",
            "--merge-chunksize",
            "7",
            "--collect-unique-stats",
        ]
    )

    assert result == 0
    assert captured["duplicate_peptide_handling_mode"] == "max"
    assert captured["include_unit_specific_sequence"] is True
    assert captured["output_sample_col_prefix"] == "Intensity_"
    assert captured["merge_chunksize"] == 7
    assert captured["collect_unique_stats"] is True


def test_run_prefilters_globally_zero_peptides_before_global_mapping(
    monkeypatch,
    tmp_path,
    capsys,
):
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest)
    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame(
        {
            "Sequence": ["PEPA", "PEPB", "PEPC"],
            "s1": [10, 0, 0],
            "s2": [0, 20, 0],
        }
    ).to_csv(peptide_table, sep="\t", index=False)
    taxafunc_db = tmp_path / "taxafunc.db"
    taxafunc_db.write_text("", encoding="utf-8")
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()
    captured_peptides = []

    def fake_build_global_map(**kwargs):
        captured_peptides.extend(kwargs["peptide_df"]["Sequence"].tolist())
        return {
            "PEPA": {"g1": {"g1_p1"}},
            "PEPB": {"g2": {"g2_p1"}},
        }

    class FakeMapper:
        def __init__(self, **kwargs):
            self.peptide_table = kwargs["peptide_df"].copy()
            self.final_peptide_table = self.peptide_table.copy()
            self.peptides_after_mapping = len(self.peptide_table)
            self.selected_genomes_num = len(kwargs["genome_list"])

        def all_in_one(self, **kwargs):
            sample_cols = [
                column
                for column in self.peptide_table
                if column.startswith("Intensity_")
            ]
            return pd.DataFrame(
                {
                    "Sequence": self.peptide_table["Sequence"],
                    "Proteins": self.peptide_table["Proteins"],
                    "LCA_level": ["genome"] * len(self.peptide_table),
                    "Taxon": ["d__Bacteria"] * len(self.peptide_table),
                    "Taxon_prop": [1.0] * len(self.peptide_table),
                    **{
                        column: self.peptide_table[column].tolist()
                        for column in sample_cols
                    },
                }
            )

    monkeypatch.setattr(
        "metax.peptide_annotator.unit_specific_otf.build_global_unit_specific_peptide_protein_map",
        fake_build_global_map,
    )
    monkeypatch.setattr(
        "metax.peptide_annotator.unit_specific_otf.peptideProteinsMapper",
        FakeMapper,
    )

    result = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "out.tsv"),
        digested_genome_folders=str(digested_dir),
    ).run(return_dataframe=True)

    assert captured_peptides == ["PEPA", "PEPB"]
    assert result["Sequence"].tolist() == ["PEPA", "PEPB"]
    assert "PEPC" not in result["Sequence"].tolist()
    assert (
        "[Unit-specific] Digested scan candidates: 2 unique peptides with nonzero "
        "intensity in mapped manifest samples."
        in capsys.readouterr().out
    )


def test_unit_specific_folder_mode_reuses_global_map_and_filters_by_unit(monkeypatch, tmp_path):
    manifest = tmp_path / "manifest.json"
    _write_shared_genome_manifest(manifest)
    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame(
        {
            "Sequence": ["PEPA", "PEPB", "PEPZERO"],
            "s1": [10, 0, 0],
            "s2": [20, 5, 0],
        }
    ).to_csv(peptide_table, sep="\t", index=False)
    taxafunc_db = tmp_path / "taxafunc.db"
    taxafunc_db.write_text("", encoding="utf-8")
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()
    calls = []
    mapper_inputs = []

    def fake_query(**kwargs):
        calls.append(kwargs)
        return {
            "PEPA": {
                "g1": {"g1_p1"},
                "g2": {"g2_p2"},
                "g3": {"g3_p3"},
            },
            "PEPB": {"g3": {"g3_p4"}},
        }

    class FakeMapper:
        def __init__(self, **kwargs):
            assert kwargs["continue_base_on_annotaied_peptide_table"] is True
            self.peptide_table = kwargs["peptide_df"].copy()
            self.final_peptide_table = self.peptide_table.copy()
            self.peptides_after_mapping = len(self.peptide_table)
            self.selected_genomes_num = len(kwargs["genome_list"])
            self.kwargs = kwargs
            mapper_inputs.append(self.peptide_table.copy())

        def all_in_one(self, **kwargs):
            sample_cols = [c for c in self.peptide_table if c.startswith("Intensity_")]
            unit_genomes = self.kwargs["genome_list"]
            unit_label = "+".join(unit_genomes)
            return pd.DataFrame(
                {
                    "Sequence": self.peptide_table["Sequence"],
                    "Proteins": self.peptide_table["Proteins"],
                    "LCA_level": ["genome"] * len(self.peptide_table),
                    "Taxon": [f"d__Bacteria|m__{unit_label}"] * len(self.peptide_table),
                    "Taxon_prop": [1.0] * len(self.peptide_table),
                    "Mock_func": [f"func_{unit_label}"] * len(self.peptide_table),
                    **{col: self.peptide_table[col].tolist() for col in sample_cols},
                }
            )

    monkeypatch.setattr(
        "metax.peptide_annotator.unit_specific_otf.query_peptide_proteins_from_digested_genome_folders_nested",
        fake_query,
    )
    monkeypatch.setattr("metax.peptide_annotator.unit_specific_otf.peptideProteinsMapper", FakeMapper)

    result = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "out.tsv"),
        digested_genome_folders=str(digested_dir),
    ).run(return_dataframe=True)

    assert len(calls) == 1
    assert calls[0]["peptide_list"] == ["PEPA", "PEPB"]
    assert mapper_inputs[0]["Proteins"].tolist() == ["g1_p1;g2_p2"]
    assert mapper_inputs[1]["Proteins"].tolist() == ["g2_p2;g3_p3", "g3_p4"]
    assert "PEPZERO" not in result["Sequence"].tolist()
    assert result.loc[result["analysis_unit_id"] == "u1", "Proteins"].tolist() == ["g1_p1;g2_p2"]
    assert result.loc[result["analysis_unit_id"] == "u2", "Proteins"].tolist() == [
        "g2_p2;g3_p3",
        "g3_p4",
    ]
    pepa = result.loc[result["Sequence"] == "PEPA"].set_index("analysis_unit_id")
    assert pepa.loc["u1", "Taxon"] != pepa.loc["u2", "Taxon"]
    assert pepa.loc["u1", "Mock_func"] != pepa.loc["u2", "Mock_func"]
    artifacts_dir = tmp_path / "out_artifacts"
    assert not list(artifacts_dir.rglob("*.db"))
    assert not list(artifacts_dir.rglob("*.parquet"))
    assert not list(artifacts_dir.rglob("*global*map*"))


@pytest.mark.parametrize("on_empty_unit", ["warn-skip", "error"])
def test_unit_specific_folder_mode_handles_unit_without_mapped_proteins(
    monkeypatch,
    tmp_path,
    on_empty_unit,
):
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest)
    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame(
        {
            "Sequence": ["PEPA"],
            "s1": [10],
            "s2": [10],
        }
    ).to_csv(peptide_table, sep="\t", index=False)
    taxafunc_db = tmp_path / "taxafunc.db"
    taxafunc_db.write_text("", encoding="utf-8")
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()

    monkeypatch.setattr(
        "metax.peptide_annotator.unit_specific_otf.query_peptide_proteins_from_digested_genome_folders_nested",
        lambda **kwargs: {"PEPA": {"g1": {"g1_p1"}}},
    )

    class FakeMapper:
        def __init__(self, **kwargs):
            self.peptide_table = kwargs["peptide_df"].copy()
            self.final_peptide_table = self.peptide_table.copy()
            self.peptides_after_mapping = len(self.peptide_table)
            self.selected_genomes_num = len(kwargs["genome_list"])

        def all_in_one(self, **kwargs):
            return pd.DataFrame(
                {
                    "Sequence": self.peptide_table["Sequence"],
                    "Proteins": self.peptide_table["Proteins"],
                    "LCA_level": ["genome"],
                    "Taxon": ["d__Bacteria"],
                    "Taxon_prop": [1.0],
                    "Intensity_s1": self.peptide_table.get("Intensity_s1", 0),
                }
            )

    monkeypatch.setattr("metax.peptide_annotator.unit_specific_otf.peptideProteinsMapper", FakeMapper)
    annotator = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "out.tsv"),
        digested_genome_folders=str(digested_dir),
        on_empty_unit=on_empty_unit,
    )

    if on_empty_unit == "error":
        with pytest.raises(ValueError, match="u2: unit has no peptides mapped"):
            annotator.run()
    else:
        with pytest.warns(UserWarning, match="u2: unit has no peptides mapped"):
            result = annotator.run(return_dataframe=True)
        assert result["analysis_unit_id"].tolist() == ["u1"]


def test_unit_specific_otf_raises_on_invalid_output_prefix(tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    peptide_table.write_text("Sequence\ts1\nPEPA\t10\n", encoding="utf-8")
    manifest = tmp_path / "unit_specific_manifest.json"
    _write_manifest(manifest)
    taxafunc_db = tmp_path / "taxafunc.db"
    _write_taxafunc_db(taxafunc_db)
    digested_dir = tmp_path / "digested"
    digested_dir.mkdir()

    with pytest.raises(ValueError, match="Unit-specific OTF output_sample_col_prefix must be 'Intensity_'"):
        UnitSpecificOTFAnnotator(
            peptide_table_path=str(peptide_table),
            unit_specific_manifest_path=str(manifest),
            taxafunc_anno_db_path=str(taxafunc_db),
            output_path=str(tmp_path / "OTF.tsv"),
            digested_genome_folders=str(digested_dir),
            output_sample_col_prefix="LFQ intensity ",
        )


def test_unit_specific_otf_per_unit_output_filename_collisions(monkeypatch, tmp_path, capsys):
    peptide_table = tmp_path / "peptides.tsv"
    peptide_table.write_text("Sequence\ts1\ts2\nPEPA\t10\t20\n", encoding="utf-8")
    
    # Create two units whose IDs will collide when sanitized to a safe filename
    manifest_data = {
        "schema_version": "metaumbra.unit_specific_manifest.v1",
        "generated_by": {"tool": "test"},
        "default_genome_threshold": "q0.05",
        "files": {},
        "units": {
            "a/b": {
                "sample_columns": ["s1"],
                "n_samples": 1,
                "genome_ids_q005": ["g1"],
                "genome_ids_q001": ["g1"],
            },
            "a?b": {
                "sample_columns": ["s2"],
                "n_samples": 1,
                "genome_ids_q005": ["g2"],
                "genome_ids_q001": ["g2"],
            }
        }
    }
    manifest = tmp_path / "unit_specific_manifest.json"
    manifest.write_text(json.dumps(manifest_data), encoding="utf-8")

    taxafunc_db = tmp_path / "taxafunc.db"
    _write_taxafunc_db(taxafunc_db)

    peptide_db = tmp_path / "peptide.db"
    peptide_db.write_text("", encoding="utf-8")

    class FakeMapper:
        def __init__(self, *args, **kwargs):
            self.peptide_table = kwargs["peptide_df"]
            self.final_peptide_table = self.peptide_table.copy()
            self.peptides_before_mapping = len(self.peptide_table)
            self.peptides_after_mapping = len(self.peptide_table)
            self.selected_genomes_num = len(kwargs["genome_list"])

        def all_in_one(self, **kwargs):
            # Return intensity columns exactly as they exist in the chunk
            df_dict = {
                "Sequence": self.peptide_table["Sequence"],
                "Proteins": ["prot1"] * len(self.peptide_table),
                "LCA_level": ["genome"] * len(self.peptide_table),
                "Taxon": ["d__Bacteria"] * len(self.peptide_table),
                "Taxon_prop": [1.0] * len(self.peptide_table),
            }
            # Add whichever Intensity_ columns are present
            for col in self.peptide_table.columns:
                if col.startswith("Intensity_"):
                    df_dict[col] = self.peptide_table[col]

            return pd.DataFrame(df_dict)

    monkeypatch.setattr("metax.peptide_annotator.unit_specific_otf.peptideProteinsMapper", FakeMapper)

    annotator = UnitSpecificOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_specific_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "OTF.tsv"),
        db_path=str(peptide_db),
        save_per_unit_outputs=True,
    )
    result = annotator.run()

    # Check that they both succeeded and have different output paths
    per_unit_dir = tmp_path / "OTF_artifacts" / "per_unit"
    saved_files = list(per_unit_dir.glob("*_OTF.tsv"))
    assert len(saved_files) == 2
    assert saved_files[0].name != saved_files[1].name

    # Assert unit_output_records / summary preserve the original analysis_unit_id
    summary_text = (tmp_path / "OTF_artifacts" / "unit_annotation_summary.tsv").read_text(encoding="utf-8")
    assert "a/b" in summary_text
    assert "a?b" in summary_text

    # Assert merged output contains rows from both units, not duplicated rows from the overwritten file
    merged_text = (tmp_path / "OTF.tsv").read_text(encoding="utf-8")
    assert "Intensity_s1" in merged_text
    assert "Intensity_s2" in merged_text
    
    # Ensure they don't have duplicated contents, since s1 and s2 are different columns
    df = pd.read_csv(tmp_path / "OTF.tsv", sep="\t", skipinitialspace=True)
    assert len(df) == 2
    assert set(df["analysis_unit_id"].tolist()) == {"a/b", "a?b"}
