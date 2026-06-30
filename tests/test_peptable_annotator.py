import sqlite3
from collections import Counter
from concurrent.futures import ThreadPoolExecutor as RealThreadPoolExecutor

import pandas as pd
import pytest

from metax.peptide_annotator import peptable_annotator as annotator_module
from metax.peptide_annotator.peptable_annotator import PeptideAnnotator
from metax.peptide_annotator.proteins_to_taxafunc import Pep2TaxaFunc


def _write_taxafunc_db(path):
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE id2taxa (ID TEXT PRIMARY KEY, Taxa TEXT)")
        conn.execute(
            """
            CREATE TABLE id2annotation (
                ID TEXT PRIMARY KEY,
                seed_ortholog TEXT,
                evalue REAL,
                score REAL,
                KEGG_ko TEXT
            )
            """
        )
        conn.executemany(
            "INSERT INTO id2taxa VALUES (?, ?)",
            [
                ("g1", "d__Bacteria;p__P1;c__C1;o__O1;f__F1;g__G1;s__S1"),
                ("g2", "d__Bacteria;p__P2;c__C2;o__O2;f__F2;g__G2;s__S2"),
            ],
        )
        conn.executemany(
            "INSERT INTO id2annotation VALUES (?, ?, ?, ?, ?)",
            [
                ("g1_p1", "seed1", 1e-20, 100.0, "K00001"),
                ("g2_p2", "seed2", 1e-10, 90.0, "K00002"),
            ],
        )


def test_run_2_result_annotates_unique_protein_strings_once(
    monkeypatch,
    tmp_path,
    capsys,
):
    db_path = tmp_path / "taxafunc.db"
    _write_taxafunc_db(db_path)
    annotator = PeptideAnnotator(
        db_path=str(db_path),
        output_path="unused.tsv",
        peptide_df=pd.DataFrame(),
    )
    calls = []
    original_run = Pep2TaxaFunc.proteins_to_taxa_func_from_cache

    def tracked_run(self, proteins):
        calls.append(tuple(proteins))
        return original_run(self, proteins)

    monkeypatch.setattr(
        Pep2TaxaFunc,
        "proteins_to_taxa_func_from_cache",
        tracked_run,
    )
    monkeypatch.setattr(annotator, "add_additional_columns", lambda df: df)
    peptide_df = pd.DataFrame(
        {
            "Sequence": ["PEP3", "PEP1", "PEP2", "PEP4"],
            "Proteins": ["g1_p1", "g1_p1", "g2_p2", "g1_p1"],
            "Intensity_s1": [3, 1, 2, 4],
        },
        index=[30, 10, 20, 40],
    )

    result = annotator.run_2_result(peptide_df)

    assert Counter(calls) == Counter({("g1_p1",): 1, ("g2_p2",): 1})
    assert result.index.tolist() == peptide_df.index.tolist()
    assert result["Sequence"].tolist() == peptide_df["Sequence"].tolist()
    assert result.loc[30, "Taxon"] == result.loc[10, "Taxon"]
    assert result.loc[30, "Taxon"] == result.loc[40, "Taxon"]
    assert result.loc[20, "Taxon"] != result.loc[30, "Taxon"]
    assert result["Intensity_s1"].tolist() == [3, 1, 2, 4]
    output = capsys.readouterr().out
    assert "  - rows: 4" in output
    assert "  - unique protein groups: 2" in output
    assert "  - unique proteins: 2" in output
    assert "  - unique genomes: 2" in output
    assert "  - batch prefetch:" in output
    assert "  - in-memory annotation:" in output


def test_run_2_result_reuses_shared_annotation_result_cache(
    monkeypatch,
    tmp_path,
):
    db_path = tmp_path / "taxafunc.db"
    _write_taxafunc_db(db_path)
    shared_cache = {}
    calls = []
    original_run = Pep2TaxaFunc.proteins_to_taxa_func_from_cache

    def tracked_run(self, proteins):
        calls.append(tuple(proteins))
        return original_run(self, proteins)

    monkeypatch.setattr(
        Pep2TaxaFunc,
        "proteins_to_taxa_func_from_cache",
        tracked_run,
    )

    def make_annotator():
        annotator = PeptideAnnotator(
            db_path=str(db_path),
            output_path="unused.tsv",
            peptide_df=pd.DataFrame(),
            annotation_result_cache=shared_cache,
        )
        monkeypatch.setattr(
            annotator,
            "add_additional_columns",
            lambda df: df,
        )
        return annotator

    first = make_annotator().run_2_result(
        pd.DataFrame(
            {
                "Sequence": ["PEP1", "PEP2"],
                "Proteins": ["g1_p1", "g2_p2"],
                "Intensity_s1": [1, 2],
            }
        )
    )
    second = make_annotator().run_2_result(
        pd.DataFrame(
            {
                "Sequence": ["PEP3"],
                "Proteins": ["g1_p1"],
                "Intensity_s2": [3],
            }
        )
    )

    assert Counter(calls) == Counter({("g1_p1",): 1, ("g2_p2",): 1})
    assert len(shared_cache) == 2
    assert second.loc[0, "Taxon"] == first.loc[0, "Taxon"]


def test_run_2_result_cache_path_keeps_nan_protein_fallback(
    monkeypatch,
    tmp_path,
):
    db_path = tmp_path / "taxafunc.db"
    _write_taxafunc_db(db_path)
    annotator = PeptideAnnotator(
        db_path=str(db_path),
        output_path="unused.tsv",
        peptide_df=pd.DataFrame(),
        annotation_result_cache={},
    )
    monkeypatch.setattr(annotator, "add_additional_columns", lambda df: df)

    result = annotator.run_2_result(
        pd.DataFrame(
            {
                "Sequence": ["PEP1", "PEP2"],
                "Proteins": ["g1_p1", pd.NA],
                "Intensity_s1": [1, 2],
            }
        )
    )

    assert result["Sequence"].tolist() == ["PEP1", "PEP2"]
    assert result["Proteins"].isna().tolist() == [False, True]
    assert result["None_func"].tolist() == ["none_func", "none_func"]


def test_prefetch_output_matches_direct_annotation(tmp_path):
    db_path = tmp_path / "taxafunc.db"
    _write_taxafunc_db(db_path)
    groups = [
        ["g1_p1", "g2_p2"],
        ["g1_p1", "missing_p"],
        ["g2_p2"],
    ]

    with sqlite3.connect(db_path) as direct_conn:
        direct = Pep2TaxaFunc(conn=direct_conn, genome_mode=True)
        direct_results = [
            direct.proteins_to_taxa_func(group)
            for group in groups
        ]

    with sqlite3.connect(db_path) as prefetched_conn:
        prefetched = Pep2TaxaFunc(conn=prefetched_conn, genome_mode=True)
        counts = prefetched.prefetch_for_protein_groups(groups)
        prefetched_results = [
            prefetched.proteins_to_taxa_func(group)
            for group in groups
        ]

    assert counts == (3, 3)
    assert prefetched_results == direct_results


def test_genome_mode_controls_taxon_and_lca_after_prefetch(tmp_path):
    db_path = tmp_path / "taxafunc.db"
    _write_taxafunc_db(db_path)
    group = ["g1_p1"]

    with sqlite3.connect(db_path) as conn:
        genome_annotator = Pep2TaxaFunc(conn=conn, genome_mode=True)
        assert genome_annotator.prefetch_for_protein_groups([group]) == (1, 1)
        genome_result = genome_annotator.proteins_to_taxa_func(group)

    with sqlite3.connect(db_path) as conn:
        species_annotator = Pep2TaxaFunc(conn=conn, genome_mode=False)
        assert species_annotator.prefetch_for_protein_groups([group]) == (1, 1)
        species_result = species_annotator.proteins_to_taxa_func(group)

    assert "m__g1" in genome_result["Taxon"]
    assert genome_result["LCA_level"] == "genome"
    assert "m__" not in species_result["Taxon"]
    assert species_result["LCA_level"] == "species"


def test_db_path_initialization_matches_existing_connection(tmp_path):
    db_path = tmp_path / "taxafunc.db"
    _write_taxafunc_db(db_path)
    groups = [["g1_p1", "g2_p2"], ["g1_p1"]]

    with sqlite3.connect(db_path) as conn:
        existing = Pep2TaxaFunc(conn=conn)
        existing.prefetch_for_protein_groups(groups)
        expected = [
            existing.proteins_to_taxa_func_from_cache(group)
            for group in groups
        ]

    from_path = Pep2TaxaFunc(db_path=str(db_path))
    try:
        from_path.prefetch_for_protein_groups(groups)
        actual = [
            from_path.proteins_to_taxa_func_from_cache(group)
            for group in groups
        ]
        selected = from_path.conn.execute(
            'SELECT "ID" FROM id2taxa ORDER BY "ID"'
        ).fetchall()
        query_only = from_path.conn.execute(
            "PRAGMA query_only"
        ).fetchone()[0]
    finally:
        from_path.conn.close()

    assert actual == expected
    assert selected == [("g1",), ("g2",)]
    assert query_only == 1


def test_optional_pragma_failure_does_not_hide_query_failures(
    tmp_path,
):
    db_path = tmp_path / "taxafunc.db"
    _write_taxafunc_db(db_path)

    class PragmaFailingConnection:
        def __init__(self, conn):
            self._conn = conn

        def execute(self, sql, parameters=()):
            if sql.startswith("PRAGMA"):
                raise sqlite3.OperationalError("unsupported pragma")
            return self._conn.execute(sql, parameters)

    conn = sqlite3.connect(db_path)
    wrapped = PragmaFailingConnection(conn)
    Pep2TaxaFunc._configure_readonly_connection(wrapped)
    assert wrapped.execute("SELECT COUNT(*) FROM id2taxa").fetchone() == (2,)
    with pytest.raises(sqlite3.OperationalError):
        wrapped.execute("SELECT missing_column FROM id2taxa")
    conn.close()


def test_prefetch_preserves_empty_dash_and_not_found_values(tmp_path):
    db_path = tmp_path / "taxafunc_values.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE id2taxa (ID TEXT PRIMARY KEY, Taxa TEXT)")
        conn.execute(
            """
            CREATE TABLE id2annotation (
                ID TEXT PRIMARY KEY,
                seed_ortholog TEXT,
                evalue REAL,
                score REAL,
                "annotation value" TEXT
            )
            """
        )
        conn.executemany(
            'INSERT INTO id2annotation VALUES (?, ?, ?, ?, ?)',
            [
                ("g1|p1", "seed1", 1.0, 1.0, ""),
                ("g1|p2", "seed2", 1.0, 1.0, "-"),
            ],
        )
        conn.execute(
            "INSERT INTO id2taxa VALUES (?, ?)",
            ("g1", "d__Bacteria;p__;c__;o__;f__;g__;s__"),
        )

    with sqlite3.connect(db_path) as conn:
        annotator = Pep2TaxaFunc(
            conn=conn,
            protein_genome_separator="|",
        )
        counts = annotator.prefetch_for_protein_groups(
            [["g1|p1", "g1|p2", "g1|missing"]],
        )

    assert counts == (3, 1)
    assert annotator._protein_annotation_cache == {
        "g1|p1": ("-",),
        "g1|p2": ("-",),
        "g1|missing": ("not_found",),
    }
    assert set(annotator._genome_taxon_cache) == {"g1"}
    assert annotator._annotation_select_sql == (
        'SELECT "annotation value" from id2annotation where "ID" = ?'
    )


def test_prefetch_batches_sql_and_cached_annotation_uses_no_lookup_selects(
    tmp_path,
):
    db_path = tmp_path / "taxafunc.db"
    _write_taxafunc_db(db_path)
    sql_trace = []
    conn = sqlite3.connect(db_path)
    conn.set_trace_callback(sql_trace.append)
    annotator = Pep2TaxaFunc(conn=conn, genome_mode=True)

    try:
        groups = [
            ["g1_p1", "g2_p2"],
            ["g2_p2", "missing_p"],
        ]
        annotator.prefetch_protein_annotations(
            ["g1_p1", "g2_p2", "missing_p"],
            chunk_size=2,
        )
        annotator.prefetch_genome_taxa(
            ["g1", "g2", "missing"],
            chunk_size=2,
        )
        prefetch_trace = list(sql_trace)
        sql_trace.clear()
        first = annotator.proteins_to_taxa_func(groups[0])
        overlapping = annotator.proteins_to_taxa_func(groups[1])
        repeated = annotator.proteins_to_taxa_func(groups[0])
        cached_trace = list(sql_trace)
    finally:
        conn.close()

    assert repeated == first
    assert overlapping["KEGG_ko"] == "K00002"
    assert annotator._annotation_col_names == ("KEGG_ko",)
    assert annotator._annotation_select_sql == (
        'SELECT "KEGG_ko" from id2annotation where "ID" = ?'
    )
    assert annotator._protein_annotation_cache == {
        "g1_p1": ("K00001",),
        "g2_p2": ("K00002",),
        "missing_p": ("not_found",),
    }
    assert set(annotator._genome_taxon_cache) == {"g1", "g2", "missing"}
    assert annotator._genome_taxon_cache["missing"] == "not_found"
    assert sum(
        sql.lower() == "select * from id2annotation limit 1"
        for sql in prefetch_trace
    ) == 1
    assert sum(
        "from id2annotation" in sql.lower() and " in (" in sql.lower()
        for sql in prefetch_trace
    ) == 2
    assert sum(
        "from id2taxa" in sql.lower() and " in (" in sql.lower()
        for sql in prefetch_trace
    ) == 2
    assert not any(
        "from id2annotation" in sql.lower()
        or "from id2taxa" in sql.lower()
        or "from sqlite_master" in sql.lower()
        for sql in cached_trace
    )


def test_cache_only_annotation_matches_database_path_and_uses_no_sql(
    tmp_path,
):
    db_path = tmp_path / "taxafunc.db"
    _write_taxafunc_db(db_path)
    groups = [
        ["g1_p1", "g2_p2"],
        ["g2_p2", "missing_p"],
    ]
    sql_trace = []
    conn = sqlite3.connect(db_path)
    conn.set_trace_callback(sql_trace.append)
    annotator = Pep2TaxaFunc(conn=conn)

    try:
        annotator.prefetch_for_protein_groups(groups)
        database_results = [
            annotator.proteins_to_taxa_func(group)
            for group in groups
        ]
        sql_trace.clear()
        cache_results = [
            annotator.proteins_to_taxa_func_from_cache(group)
            for group in groups
            for _ in range(2)
        ]
    finally:
        conn.close()

    assert cache_results == [
        database_results[0],
        database_results[0],
        database_results[1],
        database_results[1],
    ]
    assert not any(
        "from id2annotation" in sql.lower()
        or "from id2taxa" in sql.lower()
        or "from sqlite_master" in sql.lower()
        for sql in sql_trace
    )


def test_cache_only_annotation_requires_complete_prefetch(tmp_path):
    db_path = tmp_path / "taxafunc.db"
    _write_taxafunc_db(db_path)
    with sqlite3.connect(db_path) as conn:
        annotator = Pep2TaxaFunc(conn=conn)
        annotator.prefetch_for_protein_groups([["g1_p1"]])
        with pytest.raises(KeyError, match="Protein ID was not prefetched"):
            annotator.proteins_to_taxa_func_from_cache(["g2_p2"])
        with pytest.raises(KeyError, match="Genome ID was not prefetched"):
            annotator.query_taxon_from_cache(["g2_p2"])


def test_run_2_result_parallel_cache_path_matches_single_thread(
    monkeypatch,
    tmp_path,
):
    db_path = tmp_path / "taxafunc.db"
    _write_taxafunc_db(db_path)
    peptide_df = pd.DataFrame(
        {
            "Sequence": ["PEP3", "PEP1", "PEP2", "PEP4"],
            "Proteins": ["g1_p1", "g1_p1", "g2_p2", "g1_p1;g2_p2"],
            "Intensity_s1": [3, 1, 2, 4],
        },
        index=[30, 10, 20, 40],
    )

    def make_annotator():
        annotator = PeptideAnnotator(
            db_path=str(db_path),
            output_path="unused.tsv",
            peptide_df=pd.DataFrame(),
        )
        monkeypatch.setattr(
            annotator,
            "add_additional_columns",
            lambda df: df,
        )
        return annotator

    single = make_annotator()
    monkeypatch.setattr(single, "parallel_cache_annotation_min_groups", 1000)
    expected = single.run_2_result(peptide_df)

    executor_calls = []

    class RecordingThreadPoolExecutor(RealThreadPoolExecutor):
        def __init__(self, *args, **kwargs):
            executor_calls.append(kwargs["max_workers"])
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(
        annotator_module,
        "ThreadPoolExecutor",
        RecordingThreadPoolExecutor,
    )
    monkeypatch.setattr(annotator_module.os, "cpu_count", lambda: 4)
    parallel = make_annotator()
    monkeypatch.setattr(parallel, "parallel_cache_annotation_min_groups", 1)
    monkeypatch.setattr(parallel, "parallel_cache_annotation_max_workers", 2)
    actual = parallel.run_2_result(peptide_df)

    assert executor_calls == [2]
    pd.testing.assert_frame_equal(actual, expected)
    assert actual.index.tolist() == peptide_df.index.tolist()
    assert actual.loc[30, "Taxon"] == actual.loc[10, "Taxon"]
    assert actual["Intensity_s1"].tolist() == [3, 1, 2, 4]


def test_run_annotate_preserves_otf_output_contract_and_row_order(
    monkeypatch,
    tmp_path,
):
    db_path = tmp_path / "taxafunc.db"
    _write_taxafunc_db(db_path)
    monkeypatch.setattr(
        PeptideAnnotator,
        "add_additional_columns",
        lambda self, df: df,
    )
    peptide_df = pd.DataFrame(
        {
            "Sequence": ["PEP_B", "PEP_A", "PEP_C"],
            "Proteins": ["g1_p1;g2_p2", "g1_p1;g2_p2", "g1_p1"],
            "Intensity_s1": [20, 10, 30],
            "Intensity_s2": [2, 1, 3],
        }
    )
    annotator = PeptideAnnotator(
        db_path=str(db_path),
        output_path=str(tmp_path / "unused.tsv"),
        peptide_df=peptide_df,
        duplicate_peptide_handling_mode="keep",
        exclude_protein_startwith=None,
    )

    result = annotator.run_annotate(save_output=False)

    assert result["Sequence"].tolist() == peptide_df["Sequence"].tolist()
    assert result["Proteins"].tolist() == peptide_df["Proteins"].tolist()
    assert result["Intensity_s1"].tolist() == [20, 10, 30]
    assert result["Intensity_s2"].tolist() == [2, 1, 3]
    assert result.columns.tolist() == [
        "Sequence",
        "Proteins",
        "LCA_level",
        "Taxon",
        "Taxon_prop",
        "KEGG_ko",
        "KEGG_ko_prop",
        "protein_id",
        "protein_id_prop",
        "None_func",
        "None_func_prop",
        "Intensity_s1",
        "Intensity_s2",
    ]


def test_save_result_serializes_only_zero_sample_intensities_as_empty(tmp_path):
    output_path = tmp_path / "otf.tsv"
    annotator = PeptideAnnotator(
        db_path="unused.db",
        output_path=str(output_path),
        peptide_df=pd.DataFrame(),
    )
    result = pd.DataFrame(
        {
            "Sequence": ["PEPA", "PEPB"],
            "Taxon_prop": [0.0, 1.0],
            "KEGG_ko_prop": [0.0, 1.0],
            "peptide_num": [0, 2],
            "Intensity_s1": [0.0, 12.5],
            "Intensity_s2": [3.0, 0.0],
        }
    )
    expected = result.copy()

    annotator.save_result(result)

    raw_rows = output_path.read_text(encoding="utf-8").splitlines()
    assert raw_rows[1].split("\t") == ["PEPA", "0.0", "0.0", "0", "", "3.0"]
    assert raw_rows[2].split("\t") == ["PEPB", "1.0", "1.0", "2", "12.5", ""]
    pd.testing.assert_frame_equal(result, expected)
    info_text = output_path.with_name("otf_info.txt").read_text(encoding="utf-8")
    assert "sparse_zero_intensity_output: True" in info_text
