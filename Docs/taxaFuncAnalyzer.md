# Table of Contents

- [Table of Contents](#table-of-contents)
  - [Class: TaxaFuncAnalyzer ](#class-taxafuncanalyzer-)
    - [`__init__(self, df, meta_df, func_name, meta_name, sample_list, group_list)` ](#__init__self-df-meta_df-func_name-meta_name-sample_list-group_list-)
    - [`get_sample_list_in_a_group(self, group)` ](#get_sample_list_in_a_groupself-group-)
    - [`get_meta_list(self, meta)` ](#get_meta_listself-meta-)
    - [`get_stats_anova(self, group_list, df_type)` ](#get_stats_anovaself-group_list-df_type-)
    - [`get_stats_ttest(self, group_list, df_type)` ](#get_stats_ttestself-group_list-df_type-)
    - [`get_intensity_matrix(self, func_name, taxon_name, peptide_seq, groups)` ](#get_intensity_matrixself-func_name-taxon_name-peptide_seq-groups-)
    - [`get_top_intensity(self, df, top_num, method, sample_list)` ](#get_top_intensityself-df-top_num-method-sample_list-)
    - [`replace_if_two_index(self, df)` ](#replace_if_two_indexself-df-)
    - [`get_top_intensity_matrix_of_test_res(self, df, df_type, top_num, show_stats_cols)` ](#get_top_intensity_matrix_of_test_resself-df-df_type-top_num-show_stats_cols-)
    - [`get_stats_deseq2(self, df, group_list)` ](#get_stats_deseq2self-df-group_list-)
    - [`get_stats_tukey_test(self, taxon_name, func_name)` ](#get_stats_tukey_testself-taxon_name-func_name-)
    - [`set_multi_tables(self, level, func_threshold, normalize_method, transform_method, outlier_detect_method, outlier_handle_method, outlier_handle_by_group, batch_list, processing_order)` ](#set_multi_tablesself-level-func_threshold-normalize_method-transform_method-outlier_detect_method-outlier_handle_method-outlier_handle_by_group-batch_list-processing_order-)
    - [`check_attributes(self)` ](#check_attributesself-)
    - [`get_current_time(self)` ](#get_current_timeself-)

---

## Class: TaxaFuncAnalyzer <a name="class-taxafuncanalyzer"></a>
This is the main class of the script. The class contains methods for analyzing taxonomic functions in a dataset.

### `__init__(self, df, meta_df, func_name, meta_name, sample_list, group_list)` <a name="init"></a>
The initialization method for the `TaxaFuncAnalyzer` class. It sets the initial state of the instance.

**Parameters:**

- `df` (pandas DataFrame): The input data frame that contains the main data.
- `meta_df` (pandas DataFrame): The metadata associated with the main data.
- `func_name` (str): The name of the function to be analyzed.
- `meta_name` (str): The name of the metadata.
- `sample_list` (list of str): The list of samples in the data.
- `group_list` (list of str): The list of groups in the data.

**Returns:**

- This is the constructor method and does not return a value.

### `get_sample_list_in_a_group(self, group)` <a name="get_sample_list_in_a_group"></a>
Returns a list of samples that belong to a certain group.

**Parameters:**

- `group` (str): The name of the group to be examined.

**Returns:**

- list: A list of samples that belong to the specified group.

### `get_meta_list(self, meta)` <a name="get_meta_list"></a>
Returns a list of metadata values.

**Parameters:**

- `meta` (str): The name of the metadata.

**Returns:**

- list: A list of metadata values.

### `get_stats_anova(self, group_list, df_type)` <a name="get_stats_anova"></a>
Performs an ANOVA test and returns the results.

**Parameters:**

- `group_list` (list of str): The list of groups to be included in the test.
- `df_type` (str): The type of the data frame. It can be one of the following: 'taxa-func', 'func-taxa', 'taxa', 'func', 'peptide'.

**Returns:**

- DataFrame: A dataframe containing the results of the ANOVA test.


### `get_stats_ttest(self, group_list, df_type)` <a name="get_stats_ttest"></a>
Performs a t-test and returns the results.

**Parameters:**

- `group_list` (list of str): The list of groups to be included in the test.
- `df_type` (str): The type of the data frame.

**Returns:**

- DataFrame: A dataframe containing the results of the t-test.

### `get_intensity_matrix(self, func_name, taxon_name, peptide_seq, groups)` <a name="get_intensity_matrix"></a>
Generates a matrix of the intensity of the taxon or function or peptide in each sample.

**Parameters:**

- `func_name` (str): The name of the function.
- `taxon_name` (str): The name of the taxon.
- `peptide_seq` (str): The sequence of the peptide.
- `groups` (list of str): The list of groups.

**Returns:**

- DataFrame: A dataframe containing the intensity matrix.

### `get_top_intensity(self, df, top_num, method, sample_list)` <a name="get_top_intensity"></a>
Returns the top intensity values.

**Parameters:**

- `df` (pandas DataFrame): The input data frame.
- `top_num` (int): The number of top intensities to return.
- `method` (str): The method to use for calculating the intensity. It can be one of the following: 'freq', 'mean', 'sum'.
- `sample_list` (list of str): The list of samples.

**Returns:**

- DataFrame: A dataframe containing the top intensity values.

### `replace_if_two_index(self, df)` <a name="replace_if_two_index"></a>
Replaces the index if there are two indices.

**Parameters:**

- `df` (pandas DataFrame): The input data frame.

**Returns:**

- DataFrame: The modified dataframe.

### `get_top_intensity_matrix_of_test_res(self, df, df_type, top_num, show_stats_cols)` <a name="get_top_intensity_matrix_of_test_res"></a>
Returns the top intensity matrix of test results.

**Parameters:**

- `df` (pandas DataFrame): The input data frame.
- `df_type` (str): The type of the data frame. It can be one of the following: 'anova', 'ttest', 'log2fc'.
- `top_num` (int): The number of top intensities to return.
- `show_stats_cols` (bool): Whether to show statistics columns.

**Returns:**

- DataFrame: A dataframe containing the top intensity matrix of test results.

### `get_stats_deseq2(self, df, group_list)` <a name="get_stats_deseq2"></a>
Performs a DESeq2 test and returns the results.

**Parameters:**

- `df` (pandas DataFrame): The input data frame.
- `group_list` (list of str): The list of groups to be included in the test.

**Returns:**

- DataFrame: A dataframe containing the results of the DESeq2 test.

### `get_stats_tukey_test(self, taxon_name, func_name)` <a name="get_stats_tukey_test"></a>
Performs a Tukey's test and returns the results.

**Parameters:**

- `taxon_name` (str): The name of the taxon.
- `func_name` (str): The name of the function.

**Returns:**

- DataFrame: A dataframe containing the results of the Tukey's test.

### `set_multi_tables(self, level, func_threshold, normalize_method, transform_method, outlier_detect_method, outlier_handle_method, outlier_handle_by_group, batch_list, processing_order)` <a name="set_multi_tables"></a>
Sets multiple tables for further analysis.

**Parameters:**

- `level` (str): The taxonomic level to consider.
- `func_threshold` (float): The function threshold to use.
- `normalize_method` (str): The method to use for normalization.
- `transform_method` (str): The method to use for transformation.
- `outlier_detect_method` (str): The method to use for outlier detection.
- `outlier_handle_method` (str): The method to use for handling outliers.
- `outlier_handle_by_group` (bool): Whether to handle outliers by group.
- `batch_list` (list of str): The list of batches.
- `processing_order` (list of str): The order of processing steps.

**Returns:**

- None

### `check_attributes(self)` <a name="check_attributes"></a>
Checks which attributes are set and returns them.

**Returns:**

- dict: A dictionary containing the set attributes.

### `get_current_time(self)` <a name="get_current_time"></a>
Returns the current time.

**Returns:**

- str: The current time in the format "yyyy-mm-dd hh:mm:ss".
