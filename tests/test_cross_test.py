import pytest
import pandas as pd
import sys
from types import ModuleType, SimpleNamespace

from metax.taxafunc_analyzer.analyzer_utils.cross_test import CrossTest

def test_cross_test_ttest(tfa_object):
    """
    Test that get_stats_ttest computes p-values for two groups
    without crashing and returns a valid DataFrame.
    """
    # Ensure tables are generated
    if getattr(tfa_object, 'taxa_df', None) is None:
        tfa_object.set_multi_tables(level='s', quant_method='sum', split_func=False)
        
    ct = tfa_object.CrossTest
    
    # Needs exactly 2 groups for t-test
    group_list_all = list(dict.fromkeys(tfa_object.group_list))
    assert len(group_list_all) >= 2, "Test dataset must have at least 2 groups for t-test"
    test_groups = group_list_all[:2]
    
    # Run t-test on taxa level
    res_df = ct.get_stats_ttest(group_list=test_groups, df_type='taxa')
    
    assert isinstance(res_df, pd.DataFrame)
    assert 'pvalue' in res_df.columns
    assert 'padj' in res_df.columns
    assert 't-statistic' in res_df.columns
    
    # Assert p-values are within [0, 1]
    assert res_df['pvalue'].min() >= 0.0
    assert res_df['pvalue'].max() <= 1.0

def test_cross_test_anova(tfa_object):
    """
    Test that get_stats_anova computes p-values for multiple groups
    without crashing and returns a valid DataFrame.
    """
    # Ensure tables are generated
    if getattr(tfa_object, 'func_df', None) is None:
        tfa_object.set_multi_tables(level='s', quant_method='sum', split_func=False)
        
    ct = tfa_object.CrossTest
    
    group_list_all = list(dict.fromkeys(tfa_object.group_list))
    if len(group_list_all) > 2:
        # Run anova on func level
        res_df = ct.get_stats_anova(group_list=group_list_all, df_type='func')
        
        assert isinstance(res_df, pd.DataFrame)
        assert 'pvalue' in res_df.columns
        assert 'padj' in res_df.columns
        assert 'f-statistic' in res_df.columns
    else:
        pytest.skip("Not enough groups to run ANOVA test (requires >2 groups).")


def test_run_inmoose_deseq_retries_mean_fit_on_unimplemented_local_fallback():
    ct = CrossTest(tfa=None)
    calls = []
    dds_count = 0

    def dds_factory():
        nonlocal dds_count
        dds_count += 1
        calls.append("factory")
        return {"id": dds_count}

    def fake_deseq(dds, quiet=False, fitType="parametric"):
        calls.append((dds["id"], quiet, fitType))
        if fitType == "parametric":
            raise NotImplementedError()
        return {"fitType": fitType, "dds": dds}

    result = ct._run_inmoose_deseq(fake_deseq, dds_factory, quiet=True)

    assert result["fitType"] == "mean"
    assert calls == ["factory", (1, True, "parametric"), "factory", (2, True, "mean")]


def test_restore_limma_fit_column_names_aligns_fit_with_design_columns():
    ct = CrossTest(tfa=None)
    fit = SimpleNamespace(
        coefficients=pd.DataFrame([[1.0, 2.0]], columns=["column0", "column1"]),
        stdev_unscaled=pd.DataFrame([[0.1, 0.2]], columns=["column0", "column1"]),
        cov_coefficients=pd.DataFrame(
            [[1.0, 0.0], [0.0, 1.0]],
            index=["column0", "column1"],
            columns=["column0", "column1"],
        ),
    )

    ct._restore_limma_fit_column_names(fit, ["group_V1", "group_V2"])

    assert fit.coefficients.columns.tolist() == ["group_V1", "group_V2"]
    assert fit.stdev_unscaled.columns.tolist() == ["group_V1", "group_V2"]
    assert fit.cov_coefficients.index.tolist() == ["group_V1", "group_V2"]
    assert fit.cov_coefficients.columns.tolist() == ["group_V1", "group_V2"]


def test_align_limma_design_to_assay_reorders_rows_by_sample_name():
    ct = CrossTest(tfa=None)
    assay_df = pd.DataFrame({"feature_a": [1.0, 2.0]}, index=["sample_a", "sample_b"])
    design = pd.DataFrame(
        {"group_control": [0.0, 1.0], "group_treatment": [1.0, 0.0]},
        index=["sample_b", "sample_a"],
    )

    aligned = ct._align_limma_design_to_assay(design, assay_df)

    assert aligned.index.tolist() == ["sample_a", "sample_b"]
    assert aligned.loc["sample_a", "group_control"] == 1.0
    assert aligned.loc["sample_b", "group_treatment"] == 1.0


def test_run_inmoose_ebayes_retries_scalar_df_prior_compatibility():
    ct = CrossTest(tfa=None)
    module_name = "_fake_inmoose_ebayes_for_test"
    fake_module = ModuleType(module_name)

    def squeeze_var(values):
        return {"df_prior": float("inf")}

    fake_module.squeezeVar = squeeze_var
    sys.modules[module_name] = fake_module
    calls = []

    def fake_ebayes(fit):
        calls.append("eBayes")
        if len(calls) == 1:
            raise KeyError(-2)
        return fake_module.squeezeVar([1.0, 2.0, 3.0])

    fake_ebayes.__module__ = module_name

    try:
        result = ct._run_inmoose_ebayes(fake_ebayes, fit=object())
    finally:
        sys.modules.pop(module_name, None)

    assert calls == ["eBayes", "eBayes"]
    assert result["df_prior"].tolist() == [float("inf"), float("inf"), float("inf")]


def test_normalize_deseq2_results_adds_padj_when_inmoose_omits_it():
    ct = CrossTest(tfa=None)
    res = pd.DataFrame(
        {
            "baseMean": [10.0, 20.0, 30.0],
            "log2FoldChange": [1.5, -2.0, 0.2],
            "lfcSE": [0.1, 0.2, 0.3],
            "stat": [3.0, -4.0, 0.5],
            "pvalue": [0.01, 0.04, 0.5],
        },
        index=["a", "b", "c"],
    )

    normalized = ct._normalize_deseq2_results(res)

    assert normalized.columns.tolist()[:6] == [
        "baseMean",
        "log2FoldChange",
        "lfcSE",
        "stat",
        "pvalue",
        "padj",
    ]
    assert "padj" in normalized.columns
    assert normalized["padj"].between(0, 1).all()


def test_normalize_limma_results_preserves_logfc_from_log2_input():
    ct = CrossTest(tfa=None)
    dft = pd.DataFrame(
        {
            "c1": [6.0, 8.0],
            "c2": [6.0, 8.0],
            "t1": [8.0, 6.0],
            "t2": [8.0, 6.0],
        },
        index=["feature_up", "feature_down"],
    )
    res = pd.DataFrame(
        {
            "logFC": [2.0, -2.0],
            "P.Value": [0.01, 0.02],
        },
        index=dft.index,
    )

    normalized = ct._normalize_limma_results(
        res,
        dft,
        sample_list=dft.columns.tolist(),
        concat_sample_to_result=False,
        group1_sample=["c1", "c2"],
        group2_sample=["t1", "t2"],
    )

    assert normalized.loc["feature_up", "log2FoldChange"] == pytest.approx(2.0)
    assert normalized.loc["feature_down", "log2FoldChange"] == pytest.approx(-2.0)
    assert "padj" in normalized.columns


def test_prepare_limma_input_handles_zeros_and_log2():
    import numpy as np
    tfa = SimpleNamespace(sample_list=["S1", "S2"], invert_transform=lambda df, m: df)
    ct = CrossTest(tfa=tfa)
    df = pd.DataFrame({"Feature": ["A", "B"], "S1": [0, 2], "S2": [3, 0]})
    
    res = ct.prepare_limma_input(df, log2_transform=True, zero_to_nan=True)
    assert pd.isna(res.loc[0, "S1"])
    assert res.loc[0, "S2"] == np.log2(4)
    assert res.loc[1, "S1"] == np.log2(3)
    assert pd.isna(res.loc[1, "S2"])


def test_prepare_deseq2_input_raises_on_nan_or_negative():
    import numpy as np
    tfa = SimpleNamespace(sample_list=["S1"], invert_transform=lambda df, m: df)
    ct = CrossTest(tfa=tfa)
    
    df1 = pd.DataFrame({"Feature": ["A"], "S1": [-1]})
    with pytest.raises(ValueError, match="Cannot run DESeq2 because negative values exist"):
        ct.prepare_deseq2_input(df1, validate=True)
        
    df2 = pd.DataFrame({"Feature": ["A"], "S1": [np.nan]})
    with pytest.raises(ValueError, match="Cannot run DESeq2 because NaN values exist"):
        ct.prepare_deseq2_input(df2, validate=True)


def test_filter_limma_rank_aware():
    import numpy as np
    ct = CrossTest(tfa=None)
    
    dft = pd.DataFrame({
        "Feature": ["F1", "F2", "F3"],
        "S1": [1.0, 1.0, np.nan],
        "S2": [1.0, np.nan, np.nan],
        "S3": [1.0, 1.0, 1.0]
    }).set_index("Feature")
    
    group1_sample = ["S1", "S2"]
    group2_sample = ["S3"]
    
    # rank is 2
    design = pd.DataFrame({"Intercept": [1, 1, 1], "GroupB": [0, 0, 1]})
    
    res = ct._filter_limma_rank_aware(dft, group1_sample, group2_sample, design)
    
    # F3 and F2 should be filtered out
    assert "F1" in res.index
    assert "F2" not in res.index
    assert "F3" not in res.index

    # If rank is 3, F1 would be filtered too (only 3 total samples)
    design3 = pd.DataFrame({"Intercept": [1, 1, 1], "GroupB": [0, 0, 1], "Cov": [1, 2, 3]})
    with pytest.raises(ValueError, match="Not enough samples to fit the limma design matrix."):
        ct._filter_limma_rank_aware(dft, group1_sample, group2_sample, design3)
