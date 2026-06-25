import pytest
import pandas as pd

def test_get_group_of_a_sample(tfa_object):
    """
    Test that get_group_of_a_sample correctly identifies sample groups
    from the loaded metadata.
    """
    # Assuming Example_Meta.tsv has a 'Sugar_type' column for these samples
    sample_list = tfa_object.sample_list
    assert len(sample_list) > 0, "Sample list should not be empty"
    
    # Check the group of the first sample
    first_sample = sample_list[0]
    group = tfa_object.get_group_of_a_sample(first_sample)
    assert group is not None, f"Group for {first_sample} should not be None"
    
    # Ensure all samples have a group mapping
    for sample in sample_list:
        grp = tfa_object.get_group_of_a_sample(sample)
        assert isinstance(grp, str), f"Group for {sample} must be a string"

def test_get_sample_list_in_a_group(tfa_object):
    """
    Test that get_sample_list_in_a_group returns the correct samples 
    belonging to a given group.
    """
    group_list = tfa_object.group_list
    assert group_list is not None and len(group_list) > 0, "Group list must be populated"
    
    first_group = group_list[0]
    samples_in_group = tfa_object.get_sample_list_in_a_group(first_group)
    
    assert isinstance(samples_in_group, list), "Should return a list of samples"
    assert len(samples_in_group) > 0, f"Should have at least one sample in group {first_group}"
    
    # Verify that all returned samples actually belong to that group
    for sample in samples_in_group:
        assert tfa_object.get_group_of_a_sample(sample) == first_group

def test_split_func(tfa_object):
    """
    Test split_func to ensure functions containing commas/semicolons are
    split correctly and aggregated.
    """
    # Create a small dummy dataframe that has split-able functions
    data = {
        'Taxon': ['d__Bacteria', 'd__Bacteria'],
        'KEGG_ko_name': ['FuncA, FuncB', 'FuncC'],
        'peptide_num': [2, 1]
    }
    for sample in tfa_object.sample_list:
        data[sample] = [10.0, 5.0]
        
    df = pd.DataFrame(data).set_index(['Taxon', 'KEGG_ko_name'])
    
    # Run split_func
    split_df = tfa_object.split_func(df, split_func_params={'split_by': ',', 'share_intensity': False}, df_type='taxa_func', func_name='KEGG_ko_name')
    
    # Assertions
    # After split, we should have 3 rows: FuncA, FuncB, FuncC
    assert len(split_df) == 3, f"Expected 3 rows after split, got {len(split_df)}"
    # Check index contains FuncA
    func_names = [idx[1] for idx in split_df.index.tolist()]
    assert 'FuncA' in func_names
    assert 'FuncB' in func_names
    assert 'FuncC' in func_names


@pytest.mark.parametrize("df_type", ["func", "taxa_func"])
@pytest.mark.parametrize(
    ("share_intensity", "expected_a", "expected_b"),
    [
        (False, [24.0, 12.0, 4], [15.0, 15.0, 3]),
        (True, [8.0, 4.0, 4], [7.0, 11.0, 3]),
    ],
)
def test_split_func_vectorized_preserves_legacy_aggregation(
    tfa_object,
    df_type,
    share_intensity,
    expected_a,
    expected_b,
):
    data = {
        "KEGG_ko_name": [" FuncA | FuncB | FuncA ", "FuncB"],
        "peptide_num": [2, 1],
    }
    data.update({sample: [0.0, 0.0] for sample in tfa_object.sample_list})
    data[tfa_object.sample_list[0]] = [12.0, 3.0]
    data[tfa_object.sample_list[1]] = [6.0, 9.0]
    index_cols = ["KEGG_ko_name"]
    if df_type == "taxa_func":
        data["Taxon"] = ["d__Bacteria", "d__Bacteria"]
        index_cols.insert(0, "Taxon")
    df = pd.DataFrame(data).set_index(index_cols)

    result = tfa_object.split_func(
        df,
        split_func_params={
            "split_by": "|",
            "share_intensity": share_intensity,
        },
        df_type=df_type,
        func_name="KEGG_ko_name",
    )

    func_a_index = (
        ("d__Bacteria", "FuncA") if df_type == "taxa_func" else "FuncA"
    )
    func_b_index = (
        ("d__Bacteria", "FuncB") if df_type == "taxa_func" else "FuncB"
    )
    value_cols = [
        tfa_object.sample_list[0],
        tfa_object.sample_list[1],
        "peptide_num",
    ]
    assert result.index.names == index_cols
    assert result.loc[func_a_index, value_cols].tolist() == expected_a
    assert result.loc[func_b_index, value_cols].tolist() == expected_b


def test_set_multi_tables(tfa_object):
    """
    Test that set_multi_tables successfully generates taxa, func, and taxa_func
    dataframes from the base peptide dataframe without crashing.
    """
    # Force generating the tables with sum quantification and no batch/outlier removal for speed
    tfa_object.set_multi_tables(
        level='s',
        quant_method='sum',
        split_func=False,
        data_preprocess_params={'normalize_method': 'None', 'transform_method': 'None', 'batch_meta': 'None', 'processing_order': []},
        outlier_params={'detect_method': 'none', 'handle_method': 'drop+drop'}
    )
    
    assert hasattr(tfa_object, 'taxa_df'), "taxa_df should be created"
    assert hasattr(tfa_object, 'func_df'), "func_df should be created"
    assert hasattr(tfa_object, 'taxa_func_df'), "taxa_func_df should be created"
    
    assert isinstance(tfa_object.taxa_df, pd.DataFrame), "taxa_df should be a DataFrame"
    assert isinstance(tfa_object.func_df, pd.DataFrame), "func_df should be a DataFrame"
    
    # Verify that samples are preserved as columns in these matrices
    assert set(tfa_object.sample_list).issubset(set(tfa_object.taxa_df.columns))
    assert set(tfa_object.sample_list).issubset(set(tfa_object.func_df.columns))


def _write_sparse_analyzer_otf(path, sparse):
    df = pd.DataFrame(
        {
            "Sequence": ["PEPA", "PEPB"],
            "Proteins": ["g1_p1", "g1_p2"],
            "LCA_level": ["genome", "genome"],
            "Taxon": ["d__Bacteria|m__g1", "d__Bacteria|m__g1"],
            "Taxon_prop": [1.0, 1.0],
            "KEGG_ko": ["K00001", "K00001"],
            "KEGG_ko_prop": [1.0, 1.0],
            "Intensity_s1": [10.0, 0.0],
            "Intensity_s2": [0.0, 20.0],
        }
    )
    if sparse:
        df[["Intensity_s1", "Intensity_s2"]] = df[
            ["Intensity_s1", "Intensity_s2"]
        ].mask(lambda values: values.eq(0))
    df.to_csv(path, sep="\t", index=False)


def test_direct_analyzer_defaults_fill_sparse_zero_intensities(tmp_path):
    from metax.taxafunc_analyzer.analyzer import TaxaFuncAnalyzer

    sparse_path = tmp_path / "sparse.tsv"
    dense_path = tmp_path / "dense.tsv"
    _write_sparse_analyzer_otf(sparse_path, sparse=True)
    _write_sparse_analyzer_otf(dense_path, sparse=False)
    analyzers = []
    for path in [sparse_path, dense_path]:
        tfa = TaxaFuncAnalyzer(df_path=str(path), sample_col_prefix="Intensity")
        tfa.set_func("KEGG_ko")
        tfa.set_multi_tables(
            level="m",
            quant_method="sum",
            data_preprocess_params={
                "normalize_method": "None",
                "transform_method": "None",
                "batch_meta": "None",
                "processing_order": [],
            },
        )
        analyzers.append(tfa)

    sparse_tfa, dense_tfa = analyzers
    for table_name in ["taxa_df", "func_df", "taxa_func_df"]:
        pd.testing.assert_frame_equal(
            getattr(sparse_tfa, table_name),
            getattr(dense_tfa, table_name),
        )


def test_remove_all_zero_row_removes_zero_nan_mixtures(tmp_path):
    from metax.taxafunc_analyzer.analyzer import TaxaFuncAnalyzer

    path = tmp_path / "zero_nan_rows.tsv"
    pd.DataFrame(
        {
            "Sequence": ["all_zero", "all_nan", "mixed", "positive"],
            "Proteins": ["p1", "p2", "p3", "p4"],
            "LCA_level": ["genome"] * 4,
            "Taxon": ["d__Bacteria|m__g1"] * 4,
            "Taxon_prop": [1.0] * 4,
            "KEGG_ko": ["K00001"] * 4,
            "KEGG_ko_prop": [1.0] * 4,
            "metadata_count": [1, 2, 3, 0],
            "Intensity_s1": [0.0, None, 0.0, 0.0],
            "Intensity_s2": [0.0, None, None, 5.0],
        }
    ).to_csv(path, sep="\t", index=False)

    tfa = TaxaFuncAnalyzer(df_path=str(path), sample_col_prefix="Intensity")

    assert tfa.original_df["Sequence"].tolist() == ["positive"]
    assert tfa.original_df["metadata_count"].tolist() == [0]


def _write_unit_specific_otf(tmp_path, include_unit_sequence=False, include_analysis_unit=True):
    df = pd.DataFrame(
        {
            "analysis_unit_id": ["u1", "u2"],
            "Sequence": ["PEPA", "PEPA"],
            "Proteins": ["g1_p1", "g2_p2"],
            "LCA_level": ["genome", "genome"],
            "Taxon": ["d__Bacteria|m__g1", "d__Bacteria|m__g2"],
            "Taxon_prop": [1.0, 1.0],
            "KEGG_ko": ["K00001", "K00002"],
            "KEGG_ko_prop": [1.0, 1.0],
            "None_func": ["none_func", "none_func"],
            "None_func_prop": [1.0, 1.0],
            "Intensity_s1": [10.0, 0.0],
            "Intensity_s2": [0.0, 20.0],
        }
    )
    if not include_analysis_unit:
        df = df.drop(columns=["analysis_unit_id"])
    if include_unit_sequence:
        unit_ids = ["u1", "u2"] if "analysis_unit_id" not in df.columns else df["analysis_unit_id"]
        df.insert(1, "UnitSpecificSequence", pd.Series(unit_ids).astype(str) + "||" + df["Sequence"])
    path = tmp_path / "unit_specific_otf.tsv"
    df.to_csv(path, sep="\t", index=False)
    return path


def test_unit_specific_identity_is_generated_from_analysis_unit_and_sequence(tmp_path):
    from metax.taxafunc_analyzer.analyzer import TaxaFuncAnalyzer

    path = _write_unit_specific_otf(tmp_path, include_unit_sequence=False)
    tfa = TaxaFuncAnalyzer(df_path=str(path), sample_col_prefix="Intensity")
    tfa.set_func("None_func")
    tfa.set_multi_tables(
        level="m",
        quant_method="sum",
        taxa_and_func_only_from_otf=True,
        data_preprocess_params={"normalize_method": "None", "transform_method": "None", "batch_meta": "None", "processing_order": []},
        outlier_params={"detect_method": "none", "handle_method": "drop+drop"},
    )

    assert tfa.unit_specific_mode is True
    assert tfa.peptide_identity_col == "_MetaXUnitSpecificPeptideID"
    assert "UnitSpecificSequence" not in tfa.original_df.columns
    assert tfa.peptide_df.index.tolist() == ["u1||PEPA", "u2||PEPA"]
    assert tfa.peptide_df.index.name == "_MetaXUnitSpecificPeptideID"
    assert tfa.peptide_df["Sequence"].tolist() == ["PEPA", "PEPA"]
    assert tfa.taxa_func_df.index.names == ["Taxon", "None_func"]


def test_explicit_unit_specific_sequence_otf_remains_supported(tmp_path):
    from metax.taxafunc_analyzer.analyzer import TaxaFuncAnalyzer

    path = _write_unit_specific_otf(tmp_path, include_unit_sequence=True, include_analysis_unit=False)
    tfa = TaxaFuncAnalyzer(df_path=str(path), sample_col_prefix="Intensity")

    assert tfa.unit_specific_mode is True
    assert "UnitSpecificSequence" in tfa.original_df.columns
    assert tfa.peptide_identity_col == "UnitSpecificSequence"


def test_unit_specific_tables_and_proteins_keep_duplicate_sequences_separate(tmp_path):
    from metax.taxafunc_analyzer.analyzer import TaxaFuncAnalyzer

    path = _write_unit_specific_otf(tmp_path, include_unit_sequence=False)
    tfa = TaxaFuncAnalyzer(df_path=str(path), sample_col_prefix="Intensity")
    tfa.set_func("KEGG_ko")
    common_params = {
        "level": "m",
        "quant_method": "sum",
        "taxa_and_func_only_from_otf": False,
        "data_preprocess_params": {
            "normalize_method": "None",
            "transform_method": "None",
            "batch_meta": "None",
            "processing_order": [],
        },
        "outlier_params": {"detect_method": "none", "handle_method": "drop+drop"},
    }

    tfa.set_multi_tables(sum_protein=False, **common_params)

    assert tfa.unit_specific_mode is True
    assert tfa.peptide_identity_col == "_MetaXUnitSpecificPeptideID"
    assert tfa.peptide_df.index.tolist() == ["u1||PEPA", "u2||PEPA"]
    assert tfa.peptide_df["Sequence"].tolist() == ["PEPA", "PEPA"]
    assert tfa.taxa_df["peptide_num"].sum() == 2
    assert tfa.func_df["peptide_num"].sum() == 2
    assert tfa.taxa_func_df["peptide_num"].sum() == 2
    assert tfa.taxa_df["unit_peptide_num"].sum() == 2
    assert tfa.func_df["unit_peptide_num"].sum() == 2
    assert tfa.taxa_func_df["unit_peptide_num"].sum() == 2
    assert tfa.taxa_df["bare_sequence_num"].sum() == 2

    tfa.set_multi_tables(
        sum_protein=True,
        sum_protein_params={
            "method": "razor",
            "by_sample": False,
            "rank_method": "unique_counts",
            "greedy_method": "heap",
            "peptide_num_threshold": 1,
        },
        **common_params,
    )

    assert set(tfa.protein_df.index) == {"g1_p1", "g2_p2"}
    assert tfa.protein_df.loc["g1_p1", ["s1", "s2"]].tolist() == [10.0, 0.0]
    assert tfa.protein_df.loc["g2_p2", ["s1", "s2"]].tolist() == [0.0, 20.0]
    assert set(tfa.protein_df["peptides"]) == {"u1||PEPA", "u2||PEPA"}


@pytest.mark.parametrize(
    ("share_intensity", "expected_intensity"),
    [(False, [10.0, 20.0]), (True, [5.0, 10.0])],
)
def test_unit_specific_otf_split_func_uses_unsplit_taxa_source(
    tmp_path,
    share_intensity,
    expected_intensity,
):
    from metax.taxafunc_analyzer.analyzer import TaxaFuncAnalyzer

    path = tmp_path / "unit_specific_split_otf.tsv"
    pd.DataFrame(
        {
            "analysis_unit_id": ["u1", "u2"],
            "Sequence": ["PEPA", "PEPA"],
            "Proteins": ["g1_p1", "g1_p2"],
            "LCA_level": ["genome", "genome"],
            "Taxon": ["d__Bacteria|m__g1", "d__Bacteria|m__g1"],
            "Taxon_prop": [1.0, 1.0],
            "KEGG_ko": ["K00001|K00002", "K00001|K00002"],
            "KEGG_ko_prop": [1.0, 1.0],
            "Intensity_s1": [10.0, 0.0],
            "Intensity_s2": [0.0, 20.0],
        }
    ).to_csv(path, sep="\t", index=False)

    tfa = TaxaFuncAnalyzer(df_path=str(path), sample_col_prefix="Intensity")
    tfa.set_func("KEGG_ko")
    tfa.set_multi_tables(
        level="m",
        quant_method="sum",
        split_func=True,
        split_func_params={
            "split_by": "|",
            "share_intensity": share_intensity,
        },
        taxa_and_func_only_from_otf=True,
        data_preprocess_params={
            "normalize_method": "None",
            "transform_method": "None",
            "batch_meta": "None",
            "processing_order": [],
        },
        outlier_params={"detect_method": "none", "handle_method": "drop+drop"},
    )

    taxon = "d__Bacteria|m__g1"
    assert tfa.taxa_df.loc[taxon, ["s1", "s2"]].tolist() == [10.0, 20.0]
    assert tfa.taxa_df.loc[taxon, "peptide_num"] == 2
    assert tfa.taxa_df.loc[taxon, "unit_peptide_num"] == 2
    assert tfa.taxa_df.loc[taxon, "bare_sequence_num"] == 1

    for func in ["K00001", "K00002"]:
        assert tfa.func_df.loc[func, ["s1", "s2"]].tolist() == expected_intensity
        assert tfa.func_df.loc[func, "unit_peptide_num"] == 2
        assert tfa.func_df.loc[func, "bare_sequence_num"] == 1
        assert (
            tfa.taxa_func_df.loc[(taxon, func), ["s1", "s2"]].tolist()
            == expected_intensity
        )
        assert tfa.taxa_func_df.loc[(taxon, func), "unit_peptide_num"] == 2
        assert tfa.taxa_func_df.loc[(taxon, func), "bare_sequence_num"] == 1

    assert tfa.processed_original_df["KEGG_ko"].tolist() == [
        "K00001|K00002",
        "K00001|K00002",
    ]


def test_unit_specific_count_columns_derive_missing_bare_sequence(tmp_path):
    from metax.taxafunc_analyzer.analyzer import TaxaFuncAnalyzer

    path = _write_unit_specific_otf(tmp_path, include_unit_sequence=False)
    tfa = TaxaFuncAnalyzer(df_path=str(path), sample_col_prefix="Intensity")
    peptide_df = pd.DataFrame(
        {
            "_MetaXUnitSpecificPeptideID": ["u1||PEPA", "u2||PEPA", "u2||PEPB"],
            "Taxon": ["taxon_a", "taxon_a", "taxon_a"],
        }
    )
    summary_df = pd.DataFrame(
        {"s1": [1.0], "peptide_num": [3]},
        index=pd.Index(["taxon_a"], name="Taxon"),
    )

    result = tfa._add_peptide_count_columns(
        summary_df,
        peptide_df,
        group_cols=["Taxon"],
    )

    assert result.loc["taxon_a", "peptide_num"] == 3
    assert result.loc["taxon_a", "unit_peptide_num"] == 3
    assert result.loc["taxon_a", "bare_sequence_num"] == 2


def test_non_unit_specific_count_columns_remain_unchanged(tfa_object):
    summary_df = pd.DataFrame(
        {"s1": [4.0], "peptide_num": [2]},
        index=pd.Index(["taxon_a"], name="Taxon"),
    )
    peptide_df = pd.DataFrame(
        {"Sequence": ["PEPA", "PEPB"], "Taxon": ["taxon_a", "taxon_a"]}
    )

    result = tfa_object._add_peptide_count_columns(
        summary_df,
        peptide_df,
        group_cols=["Taxon"],
    )

    pd.testing.assert_frame_equal(result, summary_df)
    assert "unit_peptide_num" not in result.columns
    assert "bare_sequence_num" not in result.columns


def test_filter_taxa_func_uses_unit_specific_pair_counts(tmp_path):
    from metax.taxafunc_analyzer.analyzer import TaxaFuncAnalyzer

    path = _write_unit_specific_otf(tmp_path, include_unit_sequence=False)
    tfa = TaxaFuncAnalyzer(df_path=str(path), sample_col_prefix="Intensity")
    tfa.set_func("KEGG_ko")
    df = pd.DataFrame(
        {
            "_MetaXUnitSpecificPeptideID": [
                "u1||PEPA",
                "u2||PEPA",
                "u1||PEPA",
                "u1||PEPA",
                "u3||PEPB",
                "u4||PEPC",
            ],
            "Taxon": [
                "taxon_a",
                "taxon_a",
                "taxon_b",
                "taxon_b",
                "taxon_b",
                "taxon_c",
            ],
            "KEGG_ko": ["func_1", "func_1", "func_1", "func_2", "func_2", "func_3"],
            "Intensity_s1": [1.0, 2.0, 1.0, 1.0, 3.0, 4.0],
        }
    )

    result = tfa.filter_peptides_num(
        df,
        peptide_num_threshold={"taxa": 1, "func": 1, "taxa_func": 2},
        df_type="taxa_func",
    )

    assert list(zip(result["Taxon"], result["KEGG_ko"])) == [
        ("taxon_a", "func_1"),
        ("taxon_a", "func_1"),
        ("taxon_b", "func_2"),
        ("taxon_b", "func_2"),
    ]
    assert result["_MetaXUnitSpecificPeptideID"].tolist() == [
        "u1||PEPA",
        "u2||PEPA",
        "u1||PEPA",
        "u3||PEPB",
    ]


def test_unit_specific_sequence_is_used_for_all_summarization_paths(tmp_path):
    from metax.taxafunc_analyzer.analyzer import TaxaFuncAnalyzer

    path = _write_unit_specific_otf(
        tmp_path,
        include_unit_sequence=True,
        include_analysis_unit=False,
    )
    tfa = TaxaFuncAnalyzer(df_path=str(path), sample_col_prefix="Intensity")
    tfa.set_func("KEGG_ko")
    tfa.set_multi_tables(
        level="m",
        quant_method="sum",
        sum_protein=True,
        sum_protein_params={
            "method": "razor",
            "by_sample": False,
            "rank_method": "unique_counts",
            "greedy_method": "heap",
            "peptide_num_threshold": 1,
        },
        taxa_and_func_only_from_otf=False,
        data_preprocess_params={
            "normalize_method": "None",
            "transform_method": "None",
            "batch_meta": "None",
            "processing_order": [],
        },
        outlier_params={"detect_method": "none", "handle_method": "drop+drop"},
    )

    assert tfa.unit_specific_mode is True
    assert tfa.peptide_identity_col == "UnitSpecificSequence"
    assert tfa.peptide_df.index.tolist() == ["u1||PEPA", "u2||PEPA"]
    assert tfa.taxa_df["peptide_num"].sum() == 2
    assert tfa.func_df["peptide_num"].sum() == 2
    assert tfa.taxa_func_df["peptide_num"].sum() == 2
    assert set(tfa.protein_df.index) == {"g1_p1", "g2_p2"}
    assert set(tfa.protein_df["peptides"]) == {"u1||PEPA", "u2||PEPA"}


def test_non_unit_specific_otf_keeps_sequence_as_peptide_identity(tfa_object):
    assert tfa_object.unit_specific_mode is False
    assert tfa_object.peptide_identity_col == tfa_object.peptide_col_name
    assert tfa_object.peptide_identity_col == "Sequence"


def test_unit_specific_lfq_uses_internal_unit_specific_identity(monkeypatch, tmp_path):
    import metax.taxafunc_analyzer.analyzer as analyzer_module
    import metax.taxafunc_analyzer.analyzer_utils.lfq as lfq_module
    from metax.taxafunc_analyzer.analyzer import TaxaFuncAnalyzer

    quant_ids = []

    def fake_run_lfq(df, protein_id, quant_id):
        quant_ids.append(quant_id)
        sample_cols = [
            col
            for col in df.columns
            if col not in {protein_id, quant_id} and pd.api.types.is_numeric_dtype(df[col])
        ]
        return df.groupby(protein_id, as_index=False)[sample_cols].sum(), None

    monkeypatch.setattr(analyzer_module, "run_lfq", fake_run_lfq)
    monkeypatch.setattr(lfq_module, "run_lfq", fake_run_lfq)
    path = _write_unit_specific_otf(tmp_path, include_unit_sequence=False)
    tfa = TaxaFuncAnalyzer(df_path=str(path), sample_col_prefix="Intensity")
    tfa.set_func("None_func")
    tfa.set_multi_tables(
        level="m",
        quant_method="lfq",
        sum_protein=True,
        sum_protein_params={
            "method": "razor",
            "by_sample": False,
            "rank_method": "unique_counts",
            "greedy_method": "heap",
            "peptide_num_threshold": 1,
        },
        taxa_and_func_only_from_otf=False,
        data_preprocess_params={"normalize_method": "None", "transform_method": "None", "batch_meta": "None", "processing_order": []},
        outlier_params={"detect_method": "none", "handle_method": "drop+drop"},
    )

    assert quant_ids
    assert set(quant_ids) == {"_MetaXUnitSpecificPeptideID"}
