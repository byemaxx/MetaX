import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch

from metax.taxafunc_ploter.sankey_plot import SankeyPlot
from metax.taxafunc_ploter.sunburst_plot import SunburstPlot
from metax.taxafunc_ploter.treemap_plot import TreeMapPlot

@pytest.fixture
def mock_taxa_df(tfa_object):
    sample_list = tfa_object.sample_list
    data = {
        'Taxon': ['d__Bacteria|p__Proteobacteria|c__Gammaproteobacteria', 
                  'd__Bacteria|p__Firmicutes|c__Bacilli',
                  'd__Bacteria|p__Proteobacteria|c__Alphaproteobacteria']
    }
    for s in sample_list:
        data[s] = np.random.randint(10, 100, 3)
    df = pd.DataFrame(data).set_index('Taxon')
    return df

@pytest.fixture
def mock_taxa_func_df(tfa_object):
    sample_list = tfa_object.sample_list
    data = {
        'Taxon': ['d__Bacteria', 'd__Bacteria'],
        'Function': ['Func_A', 'Func_B']
    }
    for s in sample_list:
        data[s] = np.random.randint(10, 100, 2)
    df = pd.DataFrame(data).set_index(['Taxon', 'Function'])
    return df

def test_sankey_plot(tfa_object, mock_taxa_func_df):
    sp = SankeyPlot(tfa_object)
    chart = sp.plot_intensity_sankey(df=mock_taxa_func_df, title="Test Sankey")
    assert chart is not None

def test_sunburst_plot(mock_taxa_df):
    sbp = SunburstPlot()
    chart = sbp.create_sunburst_chart(taxa_df=mock_taxa_df, title="Test Sunburst")
    assert chart is not None

def test_treemap_plot(mock_taxa_df):
    tmp = TreeMapPlot()
    chart = tmp.create_treemap_chart(taxa_df=mock_taxa_df, title="Test TreeMap")
    assert chart is not None
