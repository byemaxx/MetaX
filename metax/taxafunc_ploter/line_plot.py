import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

class LinePlot:
    def __init__(self, tfobj):
        self.tfobj =  tfobj
    # plot intensity line for each sample
    # Example: plot_intensity_line(sw, func_name=func_name, taxon_name=taxon_name, fig_size=(30,20))

    def plot_intensity_line(self, taxon_name:str=None, sample_list:list = None, func_name:str=None, peptide_seq=None, width:int=20, height:int=12):
        fig_size = (width, height)

        df = self.tfobj.GetMatrix.get_intensity_matrix(taxon_name=taxon_name, func_name=func_name, peptide_seq=peptide_seq, sample_list= sample_list)
        if df.empty:
            raise ValueError('No data to plot')
        # create color list for groups & rename columns
        col_names = df.columns.tolist()
        meta_df = self.tfobj.meta_df
        meta_name = self.tfobj.meta_name
        groups_list = []
        new_col_names = []
        for i in col_names:
            group = meta_df[meta_df['Sample'] == i]
            group = group[meta_name].values[0]
            new_col_names.append(f'{i} ({group})')
            groups_list.append(group)
        df.columns = new_col_names
        index_name = df.index.name
        
        # create title
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
        fig = sns.lineplot(x='Samples', y='Intensity', hue=index_name, data=dfp, palette='Set1', legend = True)
        
        fig.set_title(title, fontsize=15)
        fig.set_xlabel('Samples', fontsize=15)
        fig.set_ylabel('Intensity', fontsize=15)
        fig.tick_params(axis='x', rotation=90, labelsize=8)
        
        plt.show()
        return fig
