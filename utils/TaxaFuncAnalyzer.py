# Date: 2023-05-18
# Version: 1.0
# change log: Add a function (_data_processing) to multi table
# Data: 2023-05-23
# Version: 1.1
# change log: Add a function: remove batch effect
# Data: 2023-07-17
# Version: 1.2
# 1. Added a new function to check which attributes are set
# 2. Added a new function to set the group_dict
# Version: 1.3
# restructure the code, move the functions to AnalyzerUtils

import pandas as pd


# import AnalyzerUtils
from .AnalyzerUtils.BasicStats import BasicStats
from .AnalyzerUtils.CrossTest import CrossTest
from .AnalyzerUtils.DataPreprocessing import DataPreprocessing
from .AnalyzerUtils.GetMatrix import GetMatrix


import warnings
warnings.filterwarnings('ignore')

class TaxaFuncAnalyzer:
    def __init__(self, df_path, meta_path):
        self.original_row_num = 0
        self.original_df = None
        self.preprocessed_df = None

        self.sample_list = None
        self.meta_df = None
        self.meta_name = None
        self.group_list = None # a list of group names for each sample, not unique
        self.group_dict = None

        self.func_list = None # all the func in the taxaFunc table which has _prop
        self.func_name = None

        self.taxa_level = None
        self.clean_df = None
        self.peptide_df = None
        self.taxa_df = None
        self.func_df = None
        self.taxa_func_df = None
        self.func_taxa_df = None
        self.taxa_func_linked_dict = None
        self.func_taxa_linked_dict = None
        self.outlier_status = {'peptide': None, 'taxa': None, 'func': None, 'taxa_func': None}

        self._set_original_df(df_path)
        self._set_meta(meta_path)
        self._remove_all_zero_row()
        self.get_func_list_in_df()
        # self.set_func('eggNOG_Description')
        
    def _set_original_df(self, df_path: str) -> None:
        self.original_df = pd.read_csv(df_path, sep='\t')
        if 'Taxon_prop' not in self.original_df.columns:
            raise ValueError("The TaxaFunc data must have Taxon_prop column!")
        self.original_df.columns = self.original_df.columns.str.replace(
            ' ', '_').str.replace('Intensity_', '')

    def _set_meta(self, meta_path: str) -> None:
        # read table without fill na
        meta = pd.read_csv(meta_path, sep='\t', keep_default_na=False)
        # sample name must be in the first column
        # rename the first column to Sample
        meta.rename(columns={meta.columns[0]: 'Sample'}, inplace=True)
        # replace space with _ and remove Intensity_
        meta['Sample'] = meta.iloc[:, 0].str.replace(
            ' ', '_').str.replace('Intensity_', '')
        meta = meta.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        self.sample_list = meta['Sample'].tolist()
        self.meta_df = meta
          
        
        check_result = self.check_meta_match_df()
        if check_result[0] == False:
            raise ValueError(f"The meta data does not match the TaxaFunc data, Please check! \n\n{check_result[1]}")
    
    def update_meta(self, meta_df: str) -> None:
        self.meta_df = meta_df
        old_sample_list = self.sample_list
        new_sample_list = meta_df['Sample'].tolist()
        # drop the samples not in meta_df from original_df
        drop_list = list(set(old_sample_list) - set(new_sample_list))
        self.original_df = self.original_df.drop(drop_list, axis=1)
        self.sample_list = new_sample_list
        self._remove_all_zero_row()
    
    def set_taxa_func_linked_dict(self):
        def _index_to_nested_dict(df):
            result_dict = {}
            for (key1, key2) in df.index:
                result_dict.setdefault(key1, []).append(key2)
            return result_dict
        self.taxa_func_linked_dict = _index_to_nested_dict(self.taxa_func_df)
        self.func_taxa_linked_dict = _index_to_nested_dict(self.func_taxa_df)
    
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
    
    def check_meta_match_df(self) -> tuple:
        meta_list = self.meta_df['Sample'].tolist()
        try:
            df = self.original_df.copy()
            df[meta_list]
            return True, "Meta data matches the TaxaFunc data."
        except Exception as e:
            return False, str(e)

    
    def _remove_all_zero_row(self):
        df = self.original_df.copy()
        print(f'original df shape: {df.shape}')
        self.original_row_num = df.shape[0]
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
        self.group_dict = self._get_group_dict_from_meta(self.meta_name)
        print(f'group is set to {group}\n {set(self.group_list)}')

    # get the groups of each meta column
    def get_meta_list(self, meta: str = None) -> list:
        if meta not in self.meta_df.columns or meta is None:
            raise ValueError(f'meta must be in {self.meta_df.columns.drop("Sample")}')
        else:
            return self.meta_df[meta].tolist()

    def _get_group_dict_from_meta(self, meta: str = None) -> dict:
        if meta not in self.meta_df.columns or meta is None:
            raise ValueError(f'meta must be in {self.meta_df.columns}')
        #extract the sample and group info from meta_df
        meta_df = self.meta_df[['Sample', meta]]
        return meta_df.groupby(meta)['Sample'].apply(list).to_dict()
       
    # input a group name, return the sample list in this group
    def get_sample_list_in_a_group(self, group: str = None) -> list:
        if self.group_list is None:
            print('group is not set, please set group first.')
            return None
        if group not in self.group_list:
            raise ValueError(f'group must be in {set(self.group_list)}')
        sample_list =  self.meta_df[self.meta_df[self.meta_name] == group]['Sample'].tolist()
        sample_list = sorted(sample_list)
        return sample_list
    
    # input a sample name, return the group name of this sample
    def get_group_of_a_sample(self, sample: str = None) -> str:
        if self.group_list is None:
            print('group is not set, please set group first.')
            return None
        if sample not in self.sample_list:
            raise ValueError(f'sample must be in {set(self.sample_list)}')
        else:
            return self.meta_df[self.meta_df['Sample'] == sample][self.meta_name].tolist()[0]
    
    def replace_if_two_index(self, df):
        if isinstance(df.index, pd.MultiIndex):
            df = df.copy()
            df.reset_index(inplace=True)
            # DO NOT USE f-string here, it will cause error
            df['Taxa-Func'] = df.iloc[:,
                                        0].astype(str) + ' <' + df.iloc[:, 1].astype(str) + '>'
            df.set_index('Taxa-Func', inplace=True)
            df = df.drop(df.columns[:2], axis=1)
        return df

######### Basic Stats Begin #########
    # get a mean df by group
    def get_stats_mean_df_by_group(self, df: pd.DataFrame = None) -> pd.DataFrame:
        bs = BasicStats(self)
        return bs.get_stats_mean_df_by_group(df)
        
    def get_stats_peptide_num_in_taxa(self) -> pd.DataFrame:
        bs = BasicStats(self)
        return bs.get_stats_peptide_num_in_taxa()

    def get_stats_taxa_level(self) -> pd.DataFrame:
        bs = BasicStats(self)
        return bs.get_stats_taxa_level()

    def get_stats_func_prop(self, func_name) -> pd.DataFrame:
        bs = BasicStats(self)
        return bs.get_stats_func_prop(func_name)
######### Basic Stats End #########

######### Data Preprocessing Begin #########
    def data_preprocess(self, df: pd.DataFrame, normalize_method: str = None, 
                         transform_method: str = None, batch_list: list = None, 
                         outlier_detect_method: str = None, outlier_handle_method: str = None,
                         outlier_detect_by_group: str = None, outlier_handle_by_group: str = None, processing_order:list=None,
                         df_name:str=None) -> pd.DataFrame:
        # normalize_method: 'None', 'sum', 'minmax', 'zscore', 'pareto'
        # transform_method: 'None', 'log2', 'log10', 'sqrt', 'cube'
        # batch_list: a list of treatment names in a meta column
        # outlier_detect_method: 'None', 'iqr', 'half-zero', 'zero-dominant', 'z-score', 'zero-inflated-poisson', 'negative-binomial', 'mahalanobis-distance'
        # outlier_handle_method: 'mean', 'median', 'knn', 'original', 'drop'
        # outlier_detect_by_group: a string of meta column name
        # outlier_handle_by_group: a string of meta column name
        # processing_order: a list of processing order, e.g. ['outlier', 'batch', 'transform', 'normalize']
        
        data_preprocessing = DataPreprocessing(self)
        return data_preprocessing._data_preprocess(df=df, normalize_method=normalize_method, 
                                                  transform_method=transform_method, batch_list=batch_list, 
                                                  outlier_detect_method=outlier_detect_method, outlier_handle_method=outlier_handle_method,
                                                  outlier_detect_by_group=outlier_detect_by_group, outlier_handle_by_group=outlier_handle_by_group, 
                                                  processing_order=processing_order, df_name=df_name)
######### Data Preprocessing End #########

######### Cross Test Begin #########
    def get_stats_anova(self, group_list: list = None, df_type:str = 'taxa-func') -> pd.DataFrame:
        cross_test = CrossTest(self)
        return cross_test.get_stats_anova(group_list=group_list, df_type=df_type)
        
    def get_stats_ttest(self, group_list: list = None, df_type: str = 'taxa-func') -> pd.DataFrame:
        cross_test = CrossTest(self)
        return cross_test.get_stats_ttest(group_list=group_list, df_type=df_type)
    
    def get_stats_deseq2(self, df, group_list: list):
        cross_test = CrossTest(self)
        return cross_test.get_stats_deseq2(df, group_list)

    # Get the Tukey test result of a taxon or a function
    def get_stats_tukey_test(self, taxon_name: str=None, func_name: str=None, sum_all: bool=True):
        cross_test = CrossTest(self)
        return cross_test.get_stats_tukey_test(taxon_name=taxon_name, func_name=func_name, sum_all = sum_all)
    
    # Find out the items that are not significant in taxa but significant in function, and vice versa
    def get_stats_diff_taxa_but_func(self, group_list: list = None, p_value: float = 0.05,
                                    taxa_res_df: pd.DataFrame =None, func_res_df: pd.DataFrame=None, taxa_func_res_df: pd.DataFrame=None):
        # return a tuple involed 2 df: (df_filtered_taxa_not_significant, df_filtered_func_not_significant)
        cross_test = CrossTest(self)
        return cross_test.get_stats_diff_taxa_but_func(group_list=group_list, p_value=p_value,
                                                       taxa_res_df=taxa_res_df, func_res_df=func_res_df, taxa_func_res_df=taxa_func_res_df)

    # compare all the groups with the control group
    def get_stats_dunnett_test(self, control_group, group_list: list = None, df_type: str = 'taxa-func') -> pd.DataFrame:
            """
            Calculate the p-value and t-statistic using Dunnett's test for multiple group comparisons.

            Args:
                control_group (str, required): Name of the control group.
                group_list (list, optional): List of group names to compare. Defaults to None means all groups.
                df_type (str, optional): Type of dataframe to use for the test. Defaults to 'taxa-func'.

            Returns:
                dict: A dictionary containing two dataframes, one for p-values and one for t-statistics.
            """
            cross_test = CrossTest(self)
            return cross_test.get_stats_dunnett_test(group_list=group_list, control_group=control_group, df_type=df_type)
        
        
        
    
######### Cross Test End #########

######### Get Matrix Begin #########
    def get_intensity_matrix(self, func_name: str = None, taxon_name: str = None,
                             peptide_seq: str = None, sample_list: list = None) -> pd.DataFrame:
    # input: a taxon with its function, a function with its taxon,
    # and the peptides in the function or taxon
    # output: a matrix of the intensity of the taxon or function or peptide in each sample
        get_matrix = GetMatrix(self)
        return get_matrix.get_intensity_matrix(func_name=func_name, taxon_name=taxon_name,
                                               peptide_seq=peptide_seq, sample_list=sample_list)
    
        # df = get_top_intensity(sw.taxa_df, top_num=50, method='freq')
    def get_top_intensity(self, df, top_num: int = 10, method: str = 'mean', sample_list: list = None):
        get_matrix = GetMatrix(self)
        return get_matrix.get_top_intensity(df=df, top_num=top_num, method=method, sample_list=sample_list)
    
    # input: df, df_type, top_num, show_stats_col
    # output: df
    # df_type: 'anova' or 'ttest' or 'log2fc'
    def get_top_intensity_matrix_of_test_res(self, df, df_type: str = None, top_num: int = 100, show_stats_cols: bool = False):
        get_matrix = GetMatrix(self)
        return get_matrix.get_top_intensity_matrix_of_test_res(df=df, df_type=df_type, top_num=top_num, show_stats_cols=show_stats_cols)
######### Get Matrix End #########




    def set_multi_tables(self, level: str = 's', func_threshold:float = 1.00,
                          normalize_method: str = None, transform_method: str = None,
                          outlier_detect_method: str = None, outlier_handle_method: str = None,
                          outlier_detect_by_group: str = None, outlier_handle_by_group: str = None, batch_list: list = None, 
                          processing_order:list=None, processing_after_sum: bool = False):
        # reset outlier_status
        self.outlier_status = {'peptide': None, 'taxa': None, 'func': None, 'taxa_func': None}
        args_data_preprocess = {
            'normalize_method': normalize_method,
            'transform_method': transform_method,
            'batch_list': batch_list,
            'outlier_detect_method': outlier_detect_method,
            'outlier_handle_method': outlier_handle_method,
            'outlier_detect_by_group': outlier_detect_by_group,
            'outlier_handle_by_group': outlier_handle_by_group,
            'processing_order': processing_order
        }

        df = self.original_df.copy()
        # perform data pre-processing
        if not processing_after_sum:
            df = self.data_preprocess(df=df,df_name = 'peptide', **args_data_preprocess)
            # save the processed df
            self.preprocessed_df = df
        
        func_name = self.func_name
        sample_list = self.sample_list

        print(f"Original data shape: {df.shape}")
        print("Starting to set Function table...")
        # filter prop = 100% and func are not (NULL, -, NaN)
        df_func = df[(df[f'{func_name}_prop'] >= func_threshold) & (df[func_name].notnull()) &
                     (df[func_name] != 'unknown') & (df[func_name] != '-') & (df[func_name] != 'NaN')].copy()
        
        df_func = df_func.groupby(func_name).sum(numeric_only=True)[sample_list]
        if processing_after_sum:
            print("\n-----Starting to perform data pre-processing for Function table...-----")
            df_func = self.data_preprocess(df=df_func,df_name = 'func', **args_data_preprocess)
        print(f"Function number: {df_func.shape[0]}")

        print("Starting to set Taxa table...")
        # select taxa level and create dfc (df clean)
        def strip_taxa(x, level):
            level_dict = {'s': 7, 'g': 6, 'f': 5, 'o': 4, 'c': 3, 'p': 2, "d": 1, 'l': 1}
            return "|".join(x.split('|')[:level_dict[level]])

        level_mapping = {
            's': ['species'],
            'g': ['genus', 'species'],
            'f': ['family', 'genus', 'species'],
            'o': ['order', 'family', 'genus', 'species'],
            'c': ['class', 'order', 'family', 'genus', 'species'],
            'p': ['phylum', 'class', 'order', 'family', 'genus', 'species'],
            'd': ['domain', 'phylum', 'class', 'order', 'family', 'genus', 'species'],
            'l': ['life', 'domain', 'phylum', 'class', 'order', 'family', 'genus', 'species']
        }
        # set taxa_level info
        self.taxa_level = level_mapping[level][0]

        if level in level_mapping:
            df_t = df[df['LCA_level'].isin(level_mapping[level])]
            if level != 's':
                df_t.loc[:, 'Taxon'] = df_t['Taxon'].apply(lambda x: strip_taxa(x, level))
            dfc = df_t
        else:
            raise ValueError("Please input the correct taxa level (s, g, f, o, c, p, d, l)")
        
        
        if level != 's':
            df_t.loc[:, 'Taxon'] = df_t['Taxon'].apply(lambda x: strip_taxa(x, level))
            dfc = df_t

        if level != 's':
            df_t.loc[:, 'Taxon'] = df_t['Taxon'].apply(lambda x: strip_taxa(x, level))
            dfc = df_t


        # extract 'taxa' and sample intensity
        df_taxa = dfc.groupby('Taxon').sum(numeric_only=True)[sample_list]
        if processing_after_sum:
            print("\n-----Starting to perform data pre-processing for Taxa table...-----")
            df_taxa = self.data_preprocess(df=df_taxa,df_name = 'taxa', **args_data_preprocess)
        print(f"Taxa number: {df_taxa.shape[0]}")

        # Filter the dataframe
        filter_conditions = (
            (dfc['Taxon'] != 'unknown') &
            (dfc[f'{func_name}_prop'] >= func_threshold) &
            dfc[func_name].notnull() &
            (dfc[func_name] != 'unknown') &
            (dfc[func_name] != '-')
        )
        dfc = dfc[filter_conditions]
        
        # create clean peptide table
        if processing_after_sum:
            print("\n-----Starting to perform data pre-processing for dfc...-----")
            dfc_processed = self.data_preprocess(df=dfc, df_name = 'peptide',**args_data_preprocess)
            self.preprocessed_df = dfc_processed
            dfc_with_peptides = dfc_processed[['Sequence', 'Taxon', func_name] + sample_list]
        else:  
            dfc_with_peptides = dfc[['Sequence', 'Taxon', func_name] + sample_list]
            
        df_peptide = dfc_with_peptides.copy()
        df_peptide.index = df_peptide['Sequence']
        df_peptide = df_peptide.drop(['Sequence', 'Taxon', func_name], axis=1)

        # extract 'taxa' and 'func' and sample intensity
        extract_list = ['Taxon', func_name] + sample_list
        dfc = dfc[extract_list]

        # create taxa-func central table
        df_taxa_func = dfc.groupby(['Taxon', func_name], as_index=True).sum(numeric_only=True)
        if processing_after_sum:
            print("\n-----Starting to perform data pre-processing for Taxa-Function table...-----")
            df_taxa_func = self.data_preprocess(df=df_taxa_func,df_name = 'taxa_func', **args_data_preprocess)

        # df_func_taxa = dfc.groupby([func_name, 'Taxon'], as_index=True).sum(numeric_only=True)
        df_func_taxa = df_taxa_func.swaplevel().sort_index()


        print(f"Taxa-Function number: {df_taxa_func.shape[0]}")

        self.taxa_df = df_taxa
        self.func_df = df_func
        self.taxa_func_df = df_taxa_func
        self.func_taxa_df = df_func_taxa
        self.clean_df = dfc_with_peptides
        self.peptide_df = df_peptide
        
        # set the taxa_func_linked_dict and func_taxa_linked_dict
        self.set_taxa_func_linked_dict()
        print("Multi-tables setting finished.\n")
    
    # New function to check which attributes are set
    def check_attributes(self):
        status = {"Set": [], "Not set": []}
        for attr in vars(self):
            if getattr(self, attr) is None:
                status["Not set"].append(attr)
            else:
                status["Set"].append(attr)
        for key, value in status.items():
            # print with format
            print(f"{key}:")
            for attr in value:
                print(f"  {attr}")
            print()
        
    def get_taxa_func_linked_peptide_num_df(self):
        """
        Get the dataframe of taxa_func_linked_peptide_num
        Taxa | Function | PepNum
        """
        dft = self.clean_df[['Sequence', "Taxon", self.func_name]]
        taxa_list = dft["Taxon"].unique().tolist()
        temp_dict = {'Taxon': [], 'Function': [], 'PepNum': []}
        
        for tax in taxa_list:
            df_taxa = dft[dft["Taxon"] == tax]
            func_list = df_taxa[self.func_name].unique().tolist()
            for func in func_list:
                pep_num = len(df_taxa[df_taxa[self.func_name] == func])
                if pep_num > 0:
                    temp_dict['Taxon'].append(tax)
                    temp_dict['Function'].append(func)
                    temp_dict['PepNum'].append(pep_num)
        df = pd.DataFrame(temp_dict)
        df = df.sort_values(by=['PepNum', 'Taxon'], ascending=False, ignore_index=True)
        return df