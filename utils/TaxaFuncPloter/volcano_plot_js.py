
from pyecharts.charts import Scatter
from pyecharts import options as opts
import numpy as np


class VolcanoPlot():


    def plot_volcano_js(self, df_fc, pvalue:float=0.05, p_type ='padj',
                        log2fc_min:float=1, log2fc_max:float = 10, 
                        title_name:str='2 groups',  font_size:int=12,
                        width:int=12, height:int=8):
        
        df = df_fc.copy()
       
        if p_type not in ['pvalue', 'padj']:
            raise ValueError(f'p_type must be "pvalue" or "padj", but got {p_type}')
        
        # 首先将所有行的 'type' 列设置为 'normal'
        df['type'] = 'normal'

        # 然后根据条件覆盖 'type' 列的值
        df.loc[(df[p_type] <= pvalue) & (df['log2FoldChange'] >= log2fc_min) & (df['log2FoldChange'] < log2fc_max), 'type'] = 'up'
        df.loc[(df[p_type] <= pvalue) & (df['log2FoldChange'] >= log2fc_max), 'type'] = 'ultra-up'
        df.loc[(df[p_type] <= pvalue) & (df['log2FoldChange'] <= -log2fc_min) & (df['log2FoldChange'] > -log2fc_max), 'type'] = 'down'
        df.loc[(df[p_type] <= pvalue) & (df['log2FoldChange'] <= -log2fc_max), 'type'] = 'ultra-down'

        # 统计每种类型的数量
        count_dict = {type_name: len(df[df['type'] == type_name]) for type_name in ['up', 'down', 'ultra-up', 'ultra-down', 'normal']}
        print(count_dict)

       
        # create a new column for label
        df['label'] = df.index
        # extract the columns we need
        df = df[['log2FoldChange', p_type, 'label', 'type']]
        # -log10(padj)
        df[p_type].fillna(1, inplace=True)
        df[p_type] = df[p_type].apply(lambda x: -np.log10(x))
        df['log2FoldChange'] = df['log2FoldChange'].apply(lambda x: round(x, 3))
        df[p_type] = df[p_type].apply(lambda x: round(x, 3))
        
        def color_mapping(type_value):
            if type_value == 'up':
                return "#d23918"
            elif type_value == 'down':
                return "#68945c"
            elif type_value == 'ultra-up':
                return "#663d74"
            elif type_value == 'ultra-down':
                return "#206864"
            else: # normal
                return "#9aa7b1"

        # create a list of dict for each type
        Scatter_up = df[df['type'] == 'up'].apply(lambda p: {'name': p['label'], 'value': [p['log2FoldChange'], p[p_type]]}, axis=1)
        scatter_ultra_up = df[df['type'] == 'ultra-up'].apply(lambda p: {'name': p['label'], 'value': [p['log2FoldChange'], p[p_type]]}, axis=1)
        Scatter_down = df[df['type'] == 'down'].apply(lambda p: {'name': p['label'], 'value': [p['log2FoldChange'], p[p_type]]}, axis=1)
        scatter_ultra_down = df[df['type'] == 'ultra-down'].apply(lambda p: {'name': p['label'], 'value': [p['log2FoldChange'], p[p_type]]}, axis=1)
        Scatter_normal = df[df['type'] == 'normal'].apply(lambda p: {'name': p['label'], 'value': [p['log2FoldChange'], p[p_type]]}, axis=1)

        title = f'Volcano plot of {title_name} ({p_type} <= {pvalue},  {log2fc_min} <= log2FoldChange < {log2fc_max})'
        
        scatter = (
            Scatter(init_opts=opts.InitOpts(width=f"{width*100}px", height=f"{height*100}px"))
            .add_xaxis(df['log2FoldChange'].tolist())
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(type_="value", splitline_opts=opts.SplitLineOpts(is_show=False), name='log2FoldChange'),
                yaxis_opts=opts.AxisOpts(type_="value", splitline_opts=opts.SplitLineOpts(is_show=False), name='-log10(padj)'),
                title_opts=opts.TitleOpts(title=title, pos_left='center', title_textstyle_opts=opts.TextStyleOpts(font_size=font_size)),
                legend_opts=opts.LegendOpts(pos_left='right',  orient='vertical', textstyle_opts=opts.TextStyleOpts(font_size=font_size), pos_top="5%"),
                tooltip_opts=opts.TooltipOpts(is_show=True, position='top', formatter='{b}: {c}'),
                toolbox_opts=opts.ToolboxOpts( is_show=True, feature={"saveAsImage": {}, "restore": {}, "dataZoom": {}}),
            ) )
        
        type_to_data_color = {
            'normal': (Scatter_normal, 'normal'),
            'up': (Scatter_up, 'up'),
            'ultra-up': (scatter_ultra_up, 'ultra-up'),
            'down': (Scatter_down, 'down'),
            'ultra-down': (scatter_ultra_down, 'ultra-down')
        }

        for type_name, (scatter_data, color_name) in type_to_data_color.items():
            if count_dict[type_name] > 0:
                scatter.add_yaxis(
                    f"{type_name.title()} ({count_dict[type_name]})",
                    scatter_data.tolist(),
                    label_opts=opts.LabelOpts(is_show=False),
                    itemstyle_opts=opts.ItemStyleOpts(color=color_mapping(color_name))
                )

            
        return scatter