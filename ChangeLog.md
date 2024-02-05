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

# Version: 1.90.3
## Date: 2024-01-21
### Changes:
- Change: restructure SumProteinIntensity class
- New: Add new ranking method for protein: unique_counts


# Version: 1.90.4
## Date: 2024-01-22
### Changes:
- Fix: Fixed the bug of get tables when protein table dose not exist


# Version: 1.91.0
## Date: 2024-01-22
### Changes:
- New: Add a function to plot sunburst for taxa

# Version: 1.91.1
## Date: 2024-01-23
### Changes:
- Change: 1. Change the combobox in Annotator to enable drag a folder. 2. Changed the default ordre of data preprossing.

# Version: 1.91.2
## Date: 2024-01-23
### Changes:
- Change: Add a signal and slot to TableView get and update self.last_path.

# Version: 1.91.3
## Date: 2024-01-23
### Changes:
- New: Add Control-Group Test

# Version: 1.91.3
## Date: 2024-01-23
### Changes:
- Change: Change the function of "LiKE".

# Version: 1.91.5
## Date: 2024-01-24
### Changes:
- Change: Reverse the order of Deseq2. use Group2/Group1

# Version: 1.92.0
## Date: 2024-01-24
### Changes:
- New: Add secret function.
- Change: add option of cluster method for cross heatmap.

# Version: 1.92.1
## Date: 2024-01-24
### Changes:
- Fix: Fixed the bug of when plot alpha diversity, the label of y-axis is too much digits.

# Version: 1.92.2
## Date: 2024-01-25
### Changes:
- Fix: Fixed the bug of when plot 3 level heatmap, the col cluster option is not work.


# Version: 1.92.3
## Date: 2024-01-25
### Changes:
- Change: Changed layout position of Corss Heatmap options.
- New: Add option to plot heatmap with 3 levels deseq2 result.

# Version: 1.92.4
## Date: 2024-01-25
### Changes:
- Change: Changed the col color for heatmap to avoid the color is too light.

# Version: 1.92.5
## Date: 2024-01-25
### Changes:
- Change: Enable rename taxa for get matrix at taxa-func part.

# Version: 1.93.0
## Date: 2024-01-26
### Changes:
- New: Add a function to plot sankey diagram for taxa-func and taxa at basic part.

# Version: 1.93.1
## Date: 2024-01-26
### Changes:
- Fix: Fixed the bug of when plot top heatmap for taxa-func, the col and row cluster option raise error.

# Version: 1.93.2
## Date: 2024-01-26
### Changes:
- New: Add a condition option for Deseq2.


# Version: 1.93.3
## Date: 2024-01-26
### Changes:
- Fix: Fixed the group list selection bug of Corss Group Condition Test.

# Version: 1.93.4
## Date: 2024-01-27
### Changes:
- Fix: Fixed bugs for init  group box
- Changed: the parameters of the pca plot

# Version: 1.93.5
## Date: 2024-01-27
### Changes:
- Fix: Fixed bugs of GUI when call dese2 function in condition.


# Version: 1.93.6
## Date: 2024-01-27
### Changes:
- Change: Changed the parameters of batch effect remove function. use batch meta replace batch list.

# Version: 1.93.8
## Date: 2024-01-27
### Changes:
- Fix: Fixed the bug of when remove batch effect after sum, while the datafram is less than 2 rows, the program will raise error. 

# Version: 1.94.0
## Date: 2024-01-29
### Changes:
- New: Added Conidtion Option for each part.
- Change: improved the structure of the code.

# Version: 1.94.1
## Date: 2024-01-29
### Changes:
- Change: improved the UI of Button in heatmap part.

# Version: 1.94.2
## Date: 2024-01-29
### Changes:
- New: added theme option for basic plot.

# Version: 1.94.3
## Date: 2024-01-29
### Changes:
- Fix: Fixed the bug of when plot TUkeyHSD for taxa-func.
- New: Add a star in the plot of TukeyHSD.
- Change: Reset the default theme to when create a new object.

# Version: 1.94.5
## Date: 2024-01-30
### Changes:
- Change: Added a option to enable user to add or remove the group name form the sample name when plot.

# Version: 1.94.6
## Date: 2024-01-30
### Changes:
- Fix: Bugs fixed: plot pca 3d
- New: Add a option to copy a column to clipboard in table view.


# Version: 1.94.9
## Date: 2024-01-31
### Changes:
- New: added a option to show or hide the legend and title in the basic sankey plot.
- New: added default name for the output file of JS plot.


# Version: 1.94.10
## Date: 2024-01-31
### Changes:
- Fix: Fixed the bug of when restore the TaxaFunc Object, the dataoverview part doesn't update the data.

# Version: 1.94.11
## Date: 2024-01-31
### Changes:
- Fix: Fixed the bug of when plot sankey for Deseq2, the plot raise error.


# Version: 1.94.12
## Date: 2024-01-31
### Changes:
- New: sub_meta support to plot scatter plot and box plot.

# Version: 1.95.1
## Date: 2024-02-01
### Changes:
- New: Add color for box plot.

# Version: 1.95.2
## Date: 2024-02-02
### Changes:
- Fix: Fixed the bug of when plot box plot, when the group number is more than 10, the error will raise.

# Version: 1.96.0
## Date: 2024-02-03
### Changes:
- New: Add a logWindow to show the process when run the long time function.


# Version: 1.96.3
## Date: 2024-02-05
### Changes:
- Fix: Fixed the bug of when create a new object, the plot of taxa number will show the old data in the widget.