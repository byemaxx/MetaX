from pyecharts.charts import Sunburst
from pyecharts import options as opts
import random
import colorsys

class SunburstPlot:
    def __init__(self, theme='white'):
        self.sameple_list = None
        self.level_num = None
        self.theme = theme
        
    def adjust_color(self, rgb_color, saturation_factor=0.7, lightness_factor=1.3):
        """
        Adjusts the saturation and lightness of an RGB color.

        Parameters:
        - rgb_color (tuple): The RGB color as a tuple (r, g, b).
        - saturation_factor (float): The factor by which to adjust the saturation. Default is 0.7.
        - lightness_factor (float): The factor by which to adjust the lightness. Default is 1.3.

        Returns:
        - str: The adjusted color in the format 'rgb(r, g, b)'.
        """
        r, g, b = rgb_color
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        l = max(0, min(1, lightness_factor * l))
        s = max(0, min(1, saturation_factor * s))
        # Ensure the color doesn't become too light
        if l > 0.9:
            l = 0.9
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return f'rgb({int(r * 255)},{int(g * 255)},{int(b * 255)})'
    
    def get_random_color(self):
        while True:
            r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
            # Avoid generating pure white color
            if not (r == 255 and g == 255 and b == 255):
                color = self.adjust_color((r, g, b))
                return color
    
    
    def _build_sunburst_data(self, df, show_label, label_font_size=8):
        if 'd__' not in df.index.tolist()[0]:
           raise ValueError('The taxa_df must be a taxa table with d__ in the index')
        self.sameple_list = df.columns.tolist()
        
        df['all_samples_sum'] = df.sum(axis=1)
        #only keep all samples sum column
        df = df[['all_samples_sum']]
        df['Taxon'] = df.index
        
        
        # only keep
        self.level_num = len(df['Taxon'][0].split('|'))

        root = {}  
        color_map = {} 


                
        for _, row in df.iterrows():
            levels = row['Taxon'].split('|') 
            value = row['all_samples_sum']  
            node = root
            depth = 1  

            for level in levels:
                if level not in color_map: 
                    # random_color = f'#{random.randint(0, 0xffffff):06x}'
                    # random a rgb color
                    # random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                    # color_map[level] = self.adjust_color(random_color)
                    color_map[level] = self.get_random_color()
                    
                # 检查当前层级是否已经存在
                found = False
                for child in node.get("children", []):
                    if child.get("name") == level:
                        node = child
                        found = True
                        break

                if not found:
                    # 根据深度决定标签位置
                    label_position = 'outside' if depth ==  self.level_num else 'inside'
                    lable_padding = 3 if depth ==  self.level_num else 0
                    if show_label == 'last':
                        is_label_show = True if depth ==  self.level_num else False
                    elif show_label == 'all':
                        is_label_show = True
                    else:
                        is_label_show = False
                    # set last level and second last level label None, others tangential
                    label_rotate = None if depth >  self.level_num-2  else "tangential"
                    new_node = {
                        "name": level, 
                        "children": [], 
                        "itemStyle": {"color": color_map[level]},
                        "label": {"position": label_position, "padding": lable_padding,
                                  "show": is_label_show, "rotate": label_rotate, "fontSize": label_font_size
                                 }
                    }
                    node.setdefault("children", []).append(new_node)
                    node = new_node
                
                depth += 1  

            node["value"] = value
            # 删除空的 children 列表
            if "children" in node and not node["children"]:
                del node["children"]

        return [root]


        
    def create_sunburst_chart(self, taxa_df, width=10, height=8, title='Sunburst', show_label='last', label_font_size=8):
        print('Summarizing all samples values...')
        # chcek if d__Bacteria is in the index

        sunburst_data = self._build_sunburst_data(taxa_df, show_label, label_font_size)


        sunburst_chart = (
            Sunburst(init_opts=opts.InitOpts(width=f'{width*100}px', height=f'{height*100}px', theme=self.theme))
            .add(
                series_name="",
                data_pair=sunburst_data,
                radius=[0, "95%"],
                sort_="desc",
                highlight_policy="ancestor",
                label_layout_opts=opts.SunburstLabelLayoutOpts(is_hide_overlap=True),

            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title, 
                                        #   subtitle=str(self.sameple_list), 
                                          subtitle=None,
                                          subtitle_textstyle_opts=opts.TextStyleOpts(font_size=7)),
                tooltip_opts=opts.TooltipOpts(trigger_on="mousemove"),
                legend_opts=opts.LegendOpts(is_show=False),
                toolbox_opts=opts.ToolboxOpts(
                    is_show=True,
                    orient="vertical",
                    pos_left="left",
                    pos_top="bottom",
                    feature=opts.ToolBoxFeatureOpts( 
                                                    save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(type_="png", 
                                                                                                    background_color="black" if self.theme == 'dark' else "white",
                                                                                                    pixel_ratio=2, 
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
            .set_series_opts(itemstyle_opts=opts.ItemStyleOpts(border_width=0.1, border_color='black', 
                                                            opacity=0.8)
                            )
        )




        return sunburst_chart

# pic = SunburstPlot().create_sunburst_chart(df, width=10, height=8, title='Sunburst', show_label='all', label_font_size=10)
# pic.render_notebook()