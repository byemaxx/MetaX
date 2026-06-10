import pytest
import pandas as pd

def test_get_stats_taxa_level(tfa_object):
    """
    Test that get_stats_taxa_level accurately aggregates taxa 
    counts and respects the peptide minimum threshold.
    """
    # BasicStats object is attached to tfa
    basic_stats = tfa_object.BasicStats
    
    # Run taxa level stats with a low threshold
    stats_df = basic_stats.get_stats_taxa_level(peptide_num=1)
    
    assert isinstance(stats_df, pd.DataFrame), "Result must be a DataFrame"
    assert 'taxa_level' in stats_df.columns
    assert 'count' in stats_df.columns
    
    # Run with a very high threshold to ensure filtering works
    stats_df_high = basic_stats.get_stats_taxa_level(peptide_num=99999)
    # Most counts should be 0 or heavily reduced compared to peptide_num=1
    assert stats_df_high['count'].sum() < stats_df['count'].sum()

def test_get_stats_func_prop(tfa_object):
    """
    Test get_stats_func_prop returns proper proportions 
    for the given functional annotation.
    """
    basic_stats = tfa_object.BasicStats
    func_name = tfa_object.func_name
    
    # The original Example_OTF might not have {func_name}_prop accurately 
    # but we will just ensure it runs and returns the expected shape.
    stats_df = basic_stats.get_stats_func_prop(func_name=func_name)
    
    assert isinstance(stats_df, pd.DataFrame), "Result must be a DataFrame"
    assert 'prop' in stats_df.columns
    assert 'freq' in stats_df.columns
    assert 'label' in stats_df.columns
    assert len(stats_df) == 11, "Should have 11 proportion bins (0-0.1 up to 1)"
    
    # The total frequency should sum approximately to 100% (within rounding margin)
    # Note: if data is empty, it might be 0, but if populated it should be close to 100
    if stats_df['n'].sum() > 0:
        assert abs(stats_df['freq'].sum() - 100.0) < 1.0, "Frequency should sum to roughly 100%"
