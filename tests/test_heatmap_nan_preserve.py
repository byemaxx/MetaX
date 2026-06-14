import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock

from metax.taxafunc_ploter.heatmap_plot import HeatmapPlot

@pytest.fixture
def tfa_mock():
    mock = MagicMock()
    mock.func_name = "KO"
    return mock

def test_heatmap_table_preserves_nan_all_cond(tfa_mock):
    np.random.seed(42)
    data = np.random.rand(5, 4)
    data[1, 2] = np.nan
    data[3, 1] = np.nan
    # create 2-level columns for deseq2 res df
    cols = pd.MultiIndex.from_product([['G1_vs_G2', 'G1_vs_G3'], ['log2FoldChange', 'padj']])
    df = pd.DataFrame(data, columns=cols)
    df.index = [f"Feature_{i}" for i in range(5)]
    
    # We mock out extrcat_significant_fc_from_deseq2all
    extracted_df = pd.DataFrame(data, columns=['S1', 'S2', 'S3', 'S4'])
    extracted_df.index = [f"Feature_{i}" for i in range(5)]
    # Put some 0s to make sure they are not NaN
    extracted_df.loc["Feature_0", "S1"] = 0.0
    tfa_mock.CrossTest.extrcat_significant_fc_from_deseq2all.return_value = extracted_df.copy()

    hp = HeatmapPlot(tfa_mock)
    
    result = hp.plot_heatmap_of_all_condition_res(
        df=df,
        pvalue=0.05,
        res_df_type='deseq2',
        return_type='table',
        row_cluster=False,
        col_cluster=False,
        remove_zero_col=False
    )
    
    # Assert NaN remains NaN
    assert pd.isna(result.loc["Feature_1", "S3"])
    assert pd.isna(result.loc["Feature_3", "S2"])
    
    # Assert real 0 values remain 0 and are not confused with NaN
    assert result.loc["Feature_0", "S1"] == 0.0
    assert not pd.isna(result.loc["Feature_0", "S1"])

def test_heatmap_table_preserves_nan_top_taxa(tfa_mock):
    data = {
        'KO': ['KO1', 'KO1', 'KO2', 'KO2'],
        'Taxon': ['T1', 'T2', 'T1', 'T2'],
        'pvalue': [0.01, 0.02, 0.03, 0.04],
        'padj': [0.01, 0.02, 0.03, 0.04],
        'f-statistic': [5.0, np.nan, 4.0, 0.0]
    }
    df = pd.DataFrame(data)
    
    hp = HeatmapPlot(tfa_mock)
    result = hp.plot_top_taxa_func_heatmap_of_test_res(
        df=df,
        top_number=10,
        value_type='f',
        p_type='pvalue',
        pvalue=0.05,
        return_type='table',
        row_cluster=False,
        col_cluster=False,
        rename_taxa=False
    )
    
    # Assert NaN remains NaN
    assert pd.isna(result.loc['KO1', 'T2'])
    
    # Assert 0 remains 0
    assert result.loc['KO2', 'T2'] == 0.0
    assert not pd.isna(result.loc['KO2', 'T2'])
    
    # Assert non-NaN are non-NaN
    assert not pd.isna(result.loc['KO1', 'T1'])
