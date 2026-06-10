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
