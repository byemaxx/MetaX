import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
import seaborn as sns
import matplotlib.pyplot as plt

class BasicPlot:
    def __init__(self, tfobj):
        self.tfobj =  tfobj
    # input: self.get_stats_peptide_num_in_taxa()
    def plot_taxa_stats(self):
        df = self.tfobj.get_stats_peptide_num_in_taxa()
        custom_params = {"axes.spines.right": False, "axes.spines.top": False}

        # plt.figure(figsize=(8, 6))
        sns.set_theme(style="ticks", rc=custom_params)

        ax = sns.barplot(data=df, x='LCA_level', y='count', hue='label',dodge=False)
        for i in ax.containers:
            ax.bar_label(i,)
        ax.set_title('Number of identified peptides in different taxa level')
        ax.set_xlabel('Taxa level')
        ax.set_ylabel('Number of peptides')
        ax.legend(title='Taxa level (frequency)',  ncol=2)
        # plt.show()
        plt.close()
        return ax.get_figure()

    # input: self.get_stats_taxa_level()
    def plot_taxa_number(self):
        df = self.tfobj.get_stats_taxa_level()
        custom_params = {"axes.spines.right": False, "axes.spines.top": False}
        # plt.figure(figsize=(8, 6))
        sns.set_theme(style="ticks", rc=custom_params)

        ax = sns.barplot(data=df, x='taxa_level', y='count',dodge=False)
        for i in ax.containers:
            ax.bar_label(i,)
        ax.set_title('Number of taxa in different taxa level')
        ax.set_xlabel('Taxa level')
        ax.set_ylabel('Number of taxa')
        # plt.show()
        plt.close()
        return ax.get_figure()

    # input: self.get_stats_func_prop()
    def plot_prop_stats(self, func_name = 'Description'):
        df = self.tfobj.get_stats_func_prop(func_name)
        # #dodge=False to make the bar wider
        # plt.figure(figsize=(8, 6))
        custom_params = {"axes.spines.right": False, "axes.spines.top": False}
        sns.set_theme(style="ticks", rc=custom_params)
        ax = sns.barplot(data=df, x='prop', y='n', hue='label', dodge=False, palette='tab10_r')
        for i in ax.containers:
            ax.bar_label(i,)
        ax.set_title(f'Number of different proportions of peptides in {func_name}')
        ax.set_xlabel('Proportion of function')
        ax.set_ylabel('Number of peptides')
        ax.legend(title='Proportion of function (frequency)',  ncol=2, loc = 'upper left')
        plt.xticks(rotation=45)
        plt.subplots_adjust(bottom=0.25)
        # plt.show()
        plt.close()
        return ax.get_figure()
        
    # input: df_mat
    def plot_pca_sns(self, df, table_name = 'Table', show_label = True, group_list = None):
        try:
            meta_df = self.tfobj.meta_df.copy()
            if group_list is not None:
                meta_df = meta_df[meta_df[self.tfobj.meta_name].isin(group_list)]

            SAMPLE_LIST = meta_df['Sample']
            GROUP_LIST = meta_df[self.tfobj.meta_name]
            new_sample_name = [
                f'{SAMPLE_LIST.iloc[i]} ({GROUP_LIST.iloc[i]})'
                for i in range(len(SAMPLE_LIST))
            ]

            # from adjustText import adjust_text
            dft = df[SAMPLE_LIST]
            dft = dft.T
            mat = dft.values
            plt.figure(figsize=(10, 8))
            pca = PCA(n_components=2)
            components = pca.fit_transform(mat)
            total_var = pca.explained_variance_ratio_.sum() * 100

            fig = sns.scatterplot(x=components[:, 0], y=components[:, 1], 
                                hue=GROUP_LIST, s = 100, alpha=0.8)
            if show_label:
                text = [fig.text(components[i, 0], components[i, 1], s=new_sample_name[i], size='medium', 
                            color='black', alpha=0.6) for i in range(len(new_sample_name))]
            # text = adjust_text(text)
            fig.set_title(f'PCA of {str(table_name)} (total variance explained: {total_var:.2f}%)', 
                        fontsize=15, fontweight='bold')
            fig.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.2f}%)')
            fig.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.2f}%)')
            plt.show()

            return fig
        except Exception as e:
            plt.close('all')
            raise e

    def plot_box_sns(self, df, table_name = 'Table', show_fliers = False, group_list = None):
        import numpy as np
        meta_df = self.tfobj.meta_df.copy()
        if group_list is not None:
            meta_df = meta_df[meta_df[self.tfobj.meta_name].isin(group_list)]

        SAMPLE_LIST = meta_df['Sample']
        GROUP_LIST = meta_df[self.tfobj.meta_name]
        new_sample_name = [
            f'{SAMPLE_LIST.iloc[i]} ({GROUP_LIST.iloc[i]})'
            for i in range(len(SAMPLE_LIST))
        ]

        # Order the SAMPLE_LIST and GROUP_LIST according to the group order
        group_order = sorted(list(set(GROUP_LIST)))
        ordered_sample_list = []
        ordered_sample_name = []
        for group in group_order:
            samples_in_group = [sample for sample, group_sample in zip(SAMPLE_LIST, GROUP_LIST) if group_sample == group]
            sample_names_in_group = [sample_name for sample_name, group_sample in zip(new_sample_name, GROUP_LIST) if group_sample == group]
            ordered_sample_list.extend(samples_in_group)
            ordered_sample_name.extend(sample_names_in_group)

        # Reorder the dataframe according to the new sample list order
        dft = df[ordered_sample_list]

        # replace 0 to NaN
        dft = dft.replace(0, np.nan)

        custom_params = {"axes.spines.right": False, "axes.spines.top": False}
        sns.set_theme(style="ticks", rc=custom_params)

        # set size
        plt.figure(figsize=(10, 8))
        if show_fliers:
            ax = sns.boxplot(data=dft, showfliers=True)
            ylimit = np.quantile(dft.mean(), 0.75) * 3
        else:
            ax = sns.boxplot(data=dft, showfliers=False)
            ylimit = np.quantile(dft.mean(), 0.75) * 2
        # set x label
        ax.set_xticklabels(ordered_sample_name, rotation=90, horizontalalignment='right')
        ax.set_xlabel('Sample')
        ax.set_ylabel('Intensity')
        ax.set_title(f'Intensity Boxplot of {table_name}')
        # set y limit as the 4th quantile of average peptide number
        ax.set_ylim(0, ylimit)
        plt.show()
        # plt.close()
        return ax