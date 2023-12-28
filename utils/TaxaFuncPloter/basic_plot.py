import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

class BasicPlot:
    def __init__(self, tfobj):
        self.tfa =  tfobj
    # input: self.get_stats_peptide_num_in_taxa()
    def plot_taxa_stats(self):
        df = self.tfa.get_stats_peptide_num_in_taxa()
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
        return ax

    # input: self.get_stats_taxa_level()
    def plot_taxa_number(self):
        df = self.tfa.get_stats_taxa_level()
        custom_params = {"axes.spines.right": False, "axes.spines.top": False}
        # plt.figure(figsize=(8, 6))
        sns.set_theme(style="ticks", rc=custom_params)

        ax = sns.barplot(data=df, x='taxa_level', y='count',dodge=False, hue='taxa_level')
        for i in ax.containers:
            ax.bar_label(i,)
        ax.set_title('Number of taxa in different taxa level')
        ax.set_xlabel('Taxa level')
        ax.set_ylabel('Number of taxa')
        # plt.show()
        plt.close()
        return ax

    # input: self.get_stats_func_prop()
    def plot_prop_stats(self, func_name = 'Description'):
        df = self.tfa.get_stats_func_prop(func_name)
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
        return ax
        
    # input: df_mat
    def plot_pca_sns(self, df, table_name = 'Table', show_label = True, width=10, height=8, font_size = 10, font_transparency = 0.6, adjust_label:bool = False):
        try:
            dft= df.copy()
            
            sample_list = dft.columns
            new_sample_name = []
            group_list = []
            for i in sample_list:
                group = self.tfa.get_group_of_a_sample(i)
                new_sample_name.append(f'{i} ({group})')
                group_list.append(group)
                
            dft = dft.T
            mat = dft.values
            plt.figure(figsize=(width, height))
            pca = PCA(n_components=2)
            components = pca.fit_transform(mat)
            total_var = pca.explained_variance_ratio_.sum() * 100
            sns.set_theme(style="ticks", rc={"axes.spines.right": False, "axes.spines.top": False})
            fig = sns.scatterplot(x=components[:, 0], y=components[:, 1],
                                hue=group_list, s = 100, alpha=0.8, edgecolor='black', linewidth=0.5)
            if show_label:
                text = [fig.text(components[i, 0], components[i, 1], s=new_sample_name[i], size=font_size, 
                            color='black', alpha=font_transparency) for i in range(len(new_sample_name))]
                if adjust_label:
                    from adjustText import adjust_text
                    text = adjust_text(text)
                
            fig.set_title(f'PCA of {str(table_name)} (total variance explained: {total_var:.2f}%)', 
                        fontsize=15, fontweight='bold')
            fig.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.2f}%)')
            fig.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.2f}%)')
            # tight_layout automatically adjusts subplot params so that the subplot(s) fits in to the figure area.
            plt.tight_layout()
            plt.show()

            return fig
        except Exception as e:
            plt.close('all')
            raise e

    def plot_box_sns(self, df, table_name = 'Table', show_fliers = False, width=10, height=8, font_size = 10):
        dft = df.copy()
        
        # create a new dataframe with new sample names and sorted by group
        sample_list = dft.columns
        new_sample_name = []
        group_list = []
        for i in sample_list:
            group = self.tfa.get_group_of_a_sample(i)
            new_sample_name.append(f'{i} ({group})')
            group_list.append(group)
        
            # Order the SAMPLE_LIST and GROUP_LIST according to the group order
            group_order = sorted(list(set(group_list)))
            ordered_sample_list = []
            ordered_sample_name = []
            for group in group_order:
                samples_in_group = [sample for sample, group_sample in zip(sample_list, group_list) if group_sample == group]
                sample_names_in_group = [sample_name for sample_name, group_sample in zip(new_sample_name, group_list) if group_sample == group]
                ordered_sample_list.extend(samples_in_group)
                ordered_sample_name.extend(sample_names_in_group)
        dft = dft[ordered_sample_list]
        # replace 0 with nan
        dft = dft.replace(0, np.nan)
        
        # set style
        custom_params = {"axes.spines.right": False, "axes.spines.top": False}
        sns.set_theme(style="ticks", rc=custom_params)

        # set size
        plt.figure(figsize=(width, height))
        if show_fliers:
            ax = sns.boxplot(data=dft, showfliers=True)
        else:
            ax = sns.boxplot(data=dft, showfliers=False)
        # set x label
        ax.set_xticklabels(new_sample_name, rotation=90, horizontalalignment='right', fontsize=font_size)
        ax.set_xlabel('Sample')
        ax.set_ylabel('Intensity')
        ax.set_title(f'Intensity Boxplot of {table_name}')
        # move the botton up
        plt.subplots_adjust(bottom=0.2)
        plt.tight_layout()
        plt.show()
        # plt.close()
        return ax
    
    def plot_corr_sns(self, df, table_name = 'Table', cluster = False, width=10, height=8, font_size = 10):
        dft= df.copy()
        
        sample_list = dft.columns
        new_sample_name = []
        for i in sample_list:
            group = self.tfa.get_group_of_a_sample(i)
            new_sample_name.append(f'{i} ({group})')
        dft.columns = new_sample_name
        
        corr = dft.corr()
        # mask = np.triu(np.ones_like(corr, dtype=bool))

        try:
            if cluster:
                cluster_grid = sns.clustermap(corr, linewidths=.5, cmap='coolwarm', figsize=(width, height))
                ax = cluster_grid.ax_heatmap  # 获取热图的轴
            else:
                plt.figure(figsize=(width, height))
                ax = sns.heatmap(corr, linewidths=.5, cmap='coolwarm')
                
            ax.set_xticklabels(ax.get_xticklabels(), fontsize=font_size, rotation=90)
            ax.set_yticklabels(ax.get_yticklabels(), fontsize=font_size, rotation=0)
        
            #set title
            plt.title(f'Correlation of {table_name}')
            plt.tight_layout()
            plt.show()
            # plt.close()
            return ax
        except Exception as e:
            plt.close('all')
            raise e
        
        
    
        
        
        