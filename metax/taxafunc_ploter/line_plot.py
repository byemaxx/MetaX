import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

class LinePlot:
    def __init__(self, tfobj):
        self.tfa =  tfobj
    # plot intensity line for each sample
    # Example: plot_intensity_line(sw, func_name=func_name, taxon_name=taxon_name, fig_size=(30,20))

    def plot_intensity_line(
        self,
        taxon_name: str|None = None,
        sample_list: list|None = None,
        func_name: str|None = None,
        peptide_seq=None,
        fig_size: tuple = (20, 12),
        plot_mean: bool = False,
        rename_taxa: bool = True,
        rename_sample: bool = True,
    ):
        sns.set_theme()
        plt.style.use('bmh')

        df = self.tfa.GetMatrix.get_intensity_matrix(
            taxon_name=taxon_name,
            func_name=func_name,
            peptide_seq=peptide_seq,
            sample_list=sample_list,
        )
        if df.empty:
            raise ValueError('No data to plot')
        
        
        if plot_mean:
            df = self.tfa.BasicStats.get_stats_mean_df_by_group(df)
            rename_sample = False
        
        if rename_sample:
            df, _ = self.tfa.add_group_name_for_sample(df)
            
        index_name = df.index.name
        color_list = "tab10" if len(df) <= 10 else "tab20"
        
        # create title
        if rename_taxa and taxon_name is not None:
            taxon_name = taxon_name.split('|')[-1]
            
        if taxon_name is None:
            title = f'{func_name}'
        elif func_name is None:
            title = f'{taxon_name}'
        elif peptide_seq is not None:
            title = f'The intensity of {peptide_seq}'
        else:
            title = f'{taxon_name}\n{func_name}'
            
            
        dfp = pd.melt(df.reset_index(), id_vars=index_name, var_name='Samples', value_name='Intensity')
        plt.figure(figsize=fig_size)
        fig = sns.lineplot(
            x="Samples",
            y="Intensity",
            hue=index_name,
            data=dfp,
            palette=color_list,
            legend=True,
        )

        fig.set_title(title, fontsize=15)
        fig.set_xlabel('')
        fig.set_ylabel('Intensity', fontsize=15)
        fig.tick_params(axis='x', rotation=0, labelsize=15)
        
        
        # set legend out of the plot
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        
        
        plt.show()
        return fig


# LinePlot(sw).plot_intensity_line(taxon_name="d__Bacteria|p__Proteobacteria|c__Gammaproteobacteria|o__Enterobacterales|f__Enterobacteriaceae|g__Citrobacter_B|s__Citrobacter_B koseri", 
#                                  sample_list=sample_list, 
#                                  func_name="ko00061:Fatty acid biosynthesis",
#                                  plot_mean=True,
#                                  rename_taxa=True,
#                                  rename_sample=True,
#                                     fig_size=(10,8)
                                 
#                                  )