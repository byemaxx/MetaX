import pandas as pd
from collections import OrderedDict

class BasicStats:
    def __init__(self, tfa):
        self.tfa = tfa
        
    # get a mean df by group
    def get_stats_mean_df_by_group(self, df: pd.DataFrame = None, condition: list = None) -> pd.DataFrame:
        data = df.copy()
        # extract samples that are in the data only
        columns_list = data.columns.tolist()
        # remove samples that are not in self.tfa.sample_list. e.g. 'pep_num'
        columns_list = [sample for sample in columns_list if sample in self.tfa.sample_list]
        data = data[columns_list]
        
        
        group_order = list(OrderedDict.fromkeys(self.tfa.get_group_of_a_sample(sample) for sample in data.columns))
        print("input group order:", group_order)
        samples_used =[]
        group_means = pd.DataFrame()
        for group in group_order:
            samples = self.tfa.get_sample_list_in_a_group(group, condition=condition)
            # only use samples that are in the data
            valid_samples = [sample for sample in samples if sample in data.columns]
            if not valid_samples:
                print(f'Warning: none of the samples in group "{group}" are found in the data.')
                continue
            samples_used.extend(valid_samples)
            group_data = data[valid_samples]
            # calculate the mean of the samples in the group
            group_mean = group_data.mean(axis=1)
            # add the group mean to the group_means dataframe
            group_means[group] = group_mean
        group_means = group_means[group_order]
        print("samples used:", samples_used)
        return group_means

    def get_stats_peptide_num_in_taxa(self) -> pd.DataFrame:
        df = self.tfa.original_df.copy()
        sort_list= ['genome', 'species', 'genus', 'family', 
                    'order', 'class', 'phylum', 'domain', 
                    'life', 'notFound']
        if not self.tfa.genome_mode:
            sort_list.remove('genome')
        
        taxa_list = df['LCA_level'].tolist()
        dic = {i: taxa_list.count(i) for i in sort_list}
        df_taxa = pd.DataFrame(dic.items(), columns=['LCA_level', 'count'])
        df_taxa['freq'] = (df_taxa['count'] /
                           df_taxa['count'].sum() * 100).round(2)
        df_taxa['label'] = df_taxa.apply(
            lambda row: f"{row['LCA_level']} ({row['freq']}%)", axis=1)
        return df_taxa

    def get_stats_taxa_level(self, peptide_num = 1) -> pd.DataFrame:
        if self.tfa.any_df_mode:
            # creta a dataframe with all levles of taxa as 1
            dic = {'domain': 1, 'phylum': 1, 'class': 1, 'order': 1, 'family': 1, 'genus': 1, 'species': 1}
            return pd.DataFrame(dic.items(), columns=['taxa_level', 'count'])
        
        
        df = self.tfa.original_df.copy()
        df = df[(df['Taxon'].notnull()) & (df['Taxon'] != 'not_found')]
        dft = df['Taxon'].str.split('|', expand=True)
        #! may raise error if no any peptide annotated at species level
        # check if the taxa split by | is the same
        check_len = 8 if self.tfa.genome_mode else 7
        if len(dft.columns) != check_len:
            raise ValueError(
                f"You have {len(dft.columns)} taxa levels. It should be {check_len}. Please check the taxa split by '|'.")
        
        col_list = ['domain', 'phylum', 'class', 'order', 'family', 'genus', 'species']
        if self.tfa.genome_mode:
            col_list.append('genome')
        dft.columns = col_list
        
        dft['peptide_num'] = 1 # add a initial peptide number for each row
        
        dic = {}
        for i in col_list:
            dfi = dft[[i, 'peptide_num']].groupby(i).sum()
            # only extract the taxa with more than peptide threshold
            dfi = dfi[dfi['peptide_num'] >= peptide_num]
            set_i = set(dfi.index)
            remove_list = [f'{i[0]}__NULL', f'{i[0]}__', ' ', None, f'{i[0]}__nan']
            for j in remove_list:
                if j in set_i:
                    set_i.remove(j)
                    # print(f'remove {j} from {i} set.')
            dic[i] = len(set_i)
        res_df = pd.DataFrame(dic.items(), columns=['taxa_level', 'count'])
        return res_df

    def get_stats_func_prop(self, func_name:str) -> pd.DataFrame:
        if func_name not in self.tfa.func_list:
            raise ValueError(f'func_name must be in {self.tfa.func_list}')
        
        df = self.tfa.original_df.copy()
        # remove not_found
        df = df[ (df[func_name].notnull()) & (df[func_name] != 'not_found') & (df[func_name] != '-')]
        
        prop_name = f'{func_name}_prop'

        df_prop = pd.DataFrame({'prop': ['0-0.1', '0-0.2', '0-0.3', '0-0.4', '0-0.5', '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1', '1'],
                                'n': [len(df[(df[prop_name] >= i/10) & (df[prop_name] < (i+1)/10)]) for i in range(11)]})
        df_prop['freq'] = (df_prop['n']/df_prop['n'].sum()*100).round(2)
        df_prop['label'] = df_prop['prop'] + \
            ' (' + df_prop['freq'].astype(str) + '%)'
        return df_prop