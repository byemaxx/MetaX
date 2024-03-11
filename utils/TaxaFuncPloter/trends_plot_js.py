from pyecharts.charts import Line
from pyecharts import options as opts

class TrendsPlot_js:
    def __init__(self, tfobj):
        self.tfobj =  tfobj
        
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
    
    def _add_group_name_to_sample(self, df):
        #rename columns (sample name)
        col_names = df.columns.tolist()
        meta_df = self.tfobj.meta_df
        meta_name = self.tfobj.meta_name
        groups_list = []
        new_col_names = []
        for i in col_names:
            group = meta_df[meta_df['Sample'] == i]
            group = group[meta_name].values[0]
            new_col_names.append(f'{i} ({group})')
            groups_list.append(group)
        df.columns = new_col_names
        return df
        
    def plot_trends_js(self, df, width:int=15000, height:int=500, title:str=None, 
                       rename_taxa:bool=False, show_legend:bool=False, 
                       add_group_name:bool=False, font_size:int=10):
        # rename taxa
        if rename_taxa:
            df = self.rename_taxa(df)
        if title is None:
            title = 'Trends of Cluster'
        
        if add_group_name:
            df = self._add_group_name_to_sample(df)
            
        c = (
            Line(init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px"))
            .add_xaxis(list(df.columns))
        )

        col_num = len(df)
        if col_num > 10:
            colors = self.get_distinct_colors(col_num)
        else:
            import seaborn as sns
            colors = sns.color_palette('deep', col_num)
            colors = [f'rgb({int(i[0]*255)},{int(i[1]*255)},{int(i[2]*255)})' for i in colors]
            
            
        for i in range(df.shape[0]):
            color = colors[i]
            c.add_yaxis(
                series_name=df.index[i],
                y_axis=list(df.iloc[i, :]),
                # is_smooth=True,
                is_hover_animation=True,
                linestyle_opts=opts.LineStyleOpts(opacity=0.9, width=2),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color=color),
                emphasis_opts=opts.EmphasisOpts(focus='series'),
            )

        # add average line
        c.add_yaxis(
            series_name='Average',
            y_axis=list(df.mean()),
            # is_smooth=True,
            is_hover_animation=True,
            linestyle_opts=opts.LineStyleOpts(opacity=1, color='red', width=3, type_='dashed'),
            label_opts=opts.LabelOpts(is_show=False),
            emphasis_opts=opts.EmphasisOpts(focus='series'),
        )

        # set global options
        params = {
            "legend_opts": opts.LegendOpts(
                                           type_="scroll", page_icon_size = 8, 
                                           selector=[{"type": "all", "title": "All"}, {"type": "inverse", "title": "Inverse"}],
                                           pos_left="right", orient="vertical", 
                                           pos_top="5%",border_width=0) if show_legend else opts.LegendOpts(is_show=False),
            "xaxis_opts": opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=25, font_size=font_size)),
            "toolbox_opts": opts.ToolboxOpts(
                is_show=True, orient="vertical", pos_left="left", pos_top="bottom"
            ),
            'yaxis_opts': opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=font_size)),
            "datazoom_opts": [
                opts.DataZoomOpts(type_="inside", range_start=0, range_end=100,)
            ],
            "title_opts": opts.TitleOpts(title=title, pos_left="center", title_textstyle_opts=opts.TextStyleOpts(font_size=font_size+2, font_weight='bold')),
        }
        c.set_global_opts(**params)
        
        return c
    
    def get_distinct_colors(self, n):  
        from distinctipy import distinctipy
        # rgb colour values (floats between 0 and 1)
        RED = (1, 0, 0)
        GREEN = (0, 1, 0)
        BLUE = (0, 0, 1)
        WHITE = (1, 1, 1)
        BLACK = (0, 0, 0)

        # generated colours will be as distinct as possible from these colours
        input_colors = [BLACK]
        existing_colors = [(0, 0, 0), (1, 1, 1)]
        colors = distinctipy.get_colors(n, exclude_colors= input_colors, pastel_factor=0.6)
        converted_colors = []
        converted_colors.extend(
            f'rgb({i[0] * 255},{i[1] * 255},{i[2] * 255})' for i in colors
        )
        return converted_colors
