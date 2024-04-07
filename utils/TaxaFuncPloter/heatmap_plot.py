
from distinctipy import distinctipy
import seaborn as sns
import matplotlib.pyplot as plt
from .get_distinct_colors import GetDistinctColors

class HeatmapPlot:
    def __init__(self, tfobj):
        self.tfa =  tfobj
        self.get_distinct_colors = GetDistinctColors().get_distinct_colors
        self.assign_colors = GetDistinctColors().assign_colors
        
        # input: df, func_name, top_number, value_type, fig_size
    # EXAMPLE: plot_top_taxa_func_heatmap_of_test_res(df_anova, sw.func, 200, 'f', (30,30))
        # reset sns style
        sns.set_theme()

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
            df.index = new_index_list
        return df

    # For taxa-func table
    def plot_top_taxa_func_heatmap_of_test_res(self, df, top_number:int|str= 100, 
                                        value_type:str = 'p', fig_size:tuple|None = None, pvalue:float = 0.05, 
                                         col_cluster:bool = True, row_cluster:bool = True,
                                        cmap:str|None = None, rename_taxa:bool = True, font_size:int = 10, title:str = '',
                                        show_all_labels:tuple = (False, False), return_type:str = 'fig'):

        

        func_name = self.tfa.func_name
        dft = df.copy()
        dft.reset_index(inplace=True)
        type_map = {'f': ('f-statistic', 'Spectral_r', 1),
                    'p': ('P-value', 'Reds_r', None),
                    't': ('t-statistic', 'hot_r', 1)}

        plot_type = type_map.get(value_type, None)[0]
        if plot_type is None:
            raise ValueError("type must be 'p' or 'f' or 't'")
        
        
        if plot_type not in dft.columns: # inout wrong t-statistic to f-statistic, or reverse
            old_value_type = value_type
            value_type = 'f' if value_type == 't' else 't' if value_type == 'f' else 'p'
            print(f"Warning: [{old_value_type}] is not in the dataframe, change to [{value_type}]")
                

        if cmap is None:
            plot_type, cmap, scale = type_map.get(value_type, None)
        else:
            plot_type, _, scale = type_map.get(value_type, None)



        try:
            dft = dft[dft['P-value'] < pvalue]
            print(f"\nRESULT:\nNumber of significant rows: {len(dft)}")
            if dft.empty:
                raise ValueError(f"No significant differences between groups in {func_name}-Function")
            if 'f-statistic' in dft.columns.tolist():
                dft = dft.sort_values(by=['P-value', 'f-statistic'], ascending=[True, False], ignore_index=True)
            elif 't-statistic' in dft.columns.tolist():
                dft = dft.sort_values(by=['P-value', 't-statistic'], ascending=[True, False], ignore_index=True)
            df_top = dft.head(top_number)

            if rename_taxa:
                df_top['Taxon'] = df_top['Taxon'].apply(lambda x: x.split('|')[-1])
                # df_top = self.rename_taxa(df_top)
            df_top = df_top.pivot(index=func_name, columns='Taxon', values=plot_type)
            print(f"Top [{top_number}] significant: Taxa ({df_top.shape[1]}), Functions ({df_top.shape[0]})")
            df_plot = df_top.fillna(1) if plot_type == 'P-value' else df_top.fillna(0)
            
            sns.set_style("white")

            if return_type == 'fig':
                sns_params = {
                    "center": 0,
                    "cmap": cmap,
                    "linewidths": 0.2,
                    "linecolor": (0, 0, 0, 0.1), # last value is alpha value, 0 is transparent, 1 is opaque
                    "dendrogram_ratio": (0.1, 0.2),
                    "figsize": fig_size,
                    "col_cluster": col_cluster,
                    "row_cluster": row_cluster,
                    "method": "average",
                    "metric": "correlation",
                    "cbar_kws": {"label": plot_type, "shrink": 0.5},
                    "standard_scale": scale,
                    "mask": df_top.isnull(),
                    "vmin": 0 if plot_type == 'P-value' else None,
                    "vmax": pvalue if plot_type == 'P-value' else None,
                    "xticklabels": True if show_all_labels[0] else "auto",
                    "yticklabels": True if show_all_labels[1] else "auto",
                }

                fig = sns.clustermap(df_plot, **sns_params)
                fig.ax_heatmap.set_xlabel("Taxa")
                fig.ax_heatmap.set_ylabel("Functions")
                if title == "":
                    title = f"Significant Differences between groups in Taxa-Function (Sorted by {plot_type} Top {top_number})"
                else:
                    title = f"{title} (Sorted by {plot_type} Top {top_number})"

                plt.suptitle(title, fontsize=font_size + 2, weight='bold')

                fig.ax_heatmap.set_xticklabels(
                    fig.ax_heatmap.get_xmajorticklabels(),
                    fontsize=font_size,
                    rotation=90,
                )
                fig.ax_heatmap.set_yticklabels(
                    fig.ax_heatmap.get_ymajorticklabels(),
                    fontsize=font_size,
                    rotation=0,
                )
                    
                cbar = fig.ax_heatmap.collections[0].colorbar
                cbar.set_label(plot_type, rotation=90, labelpad=1, fontsize=font_size)
                cbar.ax.yaxis.set_ticks_position('left')
                cbar.ax.yaxis.set_label_position('left')

                plt.subplots_adjust(left=0.06, bottom=0.35, right=0.5, top=0.96, wspace=0.01, hspace=0.01)

                plt.tight_layout()
                plt.show()
                return fig

            
            elif return_type == 'table':
                sns_params = {
                    "center": 0,
                    "cmap": cmap,
                    "col_cluster": col_cluster,
                    "row_cluster": row_cluster,
                    "method": "average",
                    "metric": "correlation",
                    "standard_scale": scale,
                    "mask": df_top.isnull(),
                }
                fig = sns.clustermap(df_plot, **sns_params)
                              
                # get the sorted dataframe
                row_num = len(df_plot)
                col_num = len(df_plot.columns)
                if row_num > 1 and col_num < 2:
                    sorted_df = df_plot.iloc[fig.dendrogram_row.reordered_ind, :] if row_cluster else df_plot
                elif row_num < 2 and col_num > 1:
                    sorted_df = df_plot.iloc[:, fig.dendrogram_col.reordered_ind] if col_cluster else df_plot
                elif row_num > 1 and col_num > 1:
                    sorted_df = df_plot.iloc[fig.dendrogram_row.reordered_ind if row_cluster else slice(None),
                                        fig.dendrogram_col.reordered_ind if col_cluster else slice(None)]
                else:
                    sorted_df = df_plot
                # remove fig object
                plt.close(fig.figure)
                return sorted_df                
                
        except ValueError as e:
            print(f"Error: {e}")
            plt.close('all')
            raise ValueError(f"Error: {e}")
    

    # For taxa, func and peptides table
    def plot_basic_heatmap_of_test_res(self, df, top_number:int = 100, value_type:str = 'p', 
                                       fig_size:tuple|None = None, pvalue:float = 0.05, scale = None, 
                                       col_cluster:bool = True, row_cluster:bool = True,
                                       cmap:str|None = None, rename_taxa:bool = True, font_size:int = 10,
                                       show_all_labels:tuple = (False, False), rename_sample:bool = True
                                       ):

        dft = df.copy()

        scale_map ={None: None,
                    'None': None,
                    'row': 0,
                    'column': 1}
        scale = scale_map.get(scale)

        type_map = {'f': ('f-statistic', 'Spectral_r'),
                    'p': ('P-value', 'RdGy_r'), # Reds, hot_r were used before
                    't': ('t-statistic', 'RdGy_r')}

        if cmap is None:
            plot_type, cmap = type_map.get(value_type)
        else:
            plot_type, _ = type_map.get(value_type)

        if plot_type is None:
            raise ValueError("type must be 'p' or 'f' or 't'")

        
        if plot_type not in df.columns:
            plot_type = 'P-value'

        
        dft = dft[dft['P-value'] < pvalue]


        if 'f-statistic' in dft.columns.tolist():
            dft = dft.sort_values(by=['P-value', 'f-statistic'], ascending=[True, False])
            mat = dft.head(top_number)
            mat= mat.drop(['P-value', 'f-statistic' ], axis=1)
        elif 't-statistic' in dft.columns.tolist():
            dft = dft.sort_values(by=['P-value', 't-statistic'], ascending=[True, False])
            mat = dft.head(top_number)
            mat= mat.drop(['P-value', 't-statistic'], axis=1)
        else:
            raise ValueError("No 'f-statistic' or 't-statistic' in the dataframe")

        if len(mat) < 2:
            row_cluster = False
        if len(mat.columns) < 2:
            col_cluster = False
            
        meta_df = self.tfa.meta_df
        meta_name = self.tfa.meta_name


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
            sns_params = {'center': 0, 'cmap': cmap, 'figsize': fig_size,
                          'cbar_kws': {'label': 'Intensity',"shrink": 0.5},
                          'col_cluster': col_cluster, 'row_cluster': row_cluster,
                            'standard_scale': scale, 'col_colors': color_list,
                                "xticklabels":True if show_all_labels[0] else "auto", "yticklabels":True if show_all_labels[1] else "auto"}
            fig = sns.clustermap(mat, **sns_params)


            fig.ax_heatmap.set_xticklabels(fig.ax_heatmap.get_xmajorticklabels(), fontsize=font_size, rotation=90)
            fig.ax_heatmap.set_yticklabels(fig.ax_heatmap.get_ymajorticklabels(), fontsize=font_size, rotation=0)
            plt.suptitle(
                f"The Heatmap of intensity sorted by {plot_type} of Significant differences between groups (top {top_number})",
                fontsize=font_size + 2, weight='bold'
            )
            cbar = fig.ax_heatmap.collections[0].colorbar
            cbar.set_label("Intensity", rotation=90, labelpad=1, fontsize=font_size)
            cbar.ax.yaxis.set_ticks_position('left')
            cbar.ax.yaxis.set_label_position('left')

            plt.subplots_adjust(left=0.05, bottom=0.11, right=0.5, top=0.96, wspace=0.01, hspace=0.01)
            
            plt.tight_layout()
            plt.show()
            return fig
        except Exception as e:
            print(f'Error: {e}')
            plt.close('all')
            raise ValueError("No significant differences")
 

    # Plot basic heatmap of matrix with color bar
    # EXAMPLE: plot_heatmap(sw, mat=get_top_intensity_matrix_of_test_res(df=df_anova, df_type='anova', top_num=100), 
                #  title = 'The heatmap of top 100 significant differences between groups in Taxa-Function', 
                #  fig_size=(30,30), scale=0)
    def plot_basic_heatmap(self,  df, title = 'Heatmap',fig_size:tuple|None = None, 
                    scale = None, col_cluster:bool = True, row_cluster:bool = True, 
                    cmap:str|None = None, rename_taxa:bool = True, font_size:int = 10,
                    show_all_labels:tuple = (False, False), rename_sample:bool = True, plot_mean:bool = False
                    ):
        
        if plot_mean:
            df = self.tfa.BasicStats.get_stats_mean_df_by_group(df)
            rename_sample = False
            
        
        if len(df) < 2:
            row_cluster = False
        if len(df.columns) < 2:
            col_cluster = False
        
        scale_map ={None: None,
            'None': None,
            'row': 0,
            'column': 1}
        scale = scale_map.get(scale)

        mat = df.copy()
        meta_df = self.tfa.meta_df
        meta_name = self.tfa.meta_name

        # if index is Taxon, rename index
        if rename_taxa:
            mat = self.rename_taxa(mat)

        if cmap is None:
            cmap = 'Spectral_r'
        if fig_size is None:
            fig_size = (30,30)


        if rename_sample:
            mat, group_list = self.tfa.add_group_name_for_sample(mat)
        else:
            group_list = [self.tfa.get_group_of_a_sample(i) for i in mat.columns] if not plot_mean else mat.columns.tolist()
        
        color_list = self.assign_colors(group_list)

        
        # if only one column, remove col_cluster, set scale to None
        if len(mat.columns) < 2:
            col_cluster = False
            scale = None
        sns_params = {'center': 0, 'cmap': cmap, 'figsize': fig_size,
                      'linewidths': .01, 'linecolor': (0/255, 0/255, 0/255, 0.01), "dendrogram_ratio":(.1, .2), 
                        'cbar_kws': {'label': 'Intensity',"shrink": 0.5}, 'col_cluster': col_cluster, 'row_cluster': row_cluster,
                        'standard_scale': scale, 'col_colors': color_list if not plot_mean  else None,
                            "xticklabels":True if show_all_labels[0] else "auto", "yticklabels":True if show_all_labels[1] else "auto"}
        fig = sns.clustermap(mat, **sns_params)
            
        # fig  = sns.clustermap(mat, center=0,  cmap = cmap ,figsize=fig_size,
        #                 cbar_kws={'label': 'Intensity'}, col_cluster=col_cluster, row_cluster=row_cluster,
        #                     standard_scale=scale, col_colors=color_list)

        fig.ax_heatmap.set_xticklabels(fig.ax_heatmap.get_xmajorticklabels(), fontsize=font_size, rotation=90)
        fig.ax_heatmap.set_yticklabels(fig.ax_heatmap.get_ymajorticklabels(), fontsize=font_size, rotation=0)
        plt.suptitle(title, fontsize=font_size + 2, weight='bold')
        
        cbar = fig.ax_heatmap.collections[0].colorbar
        cbar.set_label('Intensity', rotation=90, labelpad=1, fontsize=font_size)
        cbar.ax.yaxis.set_ticks_position('left')
        cbar.ax.yaxis.set_label_position('left')

        plt.subplots_adjust(left=0.05, bottom=0.15, right=0.5, top=0.96, wspace=0.01, hspace=0.01)
        plt.tight_layout()
        plt.show()
        return fig


        # For taxa-func heatmap
    # get the top intensity matrix of taxa-func table
    def get_top_across_table(self, df, top_number:str|int = 100, value_type:str = 'p', pvalue:float = 0.05, 
                             rename_taxa:bool = False, col_cluster:bool = True, row_cluster:bool = True):
        res = self.plot_top_taxa_func_heatmap_of_test_res(df=df, top_number=top_number, value_type=value_type, pvalue=pvalue, 
                                                          col_cluster=col_cluster, row_cluster=row_cluster, rename_taxa=rename_taxa, return_type='table')
        return res
    
    # plot heatmap for all condtion results of DESeq2All or DunnettAll
    def plot_heatmap_of_all_condition_res(self, df,  pvalue:float = 0.05,scale:str|None = None, log2fc_min:float = 1.0,log2fc_max:float = 30.0,
                                       fig_size:tuple = (10,10), col_cluster:bool = True, row_cluster:bool = True,
                                       cmap:str|None = None, rename_taxa:bool = True, font_size:int = 10, 
                                       show_all_labels:tuple = (False, False), 
                                       return_type:str = 'fig', res_df_type:str = 'deseq2',
                                       p_type:str = 'padj', three_levels_df_type: str = 'same_trends',
                                       show_col_colors:bool = True, remove_zero_col:bool = True):
        import numpy as np
        # keep 4 decimal places
        pvalue = round(pvalue, 4)
        color_list = None
        if df.columns.nlevels == 2:
            if res_df_type == 'deseq2':
                dft = self.tfa.CrossTest.extrcat_significant_fc_from_deseq2all(df, p_value=pvalue, log2fc_min=log2fc_min, 
                                                                log2fc_max=log2fc_max, p_type=p_type)
            elif res_df_type == 'dunnet':
                dft = self.tfa.CrossTest.extrcat_significant_stat_from_dunnett(df, p_value=pvalue)
                
        elif df.columns.nlevels == 3:
            df_dict = self.tfa.CrossTest.extrcat_significant_fc_from_all_3_levels(df, p_value=pvalue, 
                                                                            log2fc_min=log2fc_min, log2fc_max=log2fc_max,
                                                                            p_type=p_type, df_type = res_df_type)
            dft = df_dict[three_levels_df_type].copy()
            # set level 1 index as the column color
            dft.columns = ['_'.join(col) for col in dft.columns]
            sample_list = dft.columns.tolist()
            group_list = []
            for i in sample_list:
                group_name = i.split('_')[0]
                group_list.append(group_name)
            color_list = self.assign_colors(group_list)
                    
        if dft.empty or dft is None:
            if res_df_type == 'deseq2':
                error_msg = f"No significant differences Results in {p_type} <= {pvalue}, {log2fc_min} <= log2fc <= {log2fc_max} for {three_levels_df_type} in DESeq2All"
            else:
                error_msg = f"No significant differences Results in p-value < {pvalue} for {three_levels_df_type} in Dunnett test"
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
                dft = self.scale_data(dft, scale)
            
            if cmap is None:
                cmap = sns.color_palette("vlag", as_cmap=True, n_colors=30)
            
            # 标准化颜色映射以使 0 处为白色
            from matplotlib.colors import TwoSlopeNorm
            vmax = np.max(np.abs(dft.values))  # 获取数据的最大绝对值
            norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)

            sns_params = {'cmap': cmap, 'figsize': fig_size,'norm': norm,'linewidths': .01, 
                          'linecolor': (0/255, 0/255, 0/255, 0.01), "dendrogram_ratio":(.1, .2), 
                        'col_cluster': col_cluster, 'row_cluster': row_cluster,
                        'cbar_kws': {"label":'log2FoldChange' if res_df_type == 'deseq2' else 't-statistic',
                                     "shrink": 0.5},
                        'xticklabels':True if show_all_labels[0] else "auto",
                        "yticklabels":True if show_all_labels[1] else "auto",
                        "col_colors":color_list if show_col_colors else None}
            
            if return_type == 'fig':
                fig = sns.clustermap(dft, **sns_params)

                fig.ax_heatmap.set_xticklabels(fig.ax_heatmap.get_xmajorticklabels(), fontsize=font_size, rotation=90)
                fig.ax_heatmap.set_yticklabels(fig.ax_heatmap.get_ymajorticklabels(), fontsize=font_size, rotation=0)
                if res_df_type == 'deseq2':
                    title = f"The Heatmap of log2FoldChange calculated by DESeq2 ({p_type} <= {pvalue}, {log2fc_min} <= log2fc <= {log2fc_max}, scaled by {scale})"
                else:
                    title = f"The Heatmap of t-statistic calculated by Dunnett test (p-value < {pvalue}, scaled by {scale})"                
                
                plt.suptitle(title, fontsize=font_size + 2, weight='bold')
                
                cbar = fig.ax_heatmap.collections[0].colorbar
                cbar.set_label("log2FC" if res_df_type == 'deseq2' else 't-statistic', 
                               rotation=90, labelpad=1, fontsize=font_size)
                cbar.ax.yaxis.set_ticks_position('left')
                cbar.ax.yaxis.set_label_position('left')

                plt.subplots_adjust(left=0.05, bottom=0.15, right=0.5, top=0.96, wspace=0.01, hspace=0.01)

                plt.tight_layout()
                plt.show()

                if 'df_dict' in locals():
                    return fig, df_dict
                else:
                    return fig
            elif return_type == 'table':
                fig = sns.clustermap(dft, norm=norm, 
                                    col_cluster=col_cluster, row_cluster=row_cluster,                                
                                    )
                
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
                                       show_all_labels:tuple = (False, False),  show_col_colors:bool = False    
                                       ):
        #! 只画t-statistic的heatmap, 用p-value过滤
        import pandas as pd
        import numpy as np
        
        
        pvalue = round(pvalue, 5)


        dft = self.tfa.CrossTest.extrcat_significant_stat_from_dunnett(df, p_value=pvalue)
        # fill na with 0
        dft = dft.fillna(0, inplace=False)

        # remove all 0 rows
        dft = dft.loc[~(dft==0).all(axis=1)]
        
        dft = self.tfa.replace_if_two_index(dft)
            

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
                dft = self.scale_data(dft, scale)
                
            
            if cmap is None:
                cmap = sns.color_palette("vlag", as_cmap=True, n_colors=30)

            col_colors = self.get_distinct_colors(len(dft.columns))
            # 标准化颜色映射以使 0 处为白色
            from matplotlib.colors import TwoSlopeNorm
            vmax = np.max(np.abs(dft.values))  # 获取数据的最大绝对值
            norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)

            sns_params = {'cmap': cmap, 'figsize': fig_size,'norm': norm,'linewidths': .01, 'linecolor': (0/255, 0/255, 0/255, 0.01), "dendrogram_ratio":(.1, .2), 
                        'cbar_kws': {"label":'t-statistic', "shrink": 0.5}, 'col_cluster': col_cluster, 'row_cluster': row_cluster,"col_colors":col_colors if show_col_colors else None,
                        'xticklabels':True if show_all_labels[0] else "auto", "yticklabels":True if show_all_labels[1] else "auto"}
            fig = sns.clustermap(dft, **sns_params)

            fig.ax_heatmap.set_xticklabels(fig.ax_heatmap.get_xmajorticklabels(), fontsize=font_size, rotation=90)
            fig.ax_heatmap.set_yticklabels(fig.ax_heatmap.get_ymajorticklabels(), fontsize=font_size, rotation=0)
            plt.suptitle(f"The Heatmap of t-statistic calculated by Dunnett test (p-value < {pvalue}, scaled by {scale})", 
                         fontsize=font_size + 2, weight='bold')

            cbar = fig.ax_heatmap.collections[0].colorbar
            cbar.set_label('t-statistic', rotation=90, labelpad=1, fontsize=font_size)
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
                                        col_cluster:bool = True, row_cluster:bool = True, rename_taxa:bool = True):
        import pandas as pd
        import numpy as np
        
        def scale_data(dft, scale):
            if scale == 'row':
                # 对每行单独应用双向缩放
                for index, row in dft.iterrows():
                    max_val = abs(row).max()
                    if max_val != 0:
                        dft.loc[index] = row / max_val
            elif scale == 'col':
                # 对每列单独应用双向缩放
                for col in dft:
                    max_val = abs(dft[col]).max()
                    if max_val != 0:
                        dft[col] = dft[col] / max_val
            elif scale == 'all':
                # 对整个数据框应用双向缩放
                max_val = abs(dft.values).max()
                if max_val != 0:
                    dft = dft / max_val

            return dft
        
        
        dft = self.tfa.CrossTest.extrcat_significant_stat_from_dunnett(df, p_value=pvalue)

        # fill na with 0
        dft = dft.fillna(0, inplace=False)

        # remove all 0 rows
        dft = dft.loc[~(dft==0).all(axis=1)]
        
        dft = self.tfa.replace_if_two_index(dft)
            

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
                dft = scale_data(dft, scale)
                
            
            from matplotlib.colors import TwoSlopeNorm
            vmax = np.max(np.abs(dft.values))  # 获取数据的最大绝对值
            norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)


            fig = sns.clustermap(dft, norm=norm, 
                                col_cluster=col_cluster, row_cluster=row_cluster,
                                cbar_kws = dict(label='t-statistic'),
                                   )

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
        
        

    def get_top_across_table_basic(self, df, top_number:int = 100, value_type:str = 'p', 
                                       fig_size:tuple|None = None, pvalue:float = 0.05, scale = None, 
                                       col_cluster:bool = True, row_cluster:bool = True, cmap:str|None = None, rename_taxa:bool = False):
        dft = df.copy()

        scale_map ={None: None,
                    'None': None,
                    'row': 0,
                    'column': 1}
        scale = scale_map.get(scale)

        type_map = {'f': ('f-statistic', 'Spectral_r'),
                    'p': ('P-value', 'Reds_r'),
                    't': ('t-statistic', 'hot_r')}

        if cmap is None:
            plot_type, cmap = type_map.get(value_type)
        else:
            plot_type, _ = type_map.get(value_type)

        if plot_type is None:
            raise ValueError("type must be 'p' or 'f' or 't'")

        
        if plot_type not in df.columns:
            plot_type = 'P-value'

        
        dft = dft[dft['P-value'] < pvalue]


        if 'f-statistic' in dft.columns.tolist():
            dft = dft.sort_values(by=['P-value', 'f-statistic'], ascending=[True, False])
            mat = dft.head(top_number)
            mat= mat.drop(['P-value', 'f-statistic' ], axis=1)
        elif 't-statistic' in dft.columns.tolist():
            dft = dft.sort_values(by=['P-value', 't-statistic'], ascending=[True, False])
            mat = dft.head(top_number)
            mat= mat.drop(['P-value', 't-statistic'], axis=1)

        if len(mat) < 2:
            row_cluster = False
        if len(mat.columns) < 2:
            col_cluster = False
            
        meta_df = self.tfa.meta_df
        meta_name = self.tfa.meta_name


        if fig_size is None:
            fig_size = (5,5)

        
        
        try:
            # create color list for groups & rename columns
            col_names = mat.columns.tolist()
            groups_list = []
            new_col_names = []
            for i in col_names:
                group = meta_df[meta_df['Sample'] == i]
                group = group[meta_name].values[0]
                new_col_names.append(f'{i} ({group})')
                groups_list.append(group)
            color_list = self.assign_colors(groups_list)
            mat.columns = new_col_names
            
            if rename_taxa:
                mat = self.rename_taxa(mat)
                
            fig  = sns.clustermap(mat, center=0,  cmap = cmap ,figsize=fig_size,
                            cbar_kws={'label': 'Intensity'}, col_cluster=col_cluster, row_cluster=row_cluster,
                                standard_scale=scale, col_colors=color_list)

            # get the sorted dataframe
            if row_cluster and not col_cluster:
                sorted_df = mat.iloc[fig.dendrogram_row.reordered_ind, :]
            elif col_cluster and not row_cluster:
                sorted_df = mat.iloc[:, fig.dendrogram_col.reordered_ind]
            elif row_cluster and col_cluster:
                sorted_df = mat.iloc[fig.dendrogram_row.reordered_ind, fig.dendrogram_col.reordered_ind]
            else:
                sorted_df = mat
            
            
            plt.close(fig.fig)

            return sorted_df
        except Exception as e:
            print(f'Error: {e}')
            raise ValueError("Can not get the result table, please check the error message in consel.")
        # finally:
        #     plt.close('all')


    def scale_data(self, dft, scale):
        try:
            if scale == 'row':
                # 对每行单独应用双向缩放
                for index, row in dft.iterrows():
                    max_val = abs(row).max()
                    if max_val != 0:
                        dft.loc[index] = row / max_val
            elif scale == 'col':
                # 对每列单独应用双向缩放
                for col in dft:
                    max_val = abs(dft[col]).max()
                    if max_val != 0:
                        dft[col] = dft[col] / max_val
            elif scale == 'all':
                # 对整个数据框应用双向缩放
                max_val = abs(dft.values).max()
                if max_val != 0:
                    dft = dft / max_val
                    
        except Exception as e:
            print(f'Error: {e}')

        return dft
