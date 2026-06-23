import json
import sqlite3

import pandas as pd
import pytest

from metax.cli.annotate import build_parser
from metax.peptide_annotator.unit_aware_otf import UnitAwareOTFAnnotator


def _write_manifest(path):
    path.write_text(
        json.dumps(
            {
                "schema_version": "metaumbra.unit_aware_manifest.v1",
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


def test_unit_aware_otf_builds_units_and_artifacts(monkeypatch, tmp_path):
    calls = []

    class FakeMapper:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.peptide_df = kwargs["peptide_df"]
            self.final_peptide_table = self.peptide_df.copy()
            self.peptides_after_mapping = len(self.peptide_df)
            self.selected_genomes_num = len(kwargs["genome_list"])
            calls.append(kwargs)

        def all_in_one(self, **kwargs):
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

    monkeypatch.setattr("metax.peptide_annotator.unit_aware_otf.peptideProteinsMapper", FakeMapper)

    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame(
        {
            "Sequence": ["PEPA", "PEPB"],
            "s1": [10, 0],
            "s2": [20, 5],
        }
    ).to_csv(peptide_table, sep="\t", index=False)
    manifest = tmp_path / "unit_aware_manifest.json"
    _write_manifest(manifest)
    taxafunc_db = tmp_path / "taxafunc.db"
    taxafunc_db.write_text("", encoding="utf-8")
    peptide_db = tmp_path / "peptide.db"
    peptide_db.write_text("", encoding="utf-8")
    output = tmp_path / "OTF_unit_aware.tsv"

    result = UnitAwareOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_aware_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(output),
        db_path=str(peptide_db),
        peptide_col="Sequence",
        duplicate_peptide_handling_mode="max",
    ).run()

    assert [call["genome_list"] for call in calls] == [["g1"], ["g2"]]
    assert calls[0]["selected_genomes_set"] == {"g1"}
    assert calls[1]["selected_genomes_set"] == {"g2"}
    assert [call["duplicate_peptide_handling_mode"] for call in calls] == ["max", "max"]
    assert "UnitAwareSequence" not in result.columns
    assert result[["analysis_unit_id", "Sequence"]].drop_duplicates().values.tolist() == [
        ["u1", "PEPA"],
        ["u2", "PEPA"],
        ["u2", "PEPB"],
    ]
    assert result.loc[result["analysis_unit_id"] == "u1", "Intensity_s2"].eq(0).all()
    assert result.loc[result["analysis_unit_id"] == "u2", "Intensity_s1"].eq(0).all()
    assert output.is_file()
    assert (tmp_path / "OTF_unit_aware_artifacts" / "unit_sample_column_mapping.tsv").is_file()
    assert (tmp_path / "OTF_unit_aware_artifacts" / "unit_annotation_summary.tsv").is_file()


def test_unit_aware_otf_defaults_and_path_validation(tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame({"Sequence": ["PEPA"], "Intensity_s1": [10]}).to_csv(peptide_table, sep="\t", index=False)
    manifest = tmp_path / "unit_aware_manifest.json"
    _write_manifest(manifest)
    taxafunc_db = tmp_path / "taxafunc.db"
    taxafunc_db.write_text("", encoding="utf-8")
    peptide_db = tmp_path / "peptide.db"
    peptide_db.write_text("", encoding="utf-8")

    annotator = UnitAwareOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_aware_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "out.tsv"),
        db_path=str(peptide_db),
    )
    assert annotator.distinct_genome_threshold == 0

    parser = build_parser()
    args = parser.parse_args(["--unit-aware"])
    assert args.distinct_genome_threshold == 0

    with pytest.raises(ValueError, match="duplicate_peptide_handling_mode"):
        UnitAwareOTFAnnotator(
            peptide_table_path=str(peptide_table),
            unit_aware_manifest_path=str(manifest),
            taxafunc_anno_db_path=str(taxafunc_db),
            output_path=str(tmp_path / "out.tsv"),
            db_path=str(peptide_db),
            duplicate_peptide_handling_mode="bad-mode",
        )

    with pytest.raises(FileNotFoundError, match="db_path"):
        UnitAwareOTFAnnotator(
            peptide_table_path=str(peptide_table),
            unit_aware_manifest_path=str(manifest),
            taxafunc_anno_db_path=str(taxafunc_db),
            output_path=str(tmp_path / "out.tsv"),
            db_path=str(tmp_path / "missing.db"),
        )

    not_a_dir = tmp_path / "not_a_dir.tsv"
    not_a_dir.write_text("", encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="digested_genome_folders"):
        UnitAwareOTFAnnotator(
            peptide_table_path=str(peptide_table),
            unit_aware_manifest_path=str(manifest),
            taxafunc_anno_db_path=str(taxafunc_db),
            output_path=str(tmp_path / "out.tsv"),
            digested_genome_folders=[str(not_a_dir)],
        )


def test_unit_aware_otf_real_sqlite_integration(tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame(
        {
            "Sequence": ["PEPA", "PEPB"],
            "Intensity_s1": [10, 0],
            "Intensity_s2": [20, 5],
        }
    ).to_csv(peptide_table, sep="\t", index=False)
    manifest = tmp_path / "unit_aware_manifest.json"
    _write_manifest(manifest)
    peptide_db = tmp_path / "peptide.db"
    _write_peptide_protein_db(peptide_db)
    taxafunc_db = tmp_path / "taxafunc.db"
    _write_taxafunc_db(taxafunc_db)
    output = tmp_path / "OTF_unit_aware.tsv"

    result = UnitAwareOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_aware_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(output),
        db_path=str(peptide_db),
        peptide_col="Sequence",
    ).run()

    assert "UnitAwareSequence" not in result.columns
    assert result["Sequence"].tolist() == ["PEPA", "PEPA", "PEPB"]
    assert result.loc[result["analysis_unit_id"] == "u1", "Proteins"].tolist() == ["g1_p1"]
    assert result.loc[result["analysis_unit_id"] == "u2", "Proteins"].tolist() == ["g2_p2", "g2_p3"]
    assert output.is_file()


def test_unit_aware_otf_can_include_unit_aware_sequence_for_debug(tmp_path):
    peptide_table = tmp_path / "peptides.tsv"
    pd.DataFrame({"Sequence": ["PEPA"], "Intensity_s1": [10], "Intensity_s2": [0]}).to_csv(
        peptide_table,
        sep="\t",
        index=False,
    )
    manifest = tmp_path / "unit_aware_manifest.json"
    _write_manifest(manifest)
    peptide_db = tmp_path / "peptide.db"
    _write_peptide_protein_db(peptide_db)
    taxafunc_db = tmp_path / "taxafunc.db"
    _write_taxafunc_db(taxafunc_db)

    result = UnitAwareOTFAnnotator(
        peptide_table_path=str(peptide_table),
        unit_aware_manifest_path=str(manifest),
        taxafunc_anno_db_path=str(taxafunc_db),
        output_path=str(tmp_path / "OTF_unit_aware.tsv"),
        db_path=str(peptide_db),
        include_unit_aware_sequence=True,
    ).run()

    assert "UnitAwareSequence" in result.columns
    assert result["UnitAwareSequence"].tolist() == ["u1||PEPA"]
