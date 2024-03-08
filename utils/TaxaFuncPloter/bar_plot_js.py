from pyecharts import options as opts
from pyecharts.charts import Bar


class BarPlot_js:
    def __init__(self, tfobj):
        self.tfa =  tfobj
    # plot intensity line for each sample
    # Example: plot_intensity_line(sw, func_name=func_name, taxon_name=taxon_name, fig_size=(30,20))

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

    def _add_group_name_to_sample(self, df):
        #rename columns (sample name)
        col_names = df.columns.tolist()
        meta_df = self.tfa.meta_df
        meta_name = self.tfa.meta_name
        groups_list = []
        new_col_names = []
        for i in col_names:
            group = meta_df[meta_df['Sample'] == i]
            group = group[meta_name].values[0]
            new_col_names.append(f'{i} ({group})')
            groups_list.append(group)
        df.columns = new_col_names
        return df
    
    
    def plot_intensity_bar(self, taxon_name:str=None, sample_list:list = None, 
                           func_name:str=None, peptide_seq=None, 
                           width:int=1200, height:int=800, df= None, 
                           title:str=None, rename_taxa:bool=False, 
                           show_legend:bool=True, font_size:int=10,
                           rename_sample:bool=True, plot_mean:bool=False,
                           plot_percent:bool=False
                           ):
        if df is None:
            df = self.tfa.GetMatrix.get_intensity_matrix(taxon_name=taxon_name, func_name=func_name, peptide_seq=peptide_seq, sample_list= sample_list)
            if df.empty:
                raise ValueError('No data to plot')
        
        if plot_mean:
            df = self.tfa.BasicStats.get_stats_mean_df_by_group(df)
            rename_sample = False
            
        # rename taxa
        if rename_taxa:
            df = self.rename_taxa(df)
        #rename columns (sample name)
        if rename_sample:
            df = self._add_group_name_to_sample(df)
        
        col_num = len(df)
        
        if plot_percent:
            # transform to percentage of each column
            df = df.div(df.sum(axis=0), axis=1) * 100
        
        if col_num > 10:
            colors = self.get_distinct_colors(col_num)
        else:
            import seaborn as sns
            colors = sns.color_palette('deep', col_num)
            colors = [f'rgb({int(i[0]*255)},{int(i[1]*255)},{int(i[2]*255)})' for i in colors]
               
        # create title
        if title is None:
            if taxon_name is None:
                title = f'{func_name}'
            elif func_name is None:
                title = f'{taxon_name}'
            elif peptide_seq is not None:
                title = f'The intensity of {peptide_seq}'
            else:
                title = f'{taxon_name}\n{func_name}'


        c = (
            Bar(init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px"))
            .add_xaxis(list(df.columns))
        )

        for i, name in enumerate(df.index):
            color = colors[i]
            c.add_yaxis(name, list(df.loc[name, :]), 
                        stack="stack1", 
                        category_gap="5%", 
                        itemstyle_opts=opts.ItemStyleOpts(color=color, border_type=None, border_width=0),
                        emphasis_opts=opts.EmphasisOpts(focus='series'),
                        )


            c.set_series_opts(label_opts=opts.LabelOpts(is_show=False))

        params = {
            "legend_opts": opts.LegendOpts(
                type_="scroll",
                page_icon_size=8,
                selector=[
                    {"type": "all", "title": "All"},
                    {"type": "inverse", "title": "Inverse"},
                ],
                pos_left="right",
                orient="vertical",
                pos_top="5%",
                border_width=0,
            )
            if show_legend
            else opts.LegendOpts(is_show=False),
            "datazoom_opts": [
                opts.DataZoomOpts(
                    type_="inside",
                    range_start=0,
                    range_end=100,
                )
            ],
            "toolbox_opts": opts.ToolboxOpts(
                is_show=True,
                orient="vertical",
                pos_left="left",
                pos_top="bottom",
                ),
                
                
            "title_opts": opts.TitleOpts(title=f"{title}", pos_left="center"),
            "xaxis_opts": opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=25, font_size=font_size)
            ),
            "yaxis_opts": opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(font_size=font_size),
                max_=100.02
                if plot_percent
                else None,  # set max value to 100.02 rather than 100: the sum of some columns may more than 100 due to float number
            ),
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

        # generated colors will be as distinct as possible from these colors
        input_colors = [WHITE]
        # colors = distinctipy.get_colors(n, exclude_colors= input_colors, pastel_factor=0.8,colorblind_type="Deuteranomaly")
        colors = distinctipy.get_colors(n, exclude_colors= input_colors, pastel_factor=0.7)
        converted_colors = []
        converted_colors.extend(
            f'rgb({i[0] * 255},{i[1] * 255},{i[2] * 255})' for i in colors
        )
        return converted_colors

