from pyecharts import options as opts
from pyecharts.charts import Bar


class BarPlot_js:
    def __init__(self, tfobj):
        self.tfobj =  tfobj
    # plot intensity line for each sample
    # Example: plot_intensity_line(sw, func_name=func_name, taxon_name=taxon_name, fig_size=(30,20))
    def rename_taxa(self, df):
        if df.index.name == 'Taxon':
            index_list = [i.split('|')[-1] for i in df.index.tolist()]
            df.index = index_list
        elif 'd__Bacteria' in df.index.tolist()[0]:
            new_index_list = []
            for i in df.index.tolist():
                taxon = i.split(' <')[0].split('|')[-1]
                func = i.split(' <')[1][:-1]
                new_index = f'{taxon} <{func}>'
                new_index_list.append(new_index)
            df.index = new_index_list
        return df

    def plot_intensity_bar(self, taxon_name:str=None, groups:list = None, func_name:str=None, peptide_seq=None, width:int=1200, height:int=800, df= None, title:str=None, rename_taxa:bool=False):
        if df is None:
            df = self.tfobj.get_intensity_matrix(taxon_name=taxon_name, func_name=func_name, peptide_seq=peptide_seq, groups= groups)
            if df.empty:
                raise ValueError('No data to plot')
        # rename taxa
        if rename_taxa:
            df = self.rename_taxa(df)
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
        
        # create title
        if title is None:
            if taxon_name is None:
                title = f'{func_name}'
            elif func_name is None:
                title = f'{taxon_name}'
            elif peptide_seq is not None:
                title = f'The intensity of {peptide_seq}'
            elif taxon_name is None and func_name is None:
                title = 'The intensity of '
            else:
                title = f'{taxon_name}\n{func_name}'
            
            
        c = (
            Bar(init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px"))
            .add_xaxis(list(df.columns))
        )

        for name in df.index:
            c.add_yaxis(name, list(df.loc[name, :]), stack="stack1", category_gap="50%")
            
            c.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            c.set_global_opts(datazoom_opts=[opts.DataZoomOpts( type_="inside", range_start=0, range_end=100,), opts.DataZoomOpts(type_="slider", range_start=0, range_end=100,),],
                            legend_opts=opts.LegendOpts(pos_left="right", orient="vertical", pos_top="5%",),
                            toolbox_opts=opts.ToolboxOpts( is_show=True, orient="vertical", pos_left="right", pos_top="bottom",),
                            title_opts=opts.TitleOpts(title=f"{title}", pos_left="center" ),
            )

        return c
    
