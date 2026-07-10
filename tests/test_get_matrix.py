import pytest
import pandas as pd

def test_get_intensity_matrix(tfa_object):
    """
    Test extraction of intensity matrix using get_intensity_matrix.
    """
    if not hasattr(tfa_object, 'taxa_func_df'):
        tfa_object.set_multi_tables(level='s', quant_method='sum', split_func=False)
        
    gm = tfa_object.GetMatrix
    
    # We need a valid func_name or taxon_name to test. Let's just use the first func_name in the taxa_func_df
    first_func = tfa_object.taxa_func_df.index[0][1]
    
    # Run the extraction for a specific function
    intensity_mat = gm.get_intensity_matrix(func_name=first_func)
    
    assert isinstance(intensity_mat, pd.DataFrame), "Should return a DataFrame"
    assert len(intensity_mat) > 0, "Matrix should not be empty"
    # The columns should be samples
    assert set(tfa_object.sample_list).issubset(set(intensity_mat.columns))

def test_get_top_intensity(tfa_object):
    """
    Test top intensity extraction from GetMatrix
    """
    if not hasattr(tfa_object, 'taxa_df'):
        tfa_object.set_multi_tables(level='s', quant_method='sum', split_func=False)
        
    gm = tfa_object.GetMatrix
    taxa_df = tfa_object.taxa_df
    
    top_df = gm.get_top_intensity(df=taxa_df, top_num=5, method='mean')
    
    assert isinstance(top_df, pd.DataFrame)
    assert len(top_df) <= 5
    assert set(tfa_object.sample_list).issubset(set(top_df.columns))
