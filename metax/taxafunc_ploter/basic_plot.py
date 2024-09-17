import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from adjustText import adjust_text

from .get_distinct_colors import GetDistinctColors

class BasicPlot:
    def __init__(self, tfobj,
                 linkage_method:str = 'average', distance_metric:str = 'correlation',
                 x_labels_rotation:int = 90, y_labels_rotation:int = 0):
        self.tfa =  tfobj
        self.get_distinct_colors = GetDistinctColors().get_distinct_colors
        self.assign_colors = GetDistinctColors().assign_colors
        # for heatmap
        self.linkage_method = linkage_method
        self.distance_metric = distance_metric
        self.x_labels_rotation = x_labels_rotation
        self.y_labels_rotation = y_labels_rotation

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
    def plot_pca_sns(self, df, title_name = 'Table', show_label = True,
                     width=10, height=8, font_size = 10, rename_sample:bool = False,
                     font_transparency = 0.6, adjust_label:bool = False, theme:str|None = None,
                     sub_meta:str = 'None', legend_col_num: int | None = None, dot_size: float|None = None):
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
            dot_size = (width * height)*font_size/10 if dot_size is None else dot_size
            # sns.set_theme(style="ticks", rc={"axes.spines.right": False, "axes.spines.top": False})
            fig = sns.scatterplot(x=components[:, 0], y=components[:, 1], palette=color_palette, style=style_list,
                                hue=group_list, s = dot_size,
                                alpha=0.9, edgecolor='black', linewidth=0.5)


            fig.set_title(f'PCA of {str(title_name)} (total variance explained: {total_var:.2f}%)',
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

            if show_label:
                new_sample_name = new_sample_name if rename_sample else sample_list
                texts = [fig.text(components[i, 0], components[i, 1], s=new_sample_name[i], size=font_size,
                            color='black', alpha=font_transparency) for i in range(len(new_sample_name))]
                if adjust_label:
                    texts = adjust_text(
                        texts,
                        avoid_self = False,
                        force_text =( 0.1, 0.3),
                        arrowprops=dict(
                            arrowstyle="-", color="black", alpha=font_transparency
                        ),
                    )

            plt.tight_layout()
            plt.show()

            return fig
        except Exception as e:
            plt.close('all')
            raise e


    def plot_box_sns(self, df, title_name = 'Table', show_fliers = False, width=10, height=8,
                     font_size = 10, theme:str|None = None, rename_sample:bool = False,
                     plot_samples:bool = False, legend_col_num: int | None = None, sub_meta:str|None = 'None'):
        
        def create_df(self, df, sub_meta:str|None = 'None', plot_samples:bool = False):
            df = df.copy()
            # replace 0 with nan due to optimization of boxplot
            df = df.replace(0, np.nan)
            
            sample_list = df.columns
            
            group_list = [self.tfa.get_group_of_a_sample(sample) for sample in sample_list]
            # get unique groups, and keep the order
            group_order = [x for i, x in enumerate(group_list) if i == group_list.index(x)]
            
            group_map = {sample: self.tfa.get_group_of_a_sample(sample) for sample in sample_list}
            
            df = df.melt(var_name='Sample', value_name='Intensity')
            df['Group'] = df['Sample'].map(group_map)
            
            if plot_samples:
                # resort the by sample_list
                df = df.sort_values(by='Sample', key=lambda x: x.map({v: i for i, v in enumerate(sample_list)}))
            else:
                if sub_meta not in ['None', None]:
                    sub_group_map = {sample: self.tfa.get_group_of_a_sample(sample, sub_meta) for sample in sample_list}
                    df['SubGroup'] = df['Sample'].map(sub_group_map)
                else:
                    df['SubGroup'] = df['Group'] # copy the group to sub group, avoid error
                # resort the by group
                df = df.sort_values(by='Group', key=lambda x: x.map({v: i for i, v in enumerate(group_order)}))
            
            return df
        
        
        df = create_df(self, df, sub_meta, plot_samples)
        unique_groups = df['Group'].unique() if plot_samples else df['SubGroup'].unique()

        # Determine if distinct colors are needed
        if len(unique_groups) > 10:
            distinct_colors = self.get_distinct_colors(len(unique_groups))
            color_palette = dict(zip(unique_groups, distinct_colors))
        else:
            # color_palette = dict(zip(unique_groups, sns.color_palette("deep", len(unique_groups))))
            color_palette = None

        # set style
        if theme is not None and theme != 'Auto':
            plt.style.use(theme)
        else:
            custom_params = {"axes.spines.right": False, "axes.spines.top": False}
            sns.set_theme(style="ticks", rc=custom_params)

        # set size
        plt.figure(figsize=(width, height))
        ax = sns.boxplot(
            data=df,
            x="Sample" if plot_samples else "Group",
            y="Intensity",
            hue="Group" if sub_meta in ["None", None] or plot_samples else "SubGroup",
            palette=color_palette,
            showfliers=show_fliers,
            legend=True,
        )
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
        ax.set_title(f'Boxplot of Intensity of {title_name}',
                     fontsize=font_size+2, fontweight='bold')
        
        if legend_col_num != 0:
            # set legend for group, out of the box
            plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0., 
                               fontsize=font_size+2, ncol= (len(unique_groups)//30 + 1 ) if legend_col_num is None else legend_col_num)
            
        else:
            #hide the legend
            ax.legend([],[], frameon=False)
        
        # set line if sub_meta is not None
        if sub_meta not in ['None', None] and not plot_samples:
            for i, group in enumerate(df['Group'].unique()):
                if i != 0:
                    ax.axvline(i - 0.5, linestyle='--', linewidth=1, color='grey', alpha=0.8)
        
        # set grid line for y axis is visible
        ax.grid(True, axis='y')
        # move the botton up
        plt.subplots_adjust(bottom=0.2)
        plt.tight_layout()
        plt.show()
        # plt.close()
        return ax

    def plot_corr_sns(
        self,
        df,
        title_name="Table",
        cluster=False,
        width=10,
        height=8,
        font_size=10,
        show_all_labels=(False, False),
        theme: str = None,
        cmap: str = "Auto",
        rename_sample: bool = False,
    ):
        dft= df.copy()
        if rename_sample:
            dft, group_list = self.tfa.add_group_name_for_sample(dft)
        else:
            group_list = [self.tfa.get_group_of_a_sample(i) for i in dft.columns]

        if cmap == 'Auto':
            cmap = 'RdYlBu_r'
        else:
            cmap = cmap

        color_list = self.assign_colors(group_list)
        corr = dft.corr()
        # mask = np.triu(np.ones_like(corr, dtype=bool))

        try:
            if theme is not None and theme != 'Auto':
                plt.style.use(theme)
            else:
                sns.set_theme(style="ticks")
            sns_params = {"linewidths":.01, "cmap":cmap, "cbar_kws":{ "shrink": 0.5},
                            'col_cluster':True if cluster else False,
                            'row_cluster':True if cluster else False,
                            'method':self.linkage_method,
                            'metric':self.distance_metric,
                            "linecolor":(0/255, 0/255, 0/255, 0.01), "dendrogram_ratio":(.1, .2),"col_colors":color_list,
                            "figsize":(width, height), "xticklabels":True if show_all_labels[0] else "auto",
                            "yticklabels":True if show_all_labels[1] else 'auto'}
            fig = sns.clustermap(corr, **sns_params)
            ax = fig.ax_heatmap
            
            fig.ax_heatmap.set_xticklabels(
                fig.ax_heatmap.get_xmajorticklabels(),
                fontsize=font_size,
                rotation=self.x_labels_rotation,
                ha = self.get_x_labels_ha()
            )
            fig.ax_heatmap.set_yticklabels(
                fig.ax_heatmap.get_ymajorticklabels(),
                fontsize=font_size,
                rotation=self.y_labels_rotation,
                ha = 'left',
                va = self.get_y_labels_va()
            )
            
            fig.ax_col_dendrogram.set_title(f'Correlation of {title_name}', fontsize=font_size+2, fontweight='bold')

            cbar = fig.ax_heatmap.collections[0].colorbar
            cbar.set_label('Intensity', rotation=90, labelpad=1)
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


    def plot_number_bar(self, df, title_name = 'Table', width=10, height=8, font_size = 10,
                        theme:str = 'Auto', plot_sample = False, show_label = True,
                        rename_sample:bool = False, legend_col_num: int | None = None,
                        sub_meta:str|None = 'None'):

        def create_df_plot_samples(df):
            '''
            Create a long format table for samples, group, sub_group and number
            '''
            res_dict = {}
            sample_list = df.columns.tolist()
            for sample in sample_list:
                group = self.tfa.get_group_of_a_sample(sample)
                # num = the row num df[sample] > 0
                num = df[sample].astype(bool).sum(axis=0)
                res_dict[sample] = [group, num]
                # create a long format table, sample as index, group and number as columns
            df = pd.DataFrame(res_dict).T.reset_index()
            df.rename(columns={'index': 'Sample', 0: 'Group', 1: 'Number'}, inplace=True)

            return df

        def create_df_plot_group(df, sub_meta):
            sample_list = df.columns.tolist()
            group_dict = {}
            
            for sample in sample_list:
                group = self.tfa.get_group_of_a_sample(sample)            
                if group not in group_dict:
                    group_dict[group] = []
                group_dict[group].append(sample)
            
            if sub_meta not in ['None', None]:
                res_dict = {}
                for group in group_dict: # main group
                    sub_dict = {} # a dict to store sub group and its samples
                    for sample in group_dict[group]:
                        sub_group = self.tfa.get_group_of_a_sample(sample, sub_meta)
                        if sub_group not in sub_dict:
                            sub_dict[sub_group] = []
                        sub_dict[sub_group].append(sample)
                    
                    for sub_group in sub_dict:
                        sub_df = df[sub_dict[sub_group]]
                        sub_df = sub_df[sub_df.sum(axis=1) > 0]
                        res_dict[(group, sub_group)] = sub_df.shape[0]
                # create a long format table
                df = pd.DataFrame(res_dict, index=['Number']).T.reset_index()
                df.rename(columns={'level_0': 'Group', 'level_1': 'SubGroup'}, inplace=True)
                    
            else:
                res_dict = {}
                # get subtable for each group
                for group, samples in group_dict.items():
                    sub_df = df[samples]
                    sub_df = sub_df[sub_df.sum(axis=1) > 0]
                    res_dict[group] = sub_df.shape[0]
                # create a long format table
                df = pd.DataFrame(res_dict, index=['Number']).T.reset_index()
                df.rename(columns={'index': 'Group'}, inplace=True)
            
            return df

        df = df.copy()


        #stats number of taxa for each group
        if not plot_sample:
            df = create_df_plot_group(df, sub_meta)

        else: # plot all samples
            df = create_df_plot_samples(df)

        # print the min and max value and its row to string
        min_df = df[df["Number"] == df["Number"].min()].to_string(index=False)
        max_df = df[df["Number"] == df["Number"].max()].to_string(index=False)
        print(f'The min number of {title_name}:\n{min_df}')
        print(f'The max number of {title_name}:\n{max_df}')

        unique_groups = (
            df["Group"].unique()
            if sub_meta in ["None", None] or plot_sample
            else df["SubGroup"].unique()
        )

        # Determine if distinct colors are needed
        if len(unique_groups) > 10:
            distinct_colors = self.get_distinct_colors(len(unique_groups))
            color_palette = dict(zip(unique_groups, distinct_colors))
        else:
            # color_palette = dict(zip(unique_groups, sns.color_palette("deep", len(unique_groups))))
            color_palette = None


        # set style
        custom_params = {"axes.spines.right": False, "axes.spines.top": False}
        if theme is not None and theme != 'Auto':
            plt.style.use(theme)
        else:
            sns.set_theme(style="ticks", rc=custom_params)

        # set size
        plt.figure(figsize=(width, height))
        bar_params = {
            "data": df,
            "x": "Sample" if plot_sample else "Group",
            "y": "Number",
            "hue": "Group" if sub_meta in ['None', None] or plot_sample else "SubGroup",
            "palette": color_palette,
            "err_kws": {"alpha": 0.5},
            "legend": True,
        }

        ax = sns.barplot(**bar_params)


        # set x label
        x_labels = ax.get_xticklabels()
        if rename_sample and plot_sample:
            for label in x_labels:
                text = label.get_text()
                group = self.tfa.get_group_of_a_sample(text)
                label.set_text(f'{text} ({group})')

        ax.set_xticklabels( x_labels, rotation=90, horizontalalignment='right', fontsize=font_size)
        ax.set_xlabel("Sample" if plot_sample else "Group",
                      fontsize=font_size+2)
        ax.set_ylabel('Number', fontsize=font_size+2)
        # set y limit as 0.9 * min to 1.1 * max
        ax.set_ylim(df['Number'].min() * 0.9 , df['Number'].max() * 1.1)

        title = f'The number of {title_name} for each sample' if plot_sample else f'The number of {title_name} for each group'
        ax.set_title(title, fontsize=font_size+2, fontweight='bold')

        # set legend
        if legend_col_num != 0:
            # set legend for group, out of the box
            plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0., fontsize=font_size+2,
                        ncol= (len(unique_groups)//30 + 1) if legend_col_num is None else legend_col_num)
        else:
            #hide the legend
            ax.legend([],[], frameon=False)


        if sub_meta not in ['None', None] and not plot_sample:
            # add a line to separate the groups
            for i, group in enumerate(df['Group'].unique()):
                if i != 0:
                    ax.axvline(i - 0.5, linestyle='--', linewidth=1, color='grey', alpha=0.8)

        if show_label:
            for i in ax.containers:
                ax.bar_label(
                    i,
                    fontsize=font_size,
                    rotation=90 if plot_sample or (sub_meta not in ["None", None] and not plot_sample) else 0,
                    padding=3,
                )

        # set grid
        ax.grid(True, axis='y')
        # move the botton up
        plt.subplots_adjust(bottom=0.2)
        plt.tight_layout()
        plt.show()
        # plt.close()
        return ax

    def plot_distribution_sns(self, df, title_name = 'Table', width=10, height=8, font_size = 10,
                                theme:str = 'Auto', plot_sample = False, show_label = True,
                                rename_sample:bool = False, legend_col_num: int | None = None,
                                sub_meta:str|None = 'None', bins:int = 10):
        pass

    def plot_items_corr_heatmap(
        self,
        df,
        title_name="Table",
        cluster=False,
        cmap = 'RdYlBu_r',
        width=10,
        height=8,
        font_size=10,
        show_all_labels=(False, False),
    ):
        corr = df.copy()
        # mask = np.triu(np.ones_like(corr, dtype=bool))

        try:
            if cmap == 'Auto':
                cmap = 'RdYlBu_r'
            else:
                cmap = cmap
                
            sns_params = {"linewidths":.01, "cmap":cmap, "cbar_kws":{ "shrink": 0.5},
                            'col_cluster':True if cluster else False,
                            'row_cluster':True if cluster else False,
                            'method':self.linkage_method,
                            'metric':self.distance_metric,
                            "linecolor":(0/255, 0/255, 0/255, 0.01), "dendrogram_ratio":(.1, .2),
                            "figsize":(width, height), "xticklabels":True if show_all_labels[0] else "auto",
                            "yticklabels":True if show_all_labels[1] else 'auto'}
            fig = sns.clustermap(corr, **sns_params)
            ax = fig.ax_heatmap
            
            
            fig.ax_col_dendrogram.set_title(f'Correlation of {title_name}', fontsize=font_size+2, fontweight='bold')
            fig.ax_heatmap.set_xticklabels(
                fig.ax_heatmap.get_xmajorticklabels(),
                fontsize=font_size,
                rotation=self.x_labels_rotation,
                ha = self.get_x_labels_ha()
            )
            fig.ax_heatmap.set_yticklabels(
                fig.ax_heatmap.get_ymajorticklabels(),
                fontsize=font_size,
                rotation=self.y_labels_rotation,
                ha = 'left',
                va = self.get_y_labels_va()
            )

            # hiend the x and y labels
            fig.ax_heatmap.set_xlabel('')
            fig.ax_heatmap.set_ylabel('')

            cbar = fig.ax_heatmap.collections[0].colorbar
            cbar.set_label("Correlation", rotation=90, labelpad=1)
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


    def get_x_labels_ha(self):
        x_rotation = self.x_labels_rotation
        if x_rotation > 0:
            return 'right'
        elif x_rotation < 0:
            return 'left'
        else:
            return 'center'
    def get_y_labels_va(self):
        y_rotation = self.y_labels_rotation
        if y_rotation >= 0:
            return 'baseline'
        else:
            return 'top'
