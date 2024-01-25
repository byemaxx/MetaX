
from distinctipy import distinctipy
import seaborn as sns
import matplotlib.pyplot as plt

class HeatmapPlot:
    def __init__(self, tfobj):
        self.tfa =  tfobj
    # input: df, func_name, top_number, value_type, fig_size
    # EXAMPLE: plot_top_taxa_func_heatmap_of_test_res(df_anova, sw.func, 200, 'f', (30,30))
        # reset sns style
        sns.set()

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
    def plot_top_taxa_func_heatmap_of_test_res(self, df, top_number:str = 100, 
                                        value_type:str = 'p', fig_size:tuple = None, pvalue:float = 0.05, 
                                        cmap:str = None, rename_taxa:bool = True, font_size:int = 10, title:str = '',
                                        show_all_labels:tuple = (False, False)):

        

        func_name = self.tfa.func_name
        dft = df.copy()
        dft.reset_index(inplace=True)
        type_map = {'f': ('f-statistic', 'Spectral_r', 1),
                    'p': ('P-value', 'Reds_r', None),
                    't': ('t-statistic', 'hot_r', 1)}

        if cmap is None:
            plot_type, cmap, scale = type_map.get(value_type, None)
        else:
            plot_type, _, scale = type_map.get(value_type, None)

        if plot_type is None:
            raise ValueError("type must be 'p' or 'f' or 't'")

        
        if plot_type not in df.columns:
            plot_type = 'P-value'


        try:
            dft = dft[dft['P-value'] < pvalue]
            print(f"Number of significant differences between groups in {func_name}-Function: {dft.shape[0]}")
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
            df_plot = df_top.fillna(1) if plot_type == 'P-value' else df_top.fillna(0)
            
            sns.set_style("white")
            sns_params = {'center': 0, 'cmap': cmap, 'linewidths': .01, 'linecolor': (0/255, 0/255, 0/255, 0.01), "dendrogram_ratio":(.1, .2), 
                          'figsize': fig_size,
                          'method': 'average', 'metric': 'correlation', 'cbar_kws': {'label': plot_type, "shrink": 0.5},
                            'standard_scale': scale, 'mask': df_top.isnull(), 'vmin': 0, 'vmax': 1,
                                "xticklabels":True if show_all_labels[0] else "auto", "yticklabels":True if show_all_labels[1] else "auto"}
            fig = sns.clustermap(df_plot, **sns_params)


            fig.ax_heatmap.set_xlabel('Taxa')
            fig.ax_heatmap.set_ylabel('Function')
            if title == '':
                fig.ax_col_dendrogram.set_title(f"Significant Differences between groups in Taxa-Function (Sorted by {plot_type} Top {top_number})")
            else:
                title = f'{title} (Sorted by {plot_type} Top {top_number})'
                fig.ax_col_dendrogram.set_title(title)
            fig.ax_heatmap.set_xticklabels(fig.ax_heatmap.get_xmajorticklabels(), fontsize=font_size, rotation=90)
            fig.ax_heatmap.set_yticklabels(fig.ax_heatmap.get_ymajorticklabels(), fontsize=font_size, rotation=0)
            
            plt.subplots_adjust(left=0.05, bottom=0.4, right=0.5, top=0.95, wspace=0.2, hspace=0.2)
            plt.tight_layout()
            plt.show()
            return fig
        except ValueError as e:
            print(f"Error: {e}")
            plt.close('all')
            raise ValueError(f"No significant differences between groups in {func_name}")
    

    # For taxa, func and peptides table
    def plot_basic_heatmap_of_test_res(self, df, top_number:int = 100, value_type:str = 'p', 
                                       fig_size:tuple = None, pvalue:float = 0.05, scale = None, 
                                       col_cluster:bool = True, row_cluster:bool = True,
                                       cmap:str = None, rename_taxa:bool = True, font_size:int = 10,
                                       show_all_labels:tuple = (False, False)):

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

        def assign_colors(groups):
            colors = distinctipy.get_colors(len(set(groups)))
            result = []
            for group in groups:
                index = sorted(set(groups)).index(group)
                result.append(colors[index])
            return result
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
            color_list = assign_colors(groups_list)
            mat.columns = new_col_names
            if rename_taxa:
                mat = self.rename_taxa(mat)
            sns_params = {'center': 0, 'cmap': cmap, 'figsize': fig_size,
                          'cbar_kws': {'label': 'Intensity'}, 'col_cluster': col_cluster, 'row_cluster': row_cluster,
                            'standard_scale': scale, 'col_colors': color_list,
                                "xticklabels":True if show_all_labels[0] else "auto", "yticklabels":True if show_all_labels[1] else "auto"}
            fig = sns.clustermap(mat, **sns_params)


            fig.ax_heatmap.set_xticklabels(fig.ax_heatmap.get_xmajorticklabels(), fontsize=font_size, rotation=90)
            fig.ax_heatmap.set_yticklabels(fig.ax_heatmap.get_ymajorticklabels(), fontsize=font_size, rotation=0)
            fig.ax_col_dendrogram.set_title(f"The Heatmap of intensity sorted by {plot_type} of Significant differences between groups (top {top_number})")

            plt.subplots_adjust(left=0.05, bottom=0.4, right=0.5, top=0.95, wspace=0.2, hspace=0.2)
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
    def plot_basic_heatmap(self,  df, title = 'Heatmap',fig_size:tuple = None, 
                    scale = None, col_cluster:bool = True, row_cluster:bool = True, 
                    cmap:str = None, rename_taxa:bool = True, font_size:int = 10,
                    show_all_labels:tuple = (False, False)
                    ):
        
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

        def assign_colors(groups):
            colors = distinctipy.get_colors(len(set(groups)))
            result = []
            for group in groups:
                index = sorted(set(groups)).index(group)
                result.append(colors[index])
            return result



        # create color list for groups & rename columns
        col_names = mat.columns.tolist()
        groups_list = []
        new_col_names = []
        for i in col_names:
            group = meta_df[meta_df['Sample'] == i]
            group = group[meta_name].values[0]
            new_col_names.append(f'{i} ({group})')
            groups_list.append(group)
        color_list = assign_colors(groups_list)
        mat.columns = new_col_names
        
        # if only one column, remove col_cluster, set scale to None
        if len(mat.columns) < 2:
            col_cluster = False
            scale = None
        sns_params = {'center': 0, 'cmap': cmap, 'figsize': fig_size,
                      'linewidths': .01, 'linecolor': (0/255, 0/255, 0/255, 0.01), "dendrogram_ratio":(.1, .2), 
                        'cbar_kws': {'label': 'Intensity',"shrink": 0.5}, 'col_cluster': col_cluster, 'row_cluster': row_cluster,
                        'standard_scale': scale, 'col_colors': color_list,
                            "xticklabels":True if show_all_labels[0] else "auto", "yticklabels":True if show_all_labels[1] else "auto"}
        fig = sns.clustermap(mat, **sns_params)
            
        # fig  = sns.clustermap(mat, center=0,  cmap = cmap ,figsize=fig_size,
        #                 cbar_kws={'label': 'Intensity'}, col_cluster=col_cluster, row_cluster=row_cluster,
        #                     standard_scale=scale, col_colors=color_list)

        fig.ax_heatmap.set_xticklabels(fig.ax_heatmap.get_xmajorticklabels(), fontsize=font_size, rotation=90)
        fig.ax_heatmap.set_yticklabels(fig.ax_heatmap.get_ymajorticklabels(), fontsize=font_size, rotation=0)
        fig.ax_col_dendrogram.set_title(title)


        plt.subplots_adjust(left=0.05, bottom=0.4, right=0.5, top=0.95, wspace=0.2, hspace=0.2)
        plt.tight_layout()
        plt.show()
        return fig


        # For taxa-func heatmap
    # get the top intensity matrix of taxa-func table
    def get_top_across_table(self, df, top_number:str = 100, value_type:str = 'p', pvalue:float = 0.05, rename_taxa:bool = False, col_cluster:bool = True, row_cluster:bool = True):
        func_name = self.tfa.func_name
        dft = df.copy()
        dft.reset_index(inplace=True)

        if value_type == 'f':
            plot_type = 'f-statistic'
            color = 'Spectral_r'
            scale = 1
        elif value_type == 'p':
            plot_type = 'P-value'
            color = 'Reds_r'
            scale = None
        elif value_type == 't':
            plot_type = 't-statistic'
            color = 'hot_r'
            scale = 1
        else:
            raise ValueError("type must be 'p' or 'f' or 't'")
        if plot_type not in df.columns:
            plot_type = 'P-value'


        try:        
            dft = dft[dft['P-value'] < pvalue]
            if dft.empty:
                raise ValueError(f"No significant differences between groups")
            if 'f-statistic' in dft.columns.tolist():
                dft = dft.sort_values(by=['P-value', 'f-statistic'], ascending=[True, False], ignore_index=True)
            elif 't-statistic' in dft.columns.tolist():
                dft = dft.sort_values(by=['P-value', 't-statistic'], ascending=[True, False], ignore_index=True)
            df_top = dft.head(top_number)
            
            if rename_taxa:
                df_top['Taxon'] = df_top['Taxon'].apply(lambda x: x.split('|')[-1])

            df_top = df_top.pivot(index=func_name, columns='Taxon', values=plot_type)
            mat = df_top.fillna(1) if plot_type == 'P-value' else df_top.fillna(0)
                
                
            # plt.figure()
            fig = sns.clustermap(mat, center=0, cmap = color, col_cluster=col_cluster, row_cluster=row_cluster,
                            method='average',  metric='correlation',cbar_kws={'label': plot_type}, 
                            standard_scale=scale, mask=df_top.isnull(), vmin=0, vmax=1)


            # get the sorted dataframe
            row_num = len(mat)
            col_num = len(mat.columns)
            if row_num > 1 and col_num < 2:
                sorted_df = mat.iloc[fig.dendrogram_row.reordered_ind, :]
            elif row_num < 2 and col_num > 1:
                sorted_df = mat.iloc[:, fig.dendrogram_col.reordered_ind]
            elif row_num > 1 and col_num > 1:
                sorted_df = mat.iloc[fig.dendrogram_row.reordered_ind, fig.dendrogram_col.reordered_ind]
            else:
                sorted_df = mat
            # remove fig object
            plt.close(fig.fig)
            return sorted_df
        except ValueError as e:
            print(e)
            raise ValueError(f"No significant differences between groups")
        # finally:
        #     plt.close('all')

    def plot_heatmap_of_deseq2all_res(self, df,  pvalue:float = 0.05,scale:str = None, log2fc_min:float = 1.0,log2fc_max:float = 30.0,
                                       fig_size:tuple = (10,10), col_cluster:bool = True, row_cluster:bool = True,
                                       cmap:str = None, rename_taxa:bool = True, font_size:int = 10,show_all_labels:tuple = (False, False), 
                                       return_type:str = 'fig', show_num:bool = False, p_type:str = 'padj'):
        import numpy as np
        
        if df.columns.nlevels == 2:
            dft = self.tfa.extrcat_significant_fc_from_deseq2all(df, p_value=pvalue, log2fc_min=log2fc_min, log2fc_max=log2fc_max, p_type=p_type)
        elif df.columns.nlevels == 3:
            df_dict = self.tfa.extrcat_significant_fc_from_deseq2all_3_levels(df, p_value=pvalue, log2fc_min=log2fc_min, log2fc_max=log2fc_max, p_type=p_type)
            dft = df_dict['same_trends']
            dft.columns = ['_'.join(col) for col in dft.columns]
            col_cluster = False

        if dft.empty or dft is None:
            raise ValueError(f"No significant differences Results in {p_type} <= {pvalue}, {log2fc_min} <= log2fc <= {log2fc_max}")
        
        # fill na with 0
        dft = dft.fillna(0, inplace=False)
        
        
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

            sns_params = {'cmap': cmap, 'figsize': fig_size,'norm': norm,'linewidths': .01, 'linecolor': (0/255, 0/255, 0/255, 0.01), "dendrogram_ratio":(.1, .2), 
                        'col_cluster': col_cluster, 'row_cluster': row_cluster,'cbar_kws': {"label":'log2FoldChange', "shrink": 0.5},'annot':show_num, 'fmt':'.2f',
                        'xticklabels':True if show_all_labels[0] else "auto", "yticklabels":True if show_all_labels[1] else "auto"}
            if return_type == 'fig':
                fig = sns.clustermap(dft, **sns_params)

                fig.ax_heatmap.set_xticklabels(fig.ax_heatmap.get_xmajorticklabels(), fontsize=font_size, rotation=90)
                fig.ax_heatmap.set_yticklabels(fig.ax_heatmap.get_ymajorticklabels(), fontsize=font_size, rotation=0)
                fig.ax_col_dendrogram.set_title(f"The Heatmap of log2FoldChange calculated by DESeq2 ({p_type} <= {pvalue}, {log2fc_min} <= log2fc <= {log2fc_max}, scaled by {scale})", fontsize=font_size)

                plt.subplots_adjust(left=0.05, bottom=0.4, right=0.5, top=0.95, wspace=0.2, hspace=0.2)
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
                
                plt.close(fig.fig)

                return sorted_df
                            
        except Exception as e:
            print(f'Error: {e}')
            plt.close('all')
            raise ValueError(f"Error: {e}")

    # For taxa, func and peptides table
    def plot_heatmap_of_dunnett_test_res(self, df,  pvalue:float = 0.05,scale:str = None,
                                       fig_size:tuple = None, col_cluster:bool = True, row_cluster:bool = True,
                                       cmap:str = None, rename_taxa:bool = True, font_size:int = 10,show_all_labels:tuple = (False, False)):
        #! 只画t-statistic的heatmap, 用p-value过滤
        import pandas as pd
        import numpy as np
        
        
        pvalue = round(pvalue, 5)


        df_pvalue = df.filter(regex='(p_value)')
        df_pvalue.columns = df_pvalue.columns.str.replace(r"(p_value)", "")
        df_tstatistic = df.filter(regex='(t_statistic)')
        df_tstatistic.columns = df_tstatistic.columns.str.replace(r"(t_statistic)", "")


        # only extract the location of pvalue < 0.05
        dft = np.where(df_pvalue > pvalue, 0 , df_tstatistic)
        dft = pd.DataFrame(dft, index=df_pvalue.index, columns=df_pvalue.columns)
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

            
            # 标准化颜色映射以使 0 处为白色
            from matplotlib.colors import TwoSlopeNorm
            vmax = np.max(np.abs(dft.values))  # 获取数据的最大绝对值
            norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)

            sns_params = {'cmap': cmap, 'figsize': fig_size,'norm': norm,'linewidths': .01, 'linecolor': (0/255, 0/255, 0/255, 0.01), "dendrogram_ratio":(.1, .2), 
                        'cbar_kws': {"label":'t-statistic', "shrink": 0.5}, 'col_cluster': col_cluster, 'row_cluster': row_cluster,
                        'xticklabels':True if show_all_labels[0] else "auto", "yticklabels":True if show_all_labels[1] else "auto"}
            fig = sns.clustermap(dft, **sns_params)

            fig.ax_heatmap.set_xticklabels(fig.ax_heatmap.get_xmajorticklabels(), fontsize=font_size, rotation=90)
            fig.ax_heatmap.set_yticklabels(fig.ax_heatmap.get_ymajorticklabels(), fontsize=font_size, rotation=0)
            fig.ax_col_dendrogram.set_title(f"The Heatmap of t-statistic calculated by Dunnett test (p-value < {pvalue}, scaled by {scale})", fontsize=font_size)

            plt.subplots_adjust(left=0.05, bottom=0.4, right=0.5, top=0.95, wspace=0.2, hspace=0.2)
            plt.tight_layout()
            plt.show()
            return fig
        except Exception as e:
            print(f'Error: {e}')
            plt.close('all')
            raise ValueError(f"Error: {e}")


    def get_heatmap_table_of_dunnett_res(self, df,  pvalue:float = 0.05,scale:str = None,
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
        
        
        df_pvalue = df.filter(regex='(p_value)')
        df_pvalue.columns = df_pvalue.columns.str.replace(r"(p_value)", "")
        df_tstatistic = df.filter(regex='(t_statistic)')
        df_tstatistic.columns = df_tstatistic.columns.str.replace(r"(t_statistic)", "")


        # only extract the location of pvalue < 0.05
        dft = np.where(df_pvalue > pvalue, 0 , df_tstatistic)
        dft = pd.DataFrame(dft, index=df_pvalue.index, columns=df_pvalue.columns)
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

    def get_top_across_table_basic(self, df, top_number:int = 100, value_type:str = 'p', 
                                       fig_size:tuple = None, pvalue:float = 0.05, scale = None, 
                                       col_cluster:bool = True, row_cluster:bool = True, cmap:str = None, rename_taxa:bool = False):
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

        def assign_colors(groups):
            colors = distinctipy.get_colors(len(set(groups)))
            result = []
            for group in groups:
                index = sorted(set(groups)).index(group)
                result.append(colors[index])
            return result
        
        
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
            color_list = assign_colors(groups_list)
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

