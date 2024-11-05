import pandas as pd
from collections import OrderedDict
from scipy import stats

class BasicStats:
    def __init__(self, tfa):
        self.tfa = tfa
        
    # get a mean df by group
    def get_stats_mean_df_by_group(self, df: pd.DataFrame, condition: list|None = None, zero_dominant: bool|None = None) -> pd.DataFrame:
        """
        Calculate the mean values of groups of samples in a DataFrame, optionally considering only non-zero values.

        Args:
            df (pd.DataFrame): The input DataFrame containing the sample data. Defaults to None.
            condition (list, optional): A list of conditions to filter the samples. Defaults to None.eg. ['V1', 'PBS']
            zero_domainant (bool, optional): If True, calculate the mean of non-zero values in each group if the number of zero values is less than half of the total number of values; otherwise, return 0. Defaults to False.

        Returns:
            pd.DataFrame: A DataFrame containing the mean values of the groups.
        """

        def get_mean_by_zero_dominant(df: pd.DataFrame) -> pd.Series:
            """
            Optimized function to calculate the mean of non-zero values in each row if the number of zero values
            is less than half of the total values; otherwise, return 0.
            
            Args:
                df (pd.DataFrame): Input DataFrame.

            Returns:
                pd.Series: A Series with mean values based on the zero-dominant condition.
            """
            # 计算每行的零值数量
            zero_counts = (df == 0).sum(axis=1)
            # 判断每行零值是否超过一半，超过的行直接设为0
            mean_series = pd.Series(0, index=df.index)
            non_zero_rows = zero_counts <= (df.shape[1] / 2)
            # 对非零主导的行计算非零均值
            mean_series[non_zero_rows] = df[non_zero_rows].replace(0, pd.NA).mean(axis=1, skipna=True)
            return mean_series
        
        if zero_dominant is None:
            zero_dominant = self.tfa.stat_mean_by_zero_dominant
        print(f"Caculating mean by zero_dominant: [{zero_dominant}]")
        
        mean_method = get_mean_by_zero_dominant if zero_dominant else lambda x: x.mean(axis=1)

        
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
            group_mean = mean_method(group_data)
            
            # add the group mean to the group_means dataframe
            group_means[group] = group_mean
        group_means = group_means[group_order]
        # convert to float
        group_means = group_means.astype(float)
        # print("samples used:", samples_used)
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
    
    
    def get_correlation(self, df_type: str,
                        sample_list: list[str]|None = None,
                        focus_list: list[str]|None = None,
                        plot_list_only: bool = False,
                        rename_taxa: bool = False,
                        method='pearson') -> pd.DataFrame:
        '''
        Get correlation between items in a dataframe.
        `df_type`: str: 'taxa', 'func', 'taxa_func', 'func_taxa', 'custom'
        `sample_list`: a list of samples to calculate correlation
        `plot_list_only`: bool: if True, only return the list of samples that can be plotted
        `method`: str: 'pearson', 'spearman'
        '''
        df = self.tfa.get_df(df_type)
        df = self.tfa.replace_if_two_index(df)
        if sample_list:
            df = df[sample_list]
        if plot_list_only:
            # extrat the row that index is in the focus_list
            if focus_list and len(focus_list) > 0:
                df = df.loc[focus_list]
        if rename_taxa:
            df = self.tfa.rename_taxa(df)
        
        corr = df.T.corr(method=method)
        return corr

    def get_combined_sub_meta_df(
        self,
        df: pd.DataFrame,
        sub_meta: str,
        rename_sample: bool = False,
        plot_mean: bool = False,
    ) -> tuple[pd.DataFrame, list[str]]:
        """
        Combines the sub-meta information with the main meta information in the given DataFrame and returns the combined DataFrame and a list of sub-meta groups.

        Args:
            df (pd.DataFrame): The DataFrame containing the main meta information.
            sub_meta (str): The sub-meta information to be combined with the main meta information.
            rename_sample (bool, optional): Whether to rename the samples in the DataFrame. Defaults to False.
            plot_mean (bool, optional): Whether to plot the mean values. Defaults to False.

        Returns:
            tuple[pd.DataFrame, list[str]]: A tuple containing the combined DataFrame and a list of sub-meta groups.
        """
        if sub_meta != 'None':

            sample_groups = {sample: self.tfa.get_group_of_a_sample(sample, self.tfa.meta_name) for sample in df.columns}
            sub_groups = {sample: self.tfa.get_group_of_a_sample(sample, sub_meta) for sample in df.columns}

            # Combine samples with the same meta and sub-meta, and calculate the mean value
            grouped_data = df.T.groupby([sample_groups, sub_groups]).mean().T
            
            # group_list is the sub-meta group
            group_list = [i[1] for i in grouped_data.columns] if not plot_mean else grouped_data.columns.tolist()
            
            # Convert multi-index to single index
            grouped_data.columns = ['_'.join(col).strip() for col in grouped_data.columns.values]
            
            df = grouped_data
            
        else:
            if rename_sample:
                df, group_list = self.tfa.add_group_name_for_sample(df)
            else:
                group_list = [self.tfa.get_group_of_a_sample(i) for i in df.columns] if not plot_mean else df.columns.tolist()
        
        return df, group_list
    
    # Shapiro-Wilk Test
    def shapiro_test(self, df: pd.DataFrame, alpha=0.05) :
        """
        Perform Shapiro-Wilk test on the given DataFrame and return the results.

        Args:
            df (pd.DataFrame): The DataFrame to be tested.
            alpha (float, optional): The significance level. Defaults to 0.05.

        Returns:
            dict: A dictionary containing the boolean result of the Shapiro-Wilk test for each sample.
        """
        shapiro_results = {}
        for sample in df[self.tfa.sample_list]:
            values = df[sample].dropna()
            # remove zero values
            values = values[values != 0]
            _, p = stats.shapiro(values)
            # save the boolean result in the dictionary
            shapiro_results[sample] = {'p_value': p, 'is_normal': p > alpha}
            
        return shapiro_results
