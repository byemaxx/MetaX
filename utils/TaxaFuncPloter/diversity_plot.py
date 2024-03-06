import pandas as pd
import skbio.diversity.alpha as alpha
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

from skbio.diversity import beta_diversity
from skbio.stats.ordination import pcoa

class DiversityPlot(object):
    def __init__(self, tfa):
        self.tfa = tfa
        self.ace_threshold = None
        # reset style
        plt.style.use('default')
        sns.set_theme()
        
    def ace_with_threshold(self, row):
        ace = alpha.ace(row, self.ace_threshold)
        return ace
    
    
    def plot_alpha_diversity(self, metric:str='shannon', sample_list:list=None, 
                             width:int = 10, height:int = 8,  font_size:int = 10,
                             plot_all_samples:bool = False, theme:str = None, sub_meta:str = 'None',
                             show_fliers = True
                             ):
        
        if sample_list is None:
            sample_list = self.tfa.sample_list
        
        if sub_meta != 'None' and sub_meta != self.tfa.meta_name:
            sub_group_list = []
            for i in sample_list:
                sub_group_list.append(self.tfa.get_group_of_a_sample(i, sub_meta))
        else:
            sub_group_list = None
            sub_meta = None
            
                  
        metric_dict = {
            'shannon': alpha.shannon,
            'simpson': alpha.simpson,
            'chao1': alpha.chao1,
            'observed_otus': alpha.observed_otus,
            'pielou_e': alpha.pielou_e,
            'fisher_alpha': alpha.fisher_alpha,
            'dominance': alpha.dominance,
            'menhinick': alpha.menhinick,
            'mcintosh_d': alpha.mcintosh_d,
            'mcintosh_e': alpha.mcintosh_e,
            'ace': self.ace_with_threshold,
            
        }
        if metric not in metric_dict:
            raise ValueError(f'Invalid metric: {metric}. Please choose from: {list(metric_dict.keys())}')
        
        try:
            df = self.tfa.taxa_df.copy()
            df = df[sample_list]
            
            if metric == 'ace':
                # log the df, if max value is mre than 10000, then log10
                if df.max().max() > 100000:
                    import numpy as np
                    print('log10 transform for ACE to speed up the calculation')
                    df = df.apply(lambda x: np.log10(x + 1))
                # covert to int
                df = df.astype(int)
                
                # get the threshold by 20% of the minimum value
                df2 = df[df > 0]
                threshold = int(df2.quantile(0.2).min())
                
                print(f'threshold: {threshold}')
                self.ace_threshold = threshold
            
            df_transposed = df.T
            group_diversity = {}
            # 遍历每个样本，计算其alpha多样性，并根据所属组别进行分类
            for sample_id, row in df_transposed.iterrows():
                if not plot_all_samples:
                    group = self.tfa.get_group_of_a_sample(sample_id)
                else:
                    group = sample_id

                sub_group = self.tfa.get_group_of_a_sample(sample_id, sub_meta) if sub_meta else 'All'

                if group:
                    if (group, sub_group) not in group_diversity:
                        group_diversity[(group, sub_group)] = []
                    
                    # only keep rows with non-zero values
                    row = row[row > 0]
                    diversity = metric_dict[metric](row)

                    group_diversity[(group, sub_group)].append(diversity)
            
            data = []
            for (group, sub_group), diversities in group_diversity.items():
                for diversity in diversities:
                    data.append({'Group': group, 'SubGroup': sub_group, 'Diversity': diversity})
            df = pd.DataFrame(data)

            if theme is not None and theme != 'Auto':
                plt.style.use(theme) 
            else:               
                sns.set_theme(style='whitegrid')

            # create a color palette
            group_num = len(df['SubGroup'].unique()) if sub_meta else len(df['Group'].unique())
            if group_num > 10:
                distinct_colors = self.get_distinct_colors(group_num)
                color_palette = dict(zip(df['SubGroup'].unique() if sub_meta else df['Group'].unique(), distinct_colors))
            else:
                color_palette = None

            plt.figure(figsize=(width, height))
            fig = sns.boxplot(x='Group', y='Diversity', data=df, hue='SubGroup' if sub_meta else 'Group', palette=color_palette,
                              showfliers=show_fliers)
            fig.set_xticklabels(fig.get_xticklabels(), rotation=90, fontsize=font_size)
            fig.set_yticklabels(fig.get_yticks(), fontsize=font_size)
            fig.set_xlabel('Group', fontsize=font_size)
            fig.set_ylabel(f'{metric} Index', fontsize=font_size)
            fig.set_title(f'Alpha Diversity ({metric})', fontsize=font_size+2, fontweight='bold')
            if sub_meta:
                plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0., fontsize=font_size+2, ncol= group_num//30 + 1)
                # add dashed line between groups
                for i, group in enumerate(df['Group'].unique()):
                    if i != 0:
                        fig.axvline(i - 0.5, linestyle='--', linewidth=1, color='grey', alpha=0.8)
                    

            plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
            plt.tight_layout()
            plt.show()
            return fig
        except Exception as e:
            plt.close('all')
            raise e


# metric = ['shannon', 'simpson',  'pielou_e', 'chao1', 'goods_coverage', 'observed_otus', 'fisher_alpha', 'dominance', 'doubles', 'menhinick', 'mcintosh_d', 'mcintosh_e']
# for i in metric:
#     try:
#         DiversityPlot(sw).plot_alpha_diversity(metric=i, sample_list=None, width=10, height=8,  font_size=10)
#     except:
#         print(f'{i} is not available')
# # DiversityPlot(sw).plot_alpha_diversity(metric= "mcintosh_d", sample_list=None, width=10, height=8,  font_size=10)


    def plot_beta_diversity(self, metric:str='braycurtis', sample_list:list=None, 
                             width:int = 10, height:int = 8,  font_size:int = 10, 
                             font_transparency:float = 0.8, show_label:bool = False,rename_sample:bool = False,
                              adjust_label:bool = False , theme:str = None, sub_meta:str = "None"):

        if sample_list is None:
            sample_list = self.tfa.sample_list
        
        if len(sample_list) < 2:
            raise ValueError(f'Invalid sample_list: {sample_list}. The length of sample_list must be greater than 1.')
        
        if sub_meta != 'None':
            style_list = []
            for i in sample_list:
                style_list.append(self.tfa.get_group_of_a_sample(i, sub_meta))
        else:
            style_list = None
         
        group_list_for_hue = [self.tfa.get_group_of_a_sample(sample_id) for sample_id in sample_list]

        # Determine if distinct colors are needed
        unique_groups = set(group_list_for_hue)
        if len(unique_groups) > 10:
            distinct_colors = self.get_distinct_colors(len(unique_groups))
            color_palette = dict(zip(unique_groups, distinct_colors))
        else:
            color_palette = None  # Let seaborn handle the color mapping

        try:
            df = self.tfa.taxa_df.copy()
            df = df[sample_list]
            df = df.T
            
            # bc_dm = beta_diversity("braycurtis", df, df.index)
            bc_dm = beta_diversity(metric, df, df.index)


            pcoa_res = pcoa(bc_dm)
            if theme is not None and theme != 'Auto':
                plt.style.use(theme) 
            else:               
                sns.set_theme(style='whitegrid')
                
            plt.figure(figsize=(width, height))
            dot_size = (width * height)
            fig = sns.scatterplot(x=pcoa_res.samples.PC1, y=pcoa_res.samples.PC2, s=dot_size, style=style_list,
                                  hue=group_list_for_hue, palette=color_palette, alpha=0.8, edgecolor='black', linewidth=0.5)
            if show_label:
                if rename_sample:
                    sample_list = [f'{sample_id} ({self.tfa.get_group_of_a_sample(sample_id)})' for sample_id in sample_list]
                texts = [fig.text(pcoa_res.samples.PC1[i], pcoa_res.samples.PC2[i], s=sample_list[i], size=font_size, 
                            color='black', alpha=font_transparency) for i in range(len(sample_list))]
                if adjust_label:
                    from adjustText import adjust_text
                    texts = adjust_text(texts, arrowprops=dict(arrowstyle='->', color='black'))
                
            fig.set_xlabel("PC1 (%.2f%%)" % (pcoa_res.proportion_explained[0] * 100), fontsize=font_size)
            fig.set_ylabel("PC2 (%.2f%%)" % (pcoa_res.proportion_explained[1] * 100), fontsize=font_size)
            # set title
            plt.title(f'PCoA plot of {metric} distance (Total explained variation: {pcoa_res.proportion_explained[0] * 100 + pcoa_res.proportion_explained[1] * 100:.2f}%)', fontsize=font_size+2, fontweight='bold')
            plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.,
                       fontsize=font_size +2 , ncol= len(unique_groups)//30 + 1)
            plt.tight_layout()
            plt.show()
            
            return fig
        except Exception as e:
            plt.close('all')
            raise e

                        
                        
    def get_distinct_colors(self, n):  
        from distinctipy import distinctipy
        # rgb colour values (floats between 0 and 1)
        RED = (1, 0, 0)
        GREEN = (0, 1, 0)
        BLUE = (0, 0, 1)
        WHITE = (1, 1, 1)
        BLACK = (0, 0, 0)

        # generated colours will be as distinct as possible from these colours
        input_colors = [ WHITE]
        colors = distinctipy.get_colors(n, exclude_colors= input_colors, pastel_factor=0.5)

        return colors