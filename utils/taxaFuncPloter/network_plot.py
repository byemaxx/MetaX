from pyecharts import options as opts
from pyecharts.charts import Graph

class NetworkPlot:
    def __init__(self, tfobj=None):
        self.tfobj = tfobj
    

    def create_nodes_links(self, sample_list:list = None):
        df = self.tfobj.taxa_func_df.copy()
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


        taxa_sum = df.groupby('taxa')['sum'].sum().to_dict()
        function_sum = df.groupby('function')['sum'].sum().to_dict()

        min_value = min(min(taxa_sum.values()), min(function_sum.values()))
        max_value = max(max(taxa_sum.values()), max(function_sum.values()))

        def normalize(value):
            scaled_value = 100 * (value - min_value) / (max_value - min_value)
            return max(scaled_value, 5)  # set a minimum size


        taxa = df["taxa"].unique().tolist()
        functions = df["function"].unique().tolist()
        nodes = [{"name": taxon, "category": 0, "symbolSize": normalize(taxa_sum[taxon]), "value": taxa_sum[taxon]} for taxon in taxa] + [{"name": function, "category": 1, "symbolSize": normalize(function_sum[function]), "value": function_sum[function]} for function in functions]

        links = [{"source": row["taxa"], "target": row["function"]} for _, row in df.iterrows()]

        # 定义不同类别节点的样式
        categories = [
            {"name": "Taxa", "itemStyle": {"normal": {"color": "#ff7f50"}}},
            {"name": "Function", "itemStyle": {"normal": {"color": "#87cefa"}}},
        ]


        return nodes, links, categories


    
    def plot_network(self, sample_list:list = None, width:int = 1200, height:int = 800):
        nodes, links, categories = self.create_nodes_links(sample_list)
        c = (
            Graph(init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px"))
            .add(
                "",
                nodes,
                links,
                categories,
                repulsion=50,
                friction = 0.6,
                linestyle_opts=opts.LineStyleOpts(curve=0.2),
                gravity = 0.1,
                label_opts=opts.LabelOpts(is_show=False, position="right", color="auto", formatter="{b}"),
            )
            .set_global_opts(
                legend_opts=opts.LegendOpts(is_show=False),
                title_opts=opts.TitleOpts(title=f"Taxa-Function Network", subtitle=f"{sample_list}",  subtitle_textstyle_opts=opts.TextStyleOpts(font_size=10)),
                toolbox_opts=opts.ToolboxOpts( is_show=True, feature={"saveAsImage": {}, "restore": {}}),
            )        
            )
        
        return c