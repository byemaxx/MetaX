import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

class VolcanoPlot:
    def plot_volcano(self, df_fc, pvalue: float = 0.05, p_type='padj', log2fc_min: float = 1, log2fc_max: float = 10,
                     title_name='2 groups',font_size:int=12, width=8, height=6, dot_size=15):
        
        def color_mapping(type_value):
            if type_value == 'up':
                return "#d23918"
            elif type_value == 'down':
                return "#68945c"
            elif type_value == 'ultra-up':
                return "#663d74"
            elif type_value == 'ultra-down':
                return "#206864"
            else:  # normal
                return "#6b798e"

        df = df_fc.copy()

        df['type'] = 'normal'
        df.loc[(df[p_type] <= pvalue) & (df['log2FoldChange'] >= log2fc_min) & (df['log2FoldChange'] < log2fc_max), 'type'] = 'up'
        df.loc[(df[p_type] <= pvalue) & (df['log2FoldChange'] >= log2fc_max), 'type'] = 'ultra-up'
        df.loc[(df[p_type] <= pvalue) & (df['log2FoldChange'] <= -log2fc_min) & (df['log2FoldChange'] > -log2fc_max), 'type'] = 'down'
        df.loc[(df[p_type] <= pvalue) & (df['log2FoldChange'] <= -log2fc_max), 'type'] = 'ultra-down'

        # count the number of each type
        count_dict = {type_name: len(df[df['type'] == type_name]) for type_name in ['up', 'down', 'ultra-up', 'ultra-down', 'normal']}
        print(count_dict)

        # create handles and labels for legend
        handles = []
        labels = []
        for t in ['up', 'down', 'ultra-up', 'ultra-down', 'normal']:
            if count_dict[t] == 0:
                continue
            h = plt.scatter([], [], s=150, color=color_mapping(t), alpha=0.8, linewidth=0.5, edgecolor='black')
            handles.append(h)
            labels.append(f'{t} ({count_dict[t]})')

        # close the previous plot
        plt.close()

        # create the volcano plot
        plt.figure(figsize=(width, height))
        fig = sns.scatterplot(x=df['log2FoldChange'], y=-np.log10(df[p_type]), s=dot_size*10, hue=df['type'], alpha=0.8,
                              palette={'up': '#d23918', 'down': '#68945c', 'ultra-up': '#663d74', 'ultra-down': '#206864', 'normal': '#6b798e'}, linewidth=0.5, edgecolor='black')
        plt.axhline(y=-np.log10(pvalue), linestyle='--', color='grey', linewidth=1)  # padj line
        plt.axvline(x=-log2fc_min, linestyle='--', color='grey', linewidth=1)  # log2FoldChange line
        plt.axvline(x=log2fc_min, linestyle='--', color='grey', linewidth=1)   # log2FoldChange line

        # set the title and labels
        fig.set_title(f'Volcano plot of {title_name} (padj < {pvalue}, |log2FoldChange| > {log2fc_min})', fontsize=font_size)
        fig.set_xlabel('log2FoldChange', fontsize=font_size)
        fig.set_ylabel('-log10(padj)', fontsize=font_size)
        fig.legend(handles=handles, labels=labels, loc='upper right', fontsize=font_size- 2 if font_size > 2 else 2)
        sns.despine(trim=True)

        plt.show()
        return fig

# Usage
# vp = VolcanoPlot()
# vp.plot_volcano(df_fc=df_fc, pvalue=0.05, p_type='padj', log2fc_min=1, log2fc_max=10, title_name='OTFs: PBS vs CHO',  font_size=15,
#                 width=12, height=8, dot_size=150)
