import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .get_distinct_colors import GetDistinctColors

class BasicPlot:
    def __init__(self, tfobj):
        self.tfa =  tfobj
        self.get_distinct_colors = GetDistinctColors().get_distinct_colors
        self.assign_colors = GetDistinctColors().assign_colors
        # reset the style
        plt.style.use('default')
        sns.set_theme()
        
        

    def plot_taxa_stats_pie(self, theme:str = 'Auto', res_type = 'pic', font_size = 12):
        df = self.tfa.BasicStats.get_stats_peptide_num_in_taxa()

        # if 'not_found' is 0, then remove it
        if df[df['LCA_level'] == 'notFound']['count'].values[0] == 0:
            df = df[df['LCA_level'] != 'notFound']
            
        # if 'life' is 0, then remove it
        if df[df['LCA_level'] == 'life']['count'].values[0] == 0:
            df = df[df['LCA_level'] != 'life']
            
        if 'genome' in df['LCA_level'].values and df[df['LCA_level'] == 'species']['count'].values[0] == 0:
            # rename genome to species(Genome)
            df.loc[df['LCA_level'] == 'genome', 'LCA_level'] = 'species (genome)'
            # remove species
            df = df[df['LCA_level'] != 'species']
            
        if theme is not None and theme != 'Auto':
            plt.style.use(theme)
        else:
            plt.style.use('default')
            # set color palette
            colors = sns.color_palette("deep")
            
        # set figure size base on font size
        if font_size <= 10:
            fig_size = (8, 6)
        elif font_size <= 12:
            fig_size = (10, 8)
        elif font_size <= 14:
            fig_size = (12, 10)
        elif font_size <= 16:
            fig_size = (14, 12)
        else:
            fig_size = (16, 14)
            
        
        fig = plt.figure(figsize=fig_size) if res_type == 'show' else plt.figure()
        
        wedges, texts, autotexts = plt.pie(df['count'], labels=df['LCA_level'], 
                                           autopct='%1.2f%%', startangle=40,
                                           colors=colors if theme == 'Auto' else None)
        
        for i, t in enumerate(texts):
            t.set_text(f'{t.get_text()} ({autotexts[i].get_text()})')
    
        count = df['count'].values
        for i, a in enumerate(autotexts):
            a.set_text(f'{count[i]}')

        
        plt.title('Number of identified peptides in different taxa level', fontsize=font_size+2, loc='center', fontweight='bold')
        plt.setp(autotexts, size=font_size,  color="white")
        plt.setp(texts, size=font_size)

        if res_type == 'show':
            plt.tight_layout()
            plt.show()
        else:
            plt.close()
        
        return fig

    # input: self.get_stats_taxa_level()
    def plot_taxa_number(self, peptide_num = 1, theme:str = 'Auto', res_type = 'pic', font_size = 10):
        df = self.tfa.BasicStats.get_stats_taxa_level(peptide_num)
        
        # if genome in taxa_level and count of species == count of genome, then remove genome, and rename species to species (genome)
        # if 'genome' in df['taxa_level'].values and df[df['taxa_level'] == 'species']['count'].values[0] == df[df['taxa_level'] == 'genome']['count'].values[0]:
        #     # rename species to species(Genome)
        #     # df.loc[df['taxa_level'] == 'species', 'taxa_level'] = 'species (gen)'
        #     # remove genome
        #     df = df[df['taxa_level'] != 'genome']

        if theme is not None and theme != 'Auto':
            plt.style.use(theme)
        else:
            custom_params = {"axes.spines.right": False, "axes.spines.top": False}
            sns.set_theme(style="ticks", rc=custom_params)
        plt.figure(figsize=(10, 8)) if res_type == 'show' else plt.figure()
        ax = sns.barplot(data=df, x='taxa_level', y='count',dodge=False, hue='taxa_level')
        for i in ax.containers:
            # set the label of the bar, and fontsize
            ax.bar_label(i, fontsize=font_size)
            
        ax.set_title(f'Number of taxa in different taxa level (Peptide number >= {peptide_num})', fontsize=font_size+2, fontweight='bold')
        ax.set_xlabel('Taxa level', fontsize=font_size+2)
        ax.set_ylabel('Number of taxa', fontsize=font_size+2)
        # set font size of xtikcs and yticks
        ax.set_xticklabels(ax.get_xticklabels(), fontsize=font_size)
        ax.set_yticklabels(ax.get_yticklabels(), fontsize=font_size)
        
        
        if res_type == 'show':
            plt.tight_layout()
            plt.show()
        else:
            plt.close()
            
        return ax

    # input: self.get_stats_func_prop()
    def plot_prop_stats(self, func_name = 'eggNOG_OGs', theme:str = 'Auto', res_type = 'pic', font_size = 10):
        df = self.tfa.BasicStats.get_stats_func_prop(func_name)
        # #dodge=False to make the bar wider
        # plt.figure(figsize=(8, 6))
        if theme is not None and theme != 'Auto':
            plt.style.use(theme)
        else:
            custom_params = {"axes.spines.right": False, "axes.spines.top": False} 
            sns.set_theme(style="ticks", rc=custom_params)
            
        plt.figure(figsize=(8, 6)) if res_type == 'show' else plt.figure()
        
        ax = sns.barplot(data=df, x='prop', y='n', hue='label', dodge=False, palette='tab10_r')
        for i in ax.containers:
            ax.bar_label(i, fontsize=font_size)
        ax.set_title(f'Number of different proportions of peptides in {func_name}', fontsize=font_size+2, fontweight='bold')
        ax.set_xlabel('Proportion of function', fontsize=font_size+2)
        ax.set_ylabel('Number of peptides', fontsize=font_size+2)
        ax.set_xticklabels(ax.get_xticklabels(), fontsize=font_size)
        ax.set_yticklabels(ax.get_yticklabels(), fontsize=font_size)
        
        ax.legend(title='Proportion of function (frequency)',  ncol=2, loc = 'upper left', fontsize=font_size)
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
                     font_transparency = 0.6, adjust_label:bool = False, theme:str|None = None, sub_meta:str = 'None', legend_col_num: int | None = None):
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
            # use enumerate to keep the order of the group
            unique_groups = [x for i, x in enumerate(group_list) if i == group_list.index(x)]
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
                sns.set_theme(style='whitegrid')
                
            plt.figure(figsize=(width, height))
            pca = PCA(n_components=2)
            components = pca.fit_transform(mat)
            total_var = pca.explained_variance_ratio_.sum() * 100
            # set dot size based on the width and height, and font size
            dot_size = (width * height)*font_size/10
            # sns.set_theme(style="ticks", rc={"axes.spines.right": False, "axes.spines.top": False})
            fig = sns.scatterplot(x=components[:, 0], y=components[:, 1], palette=color_palette, style=style_list,
                                hue=group_list, s = dot_size, 
                                alpha=0.9, edgecolor='black', linewidth=0.5)
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
            
            # set legend outside the plot, set size as 100
            if legend_col_num != 0:
                num_legend = len(unique_groups) if sub_meta == 'None' else len(set(style_list)) + len(unique_groups)
                plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=font_size +2, borderaxespad=0.,
                        ncol= num_legend//30 + 1 if legend_col_num is None else legend_col_num)
            else:
                #hide the legend
                plt.legend([],[], frameon=False)
                
            plt.tight_layout()
            plt.show()

            return fig
        except Exception as e:
            plt.close('all')
            raise e
        
        
    def plot_box_sns(self, df, table_name = 'Table', show_fliers = False, width=10, height=8, 
                     font_size = 10, theme:str|None = None, rename_sample:bool = False, plot_samples:bool = False, legend_col_num: int | None = None):
        # replace 0 with nan due to optimization of boxplot
        dft = df.replace(0, np.nan)
        if not plot_samples:
            # create a new dataframe with all samples in the same group
            sample_list = dft.columns
            temp_dict = {}
            for col in sample_list:
                group = self.tfa.get_group_of_a_sample(col)
                if group not in temp_dict:
                    temp_dict[group] = []
                # combine all samples in the same group
                temp_dict[group].extend(dft[col].tolist())
            
            # fill nan to the same length
            max_length = max(len(lst) for lst in temp_dict.values())
            for group in temp_dict:
                temp_dict[group].extend([np.nan] * (max_length - len(temp_dict[group])))

            dft = pd.DataFrame(temp_dict)
            unique_groups = dft.columns
        
        else: # plot_samples is True
            # create a new dataframe with new sample names and sorted by group
            sample_list = dft.columns
            group_list = []
            for i in sample_list:
                group = self.tfa.get_group_of_a_sample(i)
                group_list.append(group)
            
            # remove duplicate groups, and keep the order
            unique_groups = [x for i, x in enumerate(group_list) if i == group_list.index(x)]
            ordered_sample_list = []
            for group in unique_groups:
                samples_in_group = [sample for sample, group_sample in zip(sample_list, group_list) if group_sample == group]
                ordered_sample_list.extend(samples_in_group)

            # reorder the columns
            dft = dft[ordered_sample_list]


        # Determine if distinct colors are needed
        if len(unique_groups) > 10:
            distinct_colors = self.get_distinct_colors(len(unique_groups))
            color_palette = dict(zip(unique_groups, distinct_colors))
        else:
            color_palette = dict(zip(unique_groups, sns.color_palette("tab10", len(unique_groups))))
        
        if plot_samples:
            group_palette = {}
            for sample in dft.columns:
                group_name = self.tfa.get_group_of_a_sample(sample)
                group_palette[sample] = color_palette[group_name]
        else:
            group_palette = color_palette
        
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
        x_labels = ax.get_xticklabels()
        if rename_sample and plot_samples:
            for label in x_labels:
                text = label.get_text()
                group = self.tfa.get_group_of_a_sample(text)
                label.set_text(f'{text} ({group})')
                
        ax.set_xticklabels(x_labels, rotation=90, horizontalalignment='right', fontsize=font_size)
        ax.set_xlabel('Sample' if plot_samples else 'Group',
                      fontsize=font_size+2)
        
        ax.set_ylabel('Intensity', fontsize=font_size+2)
        ax.set_title(f'Boxplot of Intensity of {table_name}',
                     fontsize=font_size+2, fontweight='bold')
        if plot_samples:
            if legend_col_num != 0:
                # set legend for group, out of the box
                handles = [plt.Rectangle((0,0),1,1, color=color_palette[group], edgecolor='black') for group in unique_groups]
                ax.legend(handles, unique_groups, title='Group', title_fontsize=font_size, fontsize=font_size +2,borderaxespad=0.,
                        loc='upper left', bbox_to_anchor=(1.02, 1), ncol= len(unique_groups)//30 + 1 if legend_col_num is None else legend_col_num)
            else:
                #hide the legend
                ax.legend([],[], frameon=False)
        # set grid line for y axis is visible
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
            
            cbar = fig.ax_heatmap.collections[0].colorbar
            cbar.set_label('Intensity', rotation=90, labelpad=1, fontsize=font_size)
            cbar.ax.yaxis.set_ticks_position('left')
            cbar.ax.yaxis.set_label_position('left')
            plt.subplots_adjust(left=0.03, bottom=0.095, right=0.5, top=0.96, wspace=0.01, hspace=0.01)

            plt.tight_layout()
            plt.show()
            # plt.close()
            return ax
        except Exception as e:
            plt.close('all')
            raise e
        
        
    def plot_number_bar(self, df, table_name = 'Table', width=10, height=8, font_size = 10,  
                        theme:str = 'Auto', plot_sample = False, show_label = True, 
                        rename_sample:bool = False, legend_col_num: int | None = None):
        df = df.copy()
        
        #stats number of taxa for each group
        # get subtable for each group
        samlpe_list = df.columns.tolist()
        res_dict = {}

        group_dict = {}
        for sample in samlpe_list:
            group = self.tfa.get_group_of_a_sample(sample)
            if group not in group_dict:
                group_dict[group] = []
            group_dict[group].append(sample)
            
        if not plot_sample:
            # get subtable for each group    
            for group, samples in group_dict.items():
                sub_df = df[samples]
                sub_df = sub_df[sub_df.sum(axis=1) > 0]
                res_dict[group] = sub_df.shape[0]
            # create a long format table
            df = pd.DataFrame(res_dict, index=['Number']).T.reset_index()
            df.rename(columns={'index': 'Group'}, inplace=True)
        else:
            for sample in samlpe_list:
                group = self.tfa.get_group_of_a_sample(sample)
                # num = the row num df[sample] > 0
                num = df[sample].astype(bool).sum(axis=0)
                res_dict[sample] = [group, num]
                # create a long format table, sample as index, group and number as columns
            df = pd.DataFrame(res_dict).T.reset_index()
            df.rename(columns={'index': 'Sample', 0: 'Group', 1: 'Number'}, inplace=True)

            
        # print the min and max value and its row to string
        min_df = df[df["Number"] == df["Number"].min()].to_string(index=False)
        max_df = df[df["Number"] == df["Number"].max()].to_string(index=False)
        print(f'The min number of {table_name}:\n{min_df}')
        print(f'The max number of {table_name}:\n{max_df}')
        
        unique_groups = df['Group'].unique()
        # Determine if distinct colors are needed
        if len(unique_groups) > 10:
            distinct_colors = self.get_distinct_colors(len(unique_groups))
            color_palette = dict(zip(unique_groups, distinct_colors))
        else:
            color_palette = dict(zip(unique_groups, sns.color_palette("tab10", len(unique_groups))))
            

        
        # set style
        custom_params = {"axes.spines.right": False, "axes.spines.top": False}
        if theme is not None and theme != 'Auto':
            plt.style.use(theme) 
        else:               
            sns.set_theme(style="ticks", rc=custom_params)
            
        # set size
        plt.figure(figsize=(width, height))
        bar_params = {'data': df, 'x': 'Sample' if plot_sample else 'Group', 'y': 'Number', 'hue': 'Group', 'palette': color_palette}
        
        ax = sns.barplot(**bar_params)
        if show_label:
            for i in ax.containers:
                ax.bar_label(i, fontsize=font_size, rotation=90 if plot_sample else 0, padding=3)
                
        # set x label
        x_labels = ax.get_xticklabels()
        if rename_sample and plot_sample:
            for label in x_labels:
                text = label.get_text()
                group = self.tfa.get_group_of_a_sample(text)
                label.set_text(f'{text} ({group})')
        
        ax.set_xticklabels( x_labels, rotation=90, horizontalalignment='right', fontsize=font_size)
        ax.set_xlabel('Group', fontsize=font_size+2)
        ax.set_ylabel('Number', fontsize=font_size+2)
        # set y limit as 0.9 * min to 1.1 * max
        ax.set_ylim(df['Number'].min() * 0.9 , df['Number'].max() * 1.1)
        
        title = f'The number of {table_name} for each sample' if plot_sample else f'The number of {table_name} for each group'
        ax.set_title(title, fontsize=font_size+2, fontweight='bold')
        
        if plot_sample:
            if legend_col_num != 0:
                # set legend for group, out of the box
                handles, labels = ax.get_legend_handles_labels()
                ax.legend(handles, unique_groups, fontsize=font_size + 2, ncol= (len(unique_groups)//30 + 1) if legend_col_num is None else legend_col_num,
                            loc='upper left',borderaxespad=0., bbox_to_anchor=(1.02, 1))
            else:
                #hide the legend
                ax.legend([],[], frameon=False)
        # set grid
        ax.grid(True, axis='y')
        # move the botton up
        plt.subplots_adjust(bottom=0.2)
        plt.tight_layout()
        plt.show()
        # plt.close()
        return ax


    
    
    #! Deprecated function, use plot_taxa_stats_pie chart instead
    # def plot_taxa_stats_bar(self, theme:str = 'Auto', res_type = 'pic', font_size = 12):
    #     df = self.tfa.BasicStats.get_stats_peptide_num_in_taxa()
    #     # if 'not_found' is 0, then remove it
    #     if df[df['LCA_level'] == 'notFound']['count'].values[0] == 0:
    #         df = df[df['LCA_level'] != 'notFound']
            
    #     if theme is not None and theme != 'Auto':
    #         plt.style.use(theme)
    #     else:
    #         custom_params = {"axes.spines.right": False, "axes.spines.top": False}

    #         # plt.figure(figsize=(8, 6))
    #         sns.set_theme(style="ticks", rc=custom_params)
            
    #     plt.figure(figsize=(8, 6)) if res_type == 'show' else plt.figure()
        
    #     ax = sns.barplot(data=df, x='LCA_level', y='count', hue='label',dodge=False)
    #     for i in ax.containers:
    #         ax.bar_label(i, fontsize=font_size)
    #     ax.set_title('Number of identified peptides in different taxa level', fontsize=font_size+2, fontweight='bold')
    #     ax.set_xlabel('Taxa level')
    #     ax.set_ylabel('Number of peptides')
    #     ax.set_xticklabels(ax.get_xticklabels(), fontsize=font_size)
    #     ax.set_yticklabels(ax.get_yticklabels(), fontsize=font_size)
    #     ax.legend(title='Taxa level (frequency)',  ncol=2)
    #     if res_type == 'show':
    #         plt.tight_layout()
    #         plt.show()
    #     else:
    #         plt.close()
    #     return ax # use "pic = BasicPlot(self.tfa).plot_taxa_stats().get_figure()" to get the figure object in GUI script

