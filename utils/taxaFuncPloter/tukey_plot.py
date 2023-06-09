import matplotlib.pyplot as plt
import seaborn as sns


class TukeyPlot:
    # EXAMPLE:
    # taxon_name="d__Bacteria|p__Firmicutes_A|c__Clostridia|o__Lachnospirales|f__Lachnospiraceae|g__Acetatifactor|s__Acetatifactor sp900066565"
    # func_name="'Cold-shock' DNA-binding domain"
    # tukey_res = sw.get_stats_tukey_test(taxon_name=taxon_name, func_name=func_name)
    def plot_tukey(self, tukey_df):
        plt.figure(figsize=(10, 8))
        sns.set_style("whitegrid")
        fig = sns.pointplot(x='meandiff', y='group1', data=tukey_df, join=False,hue='significant', palette="Set2")
        fig.set_title('The Tukey test result')
        fig.set_xlabel('The difference of mean value')
        fig.set_ylabel('Groups')
        plt.show()
        return fig