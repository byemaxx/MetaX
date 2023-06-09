
from distinctipy import distinctipy
import seaborn as sns
import matplotlib.pyplot as plt

class HeatmapPlot:
    def __init__(self, tfobj):
        self.tfobj =  tfobj
    # input: df, func_name, top_number, value_type, fig_size
    # EXAMPLE: plot_top_taxa_func_heatmap_of_test_res(df_anova, sw.func, 200, 'f', (30,30))

    def plot_top_taxa_func_heatmap_of_test_res(self, df, func_name:str, top_number:str = 100, 
                                        value_type:str = 'p', fig_size:tuple = None, pvalue:float = 0.05):

        
        # if fig_size is None:
        #     width, length, front_title, font_size = self._fit_size(df)
        #     fig_size = (width, length)
        # else:
        #     width, length, front_title, font_size = self._fit_size(df)
        
        dft = df.copy()
        dft.reset_index(inplace=True)
        # dft = dft.iloc[:, :4]
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


        
        dft = dft[dft['P-value'] < pvalue]
        print(f"Number of significant differences between groups in {func_name}: {dft.shape[0]}")
        if dft.empty:
            raise ValueError(f"No significant differences between groups in {func_name}")
        if 'f-statistic' in dft.columns.tolist():
            dft = dft.sort_values(by=['P-value', 'f-statistic'], ascending=[True, False], ignore_index=True)
        elif 't-statistic' in dft.columns.tolist():
            dft = dft.sort_values(by=['P-value', 't-statistic'], ascending=[True, False], ignore_index=True)
        df_top = dft.head(top_number)
        #display(df_top)
        df_top = df_top.pivot(index='Taxon', columns=func_name, values=plot_type)
        df_plot = df_top.fillna(1) if plot_type == 'P-value' else df_top.fillna(0)
        
        if len(df_plot) < 2:
            print(f'Not enough significant differences between groups in {func_name}')
            return 'not'

        fig = sns.clustermap(df_plot, center=0, linewidths=.3, linecolor="grey", 
                            figsize=fig_size, cmap = color, 
                        method='average',  metric='correlation',cbar_kws={'label': plot_type}, 
                        standard_scale=scale, mask=df_top.isnull(), vmin=0, vmax=1)

        # fig.ax_heatmap.set_xticklabels(fig.ax_heatmap.get_xmajorticklabels(), fontsize = font_size)
        # fig.ax_heatmap.set_yticklabels(fig.ax_heatmap.get_ymajorticklabels(), fontsize = font_size)
        # fig.ax_heatmap.set_xlabel('Function', fontsize = front_title)
        # fig.ax_heatmap.set_ylabel('Taxa', fontsize = front_title)
        fig.ax_heatmap.set_xlabel('Function')
        fig.ax_heatmap.set_ylabel('Taxa')

        fig.ax_heatmap.set_title(f"Significant differences between groups in Taxa-Function heatmap of {plot_type} (top {top_number})")

        plt.subplots_adjust(left=0.05, bottom=0.4, right=0.5, top=0.95)
        plt.show()
        return fig


    # Plot basic heatmap of matrix with color bar
    # EXAMPLE: plot_heatmap(sw, mat=get_top_intensity_matrix_of_test_res(df=df_anova, df_type='anova', top_num=100), 
                #  title = 'The heatmap of top 100 significant differences between groups in Taxa-Function', 
                #  fig_size=(30,30), scale=0)
    def plot_basic_heatmap(self,  mat, title = 'Heatmap',fig_size:tuple = None, 
                    scale = None, col_cluster:bool = True, row_cluster:bool = True):
        if len(mat) < 2:
            row_cluster = False
        if len(mat.columns) < 2:
            col_cluster = False


        mat = mat.copy()
        meta_df = self.tfobj.meta_df
        meta_name = self.tfobj.meta_name

        # if fig_size is None:
        #     width, length, front_title, font_size = self._fit_size(mat)
        #     fig_size = (width, length)
        # else:
        #     width, length, front_title, font_size = self._fit_size(mat)


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

        fig  = sns.clustermap(mat, center=0,  cmap = 'Spectral_r',figsize=fig_size,
                        cbar_kws={'label': 'Intensity'}, col_cluster=col_cluster, row_cluster=row_cluster,
                            standard_scale=scale, col_colors=color_list)
        # fig  = sns.clustermap(mat, center=0, linewidths=.3, linecolor="grey",  cmap = 'Spectral_r',figsize=fig_size,
        #                 cbar_kws={'label': 'Intensity'}, col_cluster=col_cluster, row_cluster=row_cluster,
        #                     standard_scale=scale, col_colors=color_list)
        # fig.ax_heatmap.set_xticklabels(fig.ax_heatmap.get_xmajorticklabels(), fontsize = font_size)
        # fig.ax_heatmap.set_yticklabels(fig.ax_heatmap.get_ymajorticklabels(), fontsize = font_size)
        # fig.ax_col_dendrogram.set_title(title, fontsize = front_title)
        fig.ax_heatmap.set_xticklabels(fig.ax_heatmap.get_xmajorticklabels())
        fig.ax_heatmap.set_yticklabels(fig.ax_heatmap.get_ymajorticklabels())
        fig.ax_col_dendrogram.set_title(title)

        plt.subplots_adjust(left=0.05, bottom=0.4, right=0.5, top=0.95)
        plt.show()
        return fig



    def get_top_across_table(self, df, func_name:str, top_number:str = 100, value_type:str = 'p', pvalue:float = 0.05):

        dft = df.copy()
        dft.reset_index(inplace=True)
        # dft = dft.iloc[:, :4]
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


        
        dft = dft[dft['P-value'] < pvalue]
        if dft.empty:
            raise ValueError(f"No significant differences between groups in {func_name}")
        if 'f-statistic' in dft.columns.tolist():
            dft = dft.sort_values(by=['P-value', 'f-statistic'], ascending=[True, False], ignore_index=True)
        elif 't-statistic' in dft.columns.tolist():
            dft = dft.sort_values(by=['P-value', 't-statistic'], ascending=[True, False], ignore_index=True)
        df_top = dft.head(top_number)
        #display(df_top)
        df_top = df_top.pivot(index='Taxon', columns=func_name, values=plot_type)
        df_plot = df_top.fillna(1) if plot_type == 'P-value' else df_top.fillna(0)
        if len(df_plot) < 2:
            print(f'Not enough significant differences between groups in {func_name}')
            return 'not'

        fig = sns.clustermap(df_plot, center=0, linewidths=.3, linecolor="grey", cmap = color, 
                        method='average',  metric='correlation',cbar_kws={'label': plot_type}, 
                        standard_scale=scale, mask=df_top.isnull(), vmin=0, vmax=1)


        # get the sorted dataframe
        sorted_df = df_plot.iloc[fig.dendrogram_row.reordered_ind, fig.dendrogram_col.reordered_ind]
        # remove fig object
        plt.close(fig.fig)
        return sorted_df
        


    def get_top_across_table0(self,df, func_name:str, top_number:str = 100, 
                                        value_type:str = 'p'):
        dft = df.copy()
        dft.reset_index(inplace=True)
        # dft = dft.iloc[:, :4]
        if value_type == 'f':
            plot_type = 'f-statistic'

        elif value_type == 'p':
            plot_type = 'P-value'

        elif value_type == 't':
            plot_type = 't-statistic'

        else:
            raise ValueError("type must be 'p' or 'f' or 't'")
        if plot_type not in df.columns:
            plot_type = 'P-value'


        
        dft = dft[dft['P-value'] < 0.05]
        if 'f-statistic' in dft.columns.tolist():
            dft = dft.sort_values(by=['P-value', 'f-statistic'], ascending=[True, False], ignore_index=True)
        elif 't-statistic' in dft.columns.tolist():
            dft = dft.sort_values(by=['P-value', 't-statistic'], ascending=[True, False], ignore_index=True)
        df_top = dft.head(top_number)
        #display(df_top)
        df_top = df_top.pivot(index='Taxon', columns=func_name, values=plot_type)
        df_plot = df_top.fillna(1) if plot_type == 'P-value' else df_top.fillna(0)

        return df_plot


        
    def _fit_size(self, df):
        col_num = len(df.columns)
        row_num = len(df.index)

        # 计算宽度和长度
        width = max(12, min(40, 5 + col_num * 1))
        length = max(12, min(40, 5 + row_num * 0.5))

        # 根据行数和列数调整标题和字体大小
        if row_num > 100 or col_num > 20:
            front_title = 12
            font_size = 8
        else:
            front_title = 10
            font_size = 8
        print(f'Table size: {row_num} x {col_num}')
        print(f'Recommended figure size: width: {width}, length: {length}, front_title: {front_title}, font_size: {font_size}')
        return width, length, front_title, font_size

