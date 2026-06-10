import pytest
import pandas as pd
import numpy as np

def test_detect_and_handle_outliers(tfa_object):
    """
    Test that outlier detection and handling runs without crashing
    and processes the matrix properly.
    """
    dp = tfa_object.detect_and_handle_outliers
    
    # Create a dummy dataframe matching the samples
    samples = tfa_object.sample_list
    data = {sample: [10, 20, 1000, 15, 12] for sample in samples}
    df = pd.DataFrame(data, index=['f1', 'f2', 'f3', 'f4', 'f5'])
    
    # 1000 is an outlier. Using IQR method:
    processed_df = dp(df=df, detect_method='iqr', handle_method='mean')
    
    assert isinstance(processed_df, pd.DataFrame), "Result must be a DataFrame"
    assert len(processed_df) == 4, "Row count should be 4 since the all-outlier row is dropped"
    
    # The outlier row (f3) is removed completely, so no NaNs should be left
    assert not processed_df.isnull().any().any(), "Should not have any remaining NaNs"

def test_data_preprocess_normalization(tfa_object):
    """
    Test data normalization and transformation options.
    """
    dp = tfa_object.data_preprocess
    
    samples = tfa_object.sample_list
    data = {sample: [1.0, 2.0, 3.0] for sample in samples}
    df = pd.DataFrame(data, index=['f1', 'f2', 'f3'])
    
    # Run z-score normalization and log2 transformation
    # Note: processing_order default normally does batch -> transform -> normalize
    # Let's just provide the strings
    processed_df = dp(
        df=df, 
        normalize_method='zscore', 
        transform_method='log2',
        processing_order=['transform', 'normalize']
    )
    
    assert isinstance(processed_df, pd.DataFrame), "Result must be a DataFrame"
    # Ensure transformed values are valid numbers
    assert not processed_df.isnull().any().any(), "Transformed data should not have NaNs"
    
    # Z-score normalization shifts data. If it moves to positive, min should be >= 0
    assert processed_df[samples].min().min() >= 0, "Z-score normalization with positive shift should have >=0 minimum"
