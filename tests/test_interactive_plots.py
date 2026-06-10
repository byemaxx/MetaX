import pytest
import pandas as pd
import numpy as np

from metax.taxafunc_ploter.bar_plot_js import BarPlot
from metax.taxafunc_ploter.pca_plot_js import PcaPlot_js
from metax.taxafunc_ploter.volcano_plot_js import VolcanoPlotJS
from metax.taxafunc_ploter.trends_plot_js import TrendsPlot_js

@pytest.fixture
def mock_taxa_df(tfa_object):
    sample_list = tfa_object.sample_list
    np.random.seed(42)
    data = np.random.rand(20, len(sample_list))
    df = pd.DataFrame(data, columns=sample_list)
    df.index = [f"d__Bacteria|p__Phylum_{i}" for i in range(20)]
    return df

@pytest.fixture
def fc_df():
    np.random.seed(42)
    data = {
        'log2FoldChange': np.random.uniform(-5, 5, 100),
        'padj': np.random.uniform(0.0001, 1, 100)
    }
    df = pd.DataFrame(data)
    df.index = [f"Feature_{i}" for i in range(100)]
    return df

def test_bar_plot_js(tfa_object):
    # Ensure tfa_object has the necessary attributes generated
    tfa_object.set_multi_tables(level='s', quant_method='sum', split_func=True)
    bp = BarPlot(tfa_object)
    
    # We will just pass the first taxon from taxa_df
    taxon_name = tfa_object.taxa_df.index[0]
    
    chart = bp.plot_intensity_bar_js(taxon_name=taxon_name)
    assert chart is not None

def test_pca_plot_js(tfa_object, mock_taxa_df):
    pp = PcaPlot_js(tfa_object)
    chart = pp.plot_pca_pyecharts_3d(df=mock_taxa_df, title_name="Test PCA 3D")
    assert chart is not None

def test_volcano_plot_js(fc_df):
    vp = VolcanoPlotJS()
    chart = vp.plot_volcano_js(df_fc=fc_df)
    assert chart is not None

def test_trends_plot_js(tfa_object, mock_taxa_df):
    tp = TrendsPlot_js(tfa_object)
    chart = tp.plot_trends_js(df=mock_taxa_df)
    assert chart is not None
