from pyecharts.charts import Line
from pyecharts import options as opts

class TrendsPlot_js:
    
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
    
    def plot_trends_js(self, df, width:int=15000, height:int=500, title:str=None, rename_taxa:bool=False):
        # rename taxa
        if rename_taxa:
            df = self.rename_taxa(df)
        if title is None:
            title = 'Trends of Cluster'
            
        c = (
            Line(init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px"))
            .add_xaxis(list(df.columns))
        )

        for i in range(df.shape[0]):
            c.add_yaxis(
                series_name=df.index[i],
                y_axis=list(df.iloc[i, :]),
                # is_smooth=True,
                is_hover_animation=True,
                linestyle_opts=opts.LineStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
            )

        # add average line
        c.add_yaxis(
            series_name='Average',
            y_axis=list(df.mean()),
            # is_smooth=True,
            is_hover_animation=True,
            linestyle_opts=opts.LineStyleOpts(opacity=1, color='red', width=3),
            label_opts=opts.LabelOpts(is_show=False),
        )

        c.set_global_opts(
            legend_opts=opts.LegendOpts(is_show=False),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            toolbox_opts=opts.ToolboxOpts( is_show=True, orient="vertical", pos_left="right", pos_top="bottom"),
            datazoom_opts=[opts.DataZoomOpts( type_="inside", range_start=0, range_end=100,)],
            title_opts=opts.TitleOpts(title=title, pos_left="center"),
        )

        return c