# Version: 1.88.6
## Date: 2024-01-15
### Changes:
- Fixed: the QSplashScreen doesn't colse after update.
- Add: Add changelog display. when new version avaliable.

# Version: 1.88.7
## Date: 2024-01-15
### Changes:
- restrucetd: move all update fucntions to a signal Class file

# Version: 1.88.8
## Date: 2024-01-15
### Changes:
- added: split the seeting of show all labels for heatmap to X-Aixs, Y-Aixs separately

# Version: 1.88.9
## Date: 2024-01-16
### Changes:
- Fixed: rollback the function of hide and show "gridLayout_top_heatmap_plot" to make the "comboBox_top_heatmap_table" hide work

# Version: 1.89.0
## Date: 2024-01-16
### Changes:
- New: Create a "GenericThread" Class for runing function with another thread so and showing output
- Remove: Removed all specific QThread Class due to no longer need.
- Change: Changed the way to call Database Related functions.


# Version: 1.89.1
## Date: 2024-01-16
### Changes:
- Fixed: Use "with ThreadPoolExecutor() as executor:"  replaced "with multiprocessing.Pool() as pool:" in build_id2annotation_db to avoid restart the splash logo.
- Change: Changed the output windows deafaul size as 1/2 screen size.


# Version: 1.89.2
## Date: 2024-01-17
### Changes:
- Change: Changed the progress_text show in one line in output window.


# Version: 1.89.3
## Date: 2024-01-17
### Changes:
- Fixed: Fixed the bug of when set TaxaFuncAnalyzer failed, the button doesn't enable again.
  
# Version: 1.89.4
## Date: 2024-01-17
### Changes:
- Change: Use ThreadPoolExecutor to run the peptide to TaxaFunc Annotator to speed up.
- Change: Set default file name as 'TaxaFunc.tsv' for the result of TaxaFunc Annotator in file window.

# Version: 1.89.5
## Date: 2024-01-17
### Changes:
- Change: When meta table is not provided, try to use sample name as group, if sample name start with "Intensity".


# Version: 1.89.6
## Date: 2024-01-17
### Changes:
- Change: Add a columun as group "NA" to meta table, when meta table is not provided.

# Version: 1.89.7
## Date: 2024-01-17
### Changes:
- New: Added a option to plot taxa number with a peptide threshold in data overview part.


# Version: 1.89.8
## Date: 2024-01-18
### Changes:
- Change: Add "All Taxa", "All Functions", etc. by default when swith table type.

# Version: 1.90.0
## Date: 2024-01-20
### Changes:
- New: 
- 1. Add self.peptide_col_name, self.protein_col_name to class TaxaFuncAnalyzer to enable set the protein and peptide colnmun names of provided data frame.
- 2. Add new function to sum peptide intensity to protein intensity, include method='[razor','anti-razor'], rank by proteins count or sahred, sum by all samples or by each sample.
- Change:
- Changed the parameters to call the _data_preprocess.

# Version: 1.90.1
## Date: 2024-01-21
### Changes:
- New: Add Protein table to GUI enable to stats it.
- Fix: Fixed function get_stats_mean_df_by_group() when input df contain col does not from sample_list