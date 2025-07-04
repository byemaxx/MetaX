
# for scaling data
import pandas as pd
import re
import numpy as np
# for heatmap plot
import seaborn as sns
import matplotlib.pyplot as plt
from .get_distinct_colors import GetDistinctColors

class HeatmapPlot:
    def __init__(self, tfobj, linkage_method:str = 'average', distance_metric:str = 'correlation',
                 x_labels_rotation:int = 90, y_labels_rotation:int = 0):
        self.tfa =  tfobj
        self.get_distinct_colors = GetDistinctColors().get_distinct_colors
        self.assign_colors = GetDistinctColors().assign_colors
        self.linkage_method = linkage_method
        self.distance_metric = distance_metric
        self.x_labels_rotation = x_labels_rotation
        self.y_labels_rotation = y_labels_rotation
        
        
        # input: df, func_name, top_number, value_type, fig_size
    # EXAMPLE: plot_top_taxa_func_heatmap_of_test_res(df_anova, sw.func, 200, 'f', (30,30))
        # reset sns style
        sns.set_theme()
        plt.style.use('default')
        
    def get_x_labels_ha(self):
        x_rotation = self.x_labels_rotation
        if x_rotation > 0:
            return 'right'
        elif x_rotation < 0:
            return 'left'
        else:
            return 'center'
    def get_y_labels_va(self):
        y_rotation = self.y_labels_rotation
        if y_rotation >= 0:
            return 'baseline'
        else:
            return 'top'

    def rename_taxa(self, df):
        first_index = df.index[0]
        index_list = df.index.tolist()
        if 'd__' in first_index:
            if '<' not in first_index:
                new_index_list = [i.split('|')[-1] for i in index_list]
            else:
                new_index_list = [
                    f'{i.split(" <")[0].split("|")[-1]} <{i.split(" <")[1][:-1]}>'
                    for i in index_list
                ]
            # check if the new_index_list is unique
            if len(new_index_list) != len(set(new_index_list)):
                raise ValueError("Duplicate taxa names after renaming!")
            
            df.index = new_index_list
        return df


    def filter_data_by_x_y(self, df, x_filter_list: list = [], y_filter_list: list = [], filter_by_regex:bool = False):
        if x_filter_list:
            if filter_by_regex:
                cols = [col for col in df.columns if any(re.search(x, col) for x in x_filter_list)]
            else:
                cols = [col for col in df.columns if any(x in col for x in x_filter_list)]
            df = df[cols]
        if y_filter_list:
            if filter_by_regex:
                rows = [row for row in df.index if any(re.search(y, row) for y in y_filter_list)]
            else:
                rows = [row for row in df.index if any(y in row for y in y_filter_list)]
            df = df.loc[rows]
        if df.empty:
            raise ValueError(f"The dataframe is empty after filter with X-Aixs filter: {x_filter_list} and Y-Axis filter: {y_filter_list}")
        
        return df
    
    
    def plot_top_taxa_func_heatmap_of_test_res(self, df, top_number:int|str= 100, 
                                        value_type:str = 'p', fig_size:tuple|None = None, pvalue:float = 0.05, 
                                         col_cluster:bool = True, row_cluster:bool = True,
                                        cmap:str|None = None, rename_taxa:bool = True, font_size:int = 10, title:str = '',
                                        show_all_labels:tuple = (False, False), return_type:str = 'fig', scale = None, 
                                        scale_method:str = 'maxmin', p_type:str = 'padj',
                                        x_filter_list: list = [], y_filter_list: list = [],
                                        filter_by_regex:bool = False, linecolor:str = 'none'):

        func_name = self.tfa.func_name
        dft = df.copy()
        dft.reset_index(inplace=True)


        # type_map: 1st: plot_type, 2nd: cmap
        #! cmap for f-statistic and pvalue, only when scale_method is 'zscores', the values are negative and positive, otherwise, the values are positive
        #! cmap for t-statistic, the values always are negative and positive
        type_map = {'f': ('f-statistic', 'RdBu_r' if (scale in ['row', 'column', 'all'] and scale_method == 'zscore') else 'flare'),
                    'pvalue': ('pvalue', 'RdBu_r' if (scale in ['row', 'column', 'all'] and scale_method == 'zscore') else 'flare_r'),
                    'padj': ('padj', 'RdBu_r' if (scale in ['row', 'column', 'all'] and scale_method == 'zscore') else 'flare_r'),
                    't': ('t-statistic', 'RdBu_r')}

        plot_type = p_type if value_type in ['pvalue', 'padj'] else type_map.get(value_type, "None")[0]
        
        
        if plot_type == "None":
            raise ValueError("type must be 'f' or 'pvalue' or 'padj' or 't'")

        if plot_type not in dft.columns: # inout wrong t-statistic to f-statistic, or reverse
            old_value_type = value_type
            value_type = 'f' if value_type == 't' else 't' if value_type == 'f' else p_type
            print(f"Warning: [{old_value_type}] is not in the dataframe, change to [{value_type}]")
                

        cmap = type_map.get(value_type, "None")[1] if cmap is None else cmap
        value_col_name = type_map.get(value_type, "None")[0]



        try:
            dft = dft[dft[p_type] < pvalue]
            print(f"\nRESULT:\nNumber of significant by {p_type} < {pvalue}: {len(dft)}")
            if dft.empty:
                raise ValueError(f"No significant differences between groups in {func_name}-Function")
            if 'f-statistic' in dft.columns.tolist():
                dft = dft.sort_values(by=[p_type, 'f-statistic'], ascending=[True, False], ignore_index=True)
            elif 't-statistic' in dft.columns.tolist():
                dft = dft.sort_values(by=[p_type, 't-statistic'], ascending=[True, False], ignore_index=True)
            df_top = dft.head(top_number)

            if rename_taxa:
                df_top['Taxon'] = df_top['Taxon'].apply(lambda x: x.split('|')[-1])
                # df_top = self.rename_taxa(df_top)
            df_top = df_top.pivot(index=func_name, columns='Taxon', values=value_col_name)
            print(f"Top [{top_number}] significant: Taxa ({df_top.shape[1]}), Functions ({df_top.shape[0]})")
            
            df_top = self.filter_data_by_x_y(df_top, x_filter_list, y_filter_list, filter_by_regex)
            
            df_plot = df_top.fillna(1) if plot_type in ['pvalue', 'padj'] else df_top.fillna(0)
            df_plot = self.scale_data(df = df_plot, scale_by = scale, method = scale_method)
            
            data_include_negative_and_positive = True if (df_plot.min().min() < 0 and df_plot.max().max() > 0) else False

            sns_params = {
                'center': 0 if data_include_negative_and_positive else None,
                "cmap": cmap,
                "linewidths": 0.01, 
                "linecolor": None if linecolor == 'none' else linecolor,
                "dendrogram_ratio": (0.1, 0.2),
                "figsize": fig_size if return_type == 'fig' else None,
                "col_cluster": col_cluster if df_plot.shape[1] > 1 else False,
                "row_cluster": row_cluster if df_plot.shape[0] > 1 else False,
                "method": self.linkage_method,
                "metric": self.distance_metric,
                "cbar_kws": {"label": plot_type, "shrink": 0.5},
                "mask": df_top.isnull(),
                "xticklabels": (True if show_all_labels[0] else "auto") if return_type == 'fig' else False,
                "yticklabels": (True if show_all_labels[1] else "auto") if return_type == 'fig' else False,
            }

            fig = sns.clustermap(df_plot, **sns_params)
            
            if return_type == 'table':
                # get the sorted dataframe
                if row_cluster and not col_cluster:
                    sorted_df = df_plot.iloc[fig.dendrogram_row.reordered_ind, :]
                elif col_cluster and not row_cluster:
                    sorted_df = df_plot.iloc[:, fig.dendrogram_col.reordered_ind]
                elif row_cluster and col_cluster:
                    sorted_df = df_plot.iloc[fig.dendrogram_row.reordered_ind, fig.dendrogram_col.reordered_ind]
                else:
                    sorted_df = df_plot
                plt.close(fig.figure)
                return sorted_df
            
            
            fig.ax_heatmap.set_xlabel("Taxa")
            fig.ax_heatmap.set_ylabel("Functions")
            
            scale_title = f", scaled by {scale}" if scale in ['row', 'column', 'all'] else ''
            if title == "":
                title = f"Significant Differences in Taxa-Function (Top {top_number} sorted by {plot_type}, filtered by {p_type}{scale_title})"
            else:
                title = f"{title} (Top {top_number} sorted by {plot_type}, filtered by {p_type}{scale_title})"
                
            plt.suptitle(title)

            fig.ax_heatmap.set_xticklabels(
                fig.ax_heatmap.get_xmajorticklabels(),
                fontsize=font_size,
                rotation=self.x_labels_rotation,
                ha = self.get_x_labels_ha()
            )
            fig.ax_heatmap.set_yticklabels(
                fig.ax_heatmap.get_ymajorticklabels(),
                fontsize=font_size,
                rotation=self.y_labels_rotation,
                ha = 'left',
                va = self.get_y_labels_va()
            )
                
            cbar = fig.ax_heatmap.collections[0].colorbar
            cbar.set_label(plot_type, rotation=90, labelpad=1)
            cbar.ax.yaxis.set_ticks_position('left')
            cbar.ax.yaxis.set_label_position('left')
            
            
            plt.subplots_adjust(left=0.06, bottom=0.35, right=0.5, top=0.96, wspace=0.01, hspace=0.01)

            plt.tight_layout()
            plt.show()
            return fig
        
                
        except ValueError as e:
            print(f"Error: {e}")
            plt.close('all')
            raise ValueError(f"Error: {e}")
    

    # For taxa, func and peptides table, plot the intensity of significant differences items
    def plot_basic_heatmap_of_test_res(self, df, top_number:int = 100, value_type:str = 'p', 
                                       fig_size:tuple|None = None, pvalue:float = 0.05, scale = None, 
                                       col_cluster:bool = True, row_cluster:bool = True,
                                       cmap:str|None = None, rename_taxa:bool = True, font_size:int = 10,
                                       show_all_labels:tuple = (False, False), rename_sample:bool = True,
                                       sort_by:str = 'padj', scale_method:str = 'maxmin', return_type:str = 'fig',
                                       p_type:str = 'padj', x_filter_list: list = [], y_filter_list: list = [],
                                       filter_by_regex:bool = False, linecolor:str = 'none'):

        dft = df.copy()
        
        type_map = {'f': 'f-statistic', 't': 't-statistic', 'pvalue': 'pvalue', 'padj': 'padj'}
        plot_type = type_map.get(value_type)

        if plot_type is None:
            raise ValueError("type must be 'f' or 't' or 'pvalue' or 'padj'")

        
        if plot_type not in df.columns:
            print(f"Warning: [{plot_type}] is not in the dataframe, change to [padj]")
            plot_type = 'padj'

        
        dft = dft[dft[p_type] < pvalue]


        if 'f-statistic' in dft.columns:
            sort_column = 'f-statistic' if sort_by == 'f-statistic' else p_type
            ascending = sort_by in ['pvalue', 'padj']
            dft = dft.sort_values(by=[sort_column], ascending=ascending)
            mat = dft.head(top_number).drop(['pvalue', 'padj', 'f-statistic'], axis=1)

        elif 't-statistic' in dft.columns:
            if sort_by == 't-statistic':
                dft['abs_t-statistic'] = dft['t-statistic'].abs()
                sort_column = 'abs_t-statistic'
                ascending = False
            else:
                sort_column = p_type
                ascending = True
            
            dft = dft.sort_values(by=[sort_column], ascending=ascending)
            mat = dft.head(top_number).drop(['pvalue', 'padj','t-statistic', 'abs_t-statistic'], axis=1, errors='ignore')
        else:
            raise ValueError("No 'f-statistic' or 't-statistic' in the dataframe")
        

        mat = self.filter_data_by_x_y(mat, x_filter_list, y_filter_list, filter_by_regex)
        
        # if mat is empty, raise error
        if mat.empty:
            erro_msg = f"No significant differences between groups in {plot_type} <= [{pvalue}]"
            erro_msg += f" after filter with X-Aixs filter: {x_filter_list} and Y-Axis filter: {y_filter_list}" if x_filter_list or y_filter_list else ''
            raise ValueError(erro_msg)
        
        if len(mat) < 2:
            row_cluster = False
        if len(mat.columns) < 2:
            col_cluster = False
            

        if fig_size is None:
            fig_size = (30,30)


        try:
            if rename_sample:
                mat, group_list = self.tfa.add_group_name_for_sample(mat)
            else:
                group_list = [self.tfa.get_group_of_a_sample(i) for i in mat.columns]
        
            color_list = self.assign_colors(group_list)
           
            if rename_taxa:
                mat = self.rename_taxa(mat)
            
            mat = self.scale_data(df = mat, scale_by = scale, method = scale_method)
            
            data_include_negative_and_positive = True if (mat.min().min() < 0 and mat.max().max() > 0) else False
            
            if cmap is None:
                cmap = 'RdBu_r' if data_include_negative_and_positive else 'OrRd'
              
            sns_params = {
                "center": 0 if data_include_negative_and_positive else None,
                "cmap": cmap,
                "linewidths": 0.01, 
                "linecolor": None if linecolor == 'none' else linecolor,
                "figsize": fig_size if return_type == 'fig' else None,
                "cbar_kws": {"label": "Intensity", "shrink": 0.5},
                "col_cluster": col_cluster,
                "row_cluster": row_cluster,
                "method": self.linkage_method,
                "metric": self.distance_metric,
                "col_colors": color_list,
                "xticklabels": (True if show_all_labels[0] else "auto") if return_type == 'fig' else False,
                "yticklabels": (True if show_all_labels[1] else "auto") if return_type == 'fig' else False,
            }
            fig = sns.clustermap(mat, **sns_params)

            if return_type == 'table':
                # get the sorted dataframe
                if row_cluster and not col_cluster:
                    sorted_df = mat.iloc[fig.dendrogram_row.reordered_ind, :]
                elif col_cluster and not row_cluster:
                    sorted_df = mat.iloc[:, fig.dendrogram_col.reordered_ind]
                elif row_cluster and col_cluster:
                    sorted_df = mat.iloc[fig.dendrogram_row.reordered_ind, fig.dendrogram_col.reordered_ind]
                else:
                    sorted_df = mat
                
                plt.close(fig.figure)
                
                return sorted_df
                    
            # plot heatmap figure
            fig.ax_heatmap.set_xticklabels(
                fig.ax_heatmap.get_xmajorticklabels(),
                fontsize=font_size,
                rotation=self.x_labels_rotation,
                ha = self.get_x_labels_ha()
            )
            fig.ax_heatmap.set_yticklabels(
                fig.ax_heatmap.get_ymajorticklabels(),
                fontsize=font_size,
                rotation=self.y_labels_rotation,
                ha = 'left',
                va = self.get_y_labels_va()
            )

            scale_title = f", scaled by {scale}" if scale in ['row', 'column', 'all'] else ''
            plt.suptitle(
                f"The intensity of Significant differences (top {len(mat)} sorted by {sort_by.split('(')[0]}, filtered by {p_type}{scale_title})"
            )
            cbar = fig.ax_heatmap.collections[0].colorbar
            cbar.set_label("Intensity", rotation=90, labelpad=1)
            cbar.ax.yaxis.set_ticks_position('left')
            cbar.ax.yaxis.set_label_position('left')

            plt.subplots_adjust(left=0.05, bottom=0.11, right=0.5, top=0.96, wspace=0.01, hspace=0.01)
            
            plt.tight_layout()
            plt.show()
            return fig
        except Exception as e:
            print(f'Error: {e}')
            plt.close('all')
            raise ValueError(f"Error: {e}")
 

    # Plot basic heatmap of matrix with color bar
    # EXAMPLE: plot_heatmap(sw, mat=get_top_intensity_matrix_of_test_res(df=df_anova, df_type='anova', top_num=100), 
                #  title = 'The heatmap of top 100 significant differences between groups in Taxa-Function', 
                #  fig_size=(30,30), scale='row')
    def plot_basic_heatmap(self,  df, title = 'Heatmap',fig_size:tuple|None = None, 
                    scale = None, col_cluster:bool = True, row_cluster:bool = True, 
                    cmap:str|None = None, rename_taxa:bool = True, font_size:int = 10,
                    show_all_labels:tuple = (False, False), scale_method:str = 'maxmin', return_type:str = 'fig',
                    sample_to_group_dict:dict|None = None, x_filter_list: list = [], y_filter_list: list = [],
                    filter_by_regex:bool = False, linecolor:str = 'none', linewidths:float = 0.01):


        df = self.filter_data_by_x_y(df, x_filter_list, y_filter_list, filter_by_regex)
        # check if any row or column is all 0
        if (df == 0).all().any():
            # remove all 0 rows
            row_num = len(df)
            df = df.loc[~(df==0).all(axis=1)] if row_cluster else df
            # remove all 0 columns
            col_num = len(df.columns)
            df = df.loc[:, (df != 0).any(axis=0)] if col_cluster else df
            print(f"Remove all 0 rows and columns after calculating the mean of the data:\n{row_num - len(df)} rows are removed\n{col_num - len(df.columns)} columns are removed")
        
        if len(df) < 2:
            row_cluster = False
        if len(df.columns) < 2:
            col_cluster = False
        

        df = self.scale_data(df = df, scale_by = scale, method = scale_method)

        # if index is Taxon, rename index
        if rename_taxa:
            df = self.rename_taxa(df)

        
        if return_type == 'table':
            sns_params = {
                "col_cluster": col_cluster,
                "row_cluster": row_cluster,
                "method": self.linkage_method,
                "metric": self.distance_metric,
            }
            fig = sns.clustermap(df, **sns_params)
            # get the sorted dataframe
            if row_cluster and not col_cluster:
                sorted_df = df.iloc[fig.dendrogram_row.reordered_ind, :]
            elif col_cluster and not row_cluster:
                sorted_df = df.iloc[:, fig.dendrogram_col.reordered_ind]
            elif row_cluster and col_cluster:
                sorted_df = df.iloc[fig.dendrogram_row.reordered_ind, fig.dendrogram_col.reordered_ind]
            else:
                sorted_df = df
            plt.close(fig.figure)
            return sorted_df
        
        # else plot heatmap figure
        if cmap is None:
            cmap = 'YlOrRd'
        if fig_size is None:
            fig_size = (30,30)
        if sample_to_group_dict is not None:
            group_list = [sample_to_group_dict.get(i, i) for i in df.columns]
            color_list = self.assign_colors(group_list)
        else:
            color_list = None
            
        sns_params = {
            # "center": 0,
            "cmap": cmap,
            "figsize": fig_size,
            "linewidths": linewidths,
            "linecolor": None if linecolor == 'none' else linecolor,
            "dendrogram_ratio": (0.1, 0.2),
            "cbar_kws": {"label": "Intensity", "shrink": 0.5},
            "col_cluster": col_cluster,
            "row_cluster": row_cluster,
            "method": self.linkage_method,
            "metric": self.distance_metric,
            "col_colors": color_list,
            "xticklabels": True if show_all_labels[0] else "auto",
            "yticklabels": True if show_all_labels[1] else "auto",
        }
        fig = sns.clustermap(df, **sns_params)

        fig.ax_heatmap.set_xticklabels(
            fig.ax_heatmap.get_xmajorticklabels(),
            fontsize=font_size,
            rotation=self.x_labels_rotation,
            ha=self.get_x_labels_ha()
        )
        fig.ax_heatmap.set_yticklabels(
            fig.ax_heatmap.get_ymajorticklabels(),
            fontsize=font_size,
            rotation=self.y_labels_rotation,
            ha="left",
            va=self.get_y_labels_va()
        )
        title = f"{title} (scaled by {scale})" if scale not in [None, 'None'] else title
        plt.suptitle(title, weight='bold')
        
        cbar = fig.ax_heatmap.collections[0].colorbar
        cbar.set_label('Intensity', rotation=90, labelpad=1)
        cbar.ax.yaxis.set_ticks_position('left')
        cbar.ax.yaxis.set_label_position('left')
        
        plt.subplots_adjust(left=0.05, bottom=0.15, right=0.5, top=0.96, wspace=0.01, hspace=0.01)
        plt.tight_layout()
        plt.show()
        return fig


        # For taxa-func heatmap

    # plot heatmap for all condtion results of DESeq2All or DunnettAll
    def plot_heatmap_of_all_condition_res(self, df,  pvalue:float = 0.05,scale:str|None = None, log2fc_min:float = 1.0,log2fc_max:float = 30.0,
                                       fig_size:tuple = (10,10), col_cluster:bool = True, row_cluster:bool = True,
                                       cmap:str|None = None, rename_taxa:bool = True, font_size:int = 10, 
                                       show_all_labels:tuple = (False, False), 
                                       return_type:str = 'fig', res_df_type:str = 'deseq2',
                                       p_type:str = 'padj', three_levels_df_type: str = 'same_trends',
                                       show_col_colors:bool = True, remove_zero_col:bool = True, scale_method:str = 'maxmin',
                                       x_filter_list: list = [], y_filter_list: list = [], filter_by_regex:bool = False,
                                       linecolor:str = 'none'):
        """
        Plot a heatmap of all condition results.

        Parameters:
            - df (DataFrame): The input DataFrame containing the condition results.
            - pvalue (float): The p threshold for significance. Default is 0.05.
            - scale (str | None): The scaling method for the data. Default is None.
            - log2fc_min (float): The minimum log2 fold change value. Default is 1.0.
            - log2fc_max (float): The maximum log2 fold change value. Default is 30.0.
            - fig_size (tuple): The size of the figure. Default is (10, 10).
            - col_cluster (bool): Whether to cluster the columns. Default is True.
            - row_cluster (bool): Whether to cluster the rows. Default is True.
            - cmap (str | None): The color map for the heatmap. Default is None.
            - rename_taxa (bool): Whether to rename the taxa. Default is True.
            - font_size (int): The font size for the plot. Default is 10.
            - show_all_labels (tuple): Whether to show all labels for x-axis and y-axis. Default is (False, False).
            - return_type (str): The type of the return value. Default is 'fig'. options: 'fig', 'table'
            - res_df_type (str): The type of the result DataFrame. Default is 'deseq2'.
            - p_type (str): The type of pvalue. Default is 'padj'. options: 'pvalue', 'padj'
            - three_levels_df_type (str): The type of the three levels DataFrame. Default is 'same_trends'. options: 'all_sig', 'no_na', 'half_same_trnds', 'same_trends'
            - show_col_colors (bool): Whether to show column colors. Default is True.
            - remove_zero_col (bool): Whether to remove zero columns. Default is True.
            - scale_method (str): The scaling method for the data. Default is 'maxmin'.
            - x_filter_list (list): The list of x-axis filter. Default is [].
            - y_filter_list (list): The list of y-axis filter. Default is [].

        Returns:
            - retrun_type == 'fig': The heatmap figure. or (fig, df_dict) dict_df: {'all_sig': df1, 'no_na': df2, 'same_trends': df3}
            - retrun_type == 'table': The sorted dataframe.

        Raises:
            - ValueError: If there are no significant differences in the results.
            - ValueError: If an error occurs during plotting.

        """
        # keep 4 decimal places
        pvalue = round(pvalue, 4)
        color_list = None
        if df.columns.nlevels == 2:
            if res_df_type == 'deseq2':
                dft = self.tfa.CrossTest.extrcat_significant_fc_from_deseq2all(df, p_value=pvalue, log2fc_min=log2fc_min, 
                                                                log2fc_max=log2fc_max, p_type=p_type)
            elif res_df_type == 'dunnet':
                dft = self.tfa.CrossTest.extrcat_significant_stat_from_dunnett(df, p_value=pvalue, p_type=p_type)
                
        elif df.columns.nlevels == 3:
            df_dict = self.tfa.CrossTest.extrcat_significant_fc_from_all_3_levels(df, p_value=pvalue, 
                                                                            log2fc_min=log2fc_min, log2fc_max=log2fc_max,
                                                                            p_type=p_type, df_type = res_df_type)
            dft = df_dict[three_levels_df_type].copy()
            # set level 1 index as the column color
            dft.columns = ['~'.join(col) for col in dft.columns]
            sample_list = dft.columns.tolist()
            group_list = []
            for i in sample_list:
                group_name = i.split('~')[0]
                group_list.append(group_name)
            color_list = self.assign_colors(group_list)
        

        dft = self.filter_data_by_x_y(dft, x_filter_list, y_filter_list, filter_by_regex)
                    
        if dft.empty or dft is None:
            if res_df_type == 'deseq2':
                error_msg = f"No significant differences Results in {p_type} < {pvalue}, {log2fc_min} <= log2fc <= {log2fc_max} for {three_levels_df_type} in DESeq2All"
            else:
                error_msg = f"No significant differences Results in  {p_type} < {pvalue} for {three_levels_df_type} in Dunnett test"
            if x_filter_list or y_filter_list:
                error_msg += f" with X-Aixs filter: {x_filter_list} and Y-Axis filter: {y_filter_list}"
            raise ValueError(error_msg)
    
            
        # fill na with 0
        dft = dft.fillna(0, inplace=False)
        
        if remove_zero_col:
            print(f"The shape of the dataframe is {dft.shape}")
            dft = dft.loc[:, (dft != 0).any(axis=0)]
            print(f"Remove all zero columns, the shape of the dataframe is {dft.shape}")
        
        
        
        if len(dft) < 2:
            row_cluster = False
            print('Warning: There is only one row in the dataframe, row_cluster is set to False')
        if len(dft.columns) < 2:
            col_cluster = False
            print('Warning: There is only one column in the dataframe, col_cluster is set to False')



        try:
            if rename_taxa:
                dft = self.rename_taxa(dft)
            # scale the data
            if scale:
                dft = self.scale_data(df = dft, scale_by = scale, method = scale_method)
            
            if cmap is None:
                cmap = sns.color_palette("vlag", as_cmap=True, n_colors=30) # type: ignore
            
            # 标准化颜色映射以使 0 处为白色
            from matplotlib.colors import TwoSlopeNorm
            vmax = np.max(np.abs(dft.values))  # 获取数据的最大绝对值
            norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)

            sns_params = {
                "cmap": cmap,
                "figsize": fig_size,
                "norm": norm,
                "linewidths": 0.01, 
                "linecolor": None if linecolor == 'none' else linecolor,
                "dendrogram_ratio": (0.1, 0.2),
                "col_cluster": col_cluster,
                "row_cluster": row_cluster,
                "method": self.linkage_method,
                "metric": self.distance_metric,
                "cbar_kws": {
                    "label": "log2FoldChange"
                    if res_df_type == "deseq2"
                    else "t-statistic",
                    "shrink": 0.5,
                },
                "xticklabels": True if show_all_labels[0] else "auto",
                "yticklabels": True if show_all_labels[1] else "auto",
                "col_colors": color_list if show_col_colors else None,
            }

            if return_type == 'fig':
                fig = sns.clustermap(dft, **sns_params)

                fig.ax_heatmap.set_xticklabels(
                    fig.ax_heatmap.get_xmajorticklabels(),
                    fontsize=font_size,
                    rotation=self.x_labels_rotation,
                    ha = self.get_x_labels_ha()
                )
                fig.ax_heatmap.set_yticklabels(
                    fig.ax_heatmap.get_ymajorticklabels(),
                    fontsize=font_size,
                    rotation=self.y_labels_rotation,
                    ha = 'left',
                    va = self.get_y_labels_va()
                )
                if res_df_type == 'deseq2':
                    title = f"The Heatmap of log2FoldChange calculated by DESeq2 ({p_type} < {pvalue}, {log2fc_min} <= log2fc <= {log2fc_max}, scaled by {scale})"
                else:
                    title = f"The Heatmap of t-statistic calculated by Dunnett test ({p_type} < {pvalue}, scaled by {scale})"                
                
                plt.suptitle(title, weight='bold')
                
                cbar = fig.ax_heatmap.collections[0].colorbar
                cbar.set_label("log2FC" if res_df_type == 'deseq2' else 't-statistic', 
                               rotation=90, labelpad=1)
                cbar.ax.yaxis.set_ticks_position('left')
                cbar.ax.yaxis.set_label_position('left')
                
                plt.subplots_adjust(left=0.05, bottom=0.15, right=0.5, top=0.96, wspace=0.01, hspace=0.01)

                plt.tight_layout()
                plt.show()

                if 'df_dict' in locals(): # df_dict:{'all_sig': df1, 'no_na': df2, 'same_trends': df3}
                    return fig, df_dict
                else:
                    return fig
            elif return_type == 'table':
                sns_params = {
                    "norm": norm,
                    "col_cluster": col_cluster,
                    "row_cluster": row_cluster,
                    "method": self.linkage_method,
                    "metric": self.distance_metric,
                }
                fig = sns.clustermap(dft, **sns_params)

                # get the sorted dataframe
                if row_cluster and not col_cluster:
                    sorted_df = dft.iloc[fig.dendrogram_row.reordered_ind, :]
                elif col_cluster and not row_cluster:
                    sorted_df = dft.iloc[:, fig.dendrogram_col.reordered_ind]
                elif row_cluster and col_cluster:
                    sorted_df = dft.iloc[fig.dendrogram_row.reordered_ind, fig.dendrogram_col.reordered_ind]
                else:
                    sorted_df = dft
                
                plt.close(fig.figure)

                return sorted_df
                            
        except Exception as e:
            print(f'Error: {e}')
            plt.close('all')
            raise ValueError(f"Error: {e}")

    # For taxa, func and peptides table
    def plot_heatmap_of_dunnett_test_res(self, df,  pvalue:float = 0.05,scale:str|None = None,
                                       fig_size:tuple|None = None, col_cluster:bool = True, row_cluster:bool = True,
                                       cmap:str|None = None, rename_taxa:bool = True, font_size:int = 10,
                                       show_all_labels:tuple = (False, False),  show_col_colors:bool = False,
                                       scale_method:str = 'maxmin', p_type:str = 'padj',
                                       x_filter_list: list = [], y_filter_list: list = [],
                                        filter_by_regex:bool = False, linecolor:str = 'none'
                                       ):
        #! 只画t-statistic的heatmap, 用p_type来判断: 'padj' or 'pvalue'
        
        pvalue = round(pvalue, 5)


        dft = self.tfa.CrossTest.extrcat_significant_stat_from_dunnett(df, p_value=pvalue, p_type=p_type)
        # fill na with 0
        dft = dft.fillna(0, inplace=False)

        # remove all 0 rows
        dft = dft.loc[~(dft==0).all(axis=1)]
        
        dft = self.tfa.replace_if_two_index(dft)
        
        dft = self.filter_data_by_x_y(dft, x_filter_list, y_filter_list, filter_by_regex)

        if len(dft) < 2:
            row_cluster = False
            print('Warning: There is only one row in the dataframe, row_cluster is set to False')
        if len(dft.columns) < 2:
            col_cluster = False
            print('Warning: There is only one column in the dataframe, col_cluster is set to False')


        if fig_size is None:
            fig_size = (30,30)



        try:

            if rename_taxa:
                dft = self.rename_taxa(dft)


            # scale the data
            if scale:
                dft = self.scale_data(df = dft, scale_by = scale, method = scale_method)
                
            
            if cmap is None:
                cmap = sns.color_palette("vlag", as_cmap=True, n_colors=30) # type: ignore

            col_colors = self.get_distinct_colors(len(dft.columns))
            # 标准化颜色映射以使 0 处为白色
            from matplotlib.colors import TwoSlopeNorm
            vmax = np.max(np.abs(dft.values))  # 获取数据的最大绝对值
            norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)

            sns_params = {
                "cmap": cmap,
                "figsize": fig_size,
                "norm": norm,
                "linewidths": 0.01, 
                "linecolor": None if linecolor == 'none' else linecolor,
                "dendrogram_ratio": (0.1, 0.2),
                "cbar_kws": {"label": "t-statistic", "shrink": 0.5},
                "col_cluster": col_cluster,
                "row_cluster": row_cluster,
                "method": self.linkage_method,
                "metric": self.distance_metric,
                "col_colors": col_colors if show_col_colors else None,
                "xticklabels": True if show_all_labels[0] else "auto",
                "yticklabels": True if show_all_labels[1] else "auto",
            }
            fig = sns.clustermap(dft, **sns_params)

            fig.ax_heatmap.set_xticklabels(
                fig.ax_heatmap.get_xmajorticklabels(),
                fontsize=font_size,
                rotation=self.x_labels_rotation,
                ha = self.get_x_labels_ha()
            )
            fig.ax_heatmap.set_yticklabels(
                fig.ax_heatmap.get_ymajorticklabels(),
                fontsize=font_size,
                rotation=self.y_labels_rotation,
                ha = 'left',
                va = self.get_y_labels_va()
            )
            plt.suptitle(f"The Heatmap of t-statistic calculated by Dunnett test ({p_type} < {pvalue}, scaled by {scale})", 
                         weight='bold')

            cbar = fig.ax_heatmap.collections[0].colorbar
            cbar.set_label('t-statistic', rotation=90, labelpad=1)
            cbar.ax.yaxis.set_ticks_position('left')
            cbar.ax.yaxis.set_label_position('left')
            
            plt.subplots_adjust(left=0.05, bottom=0.15, right=0.5, top=0.96, wspace=0.01, hspace=0.01)

            plt.tight_layout()
            plt.show()
            return fig
        except Exception as e:
            print(f'Error: {e}')
            plt.close('all')
            raise ValueError(f"Error: {e}")


    def get_heatmap_table_of_dunnett_res(self, df,  pvalue:float = 0.05,scale:str|None = None,
                                        col_cluster:bool = True, row_cluster:bool = True, rename_taxa:bool = True,
                                        scale_method:str = 'maxmin', p_type:str = 'padj',
                                        x_filter_list: list = [], y_filter_list: list = [],
                                        filter_by_regex:bool = False):

        
        dft = self.tfa.CrossTest.extrcat_significant_stat_from_dunnett(df, p_value=pvalue, p_type=p_type)

        # fill na with 0
        dft = dft.fillna(0, inplace=False)

        # remove all 0 rows
        dft = dft.loc[~(dft==0).all(axis=1)]
        
        dft = self.tfa.replace_if_two_index(dft)
        
        dft = self.filter_data_by_x_y(dft, x_filter_list, y_filter_list, filter_by_regex)
            

        if len(dft) < 2:
            row_cluster = False
            print('Warning: There is only one row in the dataframe, row_cluster is set to False')
        if len(dft.columns) < 2:
            col_cluster = False
            print('Warning: There is only one column in the dataframe, col_cluster is set to False')



        try:

            if rename_taxa:
                dft = self.rename_taxa(dft)


            # scale the data
            if scale:
                dft = self.scale_data(df = dft, scale_by = scale, method = scale_method)
                
            
            from matplotlib.colors import TwoSlopeNorm
            vmax = np.max(np.abs(dft.values))  # 获取数据的最大绝对值
            norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
            
            sns_params = {
                "norm": norm,
                "col_cluster": col_cluster,
                "row_cluster": row_cluster,
                "method": self.linkage_method,
                "metric": self.distance_metric,
                "cbar_kws": {"label": "t-statistic"},
            }
            fig = sns.clustermap(dft, **sns_params)
            
            # get the sorted dataframe
            if row_cluster and not col_cluster:
                sorted_df = dft.iloc[fig.dendrogram_row.reordered_ind, :]
            elif col_cluster and not row_cluster:
                sorted_df = dft.iloc[:, fig.dendrogram_col.reordered_ind]
            elif row_cluster and col_cluster:
                sorted_df = dft.iloc[fig.dendrogram_row.reordered_ind, fig.dendrogram_col.reordered_ind]
            else:
                sorted_df = dft
            
            
            plt.close(fig.fig)

            return sorted_df
        except Exception as e:
            print(f'Error: {e}')
            raise ValueError("Can not get the result table, please check the error message in consel.")
        
        


    def scale_data(self, df: pd.DataFrame, scale_by: str | None = None, method: str | None = 'maxmin') -> pd.DataFrame:
        """
        Scale the data by row, column or all using zscore or maxmin method.
        """
        scale_by = scale_by.lower() if scale_by else None
        method = method.lower() if method else None

        print(f"Scaling the data by [{scale_by}] using method [{method}]")

        if scale_by in ['none', None] or method in ['none', None]:
            print("No scaling is performed.")
            return df

        df = df.copy()

        if scale_by == 'column':
            scale_by = 'col'

        if scale_by not in ['row', 'col', 'all']:
            raise ValueError("scale_by must be 'row', 'col', 'all' or 'none'")

        if method not in ['zscore', 'maxmin']:
            raise ValueError("method must be 'zscore' or 'maxmin' or 'none'")

        # 定义 zscore 缩放函数，对 Series 进行处理：
        # 如果 Series 中只有一个元素，则返回原值（因为标准差为0时直接缩放会变为0）
        def zscore_series(s: pd.Series) -> pd.Series:
            if len(s) == 1:
                return s
            mu = s.mean()
            sigma = s.std(ddof=0)
            if sigma == 0:
                return s  # 保持原值
            else:
                return (s - mu) / sigma

        # 定义 maxmin 缩放函数，对 Series 进行处理：
        # 如果 Series 中只有一个元素，则直接返回原值，避免 1 的归一化
        def maxmin_series(s: pd.Series) -> pd.Series:
            if len(s) == 1:
                return s
            max_val = s.abs().max()
            if max_val == 0:
                return s
            else:
                return s / max_val

        # 根据 method 和 scale_by 进行不同维度的缩放
        if method == 'zscore':
            if scale_by == 'row':
                df = df.apply(zscore_series, axis=1)
            elif scale_by == 'col':
                df = df.apply(zscore_series, axis=0)
            else:  # scale_by == 'all'
                if df.size == 1:
                    return df
                flattened = df.values.flatten()
                mu = flattened.mean()
                sigma = flattened.std(ddof=0)
                if sigma == 0:
                    return df
                else:
                    df = (df - mu) / sigma

        elif method == 'maxmin':
            if scale_by == 'row':
                df = df.apply(maxmin_series, axis=1)
            elif scale_by == 'col':
                df = df.apply(maxmin_series, axis=0)
            else:  # scale_by == 'all'
                if df.size == 1:
                    return df
                max_val = np.abs(df.values).max()
                if max_val == 0:
                    return df
                else:
                    df = df / max_val

        return df

