import pandas as pd
from pyecharts.charts import Sankey
from pyecharts import options as opts

class SankeyPlot:

    # plot sankey diagram from DESeq2 results dataframe
    # input: logFC dataframe from DESeq2
    # output: sankey diagram object
    # EXAMPLE: fc_df = sw.call_deseq2(sw.func_taxa_df, ['NDC', 'KES'])
    #         pic = plot_fc_sankey(fc_df, width=2500, height=2000, p_value=0.05, log2fc=1)
    #        pic.render_notebook()
    #     pic.render('sankey.html')
    
    def __init__(self, taxa_func_analyzer):
        self.tfa = taxa_func_analyzer

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
            dfi = df.pivot_table(value_col, index=list(i),
                                aggfunc='sum').reset_index()
            dfi.columns = [0, 1, 2]
            df2 = pd.concat([df2, dfi])  # Use pd.concat instead of append

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
        return nodes, links



    def __plot_sankey(self,link_nodes_dict, width, height, title, subtitle=''):

        # Remove duplicate nodes
        # nodes_combined = list({node['name']: node for node in nodes_up + nodes_down}.values())
        width = f'{width}px'
        height = f'{height}px'
        pic = Sankey(init_opts=opts.InitOpts(width=width, height=height))
        for key, value in link_nodes_dict.items():
            nodes  = value[0]
            links = value[1]
            num = value[2]
            pic.add(
                f'{key} (Total items: {num})',
                nodes=nodes,
                links=links,
                node_align='justify',
                layout_iterations=50,
                focus_node_mode='adjacency',
                linestyle_opt=opts.LineStyleOpts(
                    curve=0.5, opacity=0.2, color="source"),
                label_opts=opts.LabelOpts(position='right')
            )


        pic.set_global_opts(
            legend_opts=opts.LegendOpts(selected_mode='single'),
            toolbox_opts=opts.ToolboxOpts(is_show=True, feature={"saveAsImage": {}, "restore": {}, "dataView": {}}),
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
        )



        return pic


    def plot_fc_sankey(self, fc_df, width=1920, height=1080, pvalue=0.05, p_type='padj',
                       log2fc_min=1, log2fc_max=10, title='Sankey Plot'):
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
    
    
    def plot_intensity_sankey(self, df,width=1920, height=1080, title='Sankey Plot', subtitle=''):
        df = df.copy()
        df['sum'] = df.sum(axis=1)
        
        df_sankey = self.df_to_sankey_df(df, value_col='sum')
        nodes, links = self.create_nodes_links(df_sankey)
        # only state the number of last nodes
        link_nodes_dict = {'Intensity Sum': [nodes, links, len(df.index)]}

        pic = self.__plot_sankey(link_nodes_dict, width=width, height=height, title=title, subtitle= subtitle)
        return pic
    