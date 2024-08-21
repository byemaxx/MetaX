# Version: 1.111.4
## Date: 2024-08-21
### Changes:
- New: Added rotation option for the x-axis and y-axis of the heatmap plot.

# Version: 1.111.3
## Date: 2024-08-21
### Changes:
- New: Added protein_id as a function to the OTF table, only keep the first protein_id as the function.

# Version: 1.111.2
## Date: 2024-08-21
### Changes:
- Fix: Fixed the bug when restore the object, the seetings was not restored completely.


# Version: 1.111.1
## Date: 2024-08-21
### Changes:
- Fix: Fixed the bug of spliting the function items, the redundant items were not sumed.



# Version: 1.111.0
## Date: 2024-08-20
### Changes:
- New: Added a option to split the items contain multiple functions to multiple items when set OTF table.


# Version: 1.110.1
## Date: 2024-08-20
### Changes:
- Fix: Fixed the bug of sum protein by anti-razor method.
- Change: Changed the default color of the heatmap plot to make the color more clear.


# Version: 1.110.0
## Date: 2024-08-12
### Changes:
- Fix: 1. Fixed the group order was not correct in the title of the volcano plot. 2. col scale bug when plot the basic heatmap.
- Change: 1. Enable alpha/beta divversity for all type of tables. 2. Only asiign peptide to one protein rather than sahre the intensity when sum peptide to protein by razor method.


# Version: 1.109.12
## Date: 2024-08-10
### Changes:
- Fix: Fixed the function table didn't filter by taxa level.

# Version: 1.109.11
## Date: 2024-08-10
### Changes:
- Fix: Fixed the scale method and color bar of heatmap for Cross Test result table.

# Version: 1.109.10
## Date: 2024-08-9
### Changes:
- Fix: Fixed the of test result table, the t-statistic was reversed.
- New: adde z-score for heatmap scale.


# Version: 1.109.9
## Date: 2024-08-7
### Changes:
- Fix: Fixed the bug when restore the object, some cross_test top table was added to the GUI by wrong.
- Change: Changed the "pixel_ratio" from 2 to 3 for the HTML plot to make the plot more clear.


# Version: 1.109.8
## Date: 2024-08-1
### Changes:
- Fix: Fixed title of the static volcano plot.
- New: added theme option for the static volcano plot.


# Version: 1.109.7
## Date: 2024-07-31
### Changes:
- Change: Optimized the volcano plot.

# Version: 1.109.6
## Date: 2024-07-31
### Changes:
- Change: Optimized the Sankey plot.


# Version: 1.109.6
## Date: 2024-07-31
### Changes:
- New: Added a checkbox to enable user to plot 2D or 3D bar plot for the baisc plot part with sub meta.


# Version: 1.109.5
## Date: 2024-07-25
### Changes:
- Fix: Fixed the bug of when add taxa-functions list to plot, the "<>" was not correctly recognized. 

# Version: 1.109.4
## Date: 2024-07-24
### Changes:
- Fix: Fixed the size of group box in the Taxa-Functions Network plot was too small to show the content.


# Version: 1.109.3
## Date: 2024-07-24
### Changes:
- Change: Optimized the UI of plot settings.


# Version: 1.109.2
## Date: 2024-07-23
### Changes:
- Fix: Fixef the bug of data preprossing, when the 'sum' method was selected for normalization, the program will raise error.


# Version: 1.109.1
## Date: 2024-07-23
### Changes:
- New: Added a function to plot the heatmap of the correlation of the taxa, functions, taxa-functions items.
- Fix: Fixed a bug of when plot the taxa-functions network.
- Change: Changed the sankey plot for intensity, split samples to different groups to show.


# Version: 1.109.0
## Date: 2024-07-22
### Changes:
- Change: Changed the layout of the main window to make the GUI more user-friendly and clear.


# Version: 1.108.7
## Date: 2024-07-14
### Changes:
- Change: Optimized Peptide Annotator, changed them to class method for better performance.


# Version: 1.108.6
## Date: 2024-07-11
### Changes:
- Change: Optimized file structure and code structure, make easlier to install and run the MetaX by pip or conda.


# Version: 1.108.5
## Date: 2024-07-11
### Changes:
- Fix: Fixed the Settting window was not able to minimize (Not perfect yet, need to be fixed in the future).

# Version: 1.108.2
## Date: 2024-07-08
### Changes:
- Fix: Fixed the bug of when int number in the meta table, the protential error will raise.


# Version: 1.108.1
## Date: 2024-06-27
### Changes:
- New: Add Sub Meta option for the basic Heatmap plot.


# Version: 1.108.0
## Date: 2024-06-27
### Changes:
- New: Enable multiple selection for the in condition group box.

# Version: 1.107.8
## Date: 2024-06-26
### Changes:
- Change: 
- 1.Use the heap as the default data structure to apply razor method to sum peptide intensity to protein intensity.
- 2.Changed the update message to a dialog window to show the update message to avoid the update message is too long to show in the message box.

# Version: 1.107.7
## Date: 2024-06-24
### Changes:
- Change: Changed the method of summing peptiede intensity to protein intensity, changed the method "razor" to same as MaxQuant, and added a new method "rank".

# Version: 1.107.6
## Date: 2024-06-19
### Changes:
- New: added an option in Settings to enable user to set the color of the theme (white or dark) of the HTML plot.


# Version: 1.107.5
## Date: 2024-06-18
### Changes:
- Fix: Fixed the bug of when plot the Taxa-Functions Network, the fcous list items which are not linked to any other items were not removed.
- Change: Changed the default label width of the Taxa-Functions Network plot to 300 characters, then the label will be broken into multiple lines if the label is too long.

# Version: 1.107.4
## Date: 2024-06-17
### Changes:
- Change: Set the HTML plot(e.g. bar, sankey, sunburst, network) as the dark theme when the MetaX theme is dark.

# Version: 1.107.3
## Date: 2024-06-16
### Changes:
- Change: Co-expression Network plot: hide the dots if no edge connected to it.


# Version: 1.107.2
## Date: 2024-06-16
### Changes:
- New: Added an option in 'Help' menu to open the online Tutorial page.
- Change: Co-expression Network plot: Use the corelation value as the weight of the edge, and improve the layout of the plot.
- Fix: Fixed the bug of when plot the Taxa-Functions Network, the shape setting was not work withotu focus list.

# Version: 1.107.1
## Date: 2024-06-16
### Changes:
- New: Added more options for the Taxa-Functions Network plot, including the color, label, layout, and edge width. etc.

# Version: 1.107.0
## Date: 2024-06-15
### Changes:
- New: MetaX now supports make the OTFs Table from the MetaLab v2.3 MaxQuant output file.

# Version: 1.106.1
## Date: 2024-06-09
### Changes:
- New: Added the linkages method and linkage distance for the heatmap of corelation plot.

# Version: 1.106.0
## Date: 2024-06-09
### Changes:
- New: Added a parameter in Settting to enable user to set the linkages method and linkage distance for the heatmap plot.(removed some metrices due to when the data has zero, the linkage will raise error.)

# Version: 1.105.4
## Date: 2024-06-05
### Changes:
- Fix: Fixed the theme doesn't work for data overview part when figuer emebed in the GUI.

# Version: 1.105.3
## Date: 2024-05-29
### Changes:
- Fix: Fixed the bug of MetaX Updater.

# Version: 1.105.2
## Date: 2024-05-28
### Changes:
- New: Added a setting window to enable user to update to Beta version of MetaX.
- Change: updated the cookbook.

# Version: 1.105.1
## Date: 2024-05-25
### Changes:
- Change: Optimized the color assignment for Sankey, and Sunburst plot to improve the aesthetics of the figures.

# Version: 1.105.0
## Date: 2024-05-24
### Changes:
- New: Added a sub_meta option for the basic plot for 3D bar plot.
- Fix: Fixed the bug of when plot bar, the option of show all labels was not work.

# Version: 1.104.5
## Date: 2024-05-23
### Changes:
- Change: Optimized the color assignment to improve the aesthetics of the figures.

# Version: 1.104.4
## Date: 2024-05-21
### Changes:
- Change: Removed the font_size option for the heatmap plot to avoid the font size is too small when the heatmap size is large.


# Version: 1.104.3
## Date: 2024-05-19
### Changes:
- Change: Changed the "Preferred_name" to "Gene" in the OTF annotation table and updated the example data.


# Version: 1.104.2
## Date: 2024-05-19
### Changes:
- Fix: Fixed the issue of example data loss after update.


# Version: 1.104.1
## Date: 2024-05-18
### Changes:
- Change: Changed the figure title to specific taxa level or function name for the basic plot part.


# Version: 1.104.0
## Date: 2024-05-15
### Changes:
- Fix: Fixed the bug of when NaN in the table, the data preprossing will remove all the rows with NaN, and the NaN will be replaced by "-" after Peptide Annotator.
- New: Add a method [Missing-Value] to detect the missing value as outlier.


# Version: 1.103.3
## Date: 2024-05-08
### Changes:
- Fix: Fixed the bug of when add a list to plot, the order will be changed by set().


# Version: 1.103.2
## Date: 2024-05-02
### Changes:
- Change: Changed the update method to replace the example data.

# Version: 1.103.1
## Date: 2024-05-01
### Changes:
- Fix: Fixed the bug of when update the software, the example data was removed.

# Version: 1.103.0
## Date: 2024-05-01
### Changes:
- Change: Changed the method of update as Github server.


# Version: 1.102.11
## Date: 2024-04-26
### Changes:
- Fix: Fixed the bug of when select in condition, the add top and plot function was not filtered.


# Version: 1.102.10
## Date: 2024-04-18
### Changes:
- Change: Changed the default color in basic plot part, make the color follow the theme.


# Version: 1.102.9
## Date: 2024-04-18
### Changes:
- Fix: Fixed the bug of when plot the bar plot of number, the sub meta was not correct.
- Fix: Fixed the bug of when plot the box plot, the sub meta didn't work.


# Version: 1.102.8
## Date: 2024-04-18
### Changes:
- Fix: Fixed the bug of when plot the bar plot of number, the sub meta was not work.


# Version: 1.102.7
## Date: 2024-04-16
### Changes:
- New: Add a user agreement when open the software at the first time.


# Version: 1.102.6
## Date: 2024-04-09
### Changes:
- Fix: Fixed the bug of when get table in basic plot part, the rename sample name was not work.


# Version: 1.102.5
## Date: 2024-04-06
### Changes:
- Fix: Fixed the bug of when plot the cross heatmap, the tight layout raise error.


# Version: 1.102.4
## Date: 2024-04-05
### Changes:
- Fix: Fixed the bug of when plot the 2D PCA plot and beta diversity plot, the transparency was not work for adjusted lines.
- Change: Changed the default parameters for adjust labels in the 2D PCA plot and beta diversity plot.



# Version: 1.102.3
## Date: 2024-04-05
### Changes:
- New: add an option to set the dot size for the 2D PCA plot and beta diversity plot.


# Version: 1.102.2
## Date: 2024-04-05
### Changes:
- Change: Changed the alpha value of the color for the PCA plot and beta diversity plot to 0.9 to make the color more clear.


# Version: 1.102.1
## Date: 2024-04-04
### Changes:
- Fix: Fixed the bug of when plot the samples in basic plot part, the order was not correct.
- Fix: Fixed the bug of when plot samples of alpha diversity, the rename sample name was not work.
- New: re-strucutre the code of the generate the distince color and set a random seed to make the color stable.


# Version: 1.102.0
## Date: 2024-03-31
### Changes:
- New: Add a option to set the number of legend cols for the basic plot.
- Fix: Fixed the bug of when plot the bar of number, the rename sample name was not work.


# Version: 1.101.10
## Date: 2024-03-22
### Changes:
- Fix: 1. Fixed the toolbox for echarts plot was show title as Chinese. 2. Fixed the bug of when save the plot in HTML, the background color was black.


# Version: 1.101.9
## Date: 2024-03-20
### Changes:
- Fix: Fixed the bug of calculate the number of legend cols for the PCA plot and beta diversity plot when using sub meta.


# Version: 1.101.8
## Date: 2024-03-15
### Changes:
- Fix: Fixed the bug of save and restore MetaX object, the combobox of the table was not updated.


# Version: 1.101.7
## Date: 2024-03-15
### Changes:
- Fix: Fixed the bug of when the group-control test is running, the user changed the meta, the program will raise error.
- Change: Optimized the tight layout of the heatmap plot.


# Version: 1.101.6
## Date: 2024-03-15
### Changes:
- Change: 1. Optimize the dot size for the 2D PCA and beta diversity plot and volcano plot. 2. Changed the default size of the web plot.
- New: Add an option to plot box by group or by sample.
- Fix: Fixed the bug when restore the object, the table nanem was added to GUI while the object doesn't have the table.


# Version: 1.101.5
## Date: 2024-03-13
### Changes:
- Change: 1. Updated the Example data. 2. Updated the cookbook.
- New: 1.Added a result table after runnning the Alpha Diversity and Beta Diversity. 2. Added a function to search items when add a list to plot.


# Version: 1.101.4
## Date: 2024-03-12
### Changes:
- Change: Changed the table names: taxa-func -> taxa-functions, and other names to Plural form.
- Fix: Fixed the bug of update the table name in T-test and ANOVA part.


# Version: 1.101.3
## Date: 2024-03-11
### Changes:
- New: Add an option to set font size for the trends plot.



# Version: 1.101.2
## Date: 2024-03-11
### Changes:
- Fix: 1. Fixed the bug of wrong label of color bar in the heatmap plot. 2. Fixed the bug when table changed but GUI doesn't update.


# Version: 1.101.1
## Date: 2024-03-11
### Changes:
- Fix: Fixed the bug of wrong tbale names was created by last version.
- Change: Released the Dunnett's test for the Group-Contronl Test.


# Version: 1.101.0
## Date: 2024-03-10
### Changes:
- New: Add a function to allow user to use any table to do basic stats and plot.


# Version: 1.100.7
## Date: 2024-03-10
### Changes:
- Fix: Fixed the bug when select other taxa levle except "Genome", the empty annotation was not removed.


# Version: 1.100.6
## Date: 2024-03-10
### Changes:
- Fix: Fixed the bug when select "Speciec" level for multi-tables, the 's__' was not removed.


# Version: 1.100.5
## Date: 2024-03-08
### Changes:
- Fix: Fixed the bug of get distinct color for basic plot.


# Version: 1.100.4
## Date: 2024-03-07
### Changes:
- Update_lib: Updated the [pyecharts] to [2.0.5].
- Change: 1. Changed the Sunburst plot labels to avoid overlap. 2. Changed some settings of the plot by pyecharts to fit the new version.


# Version: 1.100.3
## Date: 2024-03-07
### Changes:
- Change: For HTML plot, moved all tooltips to the left bottom.
- Fix: Fixed some wrong spellings in GUI.


# Version: 1.100.1
## Date: 2024-03-06
### Changes:
- Change: 1. changed the "Genome" as default level for the taxa level. 2. remove the hide genome bar for "plot_taxa_number" when the count is equal to species count.


# Version: 1.100.0
## Date: 2024-03-05
### Changes:
- New: 1. Add a genome level to taxa level as the last level of the taxa. 2. Add an option to set font size for the plot of the data overview.
- Change: 1. changed bar plot to pie chart for the "Number of identified peptides in different taxa level". 2. Set the dot siize of the 2D PCA and beta diversity plot as width*height.


# Version: 1.99.6
## Date: 2024-03-04
### Changes:
- New: Add font size option for the plot of the deseq2 result.
- Change: Integrated size of pyecharts plots and seaborn plots as screen resolution divided by 120


# Version: 1.99.5
## Date: 2024-03-04
### Changes:
- Change: Optimize the bar plot and trends plot: 1. set the ylim as 100 when plot percentage. 2. add a buton to scroll the legend if the legend is too long.
- Fix: Fixed the bug of when plot the trends, tight layout doesn't work.


# Version: 1.99.4
## Date: 2024-03-02
### Changes:
- Change: Optimize the bar plot, decrease the gap between the bars to 5% of the bar width.
- New: Add a function to plot the percentage of each column in the bar plot.


# Version: 1.99.3
## Date: 2024-03-01
### Changes:
- Change: Optimize the color bar of the heatmap. set the label to the left of the color bar.


# Version: 1.99.2
## Date: 2024-03-01
### Changes:
- Change: Optimize the restore function of the object.


# Version: 1.99.1
## Date: 2024-03-01
### Changes:
- Change: Changed the figures of the help information of function treshold setting and the LCA threshold setting.


# Version: 1.99.0
## Date: 2024-02-28
### Changes:
- New: Add a function to save current MetaX object to a file, and load it from a file.


# Version: 1.98.0
## Date: 2024-02-22
### Changes:
- New: Add a function of right click menu for heatmap combo box to plot the all colormap.


# Version: 1.97.6
## Date: 2024-02-22
### Changes:
- New: Add a function to plot the mean for each group in the basic heatmap plot part.


# Version: 1.97.5
## Date: 2024-02-21
### Changes:
- Fix: Fixed the bug of when plot sankey while the combox of plot peptide is checked, the plot will raise error.


# Version: 1.97.4
## Date: 2024-02-21
### Changes:
- Fix: Fixed the bug of when calculate the taxa number in each level with threshold, the "s__nan" was not removed.


# Version: 1.97.3
## Date: 2024-02-15
### Changes:
- Fix: Fixed the bug of when close the log window by user, the runing status is not reset.


# Version: 1.97.2
## Date: 2024-02-14
### Changes:
- hange: Changed the number of legned cols: (group_num//30 + 1), for basic plot.



# Version: 1.97.1
## Date: 2024-02-12
### Changes:
- New: Add a new function to plot the Treemap for taxa.


# Version: 1.97.0
## Date: 2024-02-12
### Changes:
- New: Add a new function to plot the number of taxa and functions for each sample or each group.


# Version: 1.96.8
## Date: 2024-02-08
### Changes:
- New: Add an option to plot the data overview with theme.



# Version: 1.96.6
## Date: 2024-02-07
### Changes:
- Fix: Resolved an issue where error messages were not displayed when an error occurred in the background thread.
- New: Add a function to detect duplicate row in the meta table.


# Version: 1.96.5
## Date: 2024-02-07
### Changes:
- Change: Add "ACE" to alpha diversity plot.


# Version: 1.96.4
## Date: 2024-02-06
### Changes:
- Change: Add table restore function to restore the table when the object is restored.


# Version: 1.96.3
## Date: 2024-02-05
### Changes:
- Fix: Fixed the bug of when create a new object, the plot of taxa number will show the old data in the widget.



# Version: 1.96.0
## Date: 2024-02-03
### Changes:
- New: Add a logWindow to show the process when run the long time function.



# Version: 1.95.2
## Date: 2024-02-02
### Changes:
- Fix: Fixed the bug of when plot box plot, when the group number is more than 10, the error will raise.


# Version: 1.95.1
## Date: 2024-02-01
### Changes:
- New: Add color for box plot.


# Version: 1.94.12
## Date: 2024-01-31
### Changes:
- New: sub_meta support to plot scatter plot and box plot.


# Version: 1.94.11
## Date: 2024-01-31
### Changes:
- Fix: Fixed the bug of when plot sankey for Deseq2, the plot raise error.



# Version: 1.94.10
## Date: 2024-01-31
### Changes:
- Fix: Fixed the bug of when restore the TaxaFunc Object, the dataoverview part doesn't update the data.


# Version: 1.94.9
## Date: 2024-01-31
### Changes:
- New: added a option to show or hide the legend and title in the basic sankey plot.
- New: added default name for the output file of JS plot.



# Version: 1.94.6
## Date: 2024-01-30
### Changes:
- Fix: Bugs fixed: plot pca 3d
- New: Add a option to copy a column to clipboard in table view.



# Version: 1.94.5
## Date: 2024-01-30
### Changes:
- Change: Added a option to enable user to add or remove the group name form the sample name when plot.


# Version: 1.94.3
## Date: 2024-01-29
### Changes:
- Fix: Fixed the bug of when plot TUkeyHSD for taxa-func.
- New: Add a star in the plot of TukeyHSD.
- Change: Reset the default theme to when create a new object.


# Version: 1.94.2
## Date: 2024-01-29
### Changes:
- New: added theme option for basic plot.


# Version: 1.94.1
## Date: 2024-01-29
### Changes:
- Change: improved the UI of Button in heatmap part.


# Version: 1.94.0
## Date: 2024-01-29
### Changes:
- New: Added Conidtion Option for each part.
- Change: improved the structure of the code.


# Version: 1.93.8
## Date: 2024-01-27
### Changes:
- Fix: Fixed the bug of when remove batch effect after sum, while the datafram is less than 2 rows, the program will raise error. 


# Version: 1.93.6
## Date: 2024-01-27
### Changes:
- Change: Changed the parameters of batch effect remove function. use batch meta replace batch list.


# Version: 1.93.5
## Date: 2024-01-27
### Changes:
- Fix: Fixed bugs of GUI when call dese2 function in condition.



# Version: 1.93.4
## Date: 2024-01-27
### Changes:
- Fix: Fixed bugs for init  group box
- Changed: the parameters of the pca plot


# Version: 1.93.3
## Date: 2024-01-26
### Changes:
- Fix: Fixed the group list selection bug of Corss Group Condition Test.


# Version: 1.93.2
## Date: 2024-01-26
### Changes:
- New: Add a condition option for Deseq2.



# Version: 1.93.1
## Date: 2024-01-26
### Changes:
- Fix: Fixed the bug of when plot top heatmap for taxa-func, the col and row cluster option raise error.


# Version: 1.93.0
## Date: 2024-01-26
### Changes:
- New: Add a function to plot sankey diagram for taxa-func and taxa at basic part.


# Version: 1.92.5
## Date: 2024-01-25
### Changes:
- Change: Enable rename taxa for get matrix at taxa-func part.


# Version: 1.92.4
## Date: 2024-01-25
### Changes:
- Change: Changed the col color for heatmap to avoid the color is too light.


# Version: 1.92.3
## Date: 2024-01-25
### Changes:
- Change: Changed layout position of Corss Heatmap options.
- New: Add option to plot heatmap with 3 levels deseq2 result.


# Version: 1.92.2
## Date: 2024-01-25
### Changes:
- Fix: Fixed the bug of when plot 3 level heatmap, the col cluster option is not work.



# Version: 1.92.1
## Date: 2024-01-24
### Changes:
- Fix: Fixed the bug of when plot alpha diversity, the label of y-axis is too much digits.


# Version: 1.92.0
## Date: 2024-01-24
### Changes:
- New: Add secret function.
- Change: add option of cluster method for cross heatmap.


# Version: 1.91.5
## Date: 2024-01-24
### Changes:
- Change: Reverse the order of Deseq2. use Group2/Group1


# Version: 1.91.3
## Date: 2024-01-23
### Changes:
- Change: Change the function of "LiKE".


# Version: 1.91.3
## Date: 2024-01-23
### Changes:
- New: Add Control-Group Test


# Version: 1.91.2
## Date: 2024-01-23
### Changes:
- Change: Add a signal and slot to TableView get and update self.last_path.


# Version: 1.91.1
## Date: 2024-01-23
### Changes:
- Change: 1. Change the combobox in Annotator to enable drag a folder. 2. Changed the default ordre of data preprossing.


# Version: 1.91.0
## Date: 2024-01-22
### Changes:
- New: Add a function to plot sunburst for taxa


# Version: 1.90.4
## Date: 2024-01-22
### Changes:
- Fix: Fixed the bug of get tables when protein table dose not exist



# Version: 1.90.3
## Date: 2024-01-21
### Changes:
- Change: restructure SumProteinIntensity class
- New: Add new ranking method for protein: unique_counts



# Version: 1.90.1
## Date: 2024-01-21
### Changes:
- New: Add Protein table to GUI enable to stats it.
- Fix: Fixed function get_stats_mean_df_by_group() when input df contain col does not from sample_list


# Version: 1.90.0
## Date: 2024-01-20
### Changes:
- New: 
- 1. Add self.peptide_col_name, self.protein_col_name to class TaxaFuncAnalyzer to enable set the protein and peptide colnmun names of provided data frame.
- 2. Add new function to sum peptide intensity to protein intensity, include method='[razor','anti-razor'], rank by proteins count or sahred, sum by all samples or by each sample.
- Change:
- Changed the parameters to call the _data_preprocess.


# Version: 1.89.8
## Date: 2024-01-18
### Changes:
- Change: Add "All Taxa", "All Functions", etc. by default when swith table type.


# Version: 1.89.7
## Date: 2024-01-17
### Changes:
- New: Added a option to plot taxa number with a peptide threshold in data overview part.



# Version: 1.89.6
## Date: 2024-01-17
### Changes:
- Change: Add a columun as group "NA" to meta table, when meta table is not provided.


# Version: 1.89.5
## Date: 2024-01-17
### Changes:
- Change: When meta table is not provided, try to use sample name as group, if sample name start with "Intensity".



# Version: 1.89.4
## Date: 2024-01-17
### Changes:
- Change: Use ThreadPoolExecutor to run the peptide to TaxaFunc Annotator to speed up.
- Change: Set default file name as 'TaxaFunc.tsv' for the result of TaxaFunc Annotator in file window.


# Version: 1.89.3
## Date: 2024-01-17
### Changes:
- Fixed: Fixed the bug of when set TaxaFuncAnalyzer failed, the button doesn't enable again.
  

# Version: 1.89.2
## Date: 2024-01-17
### Changes:
- Change: Changed the progress_text show in one line in output window.



# Version: 1.89.1
## Date: 2024-01-16
### Changes:
- Fixed: Use "with ThreadPoolExecutor() as executor:"  replaced "with multiprocessing.Pool() as pool:" in build_id2annotation_db to avoid restart the splash logo.
- Change: Changed the output windows deafaul size as 1/2 screen size.



# Version: 1.89.0
## Date: 2024-01-16
### Changes:
- New: Create a "GenericThread" Class for runing function with another thread so and showing output
- Remove: Removed all specific QThread Class due to no longer need.
- Change: Changed the way to call Database Related functions.



# Version: 1.88.9
## Date: 2024-01-16
### Changes:
- Fixed: rollback the function of hide and show "gridLayout_top_heatmap_plot" to make the "comboBox_top_heatmap_table" hide work


# Version: 1.88.8
## Date: 2024-01-15
### Changes:
- added: split the seeting of show all labels for heatmap to X-Aixs, Y-Aixs separately


# Version: 1.88.7
## Date: 2024-01-15
### Changes:
- restrucetd: move all update fucntions to a signal Class file


# Version: 1.88.6
## Date: 2024-01-15
### Changes:
- Fixed: the QSplashScreen doesn't colse after update.
- Add: Add changelog display. when new version avaliable.