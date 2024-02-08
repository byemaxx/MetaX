import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

class BasicPlot:
    def __init__(self, tfobj):
        self.tfa =  tfobj
        # reset the style
        plt.style.use('default')
        sns.set()
        
        
    # input: self.get_stats_peptide_num_in_taxa()
    def plot_taxa_stats(self, theme:str = 'Auto', res_type = 'pic'):
        df = self.tfa.BasicStats.get_stats_peptide_num_in_taxa()
        # if 'not_found' is 0, then remove it
        if df[df['LCA_level'] == 'notFound']['count'].values[0] == 0:
            df = df[df['LCA_level'] != 'notFound']
            
        if theme is not None and theme != 'Auto':
            plt.style.use(theme)
        else:
            custom_params = {"axes.spines.right": False, "axes.spines.top": False}

            # plt.figure(figsize=(8, 6))
            sns.set_theme(style="ticks", rc=custom_params)
        plt.subplots()
        ax = sns.barplot(data=df, x='LCA_level', y='count', hue='label',dodge=False)
        for i in ax.containers:
            ax.bar_label(i,)
        ax.set_title('Number of identified peptides in different taxa level')
        ax.set_xlabel('Taxa level')
        ax.set_ylabel('Number of peptides')
        ax.legend(title='Taxa level (frequency)',  ncol=2)
        if res_type == 'show':
            plt.tight_layout()
            plt.show()
        else:
            plt.close()
        return ax

    # input: self.get_stats_taxa_level()
    def plot_taxa_number(self, peptide_num = 1, theme:str = 'Auto', res_type = 'pic'):
        df = self.tfa.BasicStats.get_stats_taxa_level(peptide_num)

        if theme is not None and theme != 'Auto':
            plt.style.use(theme)
        else:
            custom_params = {"axes.spines.right": False, "axes.spines.top": False}
            sns.set_theme(style="ticks", rc=custom_params)
        plt.subplots()
        ax = sns.barplot(data=df, x='taxa_level', y='count',dodge=False, hue='taxa_level')
        for i in ax.containers:
            ax.bar_label(i,)
        ax.set_title(f'Number of taxa in different taxa level. (Peptide number >= {peptide_num})')
        ax.set_xlabel('Taxa level')
        ax.set_ylabel('Number of taxa')
        if res_type == 'show':
            plt.tight_layout()
            plt.show()
        else:
            plt.close()
            
        return ax

    # input: self.get_stats_func_prop()
    def plot_prop_stats(self, func_name = 'eggNOG_OGs', theme:str = 'Auto', res_type = 'pic'):
        df = self.tfa.BasicStats.get_stats_func_prop(func_name)
        # #dodge=False to make the bar wider
        # plt.figure(figsize=(8, 6))
        if theme is not None and theme != 'Auto':
            plt.style.use(theme)
        else:
            custom_params = {"axes.spines.right": False, "axes.spines.top": False} 
            sns.set_theme(style="ticks", rc=custom_params)
        plt.subplots()
        ax = sns.barplot(data=df, x='prop', y='n', hue='label', dodge=False, palette='tab10_r')
        for i in ax.containers:
            ax.bar_label(i,)
        ax.set_title(f'Number of different proportions of peptides in {func_name}')
        ax.set_xlabel('Proportion of function')
        ax.set_ylabel('Number of peptides')
        ax.legend(title='Proportion of function (frequency)',  ncol=2, loc = 'upper left')
        plt.xticks(rotation=45)
        plt.subplots_adjust(bottom=0.25)
        if res_type == 'show':
            plt.tight_layout()
            plt.show()
        else:
            plt.close()

        return ax
        
    # input: df_mat
    def plot_pca_sns(self, df, table_name = 'Table', show_label = True, 
                     width=10, height=8, font_size = 10, rename_sample:bool = False,
                     font_transparency = 0.6, adjust_label:bool = False, theme:str = None, sub_meta:str = 'None'):
        try:
            dft= df.copy()
            
            sample_list = dft.columns
            if sub_meta != 'None':
                style_list = []
                for i in sample_list:
                    style_list.append(self.tfa.get_group_of_a_sample(i, sub_meta))
            else:
                style_list = None

            new_sample_name = []
            group_list = []
            for i in sample_list:
                group = self.tfa.get_group_of_a_sample(i)
                new_sample_name.append(f'{i} ({group})')
                group_list.append(group)

            # Determine if distinct colors are needed
            unique_groups = set(group_list)
            if len(unique_groups) > 10:
                distinct_colors = self.get_distinct_colors(len(unique_groups))
                color_palette = dict(zip(unique_groups, distinct_colors))
            else:
                color_palette = None  # Let seaborn handle the color mapping     
                
                
            dft = dft.T
            mat = dft.values
            

            if theme is not None and theme != 'Auto':
                plt.style.use(theme) 
            else:               
                sns.set(style='whitegrid')
                
            plt.figure(figsize=(width, height))
            pca = PCA(n_components=2)
            components = pca.fit_transform(mat)
            total_var = pca.explained_variance_ratio_.sum() * 100
            # sns.set_theme(style="ticks", rc={"axes.spines.right": False, "axes.spines.top": False})
            fig = sns.scatterplot(x=components[:, 0], y=components[:, 1], palette=color_palette, style=style_list,
                                hue=group_list, s = 150, alpha=0.8, edgecolor='black', linewidth=0.5)
            if show_label:
                new_sample_name = new_sample_name if rename_sample else sample_list
                texts = [fig.text(components[i, 0], components[i, 1], s=new_sample_name[i], size=font_size, 
                            color='black', alpha=font_transparency) for i in range(len(new_sample_name))]
                if adjust_label:
                    from adjustText import adjust_text
                    texts = adjust_text(texts, arrowprops=dict(arrowstyle='->', color='black'))


            fig.set_title(f'PCA of {str(table_name)} (total variance explained: {total_var:.2f}%)', 
                        fontsize= font_size+2, fontweight='bold')
            fig.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.2f}%)',  fontsize=font_size)
            fig.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.2f}%)',  fontsize=font_size)
            # tight_layout automatically adjusts subplot params so that the subplot(s) fits in to the figure area.
            # set legend outside the plot
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0., fontsize=font_size)
            plt.tight_layout()
            plt.show()

            return fig
        except Exception as e:
            plt.close('all')
            raise e
        
        
    def plot_box_sns(self, df, table_name = 'Table', show_fliers = False, width=10, height=8, 
                     font_size = 10, theme:str = None, rename_sample:bool = False,):
        # replace 0 with nan due to optimization of boxplot
        dft = df.replace(0, np.nan)
        
        # create a new dataframe with new sample names and sorted by group
        sample_list = dft.columns
        new_sample_name = []
        group_list = []
        for i in sample_list:
            group = self.tfa.get_group_of_a_sample(i)
            new_sample_name.append(f'{i} ({group})')
            group_list.append(group)
        
            # Order the SAMPLE_LIST and GROUP_LIST according to the group order
            unique_groups = sorted(list(set(group_list)))
            ordered_sample_list = []
            ordered_sample_name = []
            for group in unique_groups:
                samples_in_group = [sample for sample, group_sample in zip(sample_list, group_list) if group_sample == group]
                sample_names_in_group = [sample_name for sample_name, group_sample in zip(new_sample_name, group_list) if group_sample == group]
                ordered_sample_list.extend(samples_in_group)
                ordered_sample_name.extend(sample_names_in_group)

        # reorder the columns
        dft = dft[ordered_sample_list]
        
        if rename_sample:
            new_sample_name = ordered_sample_name
        else:
            new_sample_name = ordered_sample_list

        # Determine if distinct colors are needed
        if len(unique_groups) > 10:
            distinct_colors = self.get_distinct_colors(len(unique_groups))
            color_palette = dict(zip(unique_groups, distinct_colors))
        else:
            color_palette = dict(zip(unique_groups, sns.color_palette("tab10", len(unique_groups))))
            
        group_palette = {}
        for sample in dft.columns:
            group_name = self.tfa.get_group_of_a_sample(sample)
            group_palette[sample] = color_palette[group_name]

        
        # set style
        custom_params = {"axes.spines.right": False, "axes.spines.top": False}
        if theme is not None and theme != 'Auto':
            plt.style.use(theme) 
        else:               
            sns.set_theme(style="ticks", rc=custom_params)
            
        # set size
        plt.figure(figsize=(width, height))
        ax = sns.boxplot(data=dft, showfliers = show_fliers , palette=group_palette)
        # set x label
        ax.set_xticklabels(new_sample_name, rotation=90, horizontalalignment='right', fontsize=font_size)
        ax.set_xlabel('Sample', fontsize=font_size+2)
        ax.set_ylabel('Intensity', fontsize=font_size+2)
        ax.set_title(f'Intensity Boxplot of {table_name}', fontsize=font_size+2, fontweight='bold')
        # set legend for group, out of the box
        handles = [plt.Rectangle((0,0),1,1, color=color_palette[group], edgecolor='black') for group in unique_groups]
        ax.legend(handles, unique_groups, title='Group', title_fontsize=font_size, fontsize=font_size, loc='upper left', bbox_to_anchor=(1, 1))
        # set grid
        ax.grid(True, axis='y')
        # move the botton up
        plt.subplots_adjust(bottom=0.2)
        plt.tight_layout()
        plt.show()
        # plt.close()
        return ax
    
    def plot_corr_sns(self, df, table_name = 'Table', cluster = False, width=10, height=8, font_size = 10, 
                      show_all_labels = (False,False) , theme:str = None, rename_sample:bool = False):
        dft= df.copy()
        if rename_sample:
            dft, group_list = self.tfa.add_group_name_for_sample(dft)
        else:
            group_list = [self.tfa.get_group_of_a_sample(i) for i in dft.columns]
        

        color_list = self.assign_colors(group_list)
        corr = dft.corr()
        # mask = np.triu(np.ones_like(corr, dtype=bool))

        try:
            if theme is not None and theme != 'Auto':
                plt.style.use(theme)
            else:             
                sns.set_theme(style="ticks")
            sns_params = {"linewidths":.01, "cmap":'coolwarm', "cbar_kws":{ "shrink": 0.5},
                            'col_cluster':True if cluster else False,
                            'row_cluster':True if cluster else False,
                            "linecolor":(0/255, 0/255, 0/255, 0.01), "dendrogram_ratio":(.1, .2),"col_colors":color_list,
                            "figsize":(width, height), "xticklabels":True if show_all_labels[0] else "auto", 
                            "yticklabels":True if show_all_labels[1] else 'auto'}
            fig = sns.clustermap(corr, **sns_params)
            
            fig.ax_col_dendrogram.set_title(f'Correlation of {table_name}', fontsize=font_size+2, fontweight='bold')
            ax = fig.ax_heatmap 
            ax.set_xticklabels(ax.get_xticklabels(), fontsize=font_size, rotation=90)
            ax.set_yticklabels(ax.get_yticklabels(), fontsize=font_size, rotation=0)
        
            #set title
            plt.tight_layout()
            plt.show()
            # plt.close()
            return ax
        except Exception as e:
            plt.close('all')
            raise e
        
        
        
    def assign_colors(self, groups):
        colors = self.get_distinct_colors(len(set(groups)))
        result = []
        for group in groups:
            index = sorted(set(groups)).index(group)
            result.append(colors[index])
        return result
    
    def get_distinct_colors(self, n):  
        from distinctipy import distinctipy
        # rgb colour values (floats between 0 and 1)
        RED = (1, 0, 0)
        GREEN = (0, 1, 0)
        BLUE = (0, 0, 1)
        WHITE = (1, 1, 1)
        BLACK = (0, 0, 0)

        # generated colours will be as distinct as possible from these colours
        input_colors = [WHITE]
        colors = distinctipy.get_colors(n, exclude_colors= input_colors, pastel_factor=0.5)

        return colors