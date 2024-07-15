from pyecharts import options as opts
from pyecharts.charts import Graph
import pandas as pd

class NetworkPlot:
    def __init__(self, tfobj, 
                show_labels=False,
                rename_taxa=False, 
                font_size=10,
                taxa_shape='circle',
                func_shape='rect',
                taxa_color="#374E55",
                taxa_focus_color="#6A6599",
                func_color="#DF8F44",
                func_focus_color="#B24745",
                line_opacity=0.5,
                line_width=1.5,
                line_curve=0.1,
                line_color="#9aa7b1",
                repulsion=500,
                co_network_focus_color="#B24745",
                co_network_normal_color="#79af97",
                font_weight="normal",
                theme="white",
                label_position="bottom",
                text_width = 300,
                gravity = 0.2,
                show_sub_title = True,
                
                 ):
        
        self.tfa = tfobj
        self.show_labels = show_labels
        self.font_size = font_size
        self.font_weight = font_weight
        
        self.rename_taxa = rename_taxa
        self.taxa_shape = taxa_shape
        self.func_shape = func_shape
        self.taxa_color = taxa_color
        self.taxa_focus_color = taxa_focus_color
        self.func_color = func_color
        self.func_focus_color = func_focus_color
        
        self.line_opacity = line_opacity
        self.line_width = line_width
        self.line_curve = line_curve
        self.line_color = line_color
        
        self.repulsion = repulsion
        
        self.co_network_focus_color = co_network_focus_color
        self.co_network_normal_color = co_network_normal_color
        
        self.theme = theme
        self.label_position = label_position
        self.text_width = text_width
        self.gravity = gravity
        
        self.show_sub_title = show_sub_title
        

    def modify_focus_list(self, focus_list):
        '''
        Split the taxa-func item into taxa and function if it's in the focus_list
        '''
        new_focus_list = []
        for i in focus_list:
            if i.startswith('d__'):
                if ' <' in i: # taxa-func item
                    taxa = i.split(' <')[0].split('|')[-1]
                    func = i.split(' <')[1][:-1]
                    # i = taxa.split('|')[-1] + ' <' + func + '>'
                    new_focus_list.append(taxa)
                    new_focus_list.append(func)
                else: # taxa item
                    i = i.split('|')[-1]
                    new_focus_list.append(i)
            else: # function item
                new_focus_list.append(i)
                
        focus_list = new_focus_list
        return focus_list

    def create_nodes_links(
        self,
        sample_list: list = None,
        focus_list: list = [],
        plot_list_only: bool = False,
        list_only_no_link: bool = False,
    ):
        """
        Prepares data for network visualization of taxa and functions.

        This method calculates the sum of values for each taxa and function from the provided DataFrame,
        normalizes these sums for visualization, and creates nodes and links for a network graph.

        Parameters:
        - sample_list (list, optional): Specifies which samples to include. If None, all samples are used.
        - focus_list (list, optional): List of taxa and functions to highlight in the network.
        - plot_list_only (bool, optional): If True, only items and theri linked items in focus_list are plotted.
        - strict_list (bool, optional): If True, only items in focus_list are plotted.

        Returns:
        - nodes (list): Information about each node for the graph, including name and size.
        - links (list): Information about links between nodes.
        - categories (list): Categories for nodes, used for coloring in the graph.
        """
        df = self.tfa.taxa_func_df.copy()
        if self.rename_taxa:
            print("Renaming taxa to last level")
            df = self.tfa.rename_taxa(df)
            focus_list = self.modify_focus_list(focus_list)
            
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
            print("Plotting only the list provided in focus_list")
            print(f"Original df shape: {df.shape}")
            if list_only_no_link:
                df_coverd = df.loc[df['taxa'].isin(focus_list) & df['function'].isin(focus_list)]
                covered_taxa = df_coverd['taxa'].unique().tolist()
                covered_func = df_coverd['function'].unique().tolist()
                uncovered_list = [i for i in focus_list if i not in covered_taxa and i not in covered_func]

                df_taxa = df.loc[df['taxa'].isin(uncovered_list)]
                df_taxa['function'] = "" # use empty string to show the dots and not the links
                df_func = df.loc[df['function'].isin(uncovered_list)]
                df_func['taxa'] = "" 
                # concatenate the uncovered taxa and functions
                df = pd.concat([df_coverd, df_taxa, df_func])
                
                
            else:
                df = df.loc[df['taxa'].isin(focus_list) | df['function'].isin(focus_list)]
            print(f"New df shape: {df.shape}")
            
        # taxa_sum = df.groupby('taxa')['sum'].sum().to_dict()
        taxa_sum = df[df['taxa'] != ""].groupby('taxa')['sum'].sum().to_dict()
        # function_sum = df.groupby('function')['sum'].sum().to_dict()
        function_sum = df[df['function'] != ""].groupby('function')['sum'].sum().to_dict()

        min_value = min(min(taxa_sum.values()), min(function_sum.values()))
        max_value = max(max(taxa_sum.values()), max(function_sum.values()))

        def normalize(value):
            if max_value == min_value:
                return 30
            scaled_value = 100 * (value - min_value) / (max_value - min_value)
            return max(scaled_value, 10)

        taxa = [i for i in df["taxa"].unique() if i != ""]
        functions = [i for i in df["function"].unique() if i != ""]
        
        nodes = []
        if focus_list is not None and len(focus_list) > 0:
            for taxon in taxa:
                symbol = self.taxa_shape
                if taxon in focus_list:
                    nodes.append({"name": taxon, "category": 1, "symbolSize": normalize(taxa_sum[taxon]), "value": taxa_sum[taxon], "symbol": symbol})
                else:
                    nodes.append({"name": taxon, "category": 0, "symbolSize": normalize(taxa_sum[taxon]), "value": taxa_sum[taxon], "symbol": symbol})
            for function in functions:
                symbol = self.func_shape
                if function in focus_list:
                    nodes.append({"name": function, "category": 3, "symbolSize": normalize(function_sum[function]), "value": function_sum[function], "symbol": symbol})
                else:
                    nodes.append({"name": function, "category": 2, "symbolSize": normalize(function_sum[function]), "value": function_sum[function], "symbol": symbol})

            
            links = [{"source": row["taxa"], "target": row["function"]} for _, row in df.iterrows() if row["function"] != "" and row["taxa"] != ""]

            categories = [
                {"name": "Taxa", "itemStyle": {"normal": {"color": self.taxa_color}}},
                {"name": "Focus_Taxa", "itemStyle": {"normal": {"color": self.taxa_focus_color}}},
                {"name": "Function", "itemStyle": {"normal": {"color": self.func_color}}},
                {"name": "Focus_Function", "itemStyle": {"normal": {"color": self.func_focus_color}}},
            ]

            return nodes, links, categories

        else:
            nodes = [{"name": taxon, "category": 0, "symbolSize": normalize(taxa_sum[taxon]), "value": taxa_sum[taxon], "symbol": self.taxa_shape} for taxon in taxa] + \
                    [{"name": function, "category": 1, "symbolSize": normalize(function_sum[function]), "value": function_sum[function], "symbol": self.func_shape} for function in functions]

            links = [{"source": row["taxa"], "target": row["function"]} for _, row in df.iterrows()]
            categories = [
                {"name": "Taxa", "itemStyle": {"normal": {"color": self.taxa_color}}},
                {"name": "Function", "itemStyle": {"normal": {"color": self.func_color}}},
            ]

        return nodes, links, categories

    def plot_tflink_network(
        self,
        sample_list: list = None,
        width: int = 12,
        height: int = 8,
        focus_list: list = None,
        plot_list_only: bool = False,
        list_only_no_link: bool = False,
    ):
        """
        Creates a network graph of taxa and functions using Pyecharts.

        This method uses data prepared by `create_nodes_links` to generate a graph visualizing the relationships between taxa and functions. The graph's appearance and behavior are customizable through parameters.

        Parameters:
        - sample_list (list, optional): Specifies which samples to include in the graph.
        - width (int, optional): Width of the graph in pixels.
        - height (int, optional): Height of the graph in pixels.
        - focus_list (list, optional): List of taxa and functions to highlight.
        - plot_list_only (bool, optional): If True, only plots items in focus_list and their linked items.
        - strict_list_only (bool, optional): If True, only plots items in focus_list.

        Returns:
        - A Pyecharts Graph object that can be displayed in Jupyter notebooks or web pages.
        """

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
            nodes, links, categories = self.create_nodes_links(sample_list, new_list,plot_list_only, list_only_no_link)
        else:
            focus_list = []
            nodes, links, categories = self.create_nodes_links(sample_list)


        c = (
            Graph(
                init_opts=opts.InitOpts(
                    width=f"{width*100}px",
                    height=f"{height*100}px",
                    theme=self.theme
                )
            )
            .add(
                "",
                nodes,
                links,
                categories,
                repulsion=self.repulsion,
                gravity= self.gravity,
                is_focusnode=True,
                is_layout_animation=True,
                linestyle_opts=opts.LineStyleOpts(
                    curve=self.line_curve, opacity=self.line_opacity, width=self.line_width, color=self.line_color
                ),
                label_opts=opts.LabelOpts(
                    is_show=self.show_labels,
                    position=self.label_position,
                    color="auto",
                    formatter="{b}",
                    font_size=self.font_size,
                    font_weight=self.font_weight,
                    overflow = 'break',
                    text_width = self.text_width
                ),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title= "Taxa-Functions Network",
                    subtitle= f"{sample_list}" if self.show_sub_title else None,
                    subtitle_textstyle_opts=opts.TextStyleOpts(font_size=10),
                ),
                toolbox_opts=opts.ToolboxOpts(
                    is_show=True,
                    orient="vertical",
                    pos_left="left",
                    pos_top="bottom",
                    feature=opts.ToolBoxFeatureOpts(
                        save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(
                            type_="png",
                            background_color="black" if self.theme == 'dark' else "white",
                            pixel_ratio=2,
                            title="Save as PNG",
                        ),
                        restore=opts.ToolBoxFeatureRestoreOpts(title="Restore"),
                        data_zoom=opts.ToolBoxFeatureDataZoomOpts(
                            zoom_title="Zoom", is_show=False, back_title="Back"
                        ),
                        data_view=opts.ToolBoxFeatureDataViewOpts(title="Data View"),
                        magic_type=opts.ToolBoxFeatureMagicTypeOpts(
                            line_title="Line",
                            bar_title="Bar",
                            is_show=False,
                            stack_title="Stack",
                            tiled_title="Tiled",
                        ),
                    ),
                ),
            )
        )


        return c
    

    def plot_co_expression_network(self, df_type:str= 'taxa', corr_method:str = 'pearson', 
                                corr_threshold:float=0.5, sample_list:list = None, 
                                width:int = 12, height:int = 8, focus_list:list = [], plot_list_only:bool = False,
                                ):
        from matplotlib import colormaps
        #check sample_list length
        if len(sample_list) < 2:
            raise ValueError(f"sample_list should have at least 2 samples, but got {len(sample_list)}")

        df_dict = {'taxa': self.tfa.taxa_df, 
                'functions': self.tfa.func_df, 
                'taxa-functions': self.tfa.taxa_func_df, 
                'peptides': self.tfa.peptide_df,
                'proteins': self.tfa.protein_df,
                'custom': self.tfa.custom_df}
        
        df = df_dict[df_type].copy()
        if self.rename_taxa:
            print("Renaming taxa to last level")
            df = self.tfa.rename_taxa(df)
            # modify the focus_list to the last level taxa
            focus_list = self.modify_focus_list(focus_list)
                        
        if extra_cols := sample_list:
            print(f"Using sample list provided {extra_cols}")
            df = df[extra_cols]
        else:
            print("No sample list provided, using all samples")

        df = self.tfa.replace_if_two_index(df)

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
        
        categories = [{"name": "Focused", "itemStyle": {"normal": {"color": self.co_network_focus_color}}}, 
                    {"name": "Normal", "itemStyle": {"normal": {"color": self.co_network_normal_color}}}]

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
        
        connected_nodes = set()
        links = []
        # calculate the correlation between each pair of nodes, and create a link if the correlation is above a threshold
        # the color of the link is determined by the correlation value
        for i in range(len(correlation_matrix)):
            for j in range(i+1, len(correlation_matrix)):
                correlation = correlation_matrix.iloc[i, j]
                # create a link if the correlation is above a threshold
                if correlation > corr_threshold:
                    color = colormaps.get_cmap('viridis')(1 - (correlation - corr_threshold) / corr_threshold) 
                    color = '#%02x%02x%02x' % (int(color[0]*255), int(color[1]*255), int(color[2]*255))
                    line_width = (correlation - corr_threshold) / (1 - corr_threshold) * self.line_width * 2
                    links.append({"source": correlation_matrix.columns[i], "target": correlation_matrix.columns[j], "value": correlation, "lineStyle": {"color": color, "width": line_width}})
                    connected_nodes.add(correlation_matrix.columns[i])
                    connected_nodes.add(correlation_matrix.columns[j])

        nodes = []
        for item in correlation_matrix.columns:
            if item not in connected_nodes and item not in focus_list:
                continue  # Skip the node if it is not connected and not in focus list
            
            if focus_list and len(focus_list) > 0:
                if plot_list_only and item not in focus_list and item not in linked_nodes:
                    continue # skip the node if it's not in the focus list and not linked to any node in the focus list

                if item in focus_list: # mark the focus nodes with a different color
                    node_size = 50
                    color = self.co_network_focus_color
                    category = 0  # Focus category
                else:
                    node_size = (node_sizes[item] - min_node_size) / (max_node_size - min_node_size) * 30 + 10
                    color = colormaps.get_cmap('viridis_r')(node_size / 40)  # normalize the node size to [0, 1] for the color map
                    color = '#%02x%02x%02x' % (int(color[0]*255), int(color[1]*255), int(color[2]*255))
                    category = 1  # Normal category
            else:
                node_size = (node_sizes[item] - min_node_size) / (max_node_size - min_node_size) * 30 + 10
                color = colormaps.get_cmap('viridis_r')(node_size / 40)  # normalize the node size to [0, 1] for the color map
                color = '#%02x%02x%02x' % (int(color[0]*255), int(color[1]*255), int(color[2]*255))
                category = 1  # Normal category
            
            nodes.append({
                "name": item, 
                "symbolSize": node_size, 
                "itemStyle": {"color": color},
                "category": category
            })
        
        pic = (
            Graph(
                init_opts=opts.InitOpts(
                    width=f"{width*100}px",
                    height=f"{height*100}px",
                    theme=self.theme
                )
            )
            .add(
                "",
                nodes,
                links,
                categories=categories,
                gravity= self.gravity,
                repulsion=self.repulsion,
                is_layout_animation=True,
                label_opts=opts.LabelOpts(
                    is_show=self.show_labels,
                    font_size=self.font_size,
                    position=self.label_position,
                    color="auto", 
                    formatter="{b}",
                    font_weight=self.font_weight,
                    overflow = 'break',
                    text_width = self.text_width
                ),
                linestyle_opts=opts.LineStyleOpts(
                    opacity=self.line_opacity, 
                    curve=self.line_curve
                ),
            )
            .set_global_opts(
                legend_opts=opts.LegendOpts(is_show=True),
                title_opts=opts.TitleOpts(
                    title="Co-expression Network",
                    # subtitle=f"{sample_list}" if sample_list != self.tfa.sample_list else "",
                    # subtitle_textstyle_opts=opts.TextStyleOpts(font_size=10),
                ),
                toolbox_opts=opts.ToolboxOpts(
                    is_show=True,
                    orient="vertical",
                    pos_left="left",
                    pos_top="bottom",
                    feature=opts.ToolBoxFeatureOpts(
                        save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(
                            type_="png",
                            background_color="black" if self.theme == 'dark' else "white",
                            pixel_ratio=2,
                            title="Save as PNG",
                        ),
                        restore=opts.ToolBoxFeatureRestoreOpts(title="Restore"),
                        data_zoom=opts.ToolBoxFeatureDataZoomOpts(
                            zoom_title="Zoom", is_show=False, back_title="Back"
                        ),
                        data_view=opts.ToolBoxFeatureDataViewOpts(title="Data View"),
                        magic_type=opts.ToolBoxFeatureMagicTypeOpts(
                            line_title="Line",
                            bar_title="Bar",
                            is_show=False,
                            stack_title="Stack",
                            tiled_title="Tiled",
                        ),
                    ),
                ),
            )
        )
        return pic

        

# NetworkPlot(sw).plot_co_expression_network(df_type='func', corr_threshold=0.8, sample_list=sw.get_sample_list_in_a_group('V1') , focus_list=["'glutamate synthase"]).render_notebook()
    
# NetworkPlot(sw,
#             show_labels=True,
#             rename_taxa=True,
#             font_size=10

#             ).plot_tflink_network(sample_list=sw.get_sample_list_in_a_group('V1'), 
#                                   focus_list=["d__Bacteria|p__Proteobacteria|c__Gammaproteobacteria|o__Enterobacterales|f__Enterobacteriaceae <'glutamate synthase>"]
                                  
#                                     ).render_notebook()
            