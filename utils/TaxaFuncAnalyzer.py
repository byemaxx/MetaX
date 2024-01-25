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
from .AnalyzerUtils.SumProteinIntensity import SumProteinIntensity


import warnings
warnings.filterwarnings('ignore')

class TaxaFuncAnalyzer:
    def __init__(self, df_path, meta_path=None, peptide_col_name='Sequence', protein_col_name='Proteins'):
        self.original_row_num = 0
        self.original_df = None
        self.preprocessed_df = None
        
        self.peptide_col_name = peptide_col_name
        self.protein_col_name = protein_col_name
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
        self.protein_df = None
        self.outlier_status = {'peptide': None, 'taxa': None, 'func': None, 'taxa_func': None, 'protein': None}

        self._set_original_df(df_path)
        self._set_meta(meta_path)
        self._remove_all_zero_row()
        self.get_func_list_in_df()
        # self.set_func('eggNOG_Description')
        
    def _set_original_df(self, df_path: str) -> None:
        self.original_df = pd.read_csv(df_path, sep='\t')
        if 'Taxon_prop' not in self.original_df.columns:
            raise ValueError("The TaxaFunc data must have Taxon_prop column!")
        
        ### create sample_list by Intensity_*, if meta is not provided
        col_names = self.original_df.columns.tolist()
        # replace space with _ 
        col_names = [i.replace(' ', '_') for i in col_names]
        intensity_col_names = [i for i in col_names if i.startswith('Intensity_')]
        if len(intensity_col_names) > 0:
            intensity_col_names = [i.replace('Intensity_', '') for i in intensity_col_names]
            self.sample_list = intensity_col_names
        ####        
        
        # replace space with _ and remove Intensity_
        self.original_df.columns = self.original_df.columns.str.replace(
            ' ', '_').str.replace('Intensity_', '')
        
    def _set_meta(self, meta_path=None) -> None:
        if meta_path is None:
            if self.sample_list is None:
                raise ValueError("Please provide the meta data!")
            else:
                print('Meta data is not provided, sample_list is created by Intensity_* columns.')
                meta = pd.DataFrame({'Sample': self.sample_list, 'Group_NA': 'NA', 'Sample_Name': self.sample_list})
                self.meta_df = meta
        else:
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
        ### taxa is the key, func list is the value, value is a list of tuples (func, pep_num)
        
        def _index_to_nested_dict(df):
            result_dict = {}
            for (key1, key2) in df.index:
                pep_num = df.loc[(key1, key2), 'peptide_num']
                result_dict.setdefault(key1, []).append((key2, pep_num))
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
            self.original_df[meta_list]
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
    def get_sample_list_in_a_group(self, group: str = None, condition: list = None) -> list:
        if self.group_list is None:
            print('group does not exist, please set group first.')
            return None
        if group not in self.group_list:
            raise ValueError(f'group must be in {set(self.group_list)}')
        if condition is not None:
            if not isinstance(condition, list) or len(condition) != 2:
                raise ValueError('condition must be a list with 2 elements, first is the meta column name, second is the group. e.g. ["Person", "PBS"]')
            if condition[0] not in self.meta_df.columns:
                raise ValueError(f'{condition[0]} must be in {set(self.meta_df.columns)}')
            # check if the condition is valid
            if condition[1] not in self.meta_df[condition[0]].unique().tolist():
                raise ValueError(f'{condition[1]} must be in {self.meta_df[condition[0]].unique().tolist()}')
            # get the sample list
            meta_df = self.meta_df[self.meta_df[condition[0]] == condition[1]]
        else:
            meta_df = self.meta_df
                
        sample_list =  meta_df[meta_df[self.meta_name] == group]['Sample'].tolist()
        sample_list = sorted(sample_list)
        return sample_list


    # input a sample name, return the group name of this sample
    def get_group_of_a_sample(self, sample: str = None) -> str:
        if self.group_list is None:
            print('group is not set, please set group first.')
            return None
        if sample not in self.sample_list:
            raise ValueError(f'sample must be in {set(self.sample_list)}, your input is [{sample}]')
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

    def get_stats_taxa_level(self, peptide_num = 1) -> pd.DataFrame:
        bs = BasicStats(self)
        return bs.get_stats_taxa_level(peptide_num)

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
    
    ## DESeq2 Begin ##
    def get_stats_deseq2(self, df, group1, group2, concat_sample_to_result: bool = True, quiet: bool = False, condition: list = None):
        cross_test = CrossTest(self)
        return cross_test.get_stats_deseq2(df, group1, group2, concat_sample_to_result, quiet, condition)

    def get_stats_deseq2_against_control(self, df, control_group, group_list: list = None, concat_sample_to_result: bool = False, quiet: bool = True, condition: list = None) -> pd.DataFrame:
        cross_test = CrossTest(self)
        return cross_test.get_stats_deseq2_against_control(df, control_group, group_list, concat_sample_to_result, quiet, condition)
    
    def extrcat_significant_fc_from_deseq2all(self, df: pd.DataFrame, p_value=0.05, log2fc_min=1, log2fc_max=30, p_type='padj'):
        cross_test = CrossTest(self)
        return cross_test.extrcat_significant_fc_from_deseq2all(df, p_value, log2fc_min, log2fc_max, p_type)
    
    def extrcat_significant_fc_from_deseq2all_3_levels(self, df, p_value=0.05, log2fc_min=1, log2fc_max=30, p_type='padj') -> dict:
        cross_test = CrossTest(self)
        return cross_test.extrcat_significant_fc_from_deseq2all_3_levels(df, p_value, log2fc_min, log2fc_max, p_type)

    # USAGE: res_df = get_stats_deseq2_against_control_with_conditon(sw.taxa_df, 'PBS', 'Individual')
    def get_stats_deseq2_against_control_with_conditon(self, df, control_group, condition) -> pd.DataFrame:
        cross_test = CrossTest(self)
        return cross_test.get_stats_deseq2_against_control_with_conditon(df, control_group, condition)
    
    ## DESeq2 End ##
    
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
                         processing_after_sum: bool = True,
                         data_preprocess_params: dict = {'normalize_method': None, 'transform_method': None,
                                                            'batch_list': None, 'outlier_detect_method': None,
                                                            'outlier_handle_method': None,
                                                            'outlier_detect_by_group': None,
                                                            'outlier_handle_by_group': None,
                                                            'processing_order': None},
                          peptide_num_threshold: dict = {'taxa': 1, 'func': 1, 'taxa_func': 1},
                          sum_protein:bool = False, sum_protein_params: dict = { 'method': 'razor', 
                                                                                'by_sample': False, 
                                                                                'rank_method': 'unique_counts'}
                          ):
        
        # reset outlier_status
        self.outlier_status = {'peptide': None, 'taxa': None, 'func': None, 'taxa_func': None}

        df = self.original_df.copy()
        # perform data pre-processing
        if not processing_after_sum:
            df = self.data_preprocess(df=df,df_name = 'peptide', **data_preprocess_params)
            # save the processed df
            self.preprocessed_df = df
            
        print(f"Original data shape: {df.shape}")
        
        # sum the protein intensity
        if sum_protein:
            self.protein_df = SumProteinIntensity(self).sum_protein_intensity( **sum_protein_params)
            if processing_after_sum:
                self.protein_df = self.data_preprocess(df=self.protein_df,df_name = 'protein', **data_preprocess_params)


                


        print("Starting to set Function table...")
        # filter prop = 100% and func are not (NULL, -, NaN)
        df_func = df[(df[f'{self.func_name}_prop'] >= func_threshold) & (df[self.func_name].notnull()) &
                     (df[self.func_name] != 'not_found') & (df[self.func_name] != '-') & (df[self.func_name] != 'NaN')].copy()
        
        df_func = df_func.groupby(self.func_name).sum(numeric_only=True)[self.sample_list]
        if processing_after_sum:
            print("\n-----Starting to perform data pre-processing for Function table...-----")
            df_func = self.data_preprocess(df=df_func,df_name = 'func', **data_preprocess_params)
            
        # add column 'peptide_num' to df_func
        df_func['peptide_num'] = df.groupby(self.func_name).count()[self.peptide_col_name]
        # move the column 'peptide_num' to the first column
        cols = list(df_func.columns)
        cols = [cols[-1]] + cols[:-1]
        df_func = df_func[cols]
        # filter the df_func by peptide_num_threshold
        df_func = df_func[df_func['peptide_num'] >= peptide_num_threshold['func']]
        print(f"Function number with prop >= [{func_threshold}], peptide_num >= [{peptide_num_threshold['func']}]: {df_func.shape[0]}")

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
        
        # extract 'taxa', sample intensity
        df_taxa = dfc[['Taxon'] + self.sample_list].copy()
        # add column 'peptide_num' to df_taxa as 1
        df_taxa['peptide_num'] = 1
        # move the column 'peptide_num' to the first column
        cols = list(df_taxa.columns)
        cols = [cols[-1]] + cols[:-1]
        df_taxa = df_taxa[cols]
        
        # groupby 'Taxon' and sum the sample intensity
        df_taxa = df_taxa.groupby('Taxon').sum(numeric_only=True)

        # Filter the dfc to create taxa-func table
        filter_conditions = (
            (dfc['Taxon'] != 'not_found') &
            (dfc[f'{self.func_name}_prop'] >= func_threshold) &
            dfc[self.func_name].notnull() &
            (dfc[self.func_name] != 'not_found') &
            (dfc[self.func_name] != '-')
        )
        dfc = dfc[filter_conditions]
        # create clean peptide table
        if processing_after_sum:
            print("\n-----Starting to perform data pre-processing for dfc...-----")
            dfc_processed = self.data_preprocess(df=dfc, df_name = 'peptide',**data_preprocess_params)
            self.preprocessed_df = dfc_processed
            dfc_with_peptides = dfc_processed[[self.peptide_col_name, 'Taxon', self.func_name] + self.sample_list]
        else:  
            dfc_with_peptides = dfc[[self.peptide_col_name, 'Taxon', self.func_name] + self.sample_list]
            
        df_peptide = dfc_with_peptides.copy()
        df_peptide.index = df_peptide[self.peptide_col_name]
        df_peptide = df_peptide.drop([self.peptide_col_name, 'Taxon', self.func_name], axis=1)
        
        # extract 'taxa' and 'func' and sample intensity
        extract_list = [self.peptide_col_name,'Taxon', self.func_name] + self.sample_list
        dfc = dfc[extract_list]
        

        
        
                
        if processing_after_sum:
            print("\n-----Starting to perform data pre-processing for Taxa table...-----")
            df_taxa = self.data_preprocess(df=df_taxa,df_name = 'taxa', **data_preprocess_params)
            

        # filter the df_taxa by peptide_num_threshold
        df_taxa = df_taxa[df_taxa['peptide_num'] >= peptide_num_threshold['taxa']]
        print(f"Taxa number with '{level}' level, peptide_num >= [{peptide_num_threshold['taxa']}]: {df_taxa.shape[0]}")



        # create taxa-func central table
        df_taxa_func = dfc.groupby(['Taxon', self.func_name], as_index=True).sum(numeric_only=True)
        if processing_after_sum:
            print("\n-----Starting to perform data pre-processing for Taxa-Function table...-----")
            df_taxa_func = self.data_preprocess(df=df_taxa_func,df_name = 'taxa_func', **data_preprocess_params)
        
        # add column 'peptide_num' to df_taxa_func
        df_taxa_func['peptide_num'] = dfc.groupby(['Taxon', self.func_name]).count()[self.peptide_col_name]
        # filter the df by peptide_num_threshold
        df_taxa_func = df_taxa_func[df_taxa_func['peptide_num'] >= peptide_num_threshold['taxa_func']]
        # move the column 'peptide_num' to the first column
        cols = list(df_taxa_func.columns)
        cols = [cols[-1]] + cols[:-1]
        df_taxa_func = df_taxa_func[cols]

        # exchange the multi-index, sort the index
        df_func_taxa = df_taxa_func.swaplevel().sort_index()
        

        print(f"Taxa-Function number with peptide_num >= [{peptide_num_threshold['taxa_func']}]: {df_taxa_func.shape[0]}")


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
        dft = self.clean_df[[self.peptide_col_name, "Taxon", self.func_name]]
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
    
