# TaxaFuncAnalyzer

The `TaxaFuncAnalyzer` class provides a comprehensive analysis of taxonomic and functional features in metaproteomics data. It reads data from input files, processes the data, and computes various statistics.

## Table of Contents

- [TaxaFuncAnalyzer](#taxafuncanalyzer)
  - [Table of Contents](#table-of-contents)
  - [1. Introduction](#1-introduction)
  - [2. Class Attributes](#2-class-attributes)
  - [3. Initialization](#3-initialization)
  - [4. Private Methods](#4-private-methods)
    - [4.1 \_\_set\_original\_df](#41-__set_original_df)
    - [4.2 \_\_set\_meta](#42-__set_meta)
  - [5. Public Methods](#5-public-methods)
    - [5.1 set\_func](#51-set_func)
    - [5.2 set\_group](#52-set_group)
    - [5.3 get\_meta\_list](#53-get_meta_list)
    - [5.4 get\_sample\_list\_in\_a\_group](#54-get_sample_list_in_a_group)
    - [5.5 get\_stats\_peptide\_num\_in\_taxa](#55-get_stats_peptide_num_in_taxa)
    - [5.6 get\_stats\_taxa\_level](#56-get_stats_taxa_level)
    - [5.7 get\_stats\_func\_prop](#57-get_stats_func_prop)
    - [5.8 set\_multi\_tables](#58-set_multi_tables)
    - [5.9 get\_stats\_anova](#59-get_stats_anova)
    - [5.10 set\_anova](#510-set_anova)
    - [5.11 get\_stats\_ttest](#511-get_stats_ttest)
    - [5.12 get\_intensity\_matrix](#512-get_intensity_matrix)
    - [5.13 get\_top\_intensity\_matrix\_of\_test\_res](#513-get_top_intensity_matrix_of_test_res)
    - [5.14 get\_stats\_tukey\_test](#514-get_stats_tukey_test)
      - [Parameters](#parameters)
      - [Returns](#returns)
      - [Example Usage](#example-usage)

## 1. Introduction

The `TaxaFuncAnalyzer` class is designed for analyzing metaproteomics data. It takes two input files: a data file (df_path) and a metadata file (meta_path). The data file should be a tab-separated file with peptide sequences, taxonomic information, functional annotations, and sample intensities. The metadata file should be a tab-separated file containing sample information and group assignments.

## 2. Class Attributes

- `original_df`: A pandas DataFrame of the original data file
- `sample_list`: A list of sample names
- `meta_df`: A pandas DataFrame of the metadata file
- `meta_name`: The name of the column used for group assignment
- `group_list`: A list of unique group names in the metadata
- `func`: The functional annotation column used for analysis
- `clean_df`: A cleaned pandas DataFrame with only relevant data
- `taxa_df`: A pandas DataFrame with taxa-level data
- `func_df`: A pandas DataFrame with functional annotation data
- `taxa_func_df`: A pandas DataFrame with taxa and functional annotation data combined
- `func_taxa_df`: A pandas DataFrame with functional annotation and taxa data combined
- `anova_df`: A pandas DataFrame with ANOVA test results

## 3. Initialization

The `__init__` method initializes the class with the provided data and metadata file paths.

```python
def __init__(self, df_path, meta_path):
```
## 4. Private Methods

### 4.1 __set_original_df
This method reads the data file and creates a pandas DataFrame with cleaned column names.

```python
def __set_original_df(self, df_path: str)
```

### 4.2 __set_meta

This method reads the metadata file and creates a pandas DataFrame with cleaned column names.

```python
def __set_meta(self, meta_path: str)
```

## 5. Public Methods

### 5.1 set_func

This method sets the functional annotation column used for analysis.

```python
def set_func(self, func: str)
```

### 5.2 set_group

This method sets the group assignment column used for analysis.

```python
def set_group(self, group: str)
```

### 5.3 get_meta_list

This method returns a list of unique values in the specified metadata column.

```python
def get_meta_list(self, meta_name: str) -> List[str]:
```

### 5.4 get_sample_list_in_a_group

This method returns a list of sample names in a specified group.

```python
def get_sample_list_in_a_group(self, group_name: str) -> List[str]:
```

### 5.5 get_stats_peptide_num_in_taxa

This method calculates the number of peptides in each taxonomic group.

```python
def get_stats_peptide_num_in_taxa(self, level: str) -> pd.DataFrame:
```

### 5.6 get_stats_taxa_level

This method calculates the relative abundance of taxa at a specified taxonomic level.

```python
def get_stats_taxa_level(self, level: str) -> pd.DataFrame:
```

### 5.7 get_stats_func_prop

This method calculates the proportion of functional annotations in each group.

```python
def get_stats_func_prop(self) -> pd.DataFrame:
```

### 5.8 set_multi_tables

This method sets up multiple data tables for downstream analysis.

```python
def set_multi_tables(self, level: str = 's', func_threshold:float = 1.00,
                    normalize_method: str = None, transform_method: str None,
                    batch_list: list = None,  processing_order:list=None)
```
+ level: s = Speceis; g = 'Genus'
- func_threshold: The shreshould to filter the function.(defaute: 100%)
+ normalize_method: None, mean, sum, minmax, zscore
- transform_method: None, log2, log10, sqrt, cube
+ batch_list: a list for samples
- processing_order: a list like ['batch', 'transform', 'normalize']

### 5.9 get_stats_anova

This method performs an ANOVA test to compare the mean intensity values of functional annotations across groups.

```python
def get_stats_anova(self) -> pd.DataFrame:
```

### 5.10 set_anova

This method sets the ANOVA DataFrame with the test results.

```python
def set_anova(self, anova_df: pd.DataFrame)
```

### 5.11 get_stats_ttest

This method performs a t-test to compare the mean intensity values of functional annotations between two groups.

```python
def get_stats_ttest(self, group_list=['group1', 'group2') -> pd.DataFrame:
```

### 5.12 get_intensity_matrix

This method returns the intensity matrix for the specified functional annotation and taxonomic level.

```python
def get_intensity_matrix(self, func: str, level: str) -> pd.DataFrame:
```

### 5.13 get_top_intensity_matrix_of_test_res

This method returns the top intensity matrix based on the test results.

```python
def get_top_intensity_matrix_of_test_res(self, test_res: pd.DataFrame, n: int, level: str) -> pd.DataFrame:
```

### 5.14 get_stats_tukey_test

This method calculates and returns the Tukey test result for a given taxon name and/or function name.
```python
def get_stats_tukey_test(self, taxon_name:str, func_name:str): -> pd.DataFrame:
```
#### Parameters
- `taxon_name`: the name of the taxon (optional)
- `func_name`: the name of the function (optional)

#### Returns
- `tukey_result`: the result of the Tukey test

#### Example Usage
```python
my_object = MyClass()
result = my_object.get_stats_tukey_test('taxon_1', 'function_1')
print(result)
```
