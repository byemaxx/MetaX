import pytest
import pandas as pd

def test_cross_test_ttest(tfa_object):
    """
    Test that get_stats_ttest computes p-values for two groups
    without crashing and returns a valid DataFrame.
    """
    # Ensure tables are generated
    if not hasattr(tfa_object, 'taxa_df'):
        tfa_object.set_multi_tables(level='s', quant_method='sum', split_func=False)
        
    ct = tfa_object.CrossTest
    
    # Needs exactly 2 groups for t-test
    group_list_all = tfa_object.group_list
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
    if not hasattr(tfa_object, 'func_df'):
        tfa_object.set_multi_tables(level='s', quant_method='sum', split_func=False)
        
    ct = tfa_object.CrossTest
    
    group_list_all = tfa_object.group_list
    if len(group_list_all) > 2:
        # Run anova on func level
        res_df = ct.get_stats_anova(group_list=group_list_all, df_type='func')
        
        assert isinstance(res_df, pd.DataFrame)
        assert 'pvalue' in res_df.columns
        assert 'padj' in res_df.columns
        assert 'f-statistic' in res_df.columns
    else:
        pytest.skip("Not enough groups to run ANOVA test (requires >2 groups).")
