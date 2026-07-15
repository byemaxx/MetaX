# MetaX Cookbook

This guidebook is for the MetaX **GUI version**. If you are using the CLI, we recommend reading the [documentation](https://github.com/byemaxx/MetaX/blob/main/Docs/example.ipynb) for instructions on how to use each MetaX module from the command line.

# Overview

**[MetaX](https://github.com/byemaxx/MetaX)** is a novel tool for linking peptide sequences with taxonomic and functional information in **Metaproteomics**. We introduce the ***Operational Taxon-Function (OTF)*** concept to explore microbial roles and interactions ("**who is doing what and how**") within ecosystems. 

MetaX also features <u>statistical modules</u> and <u>plotting tools</u> for analyzing peptides, taxa, functions, proteins, and taxon-function contributions across groups, and can now export recorded GUI analysis steps as runnable workflow notebooks for reproducible downstream use.


![abstract](./MetaX_Cookbook.assets/abstract.png)

# Project Page

Visit **GitHub** to get more information:

[https://github.com/byemaxx/MetaX](https://github.com/byemaxx/MetaX)

# Contents

[TOC]



# Getting Started

- The main window of MetaX

  <img src="./MetaX_Cookbook.assets/main_window.png" alt="main_window"  />

- Click 'Tools Menu' to switch **different modules**

  <img src="./MetaX_Cookbook.assets/tools_menu.png" alt="tools_menu"  />

<br>

# Exploring Data with MetaX

See the **<u>[Preparing Your Data](#preparing-your-data)</u>** section to build the database and annotate peptides to OTFs before starting.

## Module 1. OTF Analyzer

After obtaining the **Operational Taxa-Functions (OTF) Table** using the <u>**[Peptide Annotator](#module-4-peptide-annotator)**</u>, you can perform downstream analysis with the **<u>OTF Analyzer</u>**.

## 1. Data Preparation

**OTFs (Operational Taxa-Functions) Table:** Obtained from the <u>[Peptide Annotator](#module-4-peptide-annotator)</u> module.

**Meta Table:** The first column is sample names, and the other columns represent different groups. If no meta table is provided, meta info will be generated automatically: (1) all samples are in the same group; (2) each sample is a separate group.

**Example Meta Table:**

| samples  | Individuals | Treatment | Sweetener |
| -------- | ----------- | --------- | --------- |
| sample_1 | V1          | Treatment | XYL       |
| sample_2 | V1          | Treatment | XYL       |
| sample_3 | V1          | Treatment | XYL       |
| sample_4 | V1          | Control   | PBS       |
| sample_5 | V1          | Control   | PBS       |
| sample_6 | V1          | Control   | PBS       |

You can load example data by **clicking the button**.

![load_example](./MetaX_Cookbook.assets/load_example.png)

Then, click **Go** to start the analysis.

- **Advanced Settings**
  - ![ad_settings_otf_analyzer](./MetaX_Cookbook.assets/ad_settings_otf_analyzer.png)
  - **Peptide Column Name:** Specifies the column in the OTF table that contains peptide information.
  - **Protein Column Name:** Specifies the column in the OTF table that contains protein information (only required if protein summation is performed in downstream analysis).
  - **Sample Column Prefix:** Identifies the prefix of sample columns to determine intensity columns in the OTF table.
  - **Any Data Mode:** Allows analysis of any table using MetaX, not limited to OTF tables (only partial tool functionality is available).
    - **Customized Table Item Column Name:** Specifies the column containing item names in any data mode. If left empty, the first column will be selected by default.

## 2. Data Overview

The Data Overview provides basic information about your data, such as the number of taxa, functions, and proportions.

- Set the threshold for linked peptides and the differences between them to plot figures.

![data_overview](./MetaX_Cookbook.assets/data_overview.png)

- Select different functions to plot the proportion distribution.

![data_overview_func](./MetaX_Cookbook.assets/data_overview_func.png)

- Filter out samples for downstream analysis.

![data_overview_filter](./MetaX_Cookbook.assets/data_overview_filter.png)

## 3. Set TaxaFunc

![set_multi_table](./MetaX_Cookbook.assets/set_multi_table.png)

### Data Selection

- **Function:** Select a function for downstream analysis (**None** in the list means no function is selected, focusing only on peptides and taxa).

- **Function Filter Threshold:** If a specific function within a protein group of a peptide has the highest proportion, it will be considered the representative function for that peptide. The default threshold is 1.00 (100%).

![FUNC_prop](./MetaX_Cookbook.assets/FUNC_prop.png)

- **Taxa Level:** Select a taxa level for downstream analysis (**Life** in the list means no filtering by taxa, and the following analysis focuses on functions).

- **Peptide Number Threshold:** Only keep taxa, functions, or OTFs that have at least the specified number of peptides.

- **Split Function:** Split the annotations with multi-functions.

  - | KO                  | Intensity |
    | ------------------- | --------- |
    | ko:K00625,ko:K13788 | 10        |

    to

    | KO        | Intensity |
    | --------- | --------- |
    | ko:K00625 | 10        |
    | ko:K13788 | 10        |

    If <u>Share Intensity</u> is checked, the intensity above will be split equally, giving <u>5</u> to each KO.

- **Remove unknown taxa:** Checked by default. When enabled, peptides that are not annotated to the selected taxonomic level will be removed. When unchecked, such peptides will be retained and labeled as *unknown*, for example:

    ```text
    d__Bacteria;p__Firmicutes_A;c__Clostridia;o__Oscillospirales;f__Ruminococcaceae;g__UMGS363;s_
    ```

    to

    ```text
    d__Bacteria;p__Firmicutes_A;c__Clostridia;o__Oscillospirales;f__Ruminococcaceae;g__UMGS363;s_unknown
    ```

- **Create Taxa and Func only from OTFs:**

  - **Without selection (checkbox not checked):**
    - <u>Taxa table:</u> Peptides are filtered based solely on taxa levels, without considering any functional categories.
    - <u>Function table:</u> Peptides are filtered solely by functional categories and thresholds, regardless of their taxa levels.
    - <u>Taxa-Function (OTFs) table:</u> Peptides are filtered by both taxa levels and functional categories simultaneously.
  - **With selection (checkbox checked):**
    - <u>Taxa table:</u> Peptides are filtered by both taxa levels and functional categories simultaneously.
    - <u>Function table:</u> Peptides are filtered by both taxa levels and functional categories simultaneously.
    - <u>Taxa-Function (OTFs) table:</u> Peptides are filtered by both taxa levels and functional categories simultaneously.

### Sum Proteins Intensity

Click **Generate Protein Intensity Table** to sum peptides to proteins if the Protein column is in the original table.

- **Occam's Razor**, **Anti-Razor** and **Rank:** Methods available for inferring shared peptides.
  
  - Razor:
    1. Build a minimal set of proteins to cover all peptides.
    2. For each peptide, choose the protein with the most peptides (if multiple proteins have the same number of peptides, share intensity to them).
  - Anti-Razor:
    - All proteins share the intensity of each peptide.
  - Rank:
    1. Build the rank of proteins.
    2. Choose the protein with a higher rank for the shared peptide.
    
    >Methods to Build Protein Rank:
    >- unique_counts: Use the counts of proteins inferred by unique peptides.
    >- all_count: Use the counts of all proteins.
    >- unique_intensity: Use the intensity of proteins inferred by unique peptides.
    >- shared_intensity: Use the intensity divided by the number of shared peptides for each protein.
    

- **Minimum peptide number per protein:** Filters out proteins that contain fewer peptides than the specified threshold.

### Data preprocessing

- **Quantitative Method:**

  - **<u>Sum</u>**: Sum the peptides intensity directly to Taxa, Functions or OTFs intensity.

  - **<u>DirectLFQ</u>**: Use DirectLFQ to normalize peptides and then estimate intensity using *intensity traces*.

    

- **Outlier handling:**

There are several methods for detecting and handling outliers.

- Two steps will be applied:
  - <u>Outlier Detection:</u> Users can select a method to mark outlier values as NaN. Then the rows `only contain NaN values and 0` will be removed. The remaining NaN values will be handled in the next step.
  - <u>Outlier Handling:</u> Users can choose a method to fill the remaining NaN values.
  



- **Outlier Detection:**

  - **IQR:** In a group, if the value is greater than Q3+1.5\*IQR or less than Q1-1.5\*IQR, the value will be marked as NaN.
  
  - **Missing-Value:** Detect nan values in the data. If a value is nan, it will be marked as a NaN.
  
  - **Half-Zero:** 
  
    ​	Applies to grouped data.
  
    - If more than half of the values in a group are zero, all *non-zero* values are replaced with NaN.
  
    - If fewer than half of the values are zero, all *zero* values are replaced with NaN.
    - If the number of zero and non-zero values is equal, *all* values in the group are replaced with NaN.
  
  - **Zero-Dominant:** 
  
    ​	Applies to grouped data.
  
    - If more than half of the values in a group are zero, all *non-zero* values are replaced with NaN.
    - Otherwise, the group remains unchanged.
  
  - **Zero-Inflated Poisson:** This method is based on the Zero-Inflated Poisson (ZIP) model, which is a type of model that is used when the data contains a lot of zeros, more than what is expected in a standard Poisson model. In this context, the ZIP model is used to detect outliers in the data. The process involves fitting the ZIP model to the data and then predicting the data values. If the predicted value is less than 0.01, then the data point is marked as an outlier (NaN).
  
  - **Negative Binomial:** This method is based on the Negative Binomial model, which is a type of model used when the variance of the data is greater than the mean. Similar to the ZIP method, the Negative Binomial model is fitted to the data and then used to predict the data values. If the predicted value is less than 0.01, then the data point is marked as an outlier (NaN).
  
  - **Z-Score:** Z-score is a statistical measure that tells how far a data point is from the mean in terms of standard deviations. Outliers are often identified as points with Z-scores greater than 2.5 or less than -2.5.
  
  - **Mahalanobis Distance:** Mahalanobis distance measures the distance between a point and a distribution, considering the correlation among variables. Outliers can be identified as points with a Mahalanobis distance that exceeds a certain threshold.

<u>In all methods, you can choose one meta column for outlier detection and another meta column for handling outliers.</u>

- **Outliers Imputation:**

  - **Drop:** Remove peptides that contain any NaN values.

  - **Original:** Keep the remaining NaN values as-is.

  - **Mean**: Outliers will be imputed by the mean.

  - **Median**: Outliers will be imputed by the median.

  - **KNN**: Outliers will be imputed by KNN (K=5). The K-Nearest Neighbors algorithm uses the mean or median of the nearest neighbours to fill in missing values.

  - **Regression**: Outliers will be imputed by using IterativeImputer with regression method. This method uses round-robin linear regression, modelling each feature with missing values as a function of other features.

  - **Multiple**: Outliers will be imputed by using IterativeImputer with multiple imputations method. It uses the IterativeImputer with a specified number (K=5) of the nearest features.

  You can choose outlier imputation by *each group* or by *all samples*.

- **Remove Batch Effect:**

  - Here, you can choose a group as the batch effect and then use [<u>reCombat</u>](https://github.com/BorgwardtLab/reComBat) to handle it.
- **Data Transformation:**

  - Log2, Log10, Square root transformation, Cube root transformation and box-cox.

- **Data Normalization:**

  - **Trace Shifting:** Reframing the Normalization Problem with Intensity traces (inspired by DirectLFQ).
    - Note: If <u>both</u> trace shifting and transformation are applied, *<u>normalization will be done before transformation.</u>*
  
  - Standard Scaling (Z-Score), Min-Max Scaling, Pareto Scaling, Mean centring, and normalization by percentage.
  

<u>If you use Z-Score, Mean centring, or Pareto Scaling for data normalization, the data will be given a minimum offset again to avoid negative values.</u>

- **Drag the item's name** to change the <u>**order**</u> of data preprocessing.

  

**Then, click Go to create a TaxaFunc object for analysis.**

![TaxaFunc_ready](./MetaX_Cookbook.assets/TaxaFunc_ready.png)

Then you can check the tables in the **Table Review** section and export them.

<img src="./MetaX_Cookbook.assets/table_review.png" alt="table_review"  />

<img src="./MetaX_Cookbook.assets/table_review_open_window.png" alt="table_review_open_window"  />



## 4. Basic Stats

### PCA, Correlation and Box Plot

<img src="./MetaX_Cookbook.assets/basic_stats_pca.png" alt="basic_stats_pca" />

You can select <u>**meta**</u> <u>**groups**</u> or <u>**samples**</u> (default: all) to plot **PCA**, **Correlation**, and **Box Plot** for **Taxa, Function, Taxa-Func, Peptide, and Protein** tables.

<img src="./MetaX_Cookbook.assets/pca.png" alt="pca"  />

<img src="./MetaX_Cookbook.assets/pca_3d.png" alt="pca_3d"  />

<img src="./MetaX_Cookbook.assets/correlation.png" alt="correlation"  />

<img src="./MetaX_Cookbook.assets/boxplot.png" alt="boxplot" style="zoom:50%;" />

- **Setting and modifying the plot**

  - Show or hide labels in the figure by checking **Show Labels**.

  - Select **Sub Meta** to plot with two meta columns.

    <img src="MetaX_Cookbook.assets/sub_meta.png" >

  - Change settings in the **PLOT PARAMETER** tab

    <img src="MetaX_Cookbook.assets/basic_setting.png" alt="basic_setting"  />

      

  - Select specific Groups **with condition**

    **For example:** Select PBS, BAS, and other groups **only in** <u>Individual</u> <u>V1</u>.

    <img src="MetaX_Cookbook.assets/group_in_condition.png">

  - Select **specific Samples** to Analysis

    <img src="./MetaX_Cookbook.assets/pca_setting.png" >

      

    <img src="./MetaX_Cookbook.assets/pic_tools_bar.png" alt="image-20230728112747731" style="zoom:80%;" />

- **Number stats**

  - Plot the counts for each table by **groups** or by **samples**.

    <img src="MetaX_Cookbook.assets/basic_number.png" alt="basic_number"  />

- **Taxa Specific**

  - Alpha/Beta Diversity

    <img src="MetaX_Cookbook.assets/alpha_div.png" alt="alpha_div"  />
    <img src="MetaX_Cookbook.assets/beta_div.png" alt="beta_div"  />

  - Sunburst

    <img src="MetaX_Cookbook.assets/sunburst.png" alt="sunburst"  />

  - TreeMap

    <img src="MetaX_Cookbook.assets/treemap.png" alt="treemap"  />

  - Sankey

    <img src="MetaX_Cookbook.assets/basic_sankey.png" alt="basic_sankey">

    


### Heatmap and Bar Plot

<img src="./MetaX_Cookbook.assets/basic_stats_heatmap.png" >

- **Select items (Taxa, Function, Taxa-Func, and Peptide) to plot:**
  - Add **All Taxa**, or select one we are interested in.

<img src="./MetaX_Cookbook.assets/add_to_list.png" alt="add_to_list"  />



- **Add items to Top List:** Select the top items to plot using a statistical method.

  - Clicking <u>filter with threshold</u> filters by the adjusted p-value of ANOVA and T-TEST, and by the adjusted p-value and Log2FC of differential expression results from DESeq2 or Limma (configured on the corresponding page).

  <img src="./MetaX_Cookbook.assets/add_top_list.png" alt="add_top_list"  />

- **Add a list for plotting:**

  - Make sure one row one item

<img src="./MetaX_Cookbook.assets/add_a_list.png" alt="add_a_list"  />





- **Setting:**

  - Change the setting fit for your data.
  - **Rename Samples**: Add group info to each sample name
  - **Rename Taxa**: Only keep the last taxonomic level to reduce to name
  - **Plot Mean**: calculate the mean of each group before plotting
  
  - **Sub Meta:** select a second meta, then combine two meta by mean for Heatmap and 3D bar plot
    <img src="./MetaX_Cookbook.assets/basic_stats_heatmap_seeting.png" >
  
  - View all color maps by right-clicking <u>**Theme**</u>.
    - ![right_click_theme](MetaX_Cookbook.assets/right_click_theme.png)
    <img src="MetaX_Cookbook.assets/all_cmap.png" alt="all_cmap">
  
- **Plot:**

  <img src="./MetaX_Cookbook.assets/heatmap_original.png" alt="heatmap_original"  />

  - **Modify** the pic to fit the window to get the **Perfect picture**:

    <img src="./MetaX_Cookbook.assets/modify_pic.png" alt="modify_pic"  />
    
    <img src="./MetaX_Cookbook.assets/heatmap_fixed.png" alt="heatmap_fixed"  />





- **Bar Plot:**

<img src="./MetaX_Cookbook.assets/basic_stats_bar.png" alt="basic_stats_bar"  />

- **Interactive functions:**

  <img src="./MetaX_Cookbook.assets/basic_stats_bar_setting.png" alt="basic_stats_bar_setting"  />

  - Change to a line plot:

    <img src="./MetaX_Cookbook.assets/basic_stats_bar_to_line.png" alt="basic_stats_bar_to_line"  />

- **3D Bar Plot**

  - Plot 3D bar by selecting a **sub meta**.
  <img src="MetaX_Cookbook.assets/basic_stats_bar_3d.png" alt="basic_stats_bar_3d"  />



### Peptide Query

- Query everything of a peptide

  <img src="./MetaX_Cookbook.assets/peptide_query.png" alt="peptide_query"  />







## 5. Cross Test

### T-TEST

- Select two groups for T-test analysis on **Taxa, Function, Taxa-Func, Peptide, and Protein** tables.

<img src="./MetaX_Cookbook.assets/t_test.png" alt="t_test"/>

### ANOVA-TEST

- Select <u>some groups</u> or <u>all groups</u> to run ANOVA on **Taxa, Function, Taxa-Func, and Peptide** tables.

<img src="./MetaX_Cookbook.assets/anova_test.png" alt="anova_test"/>

### Significant Taxa-Func

- Significant comparison helps identify cases where **<u>taxa show no significant differences between two groups, while their related functions are significantly different</u>**, and vice versa.
- ![Significant_Taxa-Func](MetaX_Cookbook.assets/Significant_Taxa-Func.png)

### Plot Cross Heatmap

- The **results** of the T-test and ANOVA test will appear in a new window.

  <img src="./MetaX_Cookbook.assets/t_test_res.png" alt="t_test_res"/>

  

- Plot Heatmap for results

  - Choose a table to plot a **top differences heatmap** or export **the top table**.

<img src="./MetaX_Cookbook.assets/corss_heatmap_setting.png" alt="corss_heatmap_setting"  />

- Taxa-Func cross heatmap:
  - The orange cells mean in the corresponding function ( X-axis) and Taxa( Y-axis) are significantly different between groups.

<img src="./MetaX_Cookbook.assets/corss_heatmap.png" alt="corss_heatmap"  />

- Func(Taxa) Heatmap:

  - The colour shows the intensity of the significant Func(Taxa) between groups.

  <img src="./MetaX_Cookbook.assets/t_test_heatmap.png" alt="t_test_heatmap"  />

- Significant Taxa-Func Heatmap:

  - The colored tiles represent the taxa which were not significantly different between groups but the related functions were.

### Group-Control TEST

- **Dunnett's Test**

  Set a Group as **"Control"**, then compare all groups to Control

  - **Comparing in Each Condition:** Select a meta such as individual, then compare groups to control in each individual.

- **DESeq2 Test**

  Bingo! You noticed the hidden function of MetaX,  click **Help -> About -> Like** 3 times to unlock the function to compare all groups to control.

  

  - ![group_control_test](./MetaX_Cookbook.assets/group_control_test.png)
  - Result of Dunnett's Test:
    - T- Statistic value shown in the heatmap
    <img src="./MetaX_Cookbook.assets/dunnetts_heatmap.png" alt="dunnetts_heatmap"  />

- **Limma / DESeq2 Group-Control Analysis**

  - After unlocking the differential expression tools, choose **Method** to run either **Limma** or **DESeq2** for group-vs-control comparisons.
  - **Limma** is the default method. It works on log2-style quantitative data. By default, zero values remain numeric zeros; enable **Convert zeros to NaN** only when zeros represent missing values and should be treated as such during preparation.
  - **DESeq2** is intended for raw count-like input. If the current table was transformed earlier, MetaX will try to guide you through safe preparation before running the test.
  - Both methods support optional covariates and the **Comparing in Each Condition** workflow.


### Differential Expression (Limma / DESeq2)

- Select **Method** to run differential expression with **Limma** or **DESeq2**.
- **Limma** is the default method for this page.
- MetaX now uses [<u>InMoose</u>](https://github.com/epigenelabs/inmoose) as the differential expression backend.
- Use **Limma** for log2-transformed quantitative tables, and use **DESeq2** for raw count-style tables.

  

<img src="./MetaX_Cookbook.assets/Differential_Expression.png">

- Select <u>p-adjust</u>, <u>log2FC</u> to plot significant results from either method.

  (**Ultra-Up(Down):** |log2FC| > Max log2FC)

  - Volcano:

    <img src="./MetaX_Cookbook.assets/volcano.png" alt="volcano"/>

  - Sankey:

    - The last node level is the functions linked to each Taxon (when plotting Taxa-Func).
    - Sankey plotting is available for both **DESeq2** and **Limma** result tables on **Taxa** and **Taxa-Func** comparisons.

    <img src="MetaX_Cookbook.assets/taxa_func_sankey.png" alt="taxa_func_sankey" />

- Differential result tables generated from **group-control** analyses can be right-clicked in the table list to:
  - Open them in the **Differential Results Extractor**
  - Generate a **long-format table** for downstream filtering, export, or plotting


### Tukey Test

<img src="./MetaX_Cookbook.assets/tukey_test.png" alt="tukey_test"/>

- **Select a function:** 

  - Test the significant groups in this function.

- **Select a Taxon:** 

  - Test the significant groups in this taxon.

- **Select both function and taxon:** 

  - Test the significant groups in this function and this taxon.

  <img src="./MetaX_Cookbook.assets/taxa_func_linked_only.png" alt="taxa_func_linked_only"  />

  - Show Linked Taxa Only: only shows the taxa linked with the current function in the taxa combo box.

  - Show Linked Func Only: Only shows the functions linked with the current taxon in the function combo box.

    **Do not forget to click <u>Reset Function Taxa List</u> to restore all items after filtering.**

  

- **Tukey result plot:**
  - The dots and lines show the difference in the mean value of the Tukey test

<img src="./MetaX_Cookbook.assets/tukey_plot.png" alt="tukey_plot"  />





## 6. Expression Analysis

### Co-Expression Networks & Heatmap

- Select groups or samples to calculate correlations and plot the network.

<img src="./MetaX_Cookbook.assets/co_network_page.png">

- Select a table, then set the correlation method and threshold.

  ![image-20230728142905839](./MetaX_Cookbook.assets/co_network_setting.png)

  - Add some items to the focus list (Optional)

  <img src="./MetaX_Cookbook.assets/co_network_focus.png" alt="image-20230728143058568"  />

- Network Plot

  - The Red dots are focus items
  - The depth of color and the width of edges represent the correlation value
  - The size of the dot indicates the number of connections

<img src="./MetaX_Cookbook.assets/co_network_pic.png" alt="co_network_pic"  />

- Expression correlation
  - ![image-20240723162241316](MetaX_Cookbook.assets/expression_corelation_heatmap.png)

### Expression Trends

- Add items to the list window to plot the clusters with similar trends of intensity

<img src="./MetaX_Cookbook.assets/trends_page.png">

- Clusters plot (clustered by **k-means**)

  - The coloured line is the average.

  <img src="./MetaX_Cookbook.assets/trends_cluster.png" style="zoom: 67%;"  >



- Select a **specific cluster** to plot <u>interactive Lines</u> or get the <u>table</u>

  - ![image-20230728144544988](./MetaX_Cookbook.assets/trends_cluster_setting.png)

  - The dashed red line  is the average 

    <img src="MetaX_Cookbook.assets/image-20240304120503032.png" alt="image-20240304120503032"  />

    





## 7. Taxa-Func Link

### Taxa-Func Link Plot

<img src="./MetaX_Cookbook.assets/taxa_func_link_page2.png">

- Check all taxa in one function (or all functions in one taxon).

  - select **a function**, and click the button **<u>Show Linked Taxa Only</u>**
    - **Linked Number**: The number shows how many taxa are linked in this function
    - **The number starts with Taxa**: The number shows how many peptides are in this Taxa-Func

  <img src="./MetaX_Cookbook.assets/taxa_func_linked_only2.png" alt="image-20230728152236517"  />

- Filter items of the Taxa and Func list

  <img src="./MetaX_Cookbook.assets/taxa_func_link_filter.png" alt="image-20230728150853953" style="zoom:50%;" />

  

- Plot Heatmap or Bar

  - Select some groups (Default all) to get **the intensity of each taxon of this function**

    <img src="./MetaX_Cookbook.assets/taxa_func_link_heatmap.png">

<img src="./MetaX_Cookbook.assets/taxa_func_link_bar.png">

- Plot **peptides** in <u>one Function of a Taxon</u>

  <img src="./MetaX_Cookbook.assets/taxa_func_link_pep_heatmap.png">

  <img src="./MetaX_Cookbook.assets/taxa_func_link_pep_bar.png">

- Switch Bar to Stacked or not ( Line)

  <img src="./MetaX_Cookbook.assets/bar_switch_satck.png" alt="bar_switch_satck"  />

- Change Bar plot to Lines

  <img src="./MetaX_Cookbook.assets/bar_to_line.png" alt="bar_to_line"  />


### Taxa-Func Network

- Select some groups or samples (default: all).
- Add some taxa, functions, or taxa-func items to focus the view (optional).

<img src="./MetaX_Cookbook.assets/taxa_func_link_page.png">

- Plot list only
  - **Plot List Only:** Show only the items in the list and the items linked to them.
  - **Without Links:** Only show the items in the focus list.
    <img src="./MetaX_Cookbook.assets/taxa_func_link_net_settings.png" >
  
- Network plot
  - The yellow dots are taxa, and the grey dots are functions, the size of the dots presents the intensity
  - The red dots are the taxa we focused on
  - The green dots are the functions we focused on
- More parameters can be set in **Dev**->**Settings**->**Others** (e.g. Nodes Shape, color, Line Style)

<img src="./MetaX_Cookbook.assets/taxa_func_network.png" alt="taxa_func_network"  />



## 8. Restore Last TaxaFunc Object

- Once you create TaxaFunc, the <u>TaxaFunc Object</u> is saved automatically, and you can restore it next time.
- You can also export the current MetaX object to a file and reload it later.
  <img src="./MetaX_Cookbook.assets/save_and_restore.png" alt="save_and_restore"/>



# Preparing Your Data

## Module 2. Database Builder

**Note:** The results from **MetaLab v2.3** MaxQuant workflow do not require database building. However, we do not recommend using these results as input to MetaX, as many peptides may be discarded.

- Build the database for the **first time** using the <u>Database Builder</u>.

  **Option 1: Build Database Using MGnify Data**

  Ensure you download the correct database type corresponding to your data.

  MetaX supports the MGnify catalogues listed in the Database Builder selector, including barley-rhizosphere, human-skin, maize-rhizosphere, marine-sediment, soil, and tomato-rhizosphere. The selector and command-line options are generated from MetaX's supported-source list. `marine-eukaryotes` is intentionally not enabled by default because it is a beta eukaryotic catalogue with an eggNOG annotation caveat.

  ![dbbuilder](./MetaX_Cookbook.assets/dbbuilder.png)

  **Option 2: Build Database Using Own Data**

  1. **Annotation Table:** A TSV table (tab-separated), with the first column as protein name joined with Genome by "_", e.g., "Genome1_protein1", and other columns containing annotation information.

  ![dbbuilder_own](./MetaX_Cookbook.assets/dbbuilder_own.png)

  2. **Taxa Table:** A TSV table (tab-separated), with the first column as Genome name, e.g., "Genome1", and the second column as taxa.

  **Example Annotation Table:**

  | Query               | Preferred_name | EC                | KEGG_ko             |
  | ------------------- | -------------- | ----------------- | ------------------- |
  | MGYG000000001_00696 | mfd            | -                 | ko:K03723           |
  | MGYG000000001_02838 | hxlR           | -                 | -                   |
  | MGYG000000001_01674 | ispG           | 1.17.7.1,1.17.7.3 | ko:K03526           |
  | MGYG000000001_02710 | glsA           | 3.5.1.2           | ko:K01425           |
  | MGYG000000001_01356 | mutS2          | -                 | ko:K07456           |
  | MGYG000000001_02630 | -              | -                 | -                   |
  | MGYG000000001_02418 | ackA           | 2.7.2.1           | ko:K00925           |
  | MGYG000000001_00728 | atpA           | 3.6.3.14          | ko:K02111           |
  | MGYG000000001_00695 | pth            | 3.1.1.29          | ko:K01056           |
  | MGYG000000001_02907 | -              | -                 | ko:K03086           |
  | MGYG000000001_02592 | rplC           | -                 | ko:K02906           |
  | MGYG000000001_00137 | -              | -                 | ko:K03480,ko:K03488 |

  **Example Taxa Table:**

  | Genome        | Lineage                                                      |
  | ------------- | ------------------------------------------------------------ |
  | MGYG000000001 | d_Bacteria;p_Firmicutes_A;c_Clostridia;o_Peptostreptococcales;f_Peptostreptococcaceae;g_GCA-900066495;s_GCA-900066495 sp902362365 |
  | MGYG000000002 | d_Bacteria;p_Firmicutes_A;c_Clostridia;o_Lachnospirales;f_Lachnospiraceae;g_Blautia_A;s_Blautia_A faecis |
  | MGYG000000003 | d_Bacteria;p_Bacteroidota;c_Bacteroidia;o_Bacteroidales;f_Rikenellaceae;g_Alistipes;s_Alistipes shahii |
  | MGYG000000004 | d_Bacteria;p_Firmicutes_A;c_Clostridia;o_Oscillospirales;f_Ruminococcaceae;g_Anaerotruncus;s_Anaerotruncus colihominis |
  | MGYG000000005 | d_Bacteria;p_Firmicutes_A;c_Clostridia;o_Peptostreptococcales;f_Peptostreptococcaceae;g_Terrisporobacter;s_Terrisporobacter glycolicus_A |
  | MGYG000000006 | d_Bacteria;p_Firmicutes;c_Bacilli;o_Staphylococcales;f_Staphylococcaceae;g_Staphylococcus;s_Staphylococcus xylosus |
  | MGYG000000007 | d_Bacteria;p_Firmicutes;c_Bacilli;o_Lactobacillales;f_Lactobacillaceae;g_Lactobacillus;s_Lactobacillus intestinalis |
  | MGYG000000008 | d_Bacteria;p_Firmicutes;c_Bacilli;o_Lactobacillales;f_Lactobacillaceae;g_Lactobacillus;s_Lactobacillus johnsonii |
  | MGYG000000009 | d_Bacteria;p_Firmicutes;c_Bacilli;o_Lactobacillales;f_Lactobacillaceae;g_Ligilactobacillus;s_Ligilactobacillus murinus |

## Module 3. Database Updater

The **Database Updater** allows updating the database built by the **Database Builder** or adding more annotations. This step is **<u>optional</u>**.

- Update the built database and extend annotations.

  ![db_updater](./MetaX_Cookbook.assets/db_updater.png)

  **Option 1: Built-in Mode**

  Built-in dbCAN_seq mode merges precomputed annotations by exact protein ID; it does not run sequence-similarity searches or re-annotate custom proteins. Incoming annotation columns replace existing columns with the same names, and MetaX writes a warning listing the replaced columns. For a custom protein database, run dbCAN/run_dbCAN on your own protein FASTA and import the resulting TSV with matching MetaX protein IDs using **Option 2**. Built-in sources are available from [dbCAN_seq](https://pro.unl.edu/dbCAN_seq/).

  **Option 2: TSV Table**

  Extend the database by adding a new database to the database table. Ensure the column separator is a tab and the first column is the Protein name, with other columns containing function annotations.

  **Example:**

  | Protein ID          | COG        | KEGG       | ...  |
  | ------------------- | ---------- | ---------- | ---- |
  | MGYG000000001_02630 | Function 1 | Function 1 | ...  |
  | MGYG000000001_01475 | Function 2 | Function 1 | ...  |
  | MGYG000000001_01539 | Function 3 | Function 1 | ...  |

## Module 4. Peptide Annotator

### 1. Peptide Direct to OTF from MAG Workflow

These peptide results use metagenome-assembled genomes (MAGs) as the reference database for protein searches, such as **DIA-NN**, **MetaLab-MAG**, **MetaLab-DIA**, and other workflows that use MAG databases like MGnify or custom MAG databases.

- Annotate the peptide to the Operational Taxa-Functions (OTF) Table before analysis using the <u>Peptide Annotator</u>.

  <img src="./MetaX_Cookbook.assets/peptide2taxafunc.png" alt="peptide2taxafunc"  />

  **Required inputs:**

  - **Digested Genome Folder**: Folder containing digested genome peptide tables created from the same protein database used for the peptide search.

  - **Protein to TaxaFunc Database**: The annotation database created by <u>[Database Builder](#module-2-database-builder)</u>. This is required when producing the final OTF table.

  - **Peptide Table**:

    - *Option 1*: A tab-separated peptide-intensity table from a MAG search workflow, such as ***final_peptides.tsv*** from MetaLab-MAG or ***xxx_report.pr_matrix.tsv*** from DIA-NN matrix export.

    - *Option 2*: Manually create a table with one column for the **peptide sequence** and another column for the **protein group** (e.g., MGYG000003683_00301; MGYG000001490_01143) from the MGnify or your own database. The remaining columns should contain the **intensity values** for each sample.

    - *Option 3*: A long-format DIA-NN parquet file. MetaX detects DIA-NN parquet by `Run`, `Stripped.Sequence`, and a supported intensity column. In the normal Peptide Direct to OTF window, the parquet must also include `Evidence` and `Q.Value`.

    **Example:**

    | Sequence                            | Proteins                                                     | Intensity_V1_01 | Intensity_V1_02 | Intensity_V1_03 | Intensity_V1_04 |
    | ----------------------------------- | ------------------------------------------------------------ | --------------- | --------------- | --------------- | --------------- |
    | (Acetyl)KGGVEPQSETVWR               | MGYG000002716_01681;MGYG000000195_00452;MGYG000001616_00519;MGYG000002926_00231;... | 714650          | 0               | 0               | 0               |
    | (Acetyl)KVIPELNGK                   | MGYG000003589_01892;MGYG000001560_01812;MGYG000001789_00244;... | 0               | 0               | 0               | 0               |
    | (Acetyl)LAELGAKAVTLSGPDGYIYDPDGITTK | MGYG000001199_02893                                          | 0               | 0               | 0               | 0               |
    | (Acetyl)LLTGLPDAYGR                 | MGYG000001757_01206;MGYG000004547_02135;MGYG000001283_00124  | 0               | 307519          | 0               | 0               |
    | (Acetyl)MDFTLDKK                    | MGYG000000076_01275;MGYG000003694_00879;MGYG000000312_02425;MGYG000000271_02102 | 306231          | 0               | 0               | 1214497         |

  - **Output Save Path**: The location to save the result table.

  - **Peptide Column Name**: The peptide sequence column. For DIA-NN parquet input, MetaX uses `Stripped.Sequence`.

  - **Prefix of Intensity Column / DIA-NN Intensity Column**: For table input, this is the sample-intensity prefix, such as `Intensity_`. For DIA-NN parquet input, select `Precursor.Normalised` or `Precursor.Quantity`; MetaX defaults to `Precursor.Normalised` when it is available.

  - **LCA Threshold**: Find the LCA with the proportion threshold for each peptide. The default is 1.00 (100%).

    ![LCA_prop](./MetaX_Cookbook.assets/LCA_prop.png)

  - **Genome separator in protein ID**: Separator between genome ID and protein ID in the searched protein identifiers, such as `_` for `MGYG000003683_00301` or `|` for `MGYG000003683|00301`.

  - **Duplicate peptide handling**: Controls how repeated peptide rows are combined before annotation. Available options are `sum`, `max`, `min`, `mean`, `first`, and `keep`.

#### Genome Selection Modes

Peptide Direct to OTF has three genome-selection modes:

- **Run MetaUmbra scoring, then annotate OTFs**: This is the default workflow. MetaX runs `MetaUmbra score` in an isolated process, writes the intermediate genome-presence table under `metax_temp`, selects genomes by the configured MetaUmbra q-value cutoff, scans the digested genome folder for peptide-to-protein matches from those genomes, and then annotates the final OTF table.

- **Run MetaUmbra scoring only**: Enable **Stop after MetaUmbra** when you only want the MetaUmbra genome-presence table. The output path changes to a genome-presence TSV, and MetaX does not require the Protein to TaxaFunc database for this mode.

- **Use selected genome list**: Open or paste a genome list, or load a MetaUmbra genome-presence result. MetaX skips MetaUmbra scoring and directly scans the digested genome folder for the selected genomes. This is useful when you already reviewed the selected genomes or want to reuse the same genome set across runs.

MetaUmbra scoring currently requires a tab-separated peptide table. When a DIA-NN parquet file is selected, MetaX first prepares a temporary tab-separated peptide table in `metax_temp` before running MetaUmbra.

#### DIA-NN Parquet Preparation

When the input is a DIA-NN parquet file, MetaX reads only the required columns and pivots the long-format table into a direct-to-OTF peptide table:

- `Run` becomes sample-specific intensity columns named `Intensity_<sample>`.
- `Stripped.Sequence` becomes the peptide sequence column.
- `Precursor.Normalised` is preferred as the intensity source; `Precursor.Quantity` is used when selected or when normalized intensity is not available.
- `Evidence` and `Q.Value` are required in the normal Peptide Direct to OTF window and are preserved for MetaUmbra scoring.
- Run names are cleaned into safe sample column names. The selected DIA-NN intensity source is recorded in conversion metadata, but `Precursor.Normalised` or `Precursor.Quantity` is not embedded in the sample-column names.

The same global workflow is available without Qt through the shared annotation backend. For automation, prefer the module entry point so MetaX runs in the caller's active Python environment:

```bash
python -m metax.cli.annotate \
  --mode global \
  --peptide-table report.parquet \
  --digested-genome-folders digested_genomes/ \
  --taxafunc-db MetaX_taxafunc.db \
  --output OTF.tsv \
  --selection-mode metaumbra \
  --result-json annotation_result.json
```

Global mode also accepts `--selection-mode provided` with `--selected-genomes` or `--genome-list-file`, and `--selection-mode automatic` for the existing MetaX genome-ranking path. See [MetaX annotation CLI and automation contract](Annotation_CLI.md) for configuration files, installation profiles, result JSON, workflow API version, and exit codes.

### 2. MetaUmbra Unit-Specific Direct-to-OTF Annotation

MetaX can consume a MetaUmbra `unit_specific_manifest.json` as the preferred backend interface for unit-specific OTF annotation. In this mode, MetaX uses `sample_columns` from each analysis unit to split the peptide intensity table, and uses `genome_ids_q005` or `genome_ids_q001` to restrict peptide-to-protein mapping per unit. If `--genome-threshold` is not provided, the manifest `default_genome_threshold` is used.

This backend is additive to the normal/global Peptide Direct to OTF workflow. When unit-specific mode is disabled, MetaX uses the selected normal mode: MetaUmbra genome scoring, a user-provided genome list, or MetaUmbra scoring-only output. Unit-specific mode does not run the normal global genome-selection path; each analysis unit receives its own genome list directly from the MetaUmbra manifest.

The unit-specific distinct-genome filter defaults to `0`, so MetaX trusts the manifest-selected genome list. Set `--distinct-genome-threshold` to a value greater than `0` only when you want an additional MetaX-side filter requiring that many distinct peptides per genome after mapping.

Sample columns are matched from manifest `sample_columns` to peptide-table columns in this order: exact name, `Intensity_` prefix, configured output prefix, configured input prefix, stripped `Intensity_`, stripped output prefix, stripped input prefix, leading underscores removed, and raw-file basename without `.raw`, `.mzML`, or `.mzXML`. Use `--input-sample-col-prefix` for inputs such as `LFQ intensity sample_1`.

The merged unit-specific OTF table includes `analysis_unit_id` and the original `Sequence` column. MetaX internally derives the unit-specific peptide evidence ID as `analysis_unit_id + "||" + Sequence` when downstream analysis needs a unique peptide identity; `UnitSpecificSequence` is not written by default. Do not deduplicate unit-specific output by `Sequence` alone. Downstream final OTF identity remains Taxon + Function.

In the GUI, select the MetaUmbra `unit_specific_manifest.json` and genome threshold in the main Peptide Direct to OTF window. The Unit-specific Settings dialog does not select a separate manifest or threshold; it configures sample-column matching behavior and missing/empty unit handling, and validates the selected manifest against the current peptide table when possible. Unit-specific mode disables the legacy global genome scoring controls, and the duplicate peptide handling selector still applies. A manual manifest builder is not implemented yet.

Unit-specific annotation accepts either a wide peptide-intensity table with one sample intensity column per manifest sample or a long-format DIA-NN parquet containing `Run`, `Stripped.Sequence`, and either `Precursor.Normalised` or `Precursor.Quantity`. Long-format parquet input is pivoted automatically, and common raw-file suffixes such as `.raw`, `.mzML`, and `.mzXML` are ignored when matching `Run` values to manifest samples.

The default unit-specific execution path is disk-backed. Per-unit temporary files are written under `<output_stem>_artifacts/per_unit/unit_otf/`, merged into the final OTF table by streaming append, and then cleaned up. The final artifacts include:

- The merged OTF table selected in **OTFs Save To**.
- `<output_stem>_info.txt`, with input parameters and annotation summary.
- `<output_stem>_artifacts/unit_annotation_summary.tsv`, with one row per analysis unit.
- `<output_stem>_artifacts/unit_sample_column_mapping.tsv`, with manifest sample to peptide-table column mapping.

For downstream analysis, unit-specific public count columns use these meanings:

- `peptide_num`: unique biological `Sequence` count.
- `peptide_feature_num`: unique unit-specific peptide feature count.

Example:

```bash
python -m metax.cli.annotate \
  --mode unit-specific \
  --peptide-table report.tsv \
  --unit-specific-manifest unit_specific_manifest.json \
  --genome-threshold q0.05 \
  --taxafunc-db MetaX_taxafunc.db \
  --digested-genome-folders digested_genomes/ \
  --output OTF_unit_specific.tsv \
  --peptide-col Sequence \
  --input-sample-col-prefix "LFQ intensity " \
  --duplicate-peptide-handling-mode sum \
  --n-jobs 4 \
  --result-json annotation_result.json
```

### 3. Results from MaxQuant Workflow

These peptide results come from the **MetaLab 2.3** MaxQuant workflow.

- Select the **MetaLab** result folder, which contains the **maxquant_search** folder.

  <img src="MetaX_Cookbook.assets/peptide2taxafunc_tab2_1.png" alt="peptide2taxafunc_tab2_1" style="zoom:80%;" />

- The **Peptide Annotator** will automatically find the **peptides_report.txt**, **BuiltIn.pepTaxa.csv**, and **functions.tsv** in the **maxquant_search** folder. Alternatively, you can select the files manually.

  - Select **OTFs Save To** to set the location to save the result table.

  <img src="MetaX_Cookbook.assets/peptide2taxafunc_tab2_2.png" alt="peptide2taxafunc_tab2_2" style="zoom:80%;" />

<br>




# Developer Tools

## Auto OTF report

The auto report writes a self-contained `MetaX_Report` folder when an output parent
is selected in the GUI. Existing non-empty report directories are rejected unless
**Overwrite** is enabled, which prevents outputs from different runs being mixed.

Group-vs-control testing uses limma via InMoose by default on
`log2(x + 1)`-transformed abundance. Zero abundance remains numeric zero during
limma preprocessing. The legacy GUI Dunnett workflow remains available by setting
`statistics.diff_method: dunnett` or using `--diff-method dunnett`.

The effective configuration is saved as `config_used.yaml`. Static figure output
defaults to 300 DPI PNG and can include editable-text SVG/PDF:

```yaml
statistics:
  diff_method: limma
report:
  figure_formats: [png, svg, pdf]
  dpi: 300
```

Equivalent CLI options are `--diff-method`, `--figure-formats`, and `--dpi`.
The report home page identifies the main taxa level and function column, lists
other combinations as extended results, and shows optional analysis-unit metadata
when `analysis_unit_id` or a compatible unit column is present.

- **Export Log**

  - You can export the log file for debugging or reporting the issue.
  - ![dev_menu](MetaX_Cookbook.assets/dev_menu.png)

- **Export Workflow Notebook**

  - MetaX records GUI analysis steps during the current session and can export selected steps as a runnable workflow package.
  - Use **Developer Tools -> Export Workflow Notebook** to save:
    - a Jupyter notebook (`.ipynb`)
    - a Python script (`.py`)
    - a workflow description file (`.yaml`)
  - This is useful when you want to reproduce a GUI analysis, review the exact parameters used, or continue the workflow in code.

- **Show or Hide the Console**

  <img src="MetaX_Cookbook.assets/show_console.png" alt="show_console"  />

  

- **Settings**

  - Check **Auto Check Update** to enable or disable update checks on launch.
  - Choose whether to update from the **stable version** or **beta version** in Settings.
  <img src="MetaX_Cookbook.assets/settings.png" alt="settings"  />
  - Other Options Settings
  - ![settings_page2](./MetaX_Cookbook.assets/settings_page2.png)
  
  


# Enjoy MetaX

If you have any issues or suggestions, please open a new issue on [GitHub](https://github.com/byemaxx/MetaX).
