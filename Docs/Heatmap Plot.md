# HeatmapPlot Class

The `HeatmapPlot` class provides two functions for visualizing data using heatmaps.

## plot_top_taxa_func_heatmap_of_test_res

This function generates a heatmap for the top significant taxa-function relationships based on the test results.

**Parameters:**
- `df`: A DataFrame containing the test results.
- `func_name` (str): The name of the function to be plotted.
- `top_number` (str, optional): The number of top significant taxa-function relationships to be plotted. Default is 100.
- `value_type` (str, optional): The type of value to be plotted, can be either 'p' (P-value), 'f' (f-statistic), or 't' (t-statistic). Default is 'p'.
- `fig_size` (tuple, optional): The size of the figure to be plotted. Default is None, and the function will determine the size based on the data.

**Usage Example:**

```python
heatmap_plot = HeatmapPlot(tfobj)
heatmap_plot.plot_top_taxa_func_heatmap_of_test_res(df_anova, sw.func, 200, 'f', (30, 30))
```
## plot_basic_heatmap
This function generates a basic heatmap of the input matrix with a color bar.

**Parameters:**
- `mat`: A matrix to be plotted.
- `title` (str, optional): The title of the heatmap. Default is `Heatmap`.
- `fig_size` (tuple, optional): The size of the figure to be plotted. Default is `None`, and the function will determine the size based on the data.
- `scale` (int, optional): The scale to be applied to the data. Default is `None`.
- `col_cluster` (bool, optional): Whether to cluster columns. Default is `True`.
- `row_cluster` (bool, optional): Whether to cluster rows. Default is `True`.

**Usage Example:**
```python
heatmap_plot = HeatmapPlot(tfobj)
heatmap_plot.plot_basic_heatmap(sw, mat=get_top_intensity_matrix_of_test_res(df=df_anova, df_type='anova', top_num=100), title='The heatmap of top 100 significant differences between groups in Taxa-Function', fig_size=(30, 30), scale=0)
```