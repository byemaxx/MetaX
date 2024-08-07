from pyecharts.charts import TreeMap
from pyecharts import options as opts
# from .get_distinct_colors import GetDistinctColors


class TreeMapPlot:
    def __init__(self, theme='white'):
        self.sample_list = None
        self.level_num = None
        self.legend = False
        self.font_size = 5
        self.show_title = True
        self.theme = theme


    def _build_treemap_data(self, df):
        
        self.sample_list = df.columns.tolist()
        df['all_samples_sum'] = df.sum(axis=1)
        df = df[['all_samples_sum']]
        df['Taxon'] = df.index
        self.level_num = len(df['Taxon'][0].split('|'))
        
        root = []
        path_map = {}

        for _, row in df.iterrows():
            levels = row['Taxon'].split('|')
            value = row['all_samples_sum']
            current_path = ""

            for depth, level in enumerate(levels):
                if current_path != "":
                    current_path += "|"
                current_path += level

                if current_path not in path_map:
                    node = {"name": level, "value": value}
                    path_map[current_path] = node
                    if depth == 0:  # 根节点
                        root.append(node)
                    else:
                        parent_path = "|".join(current_path.split("|")[:-1])
                        parent_node = path_map[parent_path]
                        parent_node.setdefault("children", []).append(node)
        
        # 定义递归函数来计算节点的值
        def _calc_node_value(node):
            # 如果节点有子节点，则递归计算其所有子节点的值
            if 'children' in node:
                total_value = sum(_calc_node_value(child) for child in node['children'])
                node['value'] = total_value
            return node['value']
        
        # 计算每个根节点的值
        for node in root:
            _calc_node_value(node)

        return root




    def create_treemap_chart(self, taxa_df, width=10, height=8, title='TreeMap', show_sub_title:bool = True, font_size=8):
        self.show_title = show_sub_title
        self.font_size = font_size
        
        print('Summarizing all samples values...')
        # chcek if d__
        if 'd__' not in taxa_df.index.tolist()[0]:
            raise ValueError('The taxa_df must be a taxa table with d__ in the index')
        # check how many different d__ in the index
        index = taxa_df.index.tolist()
        d_list = [i.split('|')[0] for i in index]
        d_list = list(set(d_list))
        df_dict = {}
        if len(d_list) > 1:
            # divide the taxa_df into different d__ and plot them separately
            print(f'The taxa_df contains more than one d__: {d_list}')
            self.legend = True
            
            
        for d in d_list:
            dft = taxa_df[taxa_df.index.str.contains(d)]
            #remove d__ from the index
            dft.index = [i.split('|', 1)[1] for i in dft.index]
            df_dict[d] = dft

        
        treemap_data_dict = {}
        for name, dft in df_dict.items():
            treemap_data = self._build_treemap_data(dft)
            treemap_data_dict[name] = treemap_data
            
            max_depth = dft.index.to_list()[0].count('|') + 10
            
            # 为每个层级设置样式
            levels_styles = []
            for d in range(max_depth + 1):
                color_saturation = [0.2 + 0.6 * (d / max_depth), 0.3 + 0.6 * (d / max_depth)]
                item_style = opts.TreeMapItemStyleOpts(
                    border_color_saturation=  None if d == 0 else (0.7 - d / max_depth),
                    gap_width=max(0.2, 1 - d / max_depth) if d != 0 else 1,
                    border_width=max(0.2, 1 - d / max_depth) if d != 0 else 1,
                    border_color="#555"  if d == 0 else None,
                )
                    
                levels_styles.append(opts.TreeMapLevelsOpts(color_saturation=color_saturation, treemap_itemstyle_opts=item_style))
                
        c = TreeMap(
            init_opts=opts.InitOpts(
                width=f"{width*100}px", height=f"{height*100}px", theme=self.theme
            )
        )
        
        colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc']
        # colors = GetDistinctColors().get_distinct_colors(10, convert=True)
        c.options.update(color=colors)

        # make d__Bacteria frist in dict
        if 'd__Bacteria' in treemap_data_dict:
            treemap_data_dict = {'d__Bacteria': treemap_data_dict.pop('d__Bacteria')} | treemap_data_dict
        
        for name, treemap_data in treemap_data_dict.items():
            c.add(
                series_name=name,
                data=treemap_data,
        levels=levels_styles
    )
    
        c.set_global_opts(
            title_opts=opts.TitleOpts(title=title, subtitle=None) if not self.show_title else opts.TitleOpts(title=title, subtitle=str(self.sample_list), 
                                      subtitle_textstyle_opts=opts.TextStyleOpts(font_size=self.font_size)),
            legend_opts=opts.LegendOpts(is_show=self.legend, selected_mode='single'),
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
                                                data_view=opts.ToolBoxFeatureDataViewOpts(title="Data View"),
                                                data_zoom=opts.ToolBoxFeatureDataZoomOpts(zoom_title="Zoom", 
                                                                                            is_show=False,
                                                                                        back_title="Back"),
                                                magic_type=opts.ToolBoxFeatureMagicTypeOpts(line_title="Line", 
                                                                                            bar_title="Bar",
                                                                                            is_show=False, 
                                                                                            stack_title="Stack",
                                                                                            tiled_title="Tiled"),
                                                
                                                ),
                ),
        
        )
        
        return c



# pic = TreeMapPlot().create_treemap_chart(dft, width=10, height=8, title='TreeMap', show_sub_title=False, font_size=8)
# pic.render_notebook()
