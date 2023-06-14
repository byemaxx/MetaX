# Date: 2023-05-18
# Version: 1.0
# change log: Add a function (_data_processing) to multi table
# Data: 2023-05-23
# Version: 1.1
# change log: Add a function: remove batch effect


from .reComBat import reComBat

import pandas as pd
import numpy as np
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy.stats import f_oneway
from scipy.stats import ttest_ind
from tqdm import tqdm
from pydeseq2.ds import DeseqStats
from pydeseq2.dds import DeseqDataSet


class TaxaFuncAnalyzer:
    def __init__(self, df_path, meta_path):
        self.original_df = None

        self.sample_list = None
        self.meta_df = None
        self.meta_name = None
        self.group_list = None

        self.func_list = None
        self.func_name = None

        self.clean_df = None
        self.taxa_df = None
        self.func_df = None
        self.taxa_func_df = None
        self.func_taxa_df = None

        self.anova_df = None

        self._set_original_df(df_path)
        self._set_meta(meta_path)
        self._remove_all_zero_row()
        self.get_func_list_in_df()
        self.set_func('Description')

    def _set_original_df(self, df_path: str) -> None:
        self.original_df = pd.read_csv(df_path, sep='\t')
        self.original_df.columns = self.original_df.columns.str.replace(
            ' ', '_').str.replace('Intensity_', '')

    def _set_meta(self, meta_path: str) -> None:
        meta = pd.read_csv(meta_path, sep='\t')
        # sample name must be in the first column
        # rename the first column to Sample
        meta.rename(columns={meta.columns[0]: 'Sample'}, inplace=True)
        # replace space with _ and remove Intensity_
        meta['Sample'] = meta.iloc[:, 0].str.replace(
            ' ', '_').str.replace('Intensity_', '')

        self.sample_list = meta['Sample'].tolist()
        self.meta_df = meta
    
    def get_func_list_in_df(self) -> list:
        col_names = self.original_df.columns.tolist()
        func_list = []
        for i in col_names:
            if "_prop" in i:
                i = i.replace("_prop", "")
                if i == 'Taxon':
                    continue
                else:
                    func_list.append(i)
        self.func_list = func_list
        return func_list
    
    def check_meta_match_df(self) -> bool:
        meta_list = self.meta_df['Sample'].tolist()
        try:
            df = self.original_df.copy()
            df[meta_list]
            return True
        except:
            return False
    
    def _remove_all_zero_row(self):
        df = self.original_df.copy()
        print(f'original df shape: {df.shape}')
        df = df.drop(df[(df[self.sample_list] == 0).all(axis=1)].index)
        print(f'after remove all zero row: {df.shape}')
        self.original_df = df

    

    def set_func(self, func):
        
        # check_list = ['eggNOG_OGs', 'max_annot_lvl', 'COG_category', 'Description', 'Preferred_name', 'GOs', 
        #               'EC', 'KEGG_ko', 'KEGG_Pathway', 'KEGG_Module', 'KEGG_Reaction', 'KEGG_rclass', 'BRITE', 
        #               'KEGG_TC', 'CAZy', 'BiGG_Reaction', 'PFAMs']
        check_list = self.func_list
        if func not in check_list:
            raise ValueError(f'func must be in {check_list}')
        else:
            self.func_name = func

    # set which group in meta_df to use
    def set_group(self, group: str):
        if group not in self.meta_df.columns:
            raise ValueError(f'group must be in {self.meta_df.columns}')
        self.group_list = self.get_meta_list(group)
        self.meta_name = group
        print(f'group is set to {group}\n {set(self.group_list)}')

    # get the groups of each meta column
    def get_meta_list(self, meta: str = None) -> list:
        if meta not in self.meta_df.columns or meta is None:
            raise ValueError(f'meta must be in {self.meta_df.columns}')
        else:
            return self.meta_df[meta].tolist()

    # input a group name, return the sample list in this group
    def get_sample_list_in_a_group(self, group: str = None) -> list:
        if self.group_list is None:
            print('group is not set, please set group first.')
            return None
        if group not in self.group_list:
            raise ValueError(f'group must be in {set(self.group_list)}')
        else:
            return self.meta_df[self.meta_df[self.meta_name] == group]['Sample'].tolist()

    def get_stats_peptide_num_in_taxa(self) -> pd.DataFrame:
        df = self.original_df.copy()
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
        df = self.original_df.copy()
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
        if func_name not in self.func_list:
            raise ValueError(f'func_name must be in {self.func_list}')
        
        df = self.original_df.copy()
        # remove unknown
        df = df[ (df[func_name].notnull()) & (df[func_name] != 'unknown')]
        
        prop_name = f'{func_name}_prop'

        df_prop = pd.DataFrame({'prop': ['0-0.1', '0-0.2', '0-0.3', '0-0.4', '0-0.5', '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1', '1'],
                                'n': [len(df[(df[prop_name] >= i/10) & (df[prop_name] < (i+1)/10)]) for i in range(11)]})
        df_prop['freq'] = (df_prop['n']/df_prop['n'].sum()*100).round(2)
        df_prop['label'] = df_prop['prop'] + \
            ' (' + df_prop['freq'].astype(str) + '%)'
        return df_prop
    
    # data pre-processing for multi-tables
    def _remove_batch_effect(self, df: pd.DataFrame= None, batch_list: list =None) -> pd.DataFrame:
        if df is not None and batch_list is not None and batch_list != 'None':

            df_t = df.copy()
            sample_list = self.sample_list
            batch_list = batch_list
            df_samples = df_t[sample_list]
            df_samples += 1

            # display(df_samples.head())

            batch  = pd.Series(index=df_samples.columns, data=batch_list)
            # display(batch.head())
            # print(Counter(batch))

            combat = reComBat()
            df_corrected = combat.fit_transform(df_samples.T, batch).T

            df_corrected = np.where(df_corrected < 2, 0, df_corrected)
            df_t[sample_list] = df_corrected

            return df_t
        
        elif batch_list is None or batch_list == 'None':
            print('batch_list is not set, Batch effect removal did not perform.')
            return df
        else:
            print('df and batch_list are not set, Batch effect removal did not perform.')
            return df
            
    
    def _data_transform(self, df: pd.DataFrame, transform_method: str = None) -> pd.DataFrame:
        if transform_method is None:
            print('transform_method is not set, data transform did not perform.')
            return df
        else:
            df = df.copy()
            df_mat = df[self.sample_list]

            transform_operations = {
                'None': lambda x: x,
                'cube': np.cbrt,
                'log10': lambda x: np.log10(x + 1),
                'log2': lambda x: np.log2(x + 1),
                'sqrt': np.sqrt
            }

            if transform_method is not None:
                if transform_method in transform_operations:
                    df_mat = transform_operations[transform_method](df_mat)
                    print(f'Data transformed by {transform_method}')
                else:
                    raise ValueError('transform_method must be in [None, log2, log10, sqrt, cube]')

            df[self.sample_list] = df_mat
            return df
    
    def _data_normalization(self, df: pd.DataFrame, normalize_method: str = None) -> pd.DataFrame:
        if normalize_method is None:
            print('normalize_method is not set, data normalization did not perform.')
            return df
        else:
            df = df.copy()
            df_mat = df[self.sample_list]

            # plus 1e-10 to avoid divided by zero
            normalize_operations = {
                'None': lambda x: x,
                'mean': lambda x: x - x.mean(),
                'sum': lambda x: x / (x.sum() + 1e-10),
                'minmax': lambda x: (x - x.min()) / (x.max() - x.min() + 1e-10),
                'zscore': lambda x: (x - x.mean()) / (x.std() + 1e-10),
                'pareto': lambda x: (x - x.mean()) / np.sqrt(x.std())
            }

            if normalize_method in normalize_operations:
                df_mat = normalize_operations[normalize_method](df_mat)
                print(f'Data normalized by {normalize_method}')
            else:
                raise ValueError('normalize_method must be in [None, mean, sum, minmax, zscore]')
            
            # shift values by their absolute minimum to ensure all values are non-negative
            df_mat = df_mat - df_mat.min()

            df[self.sample_list] = df_mat
            return df

    def _data_preprocess(self, df: pd.DataFrame, normalize_method: str = None, transform_method: str = None, batch_list: list = None, processing_order:list=None) -> pd.DataFrame:
        df = df.copy()
        if processing_order is None:
            processing_order = ['batch', 'transform', 'normalize']
        else:
            processing_order = processing_order
        # perform data processing in order
        for process in processing_order:
            if process == 'batch':
                df = self._remove_batch_effect(df, batch_list)
            elif process == 'transform':
                df = self._data_transform(df, transform_method)
            elif process == 'normalize':
                df = self._data_normalization(df, normalize_method)
            else:
                raise ValueError('processing_order must be in [batch, transform, normalize]')
        return df
    



    def get_stats_anova(self, group_list: list = None, df_type:str = 'taxa-func') -> pd.DataFrame:
        group_list_all = sorted(set(self.get_meta_list(self.meta_name)))

        if group_list is None:
            group_list = group_list_all
        elif any(i not in group_list_all for i in group_list):
            raise ValueError(f"groups must be in {group_list_all}")
        if len(group_list) <= 2:
            raise ValueError(
                "groups must be more than 2 for ANOVA test, please use t-test")

        all_sample_list = [sample for group in group_list for sample in self.get_sample_list_in_a_group(group)]

        if df_type in ['taxa-func', 'func-taxa', 'taxa', 'func']:
            if df_type == 'taxa-func':
                df, primary, secondary = self.taxa_func_df, 'Taxon', self.func_name
            elif df_type == 'func-taxa':
                df, primary, secondary = self.func_taxa_df, self.func_name, 'Taxon'
            elif df_type == 'taxa':
                df, primary = self.taxa_df, 'Taxon'
            elif df_type == 'func':
                df, primary = self.func_df, self.func_name

            print(f"ANOVA test for {primary} in {group_list}")

            res = {primary: [], "P-value": [], "f-statistic": []}
            if df_type in ['taxa-func', 'func-taxa']:
                res[secondary] = []

            for row in tqdm(df.iterrows(), total=len(df)):
                primary_value = row[0]
                if df_type in ['taxa-func', 'func-taxa']:
                    primary_value = row[0][0]
                    secondary_value = row[0][1]
                    res[secondary].append(secondary_value)

                res[primary].append(primary_value)

                list_for_anova = [row[1][self.get_sample_list_in_a_group(group)].to_list() for group in group_list]

                f, p = f_oneway(*list_for_anova)
                res["P-value"].append(p)
                res["f-statistic"].append(f)

            res = pd.DataFrame(res)
            on_values = [primary]
            if df_type in ['taxa-func', 'func-taxa']:
                on_values.append(secondary)
            res_all = pd.merge(df, res, on=on_values)
            res_all.index = df.index
            res_all = res_all[['P-value', 'f-statistic'] + all_sample_list]
            return res_all

    def set_anova(self, group_list: list = None):
        df_anova = self.get_stats_anova(group_list)
        self.anova_df = df_anova
        
    def get_stats_ttest(self, group_list: list = None, df_type: str = 'taxa-func') -> pd.DataFrame:

        group_list_all = sorted(set(self.get_meta_list(self.meta_name)))

        if group_list is None:
            group_list = group_list_all
        elif any(i not in group_list_all for i in group_list):
            raise ValueError(f"groups must be in {group_list_all}")
        if len(group_list) != 2:
            raise ValueError("groups must be 2")

        all_sample_list = [sample for group in group_list for sample in self.get_sample_list_in_a_group(group)]

        if df_type in ['taxa-func', 'func-taxa', 'taxa', 'func']:
            if df_type == 'taxa-func':
                df, primary, secondary = self.taxa_func_df, 'Taxon', self.func_name
            elif df_type == 'func-taxa':
                df, primary, secondary = self.func_taxa_df, self.func_name, 'Taxon'
            elif df_type == 'taxa':
                df, primary = self.taxa_df, 'Taxon'
            elif df_type == 'func':
                df, primary = self.func_df, self.func_name

            print(f"t-test for {primary} in {group_list}")

            res = {primary: [], "P-value": [], "t-statistic": []}
            if df_type in ['taxa-func', 'func-taxa']:
                res[secondary] = []

            for row in tqdm(df.iterrows(), total=len(df)):
                primary_value = row[0]
                if df_type in ['taxa-func', 'func-taxa']:
                    primary_value = row[0][0]
                    secondary_value = row[0][1]
                    res[secondary].append(secondary_value)

                res[primary].append(primary_value)

                list_for_ttest = [row[1][self.get_sample_list_in_a_group(group)].to_list() for group in group_list]
                # check if the sample size more than 1
                if any(len(i) < 2 for i in list_for_ttest):
                    raise ValueError(f"sample size must be more than 1 for t-test")

                t, p = ttest_ind(*list_for_ttest)
                res["P-value"].append(p)
                res["t-statistic"].append(t)

            res = pd.DataFrame(res)
            on_values = [primary]
            if df_type in ['taxa-func', 'func-taxa']:
                on_values.append(secondary)
            res_all = pd.merge(df, res, on=on_values)
            res_all.index = df.index
            res_all = res_all[['P-value', 't-statistic'] + all_sample_list]
            return res_all
    # input: a taxon with its function, a function with its taxon,
    # and the peptides in the function or taxon
    # output: a matrix of the intensity of the taxon or function or peptide in each sample
    def get_intensity_matrix(self, func_name: str = None, taxon_name: str = None,
                             peptide_seq: str = None, groups: list = None):

        if func_name is not None:
            dft = self.func_taxa_df.copy()
            dft.reset_index(inplace=True)

            if taxon_name is None:
                dft = dft[dft[self.func_name] == func_name]
                dft.set_index('Taxon', inplace=True)
            if taxon_name is not None:
                dft = self.clean_df[(self.clean_df['Taxon'] == taxon_name) & (
                    self.clean_df[self.func_name] == func_name)]
                dft.set_index('Sequence', inplace=True)

        elif taxon_name is not None and peptide_seq is None:
            dft = self.func_taxa_df.copy()
            dft.reset_index(inplace=True)
            dft = dft[dft['Taxon'] == taxon_name]
            dft.set_index(self.func_name, inplace=True)

        elif peptide_seq is not None and taxon_name is None:
            dft = self.original_df[self.original_df['Sequence'] == peptide_seq]
            dft.set_index('Sequence', inplace=True)

        else:
            raise ValueError(
                "Please input either func_name or taxon_name or peptide_seq")

        # Create the samples list of groups
        if groups is not None:
            group_list_all = list(set(self.get_meta_list(self.meta_name)))
            if any(i not in group_list_all for i in groups):
                raise ValueError(f"groups must be in {group_list_all}")
            sample_list = []
            for i in groups:
                sample_list += self.get_sample_list_in_a_group(i)
        else:
            groups = list(set(self.get_meta_list(self.meta_name)))
            sample_list = self.sample_list

        # Get the intensity matrix of the samples
        dft = dft[sample_list]
        return dft

    # input: df, df_type, top_num, show_stats_col
    # output: df
    # df_type: 'anova' or 'ttest' or 'log2fc'
    def get_top_intensity_matrix_of_test_res(self, df, df_type: str = None, top_num: int = 100, show_stats_cols: bool = False):
        def replace_if_two_index(df):
            if isinstance(df.index, pd.MultiIndex):
                df = df.copy()
                df.reset_index(inplace=True)
                # DO NOT USE f-string here, it will cause error
                df['Taxa-Func'] = df.iloc[:,
                                          0].astype(str) + ' [' + df.iloc[:, 1].astype(str) + ']'
                df.set_index('Taxa-Func', inplace=True)
                df = df.drop(df.columns[:2], axis=1)
            return df

        dft = df.copy()
        if df_type is None:
            dft = dft.head(top_num)

        elif df_type == 'anova':
            dft = dft.sort_values(
                by=['P-value', 'f-statistic'], ascending=[True, False], ignore_index=False)

        elif df_type == 'ttest':
            dft = dft.sort_values(
                by=['P-value'], ascending=[True], ignore_index=False)

        elif df_type == 'log2fc':
            dft['abs_log2FoldChange'] = dft['log2FoldChange'].abs()
            dft = dft.sort_values(by=['padj', 'abs_log2FoldChange'], ascending=[
                                  True, False], ignore_index=False)
            dft = dft.drop('abs_log2FoldChange', axis=1)

        dft = replace_if_two_index(dft)

        if show_stats_cols:
            dft = dft.head(top_num)
        else:
            if df_type == 'log2fc':
                dft = dft.drop(df.columns[:6], axis=1)
            elif df_type in {'ttest', 'anova'}:
                dft = dft.drop(df.columns[:2], axis=1)

            dft = dft.head(top_num)

        return dft

    def get_stats_deseq2(self, df, group_list: list):


        def replace_if_two_index(df):
            if isinstance(df.index, pd.MultiIndex):
                df = df.copy()
                df.reset_index(inplace=True)
                # DO NOT USE f-string here, it will cause error
                df['Taxa-Func'] = df.iloc[:,
                                          0].astype(str) + ' [' + df.iloc[:, 1].astype(str) + ']'
                df.set_index('Taxa-Func', inplace=True)
                df = df.drop(df.columns[:2], axis=1)
            else:
                df = df.copy()
            return df

        sample_list = []
        for i in group_list:
            sample = self.get_sample_list_in_a_group(i)
            sample_list += sample

        # Create intensity matrix
        df = df[sample_list]

        df = replace_if_two_index(df)
        counts_df = df.T
        # if the max value > 10000, divide by 100
        if counts_df.max().max() > 10000:
            counts_df = counts_df/100
        
        counts_df = counts_df.astype(int)
        counts_df = counts_df.sort_index()

        # Create meta data
        meta_df = self.meta_df
        meta_df = meta_df[meta_df['Sample'].isin(sample_list)]

        meta_df.set_index('Sample', inplace=True)
        meta_df = meta_df.sort_index()

        dds = DeseqDataSet(
            counts=counts_df,
            clinical=meta_df,
            design_factors=self.meta_name,
            refit_cooks=True)

        dds.deseq2()
        stat_res = DeseqStats(dds)
        stat_res.summary()

        res = stat_res.results_df
        res_merged = pd.merge(res, df, left_index=True, right_index=True)

        return res_merged

    # Get the Tukey test result of a taxon or a function
    def get_stats_tukey_test(self, taxon_name: str=None, func_name: str=None):
        # :param taxon_name: the taxon name
        # :param func_name: the function name
        # :return: the Tukey test result


        df = self.taxa_func_df.copy()
        df = df.reset_index()

        # Correct the logic for filtering the dataframe based on taxon_name and func_name
        if taxon_name is not None and func_name is not None:
            df = df[(df['Taxon'] == taxon_name) & (df[self.func_name] == func_name)]
        elif taxon_name is not None:
            df = df[df['Taxon'] == taxon_name]
        elif func_name is not None:
            df = df[df[self.func_name] == func_name]
        else:
            raise ValueError(
                "Please input the taxon name or the function name or both of them")
        if df.empty:
            raise ValueError(
                "Got empty dataframe, please check the taxon name or the function name")

        df = df[self.sample_list]
        Group = []
        Value = []

        for sample in self.sample_list:
            group = self.meta_df[self.meta_df['Sample']
                                 == sample][self.meta_name].values[0]
            value = df[sample].values[0]
            Group += [group]
            Value += [value]

        new_df = pd.DataFrame({'Group': Group, 'Value': Value})

        # Perform Tukey's test
        tukey_result = pairwise_tukeyhsd(new_df["Value"], new_df["Group"])
        print(tukey_result)

        tukey_df = pd.DataFrame(
            data=tukey_result._results_table.data[1:], columns=tukey_result._results_table.data[0])
        tukey_df['significant'] = tukey_df['reject'].apply(
            lambda x: 'Yes' if x else 'No')

        return tukey_df

    def set_multi_tables(self, level: str = 's', func_threshold:float = 1.00,
                          normalize_method: str = None, transform_method: str = None,
                            batch_list: list = None,  processing_order:list=None):
        
        if self.check_meta_match_df() is False:
            raise ValueError("The meta data does not match the TaxaFunc data, Please check!")

        
        df = self.original_df.copy()
        # perform data pre-processing
        df = self._data_preprocess(df, normalize_method, transform_method, batch_list, processing_order)
        
        func_name = self.func_name
        sample_list = self.sample_list

        print(f"Original data shape: {df.shape}")
        print("Starting to set Function table...")
        # filter prop = 100% and func are not (NULL, -, NaN)
        df_func = df[(df[f'{func_name}_prop'] >= func_threshold) & (df[func_name].notnull()) &
                     (df[func_name] != 'unknown')].copy()
        


        df_func = df_func.groupby(func_name).sum(numeric_only=True)[sample_list]
        print(f"Function number: {df_func.shape[0]}")

        print("Starting to set Taxa table...")
        # select taxa level and create dfc (df clean)
        def strip_taxa(x, level):
            level_dict = {'s': 7, 'g': 6, 'f': 5, 'o': 4, 'c': 3, 'p': 2, "d": 1, 'l': 1}
            return "|".join(x.split('|')[:level_dict[level]])
        
        if level == 's':
            dfc = df[df['LCA_level'] == 'species']

        elif level == 'g':
            df_t = df[(df['LCA_level'] == 'genus') | (df['LCA_level'] == 'species')]

        elif level == 'f':
            df_t = df[(df['LCA_level'] == 'family') | (df['LCA_level'] == 'genus') | (df['LCA_level'] == 'species')]
 
        elif level == 'o':
            df_t = df[(df['LCA_level'] == 'order') | (df['LCA_level'] == 'family') | (df['LCA_level'] == 'genus') | (df['LCA_level'] == 'species')]

        elif level == 'c':
            df_t = df[(df['LCA_level'] == 'class') | (df['LCA_level'] == 'order') | (df['LCA_level'] == 'family') | (df['LCA_level'] == 'genus') | (df['LCA_level'] == 'species')]

        elif level == 'p':
            df_t = df[(df['LCA_level'] == 'phylum') | (df['LCA_level'] == 'class') | (df['LCA_level'] == 'order') | (df['LCA_level'] == 'family') | (df['LCA_level'] == 'genus') | (df['LCA_level'] == 'species')]

        elif level == 'd':
            df_t = df[(df['LCA_level'] == 'domain') | (df['LCA_level'] == 'phylum') | (df['LCA_level'] == 'class') | (df['LCA_level'] == 'order') | (df['LCA_level'] == 'family') | (df['LCA_level'] == 'genus') | (df['LCA_level'] == 'species')]

        elif level == 'l':
            df_t = df[(df['LCA_level'] == 'life') | (df['LCA_level'] == 'domain') | (df['LCA_level'] == 'phylum') | (df['LCA_level'] == 'class') | (df['LCA_level'] == 'order') | (df['LCA_level'] == 'family') | (df['LCA_level'] == 'genus') | (df['LCA_level'] == 'species')]
        else:    
            raise ValueError("Please input the correct taxa level (s, g, f, o, c, p, d, l)")
        
        if level != 's':
            df_t['Taxon'] = df_t['Taxon'].apply(lambda x: strip_taxa(x, level))
            dfc = df_t


        # extract 'taxa' and sample intensity
        df_taxa = dfc.groupby('Taxon').sum(numeric_only=True)[sample_list]
        print(f"Taxa number: {df_taxa.shape[0]}")

        dfc = dfc[(dfc['Taxon'] != 'unknown')]
        dfc = dfc[(dfc[f'{func_name}_prop'] >= func_threshold) & (dfc[func_name].notnull()) & (dfc[func_name] != 'unknown')].copy()

        dfc_with_peptides = dfc[['Sequence', 'Taxon', func_name] + sample_list]

        # extract 'taxa' and 'func' and sample intensity
        extract_list = ['Taxon', func_name] + sample_list
        dfc = dfc[extract_list]

        # create taxa-func central table
        df_taxa_func = dfc.groupby(['Taxon', func_name], as_index=True).sum(numeric_only=True)

        df_func_taxa = dfc.groupby([func_name, 'Taxon'], as_index=True).sum(numeric_only=True)

        print(f"Taxa-Function number: {df_taxa_func.shape[0]}")

        self.taxa_df = df_taxa
        self.func_df = df_func
        self.taxa_func_df = df_taxa_func
        self.func_taxa_df = df_func_taxa
        self.clean_df = dfc_with_peptides