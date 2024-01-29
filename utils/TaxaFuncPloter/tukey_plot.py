import matplotlib.pyplot as plt
import seaborn as sns


class TukeyPlot:
    # EXAMPLE:
    # taxon_name="d__Bacteria|p__Firmicutes_A|c__Clostridia|o__Lachnospirales|f__Lachnospiraceae|g__Acetatifactor|s__Acetatifactor sp900066565"
    # func_name="'Cold-shock' DNA-binding domain"
    # tukey_res = sw.CrossTest.get_stats_tukey_test(taxon_name=taxon_name, func_name=func_name)
    def plot_tukey(self, tukey_df):
        # stats number of groups
        n_groups = len(tukey_df['group1'].unique())
        figsize = (n_groups * 1.2, 8)
        plt.figure(figsize=figsize)
        fig = sns.barplot(data=tukey_df, x='group1', y='meandiff', hue='group2', capsize=.2, palette='Set3')
        plt.xticks(rotation=45)
        plt.title('Confidence Intervals of Mean Differences')
        plt.legend(title='Group 2', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.show()
        return fig