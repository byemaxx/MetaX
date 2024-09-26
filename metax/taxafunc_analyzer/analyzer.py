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
from typing import Optional, Dict, List, Union
from tqdm import tqdm 
from collections import defaultdict

# import AnalyzerUtils
if __name__ == '__main__':
    from analyzer_utils.data_preprocessing import DataPreprocessing
    from analyzer_utils.sum_protein_intensity import SumProteinIntensity
    from analyzer_utils.basic_stats import BasicStats
    from analyzer_utils.cross_test import CrossTest
    from analyzer_utils.get_matrix import GetMatrix
else:
    from .analyzer_utils.data_preprocessing import DataPreprocessing
    from .analyzer_utils.sum_protein_intensity import SumProteinIntensity
    from .analyzer_utils.basic_stats import BasicStats
    from .analyzer_utils.cross_test import CrossTest
    from .analyzer_utils.get_matrix import GetMatrix


import warnings
warnings.filterwarnings('ignore')

class TaxaFuncAnalyzer:
    def __init__(
        self,
        df_path,
        meta_path=None,
        peptide_col_name="Sequence",
        protein_col_name="Proteins",
        any_df_mode=False,
        custom_col_name="Custom",
    ):
        self.original_row_num = 0
        self.original_df: Optional[pd.DataFrame] = None
        self.has_na_in_original_df = False
        self.genome_mode = True

        self.peptide_col_name = peptide_col_name
        self.protein_col_name = protein_col_name
        self.custom_col_name = custom_col_name
        self.sample_list: Optional[List[str]] = None
        self.meta_df: Optional[pd.DataFrame] = None
        self.meta_name: Optional[str] = None
        self.group_list: Optional[List[str]] = None # a list of group names for each sample, not unique
        self.group_dict: Optional[Dict[str, List[str]]] = None

        self.func_list: Optional[List[str]] = None # all the func in the taxaFunc table which has _prop
        self.func_name: Optional[str] = None

        self.taxa_level: Optional[str] = None
        self.processed_original_df: Optional[pd.DataFrame] = None # the pep_taxa_func_sample table after filtering and data preprocessing
        self.peptide_df: Optional[pd.DataFrame] = None
        self.taxa_df: Optional[pd.DataFrame] = None
        self.func_df: Optional[pd.DataFrame] = None
        self.taxa_func_df: Optional[pd.DataFrame] = None
        self.func_taxa_df: Optional[pd.DataFrame] = None
        self.taxa_func_linked_dict: Optional[Dict[str, List[tuple]]] = None
        self.func_taxa_linked_dict: Optional[Dict[str, List[tuple]]] = None
        self.peptides_linked_dict = {'taxa': {}, 'func': {}, 'taxa_func': {}}
        self.protein_df: Optional[pd.DataFrame] = None
        self.any_df_mode = any_df_mode  # if True, the consider the TaxaFunc df as other_df
        self.custom_df: Optional[pd.DataFrame] = None # other df, any df that user want to add
        self.peptide_num_used = {'taxa': 0, 'func': 0, 'taxa_func': 0, 'protein': 0}
        
        self.split_func_status:bool = False
        self.split_func_sep:str = ''

        # load function
        self.BasicStats = BasicStats(self)
        self.CrossTest = CrossTest(self)
        self.GetMatrix = GetMatrix(self)
        self.detect_and_handle_outliers = DataPreprocessing(self).detect_and_handle_outliers
        self.data_preprocess = DataPreprocessing(self).data_preprocess


        self._set_original_df(df_path)
        self._set_meta(meta_path)
        self._remove_all_zero_row()
        self.get_func_list_in_df()
        # self.set_func('eggNOG_Description')

    def _set_original_df(self, df_path: str) -> None:
        self.original_df = pd.read_csv(df_path, sep='\t')

        if self.any_df_mode:
            self.custom_col_name = self.original_df.columns.tolist()[0] if self.custom_col_name == 'Custom' else self.custom_col_name
            self.sample_list = self.original_df.columns.tolist()[1:]
            #create a column 'LCA_level' with 'life' for other_df
            self.original_df['LCA_level'] = 'life'
            self.original_df['Taxon'] = 'd__Bacteria'
            self.original_df['Taxon_prop'] = 1
            # create a fake function column as Not_Exist
            self.original_df['Not_Applicable'] = 'Not_Exist'
            self.original_df['Not_Applicable_prop'] = 1
            # create a fake peptide column
            self.original_df['Sequence'] = 'Not_Exist'
        else: # for normal mode
            if 'Taxon_prop' not in self.original_df.columns:
                raise ValueError("The TaxaFunc data must have Taxon_prop column!")

            # check if the 'genome' in LCA_level, if no, set genome_mode to False
            if 'genome' not in self.original_df['LCA_level'].unique():
                self.genome_mode = False
                print("The genome mode is set to False, the LCA_level does not contain 'genome'.")


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
            # read table without fill na, and as string
            meta = pd.read_csv(meta_path, sep='\t', keep_default_na=False, dtype=str)
            # sample name must be in the first column
            # rename the first column to Sample
            meta.rename(columns={meta.columns[0]: 'Sample'}, inplace=True)
            # replace space with _ and remove Intensity_
            meta['Sample'] = meta.iloc[:, 0].apply(lambda x: x.strip().replace(' ', '_').replace('Intensity_', ''))
            meta = meta.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            # remove duplicate rows if exists
            if meta.duplicated().any():
                # print the duplicated rows
                dup_row = (meta[meta.duplicated()])
                print(f"[{dup_row.shape[0]}] duplicated rows are found in the meta data!\n{dup_row}\n")
                meta = meta.drop_duplicates()
                print(f"Duplicated rows are removed! Samples left: {meta.shape[0]}")

            self.sample_list = meta['Sample'].tolist()
            self.meta_df = meta


            check_result = self.check_meta_match_df()
            if check_result[0] == False:
                raise ValueError(f"The meta data does not match the TaxaFunc data, Please check! \n\n{check_result[1]}")
        
        # check if there is NA in the original_df[self.sample_list]
        if self.original_df[self.sample_list].isnull().values.any():
            self.has_na_in_original_df = True
            print("[NaN] exists in the original_df!")
        else:
            self.has_na_in_original_df = False

    def update_meta(self, meta_df: pd.DataFrame) -> None:
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
        print("Setting taxa_func_linked_dict and func_taxa_linked_dict...")
        
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

    def rename_taxa(self, df):
        first_index = df.index[0]
        index_list = df.index.tolist()
        
        # check if the df has two index
        if isinstance(first_index, tuple) and len(first_index) > 1:  # multi-index, taxa-func table or func-taxa table
            if 'd__' in first_index[0]:
                new_index_list = [(i[0].split('|')[-1], i[1]) for i in index_list]
            elif 'd__' in first_index[1]:
                new_index_list = [(i[0], i[1].split('|')[-1]) for i in index_list]
            df.index = pd.MultiIndex.from_tuples(new_index_list, names=df.index.names)
        else:       
            # single index, taxa table   
            if 'd__' in first_index:
                if '<' not in first_index:
                    new_index_list = [i.split('|')[-1] for i in index_list]
                else:
                    new_index_list = [
                        f'{i.split(" <")[0].split("|")[-1]} <{i.split(" <")[1][:-1]}>'
                        for i in index_list
                    ]
                df.index = new_index_list
        return df

    def rename_sample(self, df):
        df.columns = [f'{i} ({self.get_group_of_a_sample(i)})' for i in df.columns]
        return df


    def set_func(self, func):
        if self.any_df_mode:
            print("ANY_DF_MODE is set, the function is not applicable.")
            self.func_name = 'Not_Applicable'
            return
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
    def get_sample_list_in_a_group(
        self, group: Optional[str] = None, 
        condition: Optional[List[Union[str, list]]] = None
    ) -> List:
        """
        Get a list of samples in a specific group.

        Args:
            group (Optional[str]): The name of the group. Defaults to None.
            condition (Optional[List[Union[str, list]]]): A list with 2 elements, where the first element is the meta column name 
                                                        and the second element is the group. 
                                                        For example: 1. ["Individual", "V1"] 2.["Individual", ["V1", "V2"]].
                                                        Defaults to None.

        Returns:
            List: A sorted list of sample names in the specified group.

        Raises:
            ValueError: If the group is not in the group list.
            ValueError: If the condition is not a list with 2 elements.
            ValueError: If the meta column name in the condition is not in the meta dataframe columns.
            ValueError: If the group in the condition is not in the unique values of the specified meta column.
        """
        # Check if group list is defined
        if self.group_list is None:
            raise ValueError('Group list does not exist, please set group first.')
        
        # Check if the specified group is valid
        if group not in self.group_list:
            raise ValueError(f'Group must be in {set(self.group_list)}')
        
        if condition:
            # Validate condition format and values
            if not isinstance(condition, list) or len(condition) != 2:
                raise ValueError('Condition must be a list with 2 elements: [meta_column, group]. e.g. ["Individual", "V1"]')
            meta_column, condition_group = condition
            
            if meta_column not in self.meta_df.columns:
                raise ValueError(f'{meta_column} must be in {set(self.meta_df.columns)}')
            
            # Filter the dataframe based on the condition
            if isinstance(condition_group, str):
                if condition_group not in self.meta_df[meta_column].unique():
                    raise ValueError(f'{condition_group} must be in {self.meta_df[meta_column].unique().tolist()}')
                meta_df = self.meta_df[self.meta_df[meta_column] == condition_group]
            elif isinstance(condition_group, list):
                invalid_groups = [g for g in condition_group if g not in self.meta_df[meta_column].unique()]
                if invalid_groups:
                    raise ValueError(f'{invalid_groups} must be in {self.meta_df[meta_column].unique().tolist()}')
                meta_df = self.meta_df[self.meta_df[meta_column].isin(condition_group)]
            else:
                raise ValueError('Condition group must be either a string or a list of strings.')
        else:
            meta_df = self.meta_df

        # Get the sample list for the specified group
        sample_list = meta_df[meta_df[self.meta_name] == group]['Sample'].tolist()
        return sample_list

    def get_sample_list_for_group_list(
        self, 
        group_list: Optional[List] = None, 
        condition: Optional[List[Union[str, list]]] = None
    ) -> list:
        """
        Returns a list of sample names for the given group list and condition.

        Args:
            group_list (Optional[List]): List of group names. If not provided, all groups in meta_df will be used.
            condition (Optional[List[Union[str, list]]]): Condition list where the first element is the meta column name 
                                                        and the second element is the group. Defaults to None. 
                                                        The second element can be a string or a list of strings. 
                                                        e.g. ["Individual", ["V1", "V2"]].

        Returns:
            List: List of sample names.

        Examples:
            get_sample_list_for_group_list(group_list=['PBS', 'BAS'], condition=["Individual", "V1"])
            This will return a list of sample names for the groups 'PBS' and 'BAS' with only in "V1".
        """
        if group_list is None:
            print("group_list not provided, using all groups in meta_df.")
            group_list = self.meta_df[self.meta_name].unique().tolist()

        sample_list = []
        for group in group_list:
            sample_list += self.get_sample_list_in_a_group(group, condition)

        return sample_list

    # input a sample name, return the group name of this sample
    def get_group_of_a_sample(self, sample: str, meta_name:str|None='') -> str:
            """
            Returns the group of a given sample.

            Args:
                `sample (str)`: The name of the sample.
                `meta_name (str, optional)`: The name of the metadata column to retrieve. Defaults to ''.

            Returns:
                str: The group of the sample.

            Raises:
                ValueError: If the sample is not in the list of samples.

            """
            if self.group_list is None:
                print('group is not set, please set group first.')
                return None
            if sample not in self.sample_list:
                raise ValueError(f'sample must be in {set(self.sample_list)}, your input is [{sample}]')
            else:
                if meta_name != '':
                    return self.meta_df[self.meta_df['Sample'] == sample][meta_name].tolist()[0]
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

    def add_group_name_for_sample(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        '''
        Adds group names to sample names in the given DataFrame.

        Parameters:
        df (pd.DataFrame): The DataFrame containing the samples.

        Returns:
        tuple[pd.DataFrame, list[str]]: A tuple containing the modified DataFrame with updated sample names and a list of group names.

        Example:
        >>> df = pd.DataFrame({'Sample1': [1, 2, 3], 'Sample2': [4, 5, 6]})
        >>> analyzer = Analyzer()
        >>> modified_df, group_names = analyzer.add_group_name_for_sample(df)
        >>> modified_df
           Sample1 (Group1)  Sample2 (Group2)
        0                 1                 4
        1                 2                 5
        2                 3                 6
        >>> group_names
        ['Group1', 'Group2']
        '''
        sample_list = df.columns.tolist()

        new_sample_list = []
        new_group_list = []

        for i in sample_list:
            group = self.get_group_of_a_sample(i)
            new_sample_name = f'{i} ({group})'
            new_sample_list.append(new_sample_name)
            new_group_list.append(group)

        df.columns = new_sample_list
        return df, new_group_list


######### Data Preprocessing End #########

    def check_if_condition_valid(self, condition_meta: str, condition_group: str = None, current_group_list: list = None) -> bool:
        meta_df = self.meta_df.copy()

        # check if the condition is in meta_df
        if condition_meta not in meta_df.columns.tolist():
            raise ValueError(f'Condition [{condition_meta}] is not in meta_df, must be one of {meta_df.columns}')

        if current_group_list is None:
            current_group_list = meta_df[self.meta_name].unique()

        condition_group_list = meta_df[condition_meta].unique() # all groups in condition_meta

        if condition_group is None:
            for group in condition_group_list:
                sub_meta = meta_df[meta_df[condition_meta] == group]
                sub_group_list = sub_meta[self.meta_name].unique()
                # compare the current group list with the sub group list
                if not set(current_group_list).issubset(set(sub_group_list)):
                    raise ValueError(f'Current groups:\n{current_group_list}\nis not a subset of the groups in condition [{condition_meta}]:\n{sub_group_list}')
        else:
            sub_meta = meta_df[meta_df[condition_meta] == condition_group]
            sub_group_list = sub_meta[self.meta_name].unique()
            # compare the current group list with the sub group list
            if not set(current_group_list).issubset(set(sub_group_list)):
                raise ValueError(f'Current groups:\n{current_group_list}\nis not a subset of the groups in condition [{condition_group}]:\n{sub_group_list}')

        return True


######### Cross Test End #########
    def set_any_df_table(self,
                         outlier_params: dict = {'detect_method': None, 'handle_method': None,
                                                 "detection_by_group" : None, "handle_by_group": None},
                         data_preprocess_params: dict = {'normalize_method': None, 'transform_method': None,
                                                            'batch_meta': None, 'processing_order': None}):
        df = self.original_df.copy()
        df =self.detect_and_handle_outliers(df=df,  **outlier_params)
        df = self.data_preprocess(df=df,df_name = 'custom', **data_preprocess_params)
        # set index as first column
        self.processed_original_df = df
        df = df.set_index(df.columns[0])
        self.custom_df = df
        # create a df with 1 row for each other table
        # taxadf: Taxon, peptide_num, sample_list
        # d__bacteria, 1, 1, ...
        peptide_dict = {'Sequence': ['Not_Exist']}
        taxa_dict = {'Taxon': ['d__Bacteria'], 'peptide_num': [1]}
        func_dict = {self.func_name: ['Not_Exist'], 'peptide_num': [1]}

        taxa_func_dict = {'Taxon': ['d__Bacteria'], self.func_name: ['Not_Exist'], 'peptide_num': [1]}
        func_taxa_dict = {self.func_name: ['Not_Exist'], 'Taxon': ['d__Bacteria'], 'peptide_num': [1]}
        for i in self.sample_list:
            peptide_dict[i] = [1]
            taxa_dict[i] = [1]
            func_dict[i] = [1]
            taxa_func_dict[i] = [1]
            func_taxa_dict[i] = [1]

        self.peptide_df = pd.DataFrame(peptide_dict).set_index('Sequence')
        self.taxa_df = pd.DataFrame(taxa_dict).set_index('Taxon')
        self.func_df = pd.DataFrame(func_dict).set_index(self.func_name)
        self.taxa_func_df = pd.DataFrame(taxa_func_dict).set_index(['Taxon', self.func_name])
        self.func_taxa_df = pd.DataFrame(func_taxa_dict).set_index([self.func_name, 'Taxon'])

        self.taxa_func_linked_dict= {'d__Bacteria': [(self.func_name, 1)]}
        self.func_taxa_linked_dict= {self.func_name: [('d__Bacteria', 1)]}

        print("Custom df is set!\nWaiting for further analysis...")
    

    def split_func(self, df, split_func_params: dict = {'split_by': ',', 'share_intensity': False}, df_type: str = 'taxa_func'):
        """
        Splits the function column in the given DataFrame based on the specified parameters.
        Parameters:
        - df (DataFrame): The DataFrame containing taxa and function data.
        - split_func_params (dict): A dictionary of parameters for the split function.
            - split_by (str): The delimiter used to split the function column (default: ',').
            - share_intensity (bool): Whether to share the intensity values among the split functions (default: False).
        Returns:
        - new_data (DataFrame): The new DataFrame with the split function column.
        """
        
        split_by = split_func_params['split_by']
        share_intensity = split_func_params['share_intensity']
        df = df.copy()
        
        print(f'Start splitting function for {df_type} by [ {split_by} ], share_intensity={share_intensity}, it may take a while...')
        
        df = df.reset_index()
        func_col = self.func_name
        sample_list = self.sample_list
        taxon_col = 'Taxon' if df_type == 'taxa_func' else None
        
        # Prepare result storage
        result_rows = []

        for _, row in tqdm(df.iterrows(), total=len(df), desc="Splitting functions"):
            split_funcs_list = row[func_col].split(split_by)
            num_splits = len(split_funcs_list)
            
            for new_func in split_funcs_list:
                new_func = new_func.strip()
                split_row = row[sample_list] / num_splits if share_intensity else row[sample_list].copy()
                split_row[func_col] = new_func
                if taxon_col:
                    split_row[taxon_col] = row[taxon_col]
                
                # Use the peptide_num of the original row
                split_row['peptide_num'] = row['peptide_num']
                
                result_rows.append(split_row)

        # Create a new DataFrame
        new_data = pd.DataFrame(result_rows)
        
        # Group and sum based on the type of DataFrame
        groupby_cols = [func_col] if df_type == 'func' else [taxon_col, func_col]
        new_data = new_data.groupby(groupby_cols).sum(numeric_only=True)

        return new_data


    def create_peptides_dict_in_taxa_func(self, df):
        """
        Creates a dictionary of peptides in taxa, func, and taxa_func.
        Parameters:
            dfc (DataFrame): The input DataFrame containing the peptide, taxon, and function columns.
        Returns:
            self.peptides_linked_dict (dict): A dictionary containing the peptides in taxa, func, and taxa_func.
        """
        print("Creating peptides_linked_dict in taxa, func, and taxa_func...")
        df = df.copy()[[self.peptide_col_name, 'Taxon', self.func_name]]

        # Use defaultdict for automatic key initialization
        peptides_in_taxa_func = defaultdict(list)
        peptides_in_taxa = defaultdict(list)
        peptides_in_func = defaultdict(list)

        if self.split_func_status:
            for row in tqdm(df.itertuples(index=False), total=len(df), desc="Creating peptides_dict"):
                peptide = row[0] 
                taxa = row[1]
                func_list = [f.strip() for f in row[2].split(self.split_func_sep)]

                # Append peptide to taxa list
                peptides_in_taxa[taxa].append(peptide)

                # Process each function in the func_list
                for func in func_list:
                    peptides_in_func[func].append(peptide)
                    taxa_func = f'{taxa} <{func}>'
                    peptides_in_taxa_func[taxa_func].append(peptide)
        else:
            for row in tqdm(df.itertuples(index=False), total=len(df), desc="Creating peptides_dict"):
                peptide =row[0] 
                taxa = taxa = row[1]
                func = row[2]

                # Append peptide to taxa list
                peptides_in_taxa[taxa].append(peptide)

                # Append peptide to func list
                peptides_in_func[func].append(peptide)

                # Create combined key for taxa_func
                taxa_func = f'{taxa} <{func}>'
                peptides_in_taxa_func[taxa_func].append(peptide)

        self.peptides_linked_dict = {'taxa': peptides_in_taxa, 'func': peptides_in_func, 'taxa_func': peptides_in_taxa_func}
        return self.peptides_linked_dict


    def filter_peptides_by_taxa_func(self, df, func_threshold, keep_unknow_func, filter_taxa):
        """
        Filters the DataFrame based on functional and taxonomic criteria.

        Parameters:
        df (pd.DataFrame): The DataFrame of peptides, taxa, and functions.
        func_threshold (float): The threshold for the functional proportion.
        keep_unknow_func (bool): If True, keeps rows with 'unknown' functional names.
        filter_taxa (bool): If True, filters out rows with 'not_found' taxa.

        Returns:
        pd.DataFrame: The filtered DataFrame.
        """
        filter_conditions = (
            (df[f'{self.func_name}_prop'] >= func_threshold) &
            df[self.func_name].notnull() &
            (df[self.func_name] != 'not_found') &
            (df[self.func_name] != '-') &
            (df[self.func_name] != 'NaN') 
        )
        if not keep_unknow_func:
            filter_conditions = filter_conditions & (df[self.func_name] != 'unknown')
        if filter_taxa:
            filter_conditions = filter_conditions & (df['Taxon'] != 'not_found')
        return df[filter_conditions]
            
    def set_multi_tables(self, level: str = 's', func_threshold:float = 1.00,
                         outlier_params: dict = {'detect_method': None, 'handle_method': None,
                                                 "detection_by_group" : None, "handle_by_group": None},
                         data_preprocess_params: dict = {'normalize_method': None, 'transform_method': None,
                                                            'batch_meta': None, 'processing_order': None},
                          peptide_num_threshold: dict = {'taxa': 1, 'func': 1, 'taxa_func': 1},
                          sum_protein:bool = False, sum_protein_params: dict = {'method': 'razor',
                                                                                'by_sample': False,
                                                                                'rank_method': 'unique_counts',
                                                                                'greedy_method': 'heap',
                                                                                'peptide_mun_threshold': 1
                                                                                },
                          keep_unknow_func: bool = False, 
                          split_func: bool = False, split_func_params: dict = {'split_by': '|', 'share_intensity': False},
                          taxa_and_func_only_from_otf: bool = False):

        """
        Example Usage:
        sw.set_multi_tables(level='s', 
        outlier_params = {'detect_method': 'zero-dominant', 'handle_method': 'original',
                            "detection_by_group" : 'Individual', "handle_by_group": None},
        data_preprocess_params = {'normalize_method': None, 'transform_method': "log10",
                                'batch_meta': "Individual", 'processing_order': ['outlier', 'transform', 'normalize', 'batch']},
                            peptide_num_threshold = {'taxa': 3, 'func': 3, 'taxa_func': 3},
                            sum_protein = False, sum_protein_params = {'method': 'razor', 'by_sample': False, 
                                                                        'rank_method': 'unique_counts', 'greedy_method': 'heap',
                                                                        'peptide_num_threshold': 3},
                            keep_unknow_func = False)
        """
        print(f"Original data shape: {self.original_df.shape}")
        

        # for any_df_mode, the df is considered as other_df
        if self.any_df_mode:
            self.set_any_df_table(outlier_params=outlier_params, data_preprocess_params=data_preprocess_params)
            return

        #! fllowing code is for the normal mode
        # add 'peptide_num_threshold' to 'data_preprocess_params
        data_preprocess_params['peptide_num_threshold'] = peptide_num_threshold
        
        #2. sum the protein intensity
        if sum_protein:
            # data preprocess for peptide table
            print("---Starting to create protein table---")
            self.peptide_num_used['protein'] = 0
            df_peptide_for_protein = self.detect_and_handle_outliers(df=self.original_df, **outlier_params)
            self.protein_df = SumProteinIntensity(taxa_func_analyzer=self, df=df_peptide_for_protein).sum_protein_intensity( **sum_protein_params)
            self.protein_df = self.data_preprocess(df=self.protein_df,df_name = 'protein', 
                                                   **data_preprocess_params)
            
        for df_name in ['taxa', 'func', 'taxa_func']:
            self.peptide_num_used[df_name] = 0  # reset the peptide_num_used
            
        # reset split_func status
        self.split_func_status = split_func
        self.split_func_sep = split_func_params['split_by']
        
        

        #3. create taxa table
        print("Starting to set Taxa table...")
        # select taxa level and create dfc (df clean)
        def strip_taxa(x, level):
            '''
            Strip the taxa name to the selected level
            '''
            level_dict = {'m': 8 , 's': 7, 'g': 6, 'f': 5, 'o': 4, 'c': 3, 'p': 2, "d": 1, 'l': 1}
            return "|".join(x.split('|')[:level_dict[level]])

        level_mapping = {
            'm': ['genome'],
            's': ['species', 'genome'],
            'g': ['genus', 'species', 'genome'],
            'f': ['family', 'genus', 'species', 'genome'],
            'o': ['order', 'family', 'genus', 'species', 'genome'],
            'c': ['class', 'order', 'family', 'genus', 'species', 'genome'],
            'p': ['phylum', 'class', 'order', 'family', 'genus', 'species', 'genome'],
            'd': ['domain', 'phylum', 'class', 'order', 'family', 'genus', 'species', 'genome'],
            'l': ['life', 'domain', 'phylum', 'class', 'order', 'family', 'genus', 'species', 'genome']
        }
        # set the taxa level parameter, e.g. 'genome', 'species'... to other class can be used
        self.taxa_level = level_mapping[level][0]

        if level in level_mapping:
            df_t = self.original_df.loc[self.original_df['LCA_level'].isin(level_mapping[level])]
            level_sign = 'm' if self.genome_mode else 's'
            if level != level_sign:
                df_t.loc[:, 'Taxon'] = df_t['Taxon'].apply(lambda x: strip_taxa(x, level))

            # When seclected level is 's'
            # remove the cases like: "d__Bacteria|p__Bacteroidota|c__Bacteroidia|o__Bacteroidales|f__Bacteroidaceae|g__Bacteroides|s__|m__MGYG000001780"
            # the genome iws identified but the species name is empty like "s__"
            # So remove the taxon column with endswith "|s__" or other level
            print(f"Remove the peptides with '{level}__'in Taxon column...")
            orignial_taxa_num = df_t.shape[0]
            df_t = df_t[~df_t['Taxon'].str.endswith(f"{level}__")]
            new_taxa_num = df_t.shape[0]
            print(f"Rmoved: [{orignial_taxa_num - new_taxa_num}], Left: [{new_taxa_num}]")

            df_filtered_peptides = df_t
            # df_filtered_peptides is a df with all cols, which filtered by the selected taxa level
        else:
            raise ValueError("Please input the correct taxa level (m, s, g, f, o, c, p, d, l)")

        
        if not taxa_and_func_only_from_otf:
            # extract 'taxa', sample intensity #! and 'peptide_col' to avoid the duplicated items when handling outlier
            df_taxa_pep = df_filtered_peptides[[self.peptide_col_name,'Taxon'] + self.sample_list]
            # add column 'peptide_num' to df_taxa as 1
            df_taxa_pep['peptide_num'] = 1
            # groupby 'Taxon' and sum the sample intensity
            print("\n-----Starting to perform outlier detection and handling for [Peptide-Taxon] table...-----")
            df_taxa_pep = self.detect_and_handle_outliers(df=df_taxa_pep, **outlier_params)
            self.peptide_num_used['taxa'] = len(df_taxa_pep)
            df_taxa = df_taxa_pep.groupby('Taxon').sum(numeric_only=True)
            print("\n-----Starting to perform data pre-processing for Taxa table...-----")
            df_taxa = self.data_preprocess(df=df_taxa,df_name = 'taxa', **data_preprocess_params)
            self.taxa_df = df_taxa
            #-----Taxa Table End-----
            
            # create func table
            df_func_pep = self.filter_peptides_by_taxa_func(df= self.original_df, func_threshold=func_threshold,
                                       keep_unknow_func=keep_unknow_func, filter_taxa=False)
            df_func_pep = df_func_pep[[self.peptide_col_name, self.func_name] + self.sample_list]
            print("\n-----Starting to perform outlier detection and handling for [Peptide-Function] table...-----")
            df_func_pep = self.detect_and_handle_outliers(df=df_func_pep, **outlier_params)
            self.peptide_num_used['func'] = len(df_func_pep)
            df_func_pep['peptide_num'] = 1
            df_func = df_func_pep.groupby(self.func_name).sum(numeric_only=True)
            
            if split_func:
                df_func = self.split_func(df=df_func, split_func_params=split_func_params, df_type='func')
                
            df_func = self.data_preprocess(df=df_func,df_name = 'func', **data_preprocess_params)
            self.func_df = df_func
            #-----Func Table End-----

        #ELSE: build the df_taxa and df_fuun from df_taxa_func 
        #* df_filtered_peptides now is the peptides table with selected taxa level and filtered by func_threshold
        df_filtered_peptides = self.filter_peptides_by_taxa_func(df= df_filtered_peptides, func_threshold=func_threshold,
                                        keep_unknow_func=keep_unknow_func, filter_taxa=True)
        
        # do outlier detection and handling for the df_filtered_peptides table
        print("\n-----Starting to perform outlier detection and handling for [Peptide (filtered by taxa level and func_threshold)] table...-----")
        df_half_processed_peptides = self.detect_and_handle_outliers(df=df_filtered_peptides, **outlier_params)
        # the preprocessed_df is the peptide table filtered by taxa level and func_threshold, then do outlier detection and handling
        #------create peptides_dict in taxa, func and taxa_func------
        self.create_peptides_dict_in_taxa_func(df_half_processed_peptides)
        ###-----outlier hanlded peptide table End-----###
        
        #Create finalpeptide table
        # do rest of data preprocess, e.g. normalize, transform, batch effect correction
        print("\n-----Starting to perform transformation, normalization, and batch effect correction for [Peptide] table...-----")
        self.processed_original_df = self.data_preprocess(df=df_half_processed_peptides[[self.peptide_col_name, 'Taxon', self.func_name] + self.sample_list], 
                                                          df_name = 'peptide', **data_preprocess_params)
        # processed_original_df is the peptide table after selected taxa level, func_threshold, outlier detection and handling, then do the rest of data preprocess
        self.peptide_df = self.processed_original_df.drop(['Taxon', self.func_name], axis=1)
        self.peptide_df = self.peptide_df.set_index(self.peptide_col_name)
        ###------Peptide Table End------###
        


        # ----- create taxa_func table -----
        df_taxa_func = df_half_processed_peptides[[self.peptide_col_name, 'Taxon', self.func_name] + self.sample_list]
        df_taxa_func['peptide_num'] = 1
        
        for key in ['taxa_func', 'taxa', 'func']:
            self.peptide_num_used[key] = len(df_taxa_func) if self.peptide_num_used[key] == 0 else self.peptide_num_used[key]


        df_taxa_func = df_taxa_func.groupby(['Taxon', self.func_name], as_index=True).sum(numeric_only=True)
        
        # split the function before data preprocess
        if split_func:
            df_taxa_func = self.split_func( df=df_taxa_func, split_func_params=split_func_params, df_type='taxa_func')
            
        print("\n-----Starting to perform data pre-processing for [Taxa-Function] table...-----")
        df_taxa_func_all_processed = self.data_preprocess(df=df_taxa_func
                                                          ,df_name = 'taxa_func', **data_preprocess_params)
        self.taxa_func_df = df_taxa_func_all_processed
        # -----taxa_func table End-----
        
        # exchange the multi-index, sort the index
        self.func_taxa_df = df_taxa_func_all_processed.swaplevel().sort_index()
        # set the taxa_func_linked_dict and func_taxa_linked_dict
        self.set_taxa_func_linked_dict()
        # ----- func_taxa table End -----
        
        #----- create taxa and func table if not generate_taxa_and_func_before_filtering
        if taxa_and_func_only_from_otf:
            print("Starting to set Taxa table...")
            df_taxa = df_taxa_func.groupby('Taxon').sum(numeric_only=True)
            print("\n-----Starting to perform data pre-processing for [Taxa] table...-----")
            df_taxa = self.data_preprocess(df=df_taxa,df_name = 'taxa', **data_preprocess_params)
            self.taxa_df = df_taxa
            
            # ----- create func table -----
            print("Starting to set Function table...")
            df_func = df_taxa_func.groupby(self.func_name).sum(numeric_only=True)            
            print("\n-----Starting to perform data pre-processing for [Function] table...-----")
            df_func = self.data_preprocess(df=df_func,df_name = 'func', **data_preprocess_params)
            self.func_df = df_func
            # ----- func table End -----
            


        print("\n\nMulti-tables Created!\nWaiting for further analysis...")

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
        dft = self.processed_original_df[[self.peptide_col_name, "Taxon", self.func_name]]
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

    def get_df(self, table_name:str = 'taxa'):
        """
        Get the dataframe without peptide_num column

        ### Parameters:
        - table_name (str): The name of the table to retrieve. Valid options are:
            - `peptide` or `peptides`: Returns the peptide_df table.
            - `taxa`: Returns the taxa_df table.
            - `func` or `functions`: Returns the func_df table.
            - `taxa_func` or `taxa-functions`: Returns the taxa_func_df table.
            - `func_taxa`: Returns the func_taxa_df table.
            - `custom`: Returns the custom_df table.
            - `protein` or `proteins`: Returns the protein_df table.

        Returns:
        - `pandas.DataFrame`

        """
        name_dict = {
            "peptide": "peptide_df",
            "peptides": "peptide_df",
            "taxa": "taxa_df",
            "func": "func_df",
            "functions": "func_df",
            "taxa_func": "taxa_func_df",
            "func_taxa": "func_taxa_df",
            "custom": "custom_df",
            "taxa-functions": "taxa_func_df",
            "protein": "protein_df",
            "proteins": "protein_df",
            
        }
        table_name = table_name.lower()
        dft = getattr(self, name_dict[table_name])
        # remove peptide_num column if exists
        if "peptide_num" in dft.columns:
            dft = dft.drop(columns="peptide_num")
        
        if table_name in ['protein', 'proteins']:
            dft = dft.drop(columns='peptides')
            
        return dft


if __name__ == '__main__':
    import os
    current_path = os.path.dirname(os.path.abspath(__file__))
    df_path = '../data/example_data/Example_OTF.tsv'
    meta_path = '../data/example_data/Example_Meta.tsv'
    df_path = os.path.join(current_path, df_path)
    meta_path = os.path.join(current_path, meta_path)
    sw = TaxaFuncAnalyzer(df_path, meta_path)
    # sw.set_func('None')
    sw.set_func('KEGG_Pathway_name')
    sw.set_group('Individual')
    sw.set_multi_tables(level='l', 
                        outlier_params = {'detect_method': 'zero-dominant', 'handle_method': 'original',
                            "detection_by_group" : 'Individual', "handle_by_group": None},
                        data_preprocess_params = {
                                                'normalize_method': None, 
                                                'transform_method': "log2",
                                                'batch_meta': 'None', 
                                                'processing_order': None},
                    peptide_num_threshold = {'taxa': 2, 'func': 2, 'taxa_func': 2},
                    keep_unknow_func=False, sum_protein=True, 
                    sum_protein_params = {'method': 'razor', 'by_sample': False, 'rank_method': 'unique_counts', 'greedy_method': 'heap'},
                    split_func=True, split_func_params = {'split_by': '|', 'share_intensity': False},
                    taxa_and_func_only_from_otf=True
                    )

    sw.check_attributes()