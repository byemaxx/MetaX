from pyecharts import options as opts
from pyecharts.charts import Scatter3D
from sklearn.decomposition import PCA
import pandas as pd

class PcaPlot_js:
    def __init__(self, tfobj=None):
        self.tfobj = tfobj

    def plot_pca_pyecharts_3d(self, df, table_name='Table',  show_label = True, width=10, height=8):
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
        pca_df['sample_name'] = new_sample_name
        group_num = len(pca_df['group'].unique())
        colors = self.get_distinct_colors(group_num)

        scatter3d = Scatter3D(init_opts=opts.InitOpts(width=width, height=height))

        for i, group in enumerate(pca_df['group'].unique()):
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
                xaxis3d_opts=opts.Axis3DOpts(type_="value", name=x_name),
                yaxis3d_opts=opts.Axis3DOpts(type_="value", name=y_name),
                zaxis3d_opts=opts.Axis3DOpts(type_="value", name=z_name),
                itemstyle_opts=opts.ItemStyleOpts(color=color),
                label_opts=opts.LabelOpts(is_show=show_label),

            )

        scatter3d.set_global_opts(
            title_opts=opts.TitleOpts(title=f'PCA of {str(table_name)} (total variance explained: {total_var:.2f}%)'),
            legend_opts=opts.LegendOpts(orient="vertical",  pos_right="2%"),


        )

        # scatter3d.render_notebook()

        return scatter3d
    
    def get_distinct_colors(self, n):  
        from distinctipy import distinctipy
        # rgb colour values (floats between 0 and 1)
        RED = (1, 0, 0)
        GREEN = (0, 1, 0)
        BLUE = (0, 0, 1)
        WHITE = (1, 1, 1)
        BLACK = (0, 0, 0)

        # generated colours will be as distinct as possible from these colours
        input_colors = [ WHITE, BLACK]
        existing_colors = [(0, 0, 0), (1, 1, 1)]
        colors = distinctipy.get_colors(n, exclude_colors= input_colors, pastel_factor=0.7)
        converted_colors = []
        converted_colors.extend(
            f'rgb({i[0] * 255},{i[1] * 255},{i[2] * 255})' for i in colors
        )
        return converted_colors






# scatter = plot_pca_pyecharts_3d(sw, df)
# scatter.render_notebook()