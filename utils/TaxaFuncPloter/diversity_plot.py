import pandas as pd
import skbio.diversity.alpha as alpha
import matplotlib.pyplot as plt
import seaborn as sns

from skbio.diversity import beta_diversity
from skbio.stats.ordination import pcoa

class DiversityPlot(object):
    def __init__(self, tfa):
        self.tfa = tfa
        # reset style
        sns.set()
        sns.set(style='whitegrid')
        

    def plot_alpha_diversity(self, metric:str='shannon', sample_list:list=None, 
                             width:int = 10, height:int = 8,  font_size:int = 10,
                             plot_all_samples:bool = False
                             ):
        
        if sample_list is None:
            sample_list = self.tfa.sample_list
        
        
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
            
        }
        if metric not in metric_dict:
            raise ValueError(f'Invalid metric: {metric}. Please choose from: {list(metric_dict.keys())}')
        
        try:
            df = self.tfa.taxa_df.copy()
            df = df[sample_list]
            df_transposed = df.T                
            group_diversity = {}
            # 遍历每个样本，计算其alpha多样性，并根据所属组别进行分类
            for sample_id, row in df_transposed.iterrows():
                if not plot_all_samples:
                    group = self.tfa.get_group_of_a_sample(sample_id)
                else:
                    group = sample_id
                    
                if group:
                    if group not in group_diversity:
                        group_diversity[group] = []
                    diversity = metric_dict[metric](row)

                    group_diversity[group].append(diversity)

            data = []
            for group, diversities in group_diversity.items():
                for diversity in diversities:
                    data.append({'Group': group, 'Diversity': diversity})
            df = pd.DataFrame(data)
            # plot boxplot
            plt.figure(figsize=(width, height))
            fig = sns.boxplot(x='Group', y='Diversity', data=df, hue='Group')
            fig.set_xticklabels(fig.get_xticklabels(), rotation=90)
            fig.set_xlabel('Group', fontsize=font_size)
            fig.set_ylabel(f'{metric} Diversity')
            fig.set_title(f'Alpha Diversity ({metric}) of Each Group')
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
                             font_transparency:float = 0.8, show_label:bool = False,
                              adjust_label:bool = False ):

        if sample_list is None:
            sample_list = self.tfa.sample_list
        
        if len(sample_list) < 2:
            raise ValueError(f'Invalid sample_list: {sample_list}. The length of sample_list must be greater than 1.')
        
         
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
            plt.figure(figsize=(width, height))
            fig = sns.scatterplot(x=pcoa_res.samples.PC1, y=pcoa_res.samples.PC2, s=100, 
                                  hue=group_list_for_hue, palette=color_palette, alpha=0.8, edgecolor='black', linewidth=0.5)
            if show_label:
                for i, txt in enumerate(pcoa_res.samples.index):
                    if adjust_label:
                        fig.text(pcoa_res.samples.PC1[i], pcoa_res.samples.PC2[i], txt, fontsize=font_size, alpha=font_transparency, ha='center', va='center')
                    else:
                        fig.text(pcoa_res.samples.PC1[i], pcoa_res.samples.PC2[i], txt, fontsize=font_size, alpha=font_transparency)
                        
            fig.set_xlabel("PC1 (%.2f%%)" % (pcoa_res.proportion_explained[0] * 100))
            fig.set_ylabel("PC2 (%.2f%%)" % (pcoa_res.proportion_explained[1] * 100))
            # set title
            plt.title(f'PCoA plot of {metric} distance (Total explained variation: {pcoa_res.proportion_explained[0] * 100 + pcoa_res.proportion_explained[1] * 100:.2f}%)')
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
        input_colors = [ BLACK]
        colors = distinctipy.get_colors(n, exclude_colors= input_colors, pastel_factor=0.5)

        return colors