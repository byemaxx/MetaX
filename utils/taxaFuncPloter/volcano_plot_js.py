
from pyecharts.charts import Scatter
from pyecharts import options as opts
import numpy as np


class VolcanoPlot():


    def plot_volcano_js(self, df_fc, padj:float=0.05, log2fc:float=1, title_name:str='2 groups', width:int=1200, height:int=800):
        df = df_fc.copy()

        # 计算不同类型的样本数并生成新的图例标签
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

        # create a new column for label
        df['label'] = df.index
        # extract the columns we need
        df = df[['log2FoldChange', 'padj', 'label', 'type']]
        # -log10(padj)
        df['padj'].fillna(1, inplace=True)
        df['padj'] = df['padj'].apply(lambda x: -np.log10(x))
        df['log2FoldChange'] = df['log2FoldChange'].apply(lambda x: round(x, 3))
        df['padj'] = df['padj'].apply(lambda x: round(x, 3))
        
        def color_mapping(type_value):
            if type_value == 'up':
                return "#d23918"
            elif type_value == 'down':
                return "#68945c"
            else:
                return "#6b798e"

        # 创建一个新的列'itemStyle'，其值是一个 ItemStyleOpts 对象
        df['itemStyle'] = df['type'].apply(lambda x: opts.ItemStyleOpts(color=color_mapping(x)))

        Scatter_up = df[df['type'] == 'up'].apply(lambda p: {'name': p['label'], 'value': [p['log2FoldChange'], p['padj']], 'itemStyle': p['itemStyle']}, axis=1)
        Scatter_down = df[df['type'] == 'down'].apply(lambda p: {'name': p['label'], 'value': [p['log2FoldChange'], p['padj']], 'itemStyle': p['itemStyle']}, axis=1)
        Scatter_normal = df[df['type'] == 'normal'].apply(lambda p: {'name': p['label'], 'value': [p['log2FoldChange'], p['padj']], 'itemStyle': p['itemStyle']}, axis=1)

        title = f'Volcano plot of {title_name} (padj < {padj}, log2FoldChange > {log2fc})'
        scatter = (
            Scatter(init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px"))
            .add_xaxis(df['log2FoldChange'].tolist())
            .add_yaxis(
                f"Normal ({count_normal})",
                Scatter_normal.tolist(),
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(type_="value", splitline_opts=opts.SplitLineOpts(is_show=False), name='log2FoldChange'),
                yaxis_opts=opts.AxisOpts(type_="value", splitline_opts=opts.SplitLineOpts(is_show=False), name='-log10(padj)'),
                title_opts=opts.TitleOpts(title=title, pos_left='center'),
                legend_opts=opts.LegendOpts(pos_left='right',  orient='vertical'),
                tooltip_opts=opts.TooltipOpts(is_show=True, position='top', formatter='{b}: {c}'),
                toolbox_opts=opts.ToolboxOpts( is_show=True, feature={"saveAsImage": {}, "restore": {}, "dataZoom": {}}),
            ) )
        
        if count_up > 0:
            scatter.add_yaxis(
                f"Up ({count_up})",
                Scatter_up.tolist(),
                label_opts=opts.LabelOpts(is_show=False),
            )
        if count_down > 0:
            scatter.add_yaxis(
                f"Down ({count_down})",
                Scatter_down.tolist(),
                label_opts=opts.LabelOpts(is_show=False) )
            
        return scatter