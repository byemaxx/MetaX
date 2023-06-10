import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt


class VolcanoPlot():

    # EXAMPLE: fc_df = sw.call_deseq2(sw.func_taxa_df, ['NDC', 'KES'])
    # plot_volcano(fc_df, 0.01, 1, 'NDC VS KES', (8, 6))

    def plot_volcano(self, df_fc, padj=0.05, log2fc=1, title_name='2 groups', width=8, height=6):
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

        # 生成图例标签和相应的句柄，并按照指定顺序排列
        handles = []
        labels = []
        for t in ['up', 'down', 'normal']:
            if t == 'up':
                h = plt.scatter([], [], s=50, color='#d23918',
                                alpha=0.6, linewidth=0.5, edgecolor='black')
            elif t == 'down':
                h = plt.scatter([], [], s=50, color='#68945c',
                                alpha=0.6, linewidth=0.5, edgecolor='black')
            else:
                h = plt.scatter([], [], s=50, color='#6b798e',
                                alpha=0.6, linewidth=0.5, edgecolor='black')
            handles.append(h)
            labels.append(f'{t} ({locals()[f"count_{t}"]})')

        # 关闭当前空图
        plt.close()

        # 绘制火山图
        plt.figure(figsize=( width, height))
        fig = sns.scatterplot(x=df['log2FoldChange'], y=-np.log10(df['padj']), s=50, hue=df['type'], alpha=0.6,
                              palette={'up': '#d23918', 'down': '#68945c', 'normal': '#6b798e'}, linewidth=0.5, edgecolor='black')

        # 设置标题、坐标轴标签和图例
        fig.set_title(
            f'Volcano plot of {title_name} (padj < {padj}, log2FoldChange > {log2fc})')
        fig.set_xlabel('log2FoldChange')
        fig.set_ylabel('-log10(padj)')
        fig.legend(handles=handles, labels=labels, loc='upper right')
        plt.show()
        return fig


