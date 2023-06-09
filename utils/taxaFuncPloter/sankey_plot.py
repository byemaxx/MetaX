import pandas as pd
from pyecharts.charts import Sankey
from pyecharts import options as opts

class SankeyPlot:
        # def __init__(self, tfobj=None):
        # self.tfobj =  tfobj
    # plot sankey diagram from DESeq2 results dataframe
    # input: logFC dataframe from DESeq2
    # output: sankey diagram object
    # EXAMPLE: fc_df = sw.call_deseq2(sw.func_taxa_df, ['NDC', 'KES'])
    #         pic = plot_fc_sankey(fc_df, width=2500, height=2000, p_value=0.05, log2fc=1)
    #        pic.render_notebook()
    #     pic.render('sankey.html')

    def convert_logfc_df_for_sankey(self, df, p_value: float = 0.05, log2fc: float = 1) -> list:
        df = df.copy()
        df = df[df['padj'] < p_value]
        df = df[df['log2FoldChange'].abs() > log2fc]
        df = df[['log2FoldChange']]
        df['index'] = df.index

        index_str = df['index'].str.split("[", expand=True)
        if '|' in index_str[0][0]:
            taxon_index = 0
            func_index = 1
        else:
            taxon_index = 1
            func_index = 0

        df['Taxon'] = index_str[taxon_index].str.replace("]", "")
        df['Function'] = index_str[func_index].str.replace("]", "")

        df_up = df[df['log2FoldChange'] > 0]
        df_down = df[df['log2FoldChange'] < 0]

        df_list = [df_up, df_down]

        df_out = []
        for df in df_list:
            df_t = df['Taxon'].str.split('|', expand=True)
            df_t = df_t.join(df['Function'])
            df_t = df_t.join(df['log2FoldChange'])
            col_name = ['domain', 'phylum', 'class', 'order','family', 'genus', 'species',  'function', 'value']
            if len(df_t.columns) == 8:
                col_name.remove('species')
                print('No species level in the taxonomy')
            elif len(df_t.columns) == 7:
                col_name.remove('genus')
                col_name.remove('species')
                print('No genus and species level in the taxonomy')
            elif len(df_t.columns) == 6:
                col_name.remove('family')
                col_name.remove('genus')
                col_name.remove('species')
                print('No family, genus and species level in the taxonomy')
            elif len(df_t.columns) == 5:
                col_name.remove('order')
                col_name.remove('family')
                col_name.remove('genus')
                col_name.remove('species')
                print('No order, family, genus and species level in the taxonomy')
            elif len(df_t.columns) == 4:
                col_name.remove('class')
                col_name.remove('order')
                col_name.remove('family')
                col_name.remove('genus')
                col_name.remove('species')
                print('No class, order, family, genus and species level in the taxonomy')
            elif len(df_t.columns) == 3:
                col_name.remove('phylum')
                col_name.remove('class')
                col_name.remove('order')
                col_name.remove('family')
                col_name.remove('genus')
                col_name.remove('species')
                print('No phylum, class, order, family, genus and species level in the taxonomy')
            elif len(df_t.columns) == 2:
                col_name.remove('domain')
                col_name.remove('phylum')
                col_name.remove('class')
                col_name.remove('order')
                col_name.remove('family')
                col_name.remove('genus')
                col_name.remove('species')
                print('No domain, phylum, class, order, family, genus and species level in the taxonomy')

            df_t.columns = col_name
            df_t['value'] = abs(df_t['value'])
            df_out.append(df_t)
        return df_out


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



    def __plot_sankey(self, nodes_up, links_up, nodes_down, links_down, width=2500, height=2000):


        # Remove duplicate nodes
        # nodes_combined = list({node['name']: node for node in nodes_up + nodes_down}.values())
        width = f'{width}px'
        height = f'{height}px'
        pic = Sankey(init_opts=opts.InitOpts(width=width, height=height))

        pic.add(
            "Up",
            nodes=nodes_up,
            links=links_up,
            node_align='justify',
            layout_iterations=50,
            focus_node_mode='adjacency',
            linestyle_opt=opts.LineStyleOpts(
                curve=0.5, opacity=0.2, color="source"),
            label_opts=opts.LabelOpts(position='right')
        )

        pic.add(
            "Down",
            nodes=nodes_down,
            links=links_down,
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
        )



        return pic


    def plot_fc_sankey(self, fc_df, width=1920, height=1080, p_value=0.05, log2fc=1):
        df_sankey = self.convert_logfc_df_for_sankey(
            fc_df, p_value=p_value, log2fc=log2fc)
        print('Creating nodes and links for upregulated...')
        nodes_up, links_up = self.create_nodes_links(df_sankey[0])
        print('Creating nodes and links for downregulated...')
        nodes_down, links_down = self.create_nodes_links(df_sankey[1])

        return self.__plot_sankey(
            nodes_up, links_up, nodes_down, links_down, width, height
        )