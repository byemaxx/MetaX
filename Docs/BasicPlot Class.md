# BasicPlot Class

The `BasicPlot` class provides several functions for visualizing data using bar plots and scatter plots.

## plot_taxa_stats

This function generates a bar plot to visualize the number of identified peptides in different taxa levels.

**Parameters:**
- `tfobj`: A `taxaFuncAnalyzer` object with the data to be plotted.

**Usage Example:**

```python
bp = BasicPlot(tfobj)
bp.plot_taxa_stats()
```
## plot_taxa_number
This function generates a bar plot to visualize the number of taxa in different taxa levels.

**Parameters:**
- `tfobj`: A `taxaFuncAnalyzer` object with the data to be plotted.
**Usage Example:**

```python
bp = BasicPlot(tfobj)
bp.plot_taxa_number()
```

## plot_prop_stats
This function generates a bar plot to visualize the number of peptides in different proportions of function.

**Parameters:**
- `tfobj`: A `taxaFuncAnalyzer` object with the data to be plotted.
**Usage Example:**

```python
bp = BasicPlot(tfobj)
bp.plot_prop_stats()
```
## plot_pca_sns
This function generates a scatter plot to visualize the PCA of the input data.

**Parameters:**
- `tfobj`: A `taxaFuncAnalyzer` object with the data to be plotted.
- `df`: A DataFrame containing the data for PCA.
- `table_name`: A string representing the name of the table. Default is `Table`.
- `show_label`: A boolean indicating whether to show sample labels on the plot. Default is `True`.

**Usage Example:**
```python
bp = BasicPlot(tfobj)
bp.plot_pca_sns( df = tfobj.taxa_df_df,  table_name = 'Taxa and Functions', show_label = False)
```
