import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch
import matplotlib.pyplot as plt
from metax.taxafunc_ploter.basic_plot import BasicPlot

@pytest.fixture(scope="module")
def basic_plot(tfa_object):
    """
    Fixture to initialize BasicPlot object.
    """
    return BasicPlot(tfa_object)

@pytest.fixture
def sample_df(tfa_object):
    """
    Create a mock DataFrame for testing plot functions.
    The DataFrame needs to have sample names as columns.
    """
    sample_list = tfa_object.sample_list
    # Create a dummy dataframe with random numeric values
    import numpy as np
    np.random.seed(42)
    data = np.random.rand(50, len(sample_list))
    
    # Ensure there are some zeros for upset plot
    data[data < 0.3] = 0
    
    df = pd.DataFrame(data, columns=sample_list)
    df.index = [f"Feature_{i}" for i in range(50)]
    return df

@patch("matplotlib.pyplot.show")
def test_plot_pca_sns(mock_show, basic_plot, sample_df):
    """
    Smoke test for plot_pca_sns
    """
    fig = basic_plot.plot_pca_sns(df=sample_df, title_name="Test PCA", show_label=True)
    assert fig is not None
    # Verify that plt.show was called (meaning the plot completed without crashing)
    mock_show.assert_called_once()
    plt.close('all')

@patch("matplotlib.pyplot.show")
def test_plot_tsne_sns(mock_show, basic_plot, sample_df):
    """
    Smoke test for plot_tsne_sns
    """
    # Use small perplexity because sample size is small
    fig = basic_plot.plot_tsne_sns(df=sample_df, title_name="Test t-SNE", show_label=True, perplexity=2)
    assert fig is not None
    mock_show.assert_called_once()
    plt.close('all')

@patch("matplotlib.pyplot.show")
def test_plot_upset(mock_show, basic_plot, sample_df):
    """
    Smoke test for plot_upset
    """
    # plot_upset returns a dataframe
    upset_df = basic_plot.plot_upset(df=sample_df, title_name="Test UpSet", show_label=True, show_percentages=True)
    assert upset_df is not None
    assert not upset_df.empty
    mock_show.assert_called_once()
    plt.close('all')

@patch("matplotlib.pyplot.show")
def test_plot_box_sns(mock_show, basic_plot, sample_df):
    """
    Smoke test for plot_box_sns
    """
    fig = basic_plot.plot_box_sns(df=sample_df, title_name="Test Box")
    assert fig is not None
    mock_show.assert_called_once()
    plt.close('all')
