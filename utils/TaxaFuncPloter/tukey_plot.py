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
        n_hues = len(tukey_df['group2'].unique())
        figsize = (n_groups * 1.2, 8)
        plt.figure(figsize=figsize)
        
        # Create the barplot
        barplot = sns.barplot(data=tukey_df, x='group1', y='meandiff', hue='group2', capsize=.2, palette='Set3')
        
        # Iterate over the rows of the dataframe and annotate significant bars
        for bar, row in zip(barplot.patches, tukey_df.itertuples(index=True)):
            # Check if the value is significant
            if row.significant == "Yes":
                # Get the x position of the bar
                x_pos = bar.get_x() + bar.get_width() / 2
                # Calculate y position for the asterisk: a bit above the bar
                star_pos = bar.get_height() + (max(tukey_df['meandiff']) - min(tukey_df['meandiff'])) * 0.01
                if star_pos < 0:
                    star_pos = (min(tukey_df['meandiff']) - max(tukey_df['meandiff'])) * 0.01
                # Annotate with an asterisk
                plt.text(x=x_pos, y=star_pos, s='*', ha='center', color='black', fontsize=15)

        # Set plot properties
        plt.xticks(rotation=45)
        plt.title('Confidence Intervals of Mean Differences')
        plt.legend(title='Group 2', bbox_to_anchor=(1.02, 1), loc='upper left', ncol=n_hues//30+1)
        plt.tight_layout()
        
        # Show the plot
        plt.show()
