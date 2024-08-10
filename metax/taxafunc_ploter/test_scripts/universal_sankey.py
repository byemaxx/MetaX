import pandas as pd
from pyecharts.charts import Sankey
from pyecharts import options as opts

class SankeyPlot:
    def __init__(self, theme='white'):
        self.font_size = 12
        self.show_legend = True
        self.theme = theme

    def df_to_sankey_df(self, df, value_col='value'):
        df.index.name = 'index'
        df['index'] = df.index
        df = df[['index', value_col]]
        
        if '<' in df['index'][0]:
            index_str = df['index'].str.split("<", expand=True)
            taxon_index, func_index = (0, 1) if '|' in index_str[0][0] else (1, 0)
            df = df[[value_col]]
            df['Taxon'] = index_str[taxon_index].str.replace(">", "")
            df['Function'] = index_str[func_index].str.replace(">", "")
        else:
            df = df[[value_col]]
            df['Taxon'] = df.index
            
        df_t = df['Taxon'].str.split('|', expand=True)
        if "Function" in df.columns:
            df_t = df_t.join(df['Function'])
        
        df_t = df_t.join(df[value_col])
        names = df_t.columns.tolist()
        names[-1] = 'value'
        df_t.columns = names
        df_t = df_t[df_t['value'] != 0]
        
        return df_t

    def convert_df_by_group_for_sankey(self, df,  plot_mean=False):
        sample_list = df.columns.tolist()
        
        if plot_mean  is not None:
            if plot_mean is None:
                df = df.mean(axis=1).to_frame(name='mean')

            group_dict = {col: col for col in df.columns}
        else:
            group_dict = {sample: sample for sample in sample_list}
                    
        df_dict = {}
        if len(sample_list) > 1:
            df['sum'] = df.sum(axis=1)
            df_dict['All'] = self.df_to_sankey_df(df, value_col='sum')
        
        for group, samples in group_dict.items():
            df_temp = df[samples]
            if isinstance(df_temp, pd.Series):
                df_temp = pd.DataFrame(df_temp)
                
            df_temp['sum'] = df_temp.sum(axis=1)
            df_temp = df_temp[df_temp['sum'] != 0]
            df_temp = self.df_to_sankey_df(df_temp, value_col='sum')
            df_dict[group] = df_temp
            
        return df_dict

    def create_nodes_links(self, df, value_col='value'):
        lis = df.columns.tolist()[:-1]
        lis1 = lis[:-1]
        lis2 = lis[1:]

        df2 = pd.DataFrame()
        for i in zip(lis1, lis2):
            dfi = df.pivot_table(value_col, index=list(i), aggfunc='sum').reset_index()
            dfi.columns = [0, 1, 2]
            df2 = pd.concat([df2, dfi])

        nodes = []
        ln = df2.iloc[:, 0].to_list() + df2.iloc[:, 1].to_list()
        ln = list(set(ln))
        for i in ln:
            dic = {'name': i}
            nodes.append(dic)
        print(f'Number of nodes: {len(nodes)}')

        links = []
        for i in df2.values:
            dic = {'source': i[0], 'target': i[1], 'value': i[2]}
            links.append(dic)
        print(f'Number of links: {len(links)}')

        colors = GetDistinctColors().get_distinct_colors(20, convert=True)
        node_colors = {}
        for idx, node in enumerate(nodes):
            available_colors = colors[:]
            for link in links:
                if link['source'] == node['name'] and link['target'] in node_colors:
                    if node_colors[link['target']] in available_colors:
                        available_colors.remove(node_colors[link['target']])
                if link['target'] == node['name'] and link['source'] in node_colors:
                    if node_colors[link['source']] in available_colors:
                        available_colors.remove(node_colors[link['source']])
            if not available_colors:
                available_colors = colors[:]
            chosen_color = available_colors[idx % len(available_colors)]
            node_colors[node['name']] = chosen_color
            node['itemStyle'] = {'color': chosen_color}

        return nodes, links

    def __plot_sankey(self, link_nodes_dict, width, height, title, subtitle=''):
        pic = Sankey(init_opts=opts.InitOpts(width=f"{width*100}px", height=f"{height*100}px", theme=self.theme))
        
        for key, value in link_nodes_dict.items():
            nodes = value[0]
            links = value[1]
            num = value[2]
            pic.add(
                f'{key} ({num})',
                nodes=nodes,
                links=links,
                node_align='justify',
                layout_iterations=100,
                node_width=25,
                emphasis_opts=opts.EmphasisOpts(focus='adjacency'),
                linestyle_opt=opts.LineStyleOpts(curve=0.5, opacity=0.3, color="gray"),
                label_opts=opts.LabelOpts(position='right', font_size=self.font_size, color='white' if self.theme == 'dark' else 'black'),
                itemstyle_opts=opts.ItemStyleOpts(border_width=1, border_color="black", opacity=0.7),
            )

        pic.set_global_opts(
            legend_opts=opts.LegendOpts(selected_mode='single', is_show=self.show_legend, type_="scroll", page_icon_size=8),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                orient="vertical",
                pos_left="left",
                pos_top="bottom",
                feature=opts.ToolBoxFeatureOpts(
                    save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(type_="png", background_color="black" if self.theme == 'dark' else "white", pixel_ratio=3, title="Save as PNG"),
                    restore=opts.ToolBoxFeatureRestoreOpts(title="Restore"),
                    data_zoom=opts.ToolBoxFeatureDataZoomOpts(zoom_title="Zoom", is_show=False, back_title="Back"),
                    data_view=opts.ToolBoxFeatureDataViewOpts(title="Data View"),
                    magic_type=opts.ToolBoxFeatureMagicTypeOpts(line_title="Line", bar_title="Bar", is_show=False, stack_title="Stack", tiled_title="Tiled"),
                ),
            ),
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle, title_textstyle_opts=opts.TextStyleOpts(font_size=self.font_size + 2)),
        )

        return pic

    def plot_intensity_sankey(self, df, width=12, height=8, title="Sankey Plot", subtitle="", font_size=12, show_legend=True, plot_mean=False):
        df = df.copy()
        self.font_size = font_size
        self.show_legend = show_legend
        
        df_sankey = self.convert_df_by_group_for_sankey(df, plot_mean=plot_mean)
        link_nodes_dict = {}
        for key, value in df_sankey.items():
            print(f'Creating nodes and links for {key}...')
            nodes, links = self.create_nodes_links(value)
            link_nodes_dict[key] = [nodes, links, len(value.index)]
        pic = self.__plot_sankey(link_nodes_dict, width=width, height=height, title=title, subtitle=subtitle)
        return pic

# df_sankey is a dataframe, index is "taxon" or "taxon < function>", columns are values
df_sankey = pd.read_csv('data.csv')
pic = SankeyPlot().plot_intensity_sankey(df_sankey, width=12, height=8, title="Sankey Plot", subtitle="", font_size=12, show_legend=False, plot_mean=False)
pic.render_notebook()