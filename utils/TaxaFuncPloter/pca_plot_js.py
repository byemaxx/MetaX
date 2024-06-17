from pyecharts import options as opts
from pyecharts.charts import Scatter3D
from sklearn.decomposition import PCA
import pandas as pd
import seaborn as sns
from .get_distinct_colors import GetDistinctColors

class PcaPlot_js:
    def __init__(self, tfobj=None, theme='white'):
        self.tfobj = tfobj
        self.get_distinct_colors = GetDistinctColors().get_distinct_colors
        self.theme = theme
        
        
    def plot_pca_pyecharts_3d(self, df, title_name='Table',  show_label = True, rename_sample = True,
                              width=10, height=8, font_size = 10, legend_col_num: int | None = None):
        width = f'{width*100}px'
        height = f'{height*100}px'

        dft = df
        sample_list = dft.columns
        new_sample_name = []
        group_list = []
        for i in sample_list:
            group = self.tfobj.get_group_of_a_sample(i)
            new_sample_name.append(f'{i} ({group})')
            group_list.append(group)

        dft = dft.T
        mat = dft.values
        pca = PCA(n_components=3)
        components = pca.fit_transform(mat)
        total_var = pca.explained_variance_ratio_.sum() * 100
        x_name = f'PC1 ({pca.explained_variance_ratio_[0]*100:.2f}%)'
        y_name = f'PC2 ({pca.explained_variance_ratio_[1]*100:.2f}%)'
        z_name = f'PC3 ({pca.explained_variance_ratio_[2]*100:.2f}%)'

        # Create a DataFrame with the PCA results
        pca_df = pd.DataFrame(components, columns=['PC1', 'PC2', 'PC3'])
        pca_df['group'] = group_list
        if rename_sample:
            pca_df['sample_name'] = new_sample_name
        else:
            pca_df['sample_name'] = sample_list
        group_num = len(pca_df['group'].unique())
        
        colors = self.get_distinct_colors(group_num, convert=True)
        
        font_color = 'white' if self.theme == 'dark' else 'black'

        scatter3d = Scatter3D(init_opts=opts.InitOpts(width=width, height=height, theme=self.theme))
        unique_group = [x for i, x in enumerate(group_list) if i == group_list.index(x)]
        for i, group in enumerate(unique_group):
            color = colors[i]
            group_df = pca_df[pca_df['group'] == group]
            # Create a list of tuples, each tuple is a pair of (x, y, z)
            xyz_data = list(
                zip(
                    group_df['PC1'],
                    group_df['PC2'],
                    group_df['PC3'],
                    group_df['sample_name'],
                )
            )

            scatter3d.add(
                series_name=group,
                data=xyz_data,
                xaxis3d_opts=opts.Axis3DOpts(type_="value", name=x_name,
                                             axislabel_opts=opts.LabelOpts(font_size=font_size,
                                                                           color=font_color),
                                             textstyle_opts=opts.TextStyleOpts(font_size=font_size,
                                                                              color=font_color)),
                yaxis3d_opts=opts.Axis3DOpts(type_="value", name=y_name,
                                             axislabel_opts=opts.LabelOpts(font_size=font_size,
                                                                           color=font_color),
                                             textstyle_opts=opts.TextStyleOpts(font_size=font_size,
                                                                              color=font_color)),
                zaxis3d_opts=opts.Axis3DOpts(type_="value", name=z_name,
                                             axislabel_opts=opts.LabelOpts(font_size=font_size,
                                                                           color=font_color),
                                             textstyle_opts=opts.TextStyleOpts(font_size=font_size,
                                                                               color=font_color)),
                itemstyle_opts=opts.ItemStyleOpts(color=color,
                                                  border_color=font_color,
                                                  border_width=0.2,
                                                  opacity=0.8),
                label_opts=opts.LabelOpts(is_show=show_label,
                                          font_size=font_size,
                                          color=font_color,
                                          position='right'),
            )

        scatter3d.set_global_opts(
            title_opts=opts.TitleOpts(title=f'PCA of {str(title_name)} (total variance explained: {total_var:.2f}%)'),
            legend_opts=opts.LegendOpts(
                is_show=True if (legend_col_num != 0) else False,
                type_="scroll",
                page_icon_size=8,
                selector=[
                    {"type": "all", "title": "All"},
                    {"type": "inverse", "title": "Inverse"},
                ],
                pos_left="right",
                orient="vertical",
                pos_top="2%",
                border_width=0,
                textstyle_opts=opts.TextStyleOpts(font_size=font_size),
            ),

        )

        # scatter3d.render_notebook()

        return scatter3d
    




# scatter = plot_pca_pyecharts_3d(sw, df)
# scatter.render_notebook()