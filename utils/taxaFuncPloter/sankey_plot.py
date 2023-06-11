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

    def convert_logfc_df_for_sankey(self, df, padj: float = 0.05, log2fc: float = 1) -> list:
        df = df.copy()
        count_up = len(df[(df['padj'] < padj) & (
            df['log2FoldChange'] > log2fc)])
        count_down = len(
            df[(df['padj'] < padj) & (df['log2FoldChange'] < -log2fc)])
        df.loc[(df['padj'] < padj) & (
            df['log2FoldChange'] > log2fc), 'type'] = 'up'
        df.loc[(df['padj'] < padj) & (
            df['log2FoldChange'] < -log2fc), 'type'] = 'down'
        df.loc[~df.index.isin(df[(df['padj'] < padj) & ((df['log2FoldChange'] > log2fc) | (
            df['log2FoldChange'] < -log2fc))].index), 'type'] = 'normal'
        count_normal = len(df[df['type'] == 'normal'])



        df['index'] = df.index

        index_str = df['index'].str.split("[", expand=True)
        if '|' in index_str[0][0]:
            taxon_index = 0
            func_index = 1
        else:
            taxon_index = 1
            func_index = 0


        df = df[['log2FoldChange', 'type']]

        df['Taxon'] = index_str[taxon_index].str.replace("]", "")
        df['Function'] = index_str[func_index].str.replace("]", "")

        df_dict = {
            i: df[df['type'] == i].drop('type', axis=1)
            for i in ['up', 'down', 'normal']
        }


        df_out_dict = {}
        for key, df in df_dict.items():
            if len(df) > 0:
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
                df_out_dict[key] = [df_t, len(df_t)]
                # df_out_dict[key] = df_t
        return df_out_dict



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



    def __plot_sankey(self,link_nodes_dict, width=2500, height=2000):

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
                f'{key} (Total: {num}))',
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
        )



        return pic


    def plot_fc_sankey(self, fc_df, width=1920, height=1080, padj=0.05, log2fc=1):
        df_sankey = self.convert_logfc_df_for_sankey(
            fc_df, padj=padj, log2fc=log2fc)
        link_nodes_dict = {}
        for key, value in df_sankey.items():
            print(f'Creating nodes and links for {key}...')
            nodes, links = self.create_nodes_links(value[0])
            link_nodes_dict[key] = [nodes, links, value[1]]
        pic = self.__plot_sankey(link_nodes_dict, width=width, height=height)
        return pic