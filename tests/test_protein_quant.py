import pytest
import pandas as pd

def test_protein_summation(tfa_object):
    """
    Test the protein summation/LFQ process during set_multi_tables.
    """
    # By calling set_multi_tables with sum_protein=True,
    # it invokes SumProteinIntensity internally.
    tfa_object.set_multi_tables(
        level='s', 
        quant_method='sum', 
        split_func=False,
        sum_protein=True,
        sum_protein_params={'method': 'razor', 'by_sample': False, 'rank_method': 'unique_counts', 'greedy_method': 'heap', 'peptide_num_threshold': 1},
        data_preprocess_params={'normalize_method': 'None', 'transform_method': 'None', 'batch_meta': 'None', 'processing_order': []},
        outlier_params={'detect_method': 'none', 'handle_method': 'drop+drop'}
    )
    
    # Check if protein_df was created
    assert hasattr(tfa_object, 'protein_df')
    assert isinstance(tfa_object.protein_df, pd.DataFrame)
    assert len(tfa_object.protein_df) > 0, "Protein matrix should not be empty"
    
    # Ensure all samples are columns in the protein matrix
    assert set(tfa_object.sample_list).issubset(set(tfa_object.protein_df.columns))

def test_lfq_execution(tfa_object):
    """
    Test setting multi tables using lfq as quant_method.
    This asserts that the LFQ calculation flow doesn't crash.
    """
    # Just run a lightweight table set with lfq
    tfa_object.set_multi_tables(
        level='s', 
        quant_method='lfq', 
        split_func=False,
        sum_protein=False,
        data_preprocess_params={'normalize_method': 'None', 'transform_method': 'None', 'batch_meta': 'None', 'processing_order': []},
        outlier_params={'detect_method': 'none', 'handle_method': 'drop+drop'}
    )
    
    assert hasattr(tfa_object, 'taxa_df')
    assert isinstance(tfa_object.taxa_df, pd.DataFrame)
