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

def test_plot_top_taxa_func_heatmap_one_row_table(tfa_mock):
    data = {
        'KO': ['KO1', 'KO1'],
        'Taxon': ['T1', 'T2'],
        'pvalue': [0.01, 0.02],
        'padj': [0.01, 0.02],
        'f-statistic': [5.0, 4.0]
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
        row_cluster=True,
        col_cluster=True,
        rename_taxa=False
    )
    
    # Assert result shape (1 row, 2 columns)
    assert result.shape == (1, 2)
    # The effective_row_cluster should have been evaluated to False, preventing error

def test_plot_top_taxa_func_heatmap_one_col_table(tfa_mock):
    data = {
        'KO': ['KO1', 'KO2'],
        'Taxon': ['T1', 'T1'],
        'pvalue': [0.01, 0.02],
        'padj': [0.01, 0.02],
        'f-statistic': [5.0, 4.0]
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
        row_cluster=True,
        col_cluster=True,
        rename_taxa=False
    )
    
    # Assert result shape (2 rows, 1 column)
    assert result.shape == (2, 1)

def test_heatmap_all_cols_removed_by_zero_col(tfa_mock):
    # Setup data with all zeros after extracting
    np.random.seed(42)
    data = np.zeros((5, 4))
    cols = pd.MultiIndex.from_product([['G1_vs_G2', 'G1_vs_G3'], ['log2FoldChange', 'padj']])
    df = pd.DataFrame(data, columns=cols)
    df.index = [f"Feature_{i}" for i in range(5)]
    
    extracted_df = pd.DataFrame(data, columns=['S1', 'S2', 'S3', 'S4'])
    extracted_df.index = [f"Feature_{i}" for i in range(5)]
    
    tfa_mock.CrossTest.extrcat_significant_fc_from_deseq2all.return_value = extracted_df.copy()
    
    hp = HeatmapPlot(tfa_mock)
    
    with pytest.raises(ValueError, match="Dataframe is empty after filtering/removing zero columns"):
        hp.plot_heatmap_of_all_condition_res(
            df=df,
            pvalue=0.05,
            res_df_type='deseq2',
            remove_zero_col=True
        )

def test_heatmap_dft_none_or_empty(tfa_mock):
    np.random.seed(42)
    data = np.random.rand(5, 4)
    cols = pd.MultiIndex.from_product([['G1_vs_G2', 'G1_vs_G3'], ['log2FoldChange', 'padj']])
    df = pd.DataFrame(data, columns=cols)
    df.index = [f"Feature_{i}" for i in range(5)]
    
    # Test None
    tfa_mock.CrossTest.extrcat_significant_fc_from_deseq2all.return_value = None
    hp = HeatmapPlot(tfa_mock)
    
    with pytest.raises(ValueError, match="No significant differences Results"):
        hp.plot_heatmap_of_all_condition_res(
            df=df,
            pvalue=0.05,
            res_df_type='deseq2',
        )

    # Test Empty
    tfa_mock.CrossTest.extrcat_significant_fc_from_deseq2all.return_value = pd.DataFrame()
    with pytest.raises(ValueError, match="No significant differences Results"):
        hp.plot_heatmap_of_all_condition_res(
            df=df,
            pvalue=0.05,
            res_df_type='deseq2',
        )
