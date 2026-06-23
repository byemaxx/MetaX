import json
import sqlite3

import pandas as pd

from metax.peptide_annotator.pep_table_to_otf import peptideProteinsMapper


def _make_peptide_db(path):
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE peptide_proteins (peptide TEXT PRIMARY KEY, proteins TEXT)")
        conn.execute(
            "INSERT INTO peptide_proteins VALUES (?, ?)",
            ("PEPA", json.dumps(["g1_p1", "g2_p2"])),
        )
        conn.execute(
            "INSERT INTO peptide_proteins VALUES (?, ?)",
            ("PEPB", json.dumps(["g2_p3"])),
        )
        conn.commit()


def test_mapper_accepts_dataframe_and_selected_genomes(tmp_path):
    db_path = tmp_path / "peptide.db"
    _make_peptide_db(db_path)
    df = pd.DataFrame(
        {
            "Sequence": ["PEPA", "PEPB"],
            "Intensity_s1": [10, 20],
        }
    )

    mapper = peptideProteinsMapper(
        peptide_table_path=str(tmp_path / "does_not_exist.tsv"),
        peptide_df=df,
        db_path=str(db_path),
        output_path=str(tmp_path / "out.tsv"),
        peptide_col="Sequence",
        intensity_col_prefix="Intensity_",
        selected_genomes_set={"g1"},
        genome_list=["g1"],
    )
    annotated = mapper.annotate_peptides()

    assert annotated["Sequence"].tolist() == ["PEPA"]
    assert annotated["Proteins"].tolist() == ["g1_p1"]


def test_all_in_one_returns_otf_dataframe(monkeypatch, tmp_path):
    import metax.peptide_annotator.peptable_annotator as peptable_annotator

    class FakePeptideAnnotator:
        def __init__(self, **kwargs):
            self.peptide_df = kwargs["peptide_df"]

        def run_annotate(self):
            out = self.peptide_df.copy()
            out["LCA_level"] = "genome"
            out["Taxon"] = "d__Bacteria|m__g1"
            out["Taxon_prop"] = 1.0
            out["None_func"] = "none_func"
            out["None_func_prop"] = 1.0
            return out

    monkeypatch.setattr(peptable_annotator, "PeptideAnnotator", FakePeptideAnnotator)
    df = pd.DataFrame({"Sequence": ["PEPA"], "Intensity_s1": [10]})
    mapper = peptideProteinsMapper(
        peptide_table_path=str(tmp_path / "missing.tsv"),
        peptide_df=df,
        db_path=str(tmp_path / "unused.db"),
        output_path=str(tmp_path / "out.tsv"),
        peptide_col="Sequence",
        intensity_col_prefix="Intensity_",
        genome_list=["g1"],
    )

    mapper.process_peptides_to_proteins = lambda genome_list=None: setattr(
        mapper,
        "final_peptide_table",
        pd.DataFrame({"Sequence": ["PEPA"], "Proteins": ["g1_p1"], "Intensity_s1": [10]}),
    )
    result = mapper.all_in_one(taxafunc_anno_db_path=str(tmp_path / "taxafunc.db"))

    assert isinstance(result, pd.DataFrame)
    assert result.loc[0, "Sequence"] == "PEPA"


def test_mapper_restores_automatic_genome_ranking_without_genome_list(tmp_path):
    df = pd.DataFrame(
        {
            "Sequence": ["PEPA", "PEPB"],
            "Proteins": ["g1_p1;g2_p1", "g2_p2"],
            "Genomes": ["g1;g2", "g2"],
            "Intensity_s1": [10, 20],
        }
    )

    mapper = peptideProteinsMapper(
        peptide_table_path=str(tmp_path / "missing.tsv"),
        peptide_df=df,
        output_path=str(tmp_path / "out.tsv"),
        peptide_col="Sequence",
        intensity_col_prefix="Intensity_",
        continue_base_on_annotaied_peptide_table=True,
        protein_peptide_coverage_cutoff=1.0,
    )
    result = mapper.run_base_on_annotaied_peptide_table()

    assert mapper.selected_genomes_num > 0
    assert mapper.genome_ranked_table is not None
    assert not result.empty
