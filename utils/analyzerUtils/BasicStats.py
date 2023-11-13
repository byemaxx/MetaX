import pandas as pd
from collections import OrderedDict

class BasicStats:
    def __init__(self, tfa):
        self.tfa = tfa
        
    # get a mean df by group
    def get_stats_mean_df_by_group(self, df: pd.DataFrame = None) -> pd.DataFrame:
        data = df.copy()
        
        group_order = list(OrderedDict.fromkeys(self.tfa.get_group_of_a_sample(sample) for sample in data.columns))
        print("input group order:", group_order)
        
        group_means = pd.DataFrame()
        for group, samples in self.tfa.group_dict.items():
            # only use samples that are in the data
            valid_samples = [sample for sample in samples if sample in data.columns]
            if not valid_samples:
                print(f'Warning: none of the samples in group "{group}" are found in the data.')
                continue
            group_data = data[valid_samples]
            # calculate the mean of the samples in the group
            group_mean = group_data.mean(axis=1)
            # add the group mean to the group_means dataframe
            group_means[group] = group_mean
        group_means = group_means[group_order]
        return group_means

    def get_stats_peptide_num_in_taxa(self) -> pd.DataFrame:
        df = self.tfa.original_df.copy()
        # sort_list = ['unknown', 'l', 'd', 'p', 'c', 'o', 'f', 'g', 's']
        sort_list = ['unknown', 'life','domain', 'phylum', 'class', 
                     'order', 'family', 'genus', 'species']
        
        taxa_list = df['LCA_level'].tolist()
        dic = {i: taxa_list.count(i) for i in sort_list}
        df_taxa = pd.DataFrame(dic.items(), columns=['LCA_level', 'count'])
        df_taxa['freq'] = (df_taxa['count'] /
                           df_taxa['count'].sum() * 100).round(2)
        df_taxa['label'] = df_taxa.apply(
            lambda row: f"{row['LCA_level']} ({row['freq']}%)", axis=1)
        return df_taxa

    def get_stats_taxa_level(self) -> pd.DataFrame:
        df = self.tfa.original_df.copy()
        df = df[(df['Taxon'].notnull()) & (df['Taxon'] != 'unknown')]

        dft = df['Taxon'].str.split('|', expand=True)
        # dft.columns = ['d', 'p', 'c', 'o', 'f', 'g', 's']
        dft.columns = ['domain', 'phylum', 'class', 'order', 'family', 'genus', 'species']
        
        dic = {}
        # for i in ['d', 'p', 'c', 'o', 'f', 'g', 's']:
        for i in ['domain', 'phylum', 'class', 'order', 'family', 'genus', 'species']:
            set_i = set(dft[i].to_list())
            remove_list = [f'{i}__NULL', f'{i}__', ' ', None]
            for j in remove_list:
                if j in set_i:
                    set_i.remove(j)
            dic[i] = len(set_i)
        return pd.DataFrame(dic.items(), columns=['taxa_level', 'count'])

    def get_stats_func_prop(self, func_name) -> pd.DataFrame:
        if func_name not in self.tfa.func_list:
            raise ValueError(f'func_name must be in {self.tfa.func_list}')
        
        df = self.tfa.original_df.copy()
        # remove unknown
        df = df[ (df[func_name].notnull()) & (df[func_name] != 'unknown') & (df[func_name] != '-')]
        
        prop_name = f'{func_name}_prop'

        df_prop = pd.DataFrame({'prop': ['0-0.1', '0-0.2', '0-0.3', '0-0.4', '0-0.5', '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1', '1'],
                                'n': [len(df[(df[prop_name] >= i/10) & (df[prop_name] < (i+1)/10)]) for i in range(11)]})
        df_prop['freq'] = (df_prop['n']/df_prop['n'].sum()*100).round(2)
        df_prop['label'] = df_prop['prop'] + \
            ' (' + df_prop['freq'].astype(str) + '%)'
        return df_prop