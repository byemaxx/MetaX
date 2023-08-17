
from distinctipy import distinctipy
import seaborn as sns
import matplotlib.pyplot as plt

class HeatmapPlot:
    def __init__(self, tfobj):
        self.tfobj =  tfobj
    # input: df, func_name, top_number, value_type, fig_size
    # EXAMPLE: plot_top_taxa_func_heatmap_of_test_res(df_anova, sw.func, 200, 'f', (30,30))
    

    def rename_taxa(self, df):
        first_index = df.index[0]
        if 'd__Bacteria' in first_index:
            if '<' not in first_index:
                index_list = [i.split('|')[-1] for i in df.index]
                df.index = index_list
            else:
                new_index_list = [
                    f'{i.split(" <")[0].split("|")[-1]} <{i.split(" <")[1][:-1]}>'
                    for i in df.index
                ]
                df.index = new_index_list
        return df

    def plot_top_taxa_func_heatmap_of_test_res(self, df, top_number:str = 100, 
                                        value_type:str = 'p', fig_size:tuple = None, pvalue:float = 0.05, cmap:str = None, rename_taxa:bool = True):

        
        # if fig_size is None:
        #     width, length, front_title, font_size = self._fit_size(df)
        #     fig_size = (width, length)
        # else:
        #     width, length, front_title, font_size = self._fit_size(df)
        func_name = self.tfobj.func_name
        dft = df.copy()
        dft.reset_index(inplace=True)
        # dft = dft.iloc[:, :4]
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
            df_top = df_top.pivot(index='Taxon', columns=func_name, values=plot_type)

            df_plot = df_top.fillna(1) if plot_type == 'P-value' else df_top.fillna(0)
            

            fig = sns.clustermap(df_plot, center=0, linewidths=.3, linecolor="grey", 
                                figsize=fig_size, cmap = cmap, 
                            method='average',  metric='correlation',cbar_kws={'label': plot_type}, 
                            standard_scale=scale, mask=df_top.isnull(), vmin=0, vmax=1)


            fig.ax_heatmap.set_xlabel('Function')
            fig.ax_heatmap.set_ylabel('Taxa')

            fig.ax_heatmap.set_title(f"Significant differences between groups in Taxa-Function heatmap of {plot_type} (top {top_number})")

            plt.subplots_adjust(left=0.05, bottom=0.4, right=0.5, top=0.95)
            plt.show()
            return fig
        except ValueError as e:
            print(f"Error: {e}")
            plt.close('all')
            raise ValueError(f"No significant differences between groups in {func_name}")
    


    def plot_basic_heatmap_of_test_res(self, df, top_number:int = 100, value_type:str = 'p', 
                                       fig_size:tuple = None, pvalue:float = 0.05, scale = None, 
                                       col_cluster:bool = True, row_cluster:bool = True, cmap:str = None, rename_taxa:bool = True):

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
            
        meta_df = self.tfobj.meta_df
        meta_name = self.tfobj.meta_name


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

            fig  = sns.clustermap(mat, center=0,  cmap = cmap ,figsize=fig_size,
                            cbar_kws={'label': 'Intensity'}, col_cluster=col_cluster, row_cluster=row_cluster,
                                standard_scale=scale, col_colors=color_list)

            fig.ax_heatmap.set_xticklabels(fig.ax_heatmap.get_xmajorticklabels())
            fig.ax_heatmap.set_yticklabels(fig.ax_heatmap.get_ymajorticklabels())
            fig.ax_col_dendrogram.set_title(f"The Heatmap of intensity sorted by {plot_type} of Significant differences between groups (top {top_number})")

            plt.subplots_adjust(left=0.05, bottom=0.4, right=0.5, top=0.95, wspace=0.2, hspace=0.2)
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
                    scale = None, col_cluster:bool = True, row_cluster:bool = True, cmap:str = None, rename_taxa:bool = True):
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
        meta_df = self.tfobj.meta_df
        meta_name = self.tfobj.meta_name

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

        fig  = sns.clustermap(mat, center=0,  cmap = cmap ,figsize=fig_size,
                        cbar_kws={'label': 'Intensity'}, col_cluster=col_cluster, row_cluster=row_cluster,
                            standard_scale=scale, col_colors=color_list)

        fig.ax_heatmap.set_xticklabels(fig.ax_heatmap.get_xmajorticklabels())
        fig.ax_heatmap.set_yticklabels(fig.ax_heatmap.get_ymajorticklabels())
        fig.ax_col_dendrogram.set_title(title)

        plt.subplots_adjust(left=0.05, bottom=0.4, right=0.5, top=0.95, wspace=0.2, hspace=0.2)
        plt.show()
        return fig



    def get_top_across_table(self, df, top_number:str = 100, value_type:str = 'p', pvalue:float = 0.05):
        func_name = self.tfobj.func_name
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

            df_top = df_top.pivot(index='Taxon', columns=func_name, values=plot_type)
            mat = df_top.fillna(1) if plot_type == 'P-value' else df_top.fillna(0)
            plt.figure()
            fig = sns.clustermap(mat, center=0, linewidths=.3, linecolor="grey", cmap = color,
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
            # plt.close(fig.fig)
            return sorted_df
        except ValueError as e:
            print(e)
            raise ValueError(f"No significant differences between groups")
        finally:
            plt.close('all')

        


    def get_top_across_table_basic(self, df, top_number:int = 100, value_type:str = 'p', 
                                       fig_size:tuple = None, pvalue:float = 0.05, scale = None, 
                                       col_cluster:bool = True, row_cluster:bool = True, cmap:str = None):
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
            
        meta_df = self.tfobj.meta_df
        meta_name = self.tfobj.meta_name


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

            return sorted_df
        except Exception as e:
            print(f'Error: {e}')
            raise ValueError("No significant differences between groups")
        finally:
            plt.close('all')

