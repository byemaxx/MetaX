from pyecharts import options as opts
from pyecharts.charts import Graph

class NetworkPlot:
    def __init__(self, tfobj=None):
        self.tfa = tfobj
    

    def create_nodes_links(self, sample_list:list = None, focus_list:list = [], plot_list_only:bool = False):
        df = self.tfa.taxa_func_df.copy()
        extra_cols = sample_list
        if extra_cols:
            print(f"Using sample list provided {extra_cols}")
            df = df[extra_cols]
        else:
            print("No sample list provided, using all samples")


        df = df.loc[~(df==0).all(axis=1)]
        df['sum'] = df.sum(axis=1)
        df.reset_index(inplace=True)
        colname = df.columns.tolist()
        colname[0] = 'taxa'
        colname[1] = 'function'
        df.columns = colname
        df = df[['taxa', 'function', 'sum']]

        if plot_list_only:
            df = df.loc[df['taxa'].isin(focus_list) | df['function'].isin(focus_list)]

        taxa_sum = df.groupby('taxa')['sum'].sum().to_dict()
        function_sum = df.groupby('function')['sum'].sum().to_dict()

        min_value = min(min(taxa_sum.values()), min(function_sum.values()))
        max_value = max(max(taxa_sum.values()), max(function_sum.values()))

        def normalize(value):
            if max_value == min_value:
                return 30
            scaled_value = 100 * (value - min_value) / (max_value - min_value)
            return max(scaled_value, 10)  # set a minimum size



        taxa = df["taxa"].unique().tolist()
        functions = df["function"].unique().tolist()
        nodes = []
        if focus_list is not None and len(focus_list) > 0:
            for taxon in taxa:
                if taxon in focus_list:
                    nodes.append({"name": taxon, "category": 1, "symbolSize": normalize(taxa_sum[taxon]), "value": taxa_sum[taxon]})
                else:
                    nodes.append({"name": taxon, "category": 0, "symbolSize": normalize(taxa_sum[taxon]), "value": taxa_sum[taxon]})
            for function in functions:
                if function in focus_list:
                    nodes.append({"name": function, "category": 3, "symbolSize": normalize(function_sum[function]), "value": function_sum[function]})
                else:
                    nodes.append({"name": function, "category": 2, "symbolSize": normalize(function_sum[function]), "value": function_sum[function]})

            links = [{"source": row["taxa"], "target": row["function"]} for _, row in df.iterrows()]

            categories = [
                {"name": "Taxa", "itemStyle": {"normal": {"color": "#f1c40f"}}},
                {"name": "Focus_Taxa", "itemStyle": {"normal": {"color": "#ff0000"}}},
                {"name": "Function", "itemStyle": {"normal": {"color": "#95a5a6"}}},
                {"name": "Focus_Function", "itemStyle": {"normal": {"color": "#27ae60"}}},
            ]

            return nodes, links, categories


        else:
            nodes = [{"name": taxon, "category": 0, "symbolSize": normalize(taxa_sum[taxon]), "value": taxa_sum[taxon]} for taxon in taxa] + [{"name": function, "category": 1, "symbolSize": normalize(function_sum[function]), "value": function_sum[function]} for function in functions]

            links = [{"source": row["taxa"], "target": row["function"]} for _, row in df.iterrows()]
            categories = [
                {"name": "Taxa", "itemStyle": {"normal": {"color": "#f1c40f"}}},
                {"name": "Function", "itemStyle": {"normal": {"color": "#95a5a6"}}},
            ]


        return nodes, links, categories


    
    def plot_tflink_network(self, sample_list:list = None, width:int = 1200, height:int = 800, focus_list: list = None, plot_list_only:bool = False):
        if focus_list is None:
            focus_list = []
        # preprocess focus_list
        if focus_list is not None and focus_list:
            new_list = []
            for i in focus_list:
                if i in self.tfa.taxa_df.index.tolist():
                    new_list.append(i)
                elif i in self.tfa.func_df.index.tolist():
                    new_list.append(i)
                elif i.startswith('d__Bacteria') and ' <' in i:
                    taxon = i.split(' <')[0]
                    func = i.split(' <')[1][:-1]
                    new_list.extend((taxon, func))
                else:
                    print(f"Warning: {i} is not in taxa or function list")
            nodes, links, categories = self.create_nodes_links(sample_list, new_list,plot_list_only)
        else:
            nodes, links, categories = self.create_nodes_links(sample_list)


        c = (
            Graph(init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px"))
            .add(
                "",
                nodes,
                links,
                categories,
                repulsion= 1000,
                is_focusnode=True,
                is_layout_animation= True,
                friction = 0.6,
                linestyle_opts=opts.LineStyleOpts(curve=0.2, opacity=0.5),
                # itemstyle_opts=opts.ItemStyleOpts(border_width=0.5, border_color="rgba(0,0,0,0.5)", opacity=0.8),
                gravity = 0.05,
                label_opts=opts.LabelOpts(is_show=False, position="right", color="auto", formatter="{b}"),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"Taxa-Function Network",  subtitle_textstyle_opts=opts.TextStyleOpts(font_size=10)),
                toolbox_opts=opts.ToolboxOpts( is_show=True, feature={"saveAsImage": {}, "restore": {}}),
            )  
            )
        if sample_list:
            c.set_global_opts(
                title_opts=opts.TitleOpts(title=f"Taxa-Function Network", subtitle=f"{sample_list}", subtitle_textstyle_opts=opts.TextStyleOpts(font_size=10)),
                toolbox_opts=opts.ToolboxOpts( is_show=True, feature={"saveAsImage": {}, "restore": {}})
            )  

        return c
    

    def plot_co_expression_network(self, df_type:str= 'taxa', corr_method:str = 'pearson', 
                                   corr_threshold:float=0.5, sample_list:list = None, 
                                   width:int = 1600, height:int = 900, focus_list:list = [], plot_list_only:bool = False):
        from matplotlib import colormaps
        #check sample_list length
        if len(sample_list) < 2:
            raise ValueError(f"sample_list should have at least 2 samples, but got {len(sample_list)}")

        df_dict = {'taxa': self.tfa.taxa_df, 
                   'func': self.tfa.func_df, 
                   'taxa-func': self.tfa.taxa_func_df, 
                   'peptide': self.tfa.peptide_df,
                   'protein': self.tfa.protein_df}
        
        df = df_dict[df_type].copy()
        if extra_cols := sample_list:
            print(f"Using sample list provided {extra_cols}")
            df = df[extra_cols]
        else:
            print("No sample list provided, using all samples")

        df = self.replace_if_two_index(df)

        df = df.T
        if  corr_method == 'pearson':
            correlation_matrix = df.corr(method='pearson')
        elif corr_method == 'spearman':
            correlation_matrix = df.corr(method='spearman')
        else:
            raise ValueError(f"corr_method should be pearson or spearman, but got {corr_method}")
            
        node_sizes = correlation_matrix.apply(lambda x: (x > corr_threshold).sum(), axis=1)
        max_node_size = node_sizes.max()
        min_node_size = node_sizes.min()
        
        categories = [{"name": "Focused", "itemStyle": {"normal": {"color": "#ff0000"}}}, 
                      {"name": "Normal", "itemStyle": {"normal": {"color": "#9AF10F"}}}]

        linked_nodes = set()
        if focus_list:
            for i in range(len(correlation_matrix)):
                for j in range(i+1, len(correlation_matrix)):
                    node_i = correlation_matrix.columns[i]
                    node_j = correlation_matrix.columns[j]
                    correlation = correlation_matrix.iloc[i, j]
                    if correlation > corr_threshold:
                        if node_i in focus_list or node_j in focus_list:
                            linked_nodes.add(node_i)
                            linked_nodes.add(node_j)

        nodes = []
        for item in correlation_matrix.columns:
            if focus_list and len(focus_list) > 0:
                if plot_list_only and item not in focus_list and item not in linked_nodes:
                    continue

                if item in focus_list:
                    node_size = 50
                    color = '#ff0000'
                    category = 0  # Focus category
                else:
                    node_size = (node_sizes[item] - min_node_size) / (max_node_size - min_node_size) * 30 + 10
                    color = colormaps.get_cmap('viridis')(node_size / 40)  # normalize the node size to [0, 1] for the color map
                    color = '#%02x%02x%02x' % (int(color[0]*255), int(color[1]*255), int(color[2]*255))
                    category = 1  # Normal category
            else:
                node_size = (node_sizes[item] - min_node_size) / (max_node_size - min_node_size) * 30 + 10
                color = colormaps.get_cmap('viridis')(node_size / 40)  # normalize the node size to [0, 1] for the color map
                color = '#%02x%02x%02x' % (int(color[0]*255), int(color[1]*255), int(color[2]*255))
                category = 1  # Normal category
            
            nodes.append({
                "name": item, 
                "symbolSize": node_size, 
                "itemStyle": {"color": color},
                "category": category
            })
        
        links = []
        for i in range(len(correlation_matrix)):
            for j in range(i+1, len(correlation_matrix)):
                correlation = correlation_matrix.iloc[i, j]
                # create a link if the correlation is above a threshold
                if correlation > corr_threshold:
                    color = colormaps.get_cmap('viridis')((correlation - corr_threshold) / corr_threshold) 
                    color = '#%02x%02x%02x' % (int(color[0]*255), int(color[1]*255), int(color[2]*255))
                    links.append({"source": correlation_matrix.columns[i], "target": correlation_matrix.columns[j], "value": correlation, "lineStyle": {"color": color}})

            
        pic = (
            Graph(
                init_opts=opts.InitOpts(
                    width=f"{width}px",
                    height=f"{height}px",
                    animation_opts=opts.AnimationOpts(
                        animation_threshold=100, animation_easing="cubicOut"
                    ),
                )
            )
            .add("", nodes, links,
                 categories=categories,
                 repulsion= 1000,
                 is_layout_animation= True,
                 label_opts=opts.LabelOpts(is_show=False, position="right", color="auto", formatter="{b}"))
            .set_global_opts(
                legend_opts=opts.LegendOpts(is_show=True),
                title_opts=opts.TitleOpts(
                    title="Co-expression Network",
                    subtitle=f"{sample_list}" if sample_list != self.tfa.sample_list else "",
                    subtitle_textstyle_opts=opts.TextStyleOpts(font_size=10),
                ), 
                toolbox_opts=opts.ToolboxOpts( is_show=True, feature={"saveAsImage": {}, "restore": {}} )
        ))
        return pic
    
    def replace_if_two_index(self, df):
        import pandas as pd
        if isinstance(df.index, pd.MultiIndex):
            df = df.copy()
            df.reset_index(inplace=True)
            # DO NOT USE f-string here, it will cause error
            df['Taxa-Func'] = df.iloc[:,
                                        0].astype(str) + ' <' + df.iloc[:, 1].astype(str) + '>'
            df.set_index('Taxa-Func', inplace=True)
            df = df.drop(df.columns[:2], axis=1)
        else:
            df = df.copy()
        return df

# NetworkPlot(sw).plot_co_expression_network(df_type='func', corr_threshold=0.8, sample_list=sw.get_sample_list_in_a_group('V1') , focus_list=["'glutamate synthase"]).render_notebook()