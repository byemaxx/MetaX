import pandas as pd
from pyecharts.charts import Sankey
from pyecharts import options as opts
from .get_distinct_colors import GetDistinctColors


class SankeyPlot:

    # plot sankey diagram from DESeq2 results dataframe
    # input: logFC dataframe from DESeq2
    # output: sankey diagram object
    # EXAMPLE: fc_df = sw.call_deseq2(sw.func_taxa_df, ['NDC', 'KES'])
    #         pic = plot_fc_sankey(fc_df, width=2500, height=2000, p_value=0.05, log2fc=1)
    #        pic.render_notebook()
    #     pic.render('sankey.html')
    
    def __init__(self, taxa_func_analyzer, theme='white'):
        self.tfa = taxa_func_analyzer
        
        self.font_size = 12
        self.show_legend = True
        self.theme = theme
        
    def convert_df_by_group_for_sankey(self,df, sub_meta, plot_mean) -> dict:
        sample_list = df.columns.tolist()
        
        if plot_mean or sub_meta != 'None':
            if plot_mean and sub_meta == 'None': # if sub_meta is not None, plot_mean is False
                df = self.tfa.BasicStats.get_stats_mean_df_by_group(df)
            elif sub_meta != 'None':
                df, _ = self.tfa.BasicStats.get_combined_sub_meta_df(df=df, sub_meta=sub_meta, plot_mean=plot_mean)
            group_dict = {col: col for col in df.columns}
            
        else:
            # group_dict = group is key, samples in a list is value
            group_dict = {}
            for sample in sample_list:
                group = self.tfa.get_group_of_a_sample(sample, self.tfa.meta_name)
                if group not in group_dict:
                    group_dict[group] = [sample]
                else:
                    group_dict[group].append(sample)
                    
        df_dict = {}
        # add all samples to the dict
        df['sum'] = df.sum(axis=1)
        df_dict['All'] = self.df_to_sankey_df(df, value_col='sum')
        # add samples for each group to the dict
        for group, samples in group_dict.items():
            df_temp = df.loc[:, samples]
            # convert to dataframe if it is a series, when there is only one sample, it will be a series
            if isinstance(df_temp, pd.Series):
                df_temp = pd.DataFrame(df_temp)
                
            df_temp['sum'] = df_temp.sum(axis=1)
            # remove values that are 0
            df_temp = df_temp[df_temp['sum'] != 0]
            df_temp = self.df_to_sankey_df(df_temp, value_col='sum')
            df_dict[group] = df_temp
            
        return df_dict
            

    def convert_logfc_df_for_sankey(self, df, pvalue: float = 0.05,p_type ='padj',
                                    log2fc_min: float = 1,log2fc_max:float = 10)  -> dict:
        df = df.copy()
        # 首先将所有行的 'type' 列设置为 'normal'
        df['type'] = 'normal'

        # 然后根据条件覆盖 'type' 列的值
        df.loc[(df[p_type] <= pvalue) & (df['log2FoldChange'] >= log2fc_min) & (df['log2FoldChange'] < log2fc_max), 'type'] = 'up'
        df.loc[(df[p_type] <= pvalue) & (df['log2FoldChange'] >= log2fc_max), 'type'] = 'ultra-up'
        df.loc[(df[p_type] <= pvalue) & (df['log2FoldChange'] <= -log2fc_min) & (df['log2FoldChange'] > -log2fc_max), 'type'] = 'down'
        df.loc[(df[p_type] <= pvalue) & (df['log2FoldChange'] <= -log2fc_max), 'type'] = 'ultra-down'

        count_dict = {}
        for i in ['up', 'down', 'ultra-up', 'ultra-down', 'normal']:
            count_dict[i] = len(df[df['type'] == i])    

        df['index'] = df.index

        if '<' in df['index'][0]:
            index_str = df['index'].str.split("<", expand=True)
            if '|' in index_str[0][0]:
                taxon_index = 0
                func_index = 1
            else:
                taxon_index = 1
                func_index = 0
            df = df[['log2FoldChange', 'type']]

            df['Taxon'] = index_str[taxon_index].str.replace(">", "")
            df['Function'] = index_str[func_index].str.replace(">", "")

        else:
            df = df[['log2FoldChange', 'type']]
            df['Taxon'] = df.index


        df_dict = {
            i: df[df['type'] == i].drop('type', axis=1)
            for i in ['up','ultra-up', 'down', 'ultra-down', 'normal']
        }


        df_out_dict = {}
        for key, df in df_dict.items():
            if len(df) > 0:
                df_t = df['Taxon'].str.split('|', expand=True)
                if "Function" in df.columns.tolist():
                    df_t = df_t.join(df['Function'])
                
                df_t = df_t.join(df['log2FoldChange'])
                names = df_t.columns.tolist()
                names[-1] = 'value'
                df_t.columns = names

                df_t['value'] = abs(df_t['value'])
                df_out_dict[key] = [df_t, len(df_t)]
                # df_out_dict[key] = df_t
        # remove normal if other not all empty,
        if len(df_out_dict) > 1:
            df_out_dict.pop('normal', None)
        return df_out_dict

    def df_to_sankey_df(self, df, value_col='value'):
        
        # if df if multi-index, split the index into two columns
        df = self.tfa.replace_if_two_index(df)
        # rename index to 'index'
        df.index.name = 'index'
        df['index'] = df.index
        df = df[['index', value_col]]
        
        if '<' in df['index'][0]:
            index_str = df['index'].str.split("<", expand=True)
            if '|' in index_str[0][0]:
                taxon_index = 0
                func_index = 1
            else:
                taxon_index = 1
                func_index = 0
            df = df[[value_col]]

            df['Taxon'] = index_str[taxon_index].str.replace(">", "")
            df['Function'] = index_str[func_index].str.replace(">", "")

        else:
            df = df[[value_col]]
            df['Taxon'] = df.index
            
        
        df_t = df['Taxon'].str.split('|', expand=True)
        if "Function" in df.columns.tolist():
            df_t = df_t.join(df['Function'])
        
        df_t = df_t.join(df[value_col])
        names = df_t.columns.tolist()
        names[-1] = 'value'
        df_t.columns = names

        # remove values that are 0
        df_t = df_t[df_t['value'] != 0]
        
        return df_t
        

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

        # Get 20 distinct colors
        colors = GetDistinctColors().get_distinct_colors(20, convert=True)

        # Assign colors to nodes ensuring adjacent nodes do not have the same color
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



    def __plot_sankey(self,link_nodes_dict, width, height, title, subtitle=''):

        # Remove duplicate nodes
        # nodes_combined = list({node['name']: node for node in nodes_up + nodes_down}.values())
        pic = Sankey(init_opts=opts.InitOpts(width=f"{width*100}px",
                                             height=f"{height*100}px",
                                             theme=self.theme))
        
        for key, value in link_nodes_dict.items():
            nodes  = value[0]
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
                linestyle_opt=opts.LineStyleOpts(
                    curve=0.5, opacity=0.3, color="gray"),
                label_opts=opts.LabelOpts(position='right', font_size=self.font_size, color='whithe' if self.theme == 'dark' else 'black'),
                itemstyle_opts=opts.ItemStyleOpts(border_width=1, border_color="black", opacity=0.7),
            )

        pic.set_global_opts(
            legend_opts=opts.LegendOpts(selected_mode='single', is_show=self.show_legend,
                                        type_="scroll",page_icon_size=8,
                                        ),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                orient="vertical",
                pos_left="left",
                pos_top="bottom",
                feature=opts.ToolBoxFeatureOpts( 
                                                save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(type_="png", 
                                                                                                background_color="black" if self.theme == 'dark' else "white",
                                                                                                pixel_ratio=3, 
                                                                                                title="Save as PNG"),
                                                restore=opts.ToolBoxFeatureRestoreOpts(title="Restore"),
                                                data_zoom=opts.ToolBoxFeatureDataZoomOpts(zoom_title="Zoom", 
                                                                                            is_show=False,
                                                                                        back_title="Back"),
                                                data_view=opts.ToolBoxFeatureDataViewOpts(title="Data View"),
                                                magic_type=opts.ToolBoxFeatureMagicTypeOpts(line_title="Line", 
                                                                                            bar_title="Bar",
                                                                                            is_show=False, 
                                                                                            stack_title="Stack",
                                                                                            tiled_title="Tiled"),
                                                
                                                ),
                ),
            
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle, title_textstyle_opts=opts.TextStyleOpts(font_size=self.font_size + 2)),
        )



        return pic


    def plot_fc_sankey(self, fc_df, width=12, height=8, pvalue=0.05, p_type='padj',
                       log2fc_min=1, log2fc_max=10, title='Sankey Plot', font_size=12):
        
        self.font_size = font_size # update font size
            
        df_sankey = self.convert_logfc_df_for_sankey(
            fc_df, pvalue=pvalue, p_type=p_type,
            log2fc_min=log2fc_min, log2fc_max=log2fc_max)
        
        link_nodes_dict = {}
        for key, value in df_sankey.items():
            print(f'Creating nodes and links for {key}...')
            nodes, links = self.create_nodes_links(value[0])
            link_nodes_dict[key] = [nodes, links, value[1]]
        pic = self.__plot_sankey(link_nodes_dict, width=width, height=height, title=title)
        return pic

    def plot_intensity_sankey(self,df, width=12, height=8, title="Sankey Plot", subtitle="",
                              font_size=12, show_legend=True, sub_meta='None', plot_mean=False):
        df = df.copy()
        self.font_size = font_size
        self.show_legend=show_legend
        
        df_sankey = self.convert_df_by_group_for_sankey(df, sub_meta, plot_mean)
        link_nodes_dict = {}
        for key, value in df_sankey.items():
            print(f'Creating nodes and links for {key}...')
            nodes, links = self.create_nodes_links(value)
            link_nodes_dict[key] = [nodes, links, len(value.index)]
        pic = self.__plot_sankey(link_nodes_dict, width=width, height=height, title=title, subtitle=subtitle)
        return pic