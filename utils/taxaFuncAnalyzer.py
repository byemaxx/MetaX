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


from .reComBat import reComBat

import pandas as pd
import numpy as np
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy.stats import f_oneway
from scipy.stats import ttest_ind
from tqdm.auto import tqdm
from pydeseq2.ds import DeseqStats
from pydeseq2.dds import DeseqDataSet
from joblib import Parallel, delayed


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
        self.group_list = None
        self.group_dict = None

        self.func_list = None # all the func in the taxaFunc table which has _prop
        self.func_name = None

        self.clean_df = None
        self.peptide_df = None
        self.taxa_df = None
        self.func_df = None
        self.taxa_func_df = None
        self.func_taxa_df = None
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
        meta = pd.read_csv(meta_path, sep='\t')
        # sample name must be in the first column
        # rename the first column to Sample
        meta.rename(columns={meta.columns[0]: 'Sample'}, inplace=True)
        # replace space with _ and remove Intensity_
        meta['Sample'] = meta.iloc[:, 0].str.replace(
            ' ', '_').str.replace('Intensity_', '')
        meta = meta.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        self.sample_list = meta['Sample'].tolist()
        self.meta_df = meta
        
        if self.check_meta_match_df() is False:
            raise ValueError("The meta data does not match the TaxaFunc data, Please check!")
    
    def update_meta(self, meta_df: str) -> None:
        self.meta_df = meta_df
        old_sample_list = self.sample_list
        new_sample_list = meta_df['Sample'].tolist()
        # dorop the samples not in meta_df from original_df
        drop_list = list(set(old_sample_list) - set(new_sample_list))
        self.original_df = self.original_df.drop(drop_list, axis=1)
        self.sample_list = new_sample_list
        self._remove_all_zero_row()

    
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
        except Exception:
            return False
    
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

    # get a mean df by group
    def get_stats_mean_df_by_group(self, df: pd.DataFrame = None) -> pd.DataFrame:
        data = df.copy()
        group_means = pd.DataFrame()
        for group, samples in self.group_dict.items():
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
        return group_means

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
        df = df[ (df[func_name].notnull()) & (df[func_name] != 'unknown') & (df[func_name] != '-')]
        
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
        else:
            df_mat = df[self.sample_list]
            # check if there are negative values
            if (df_mat < 0).any().any():
                print('Warning: Negative values exist before data transformation.')
            # check if there are na
            if df_mat.isnull().any().any():
                print('Warning: NaN values exist before data transformation.')

            transform_operations = {
                'None': lambda x: x,
                'cube': np.cbrt,
                'log10': lambda x: np.log10(x + 1),
                'log2': lambda x: np.log2(x + 1),
                'sqrt': np.sqrt
            }

            if transform_method in transform_operations:
                df_mat = transform_operations[transform_method](df_mat)
                print(f'Data transformed by [{transform_method}]')
            else:
                raise ValueError('transform_method must be in [None, log2, log10, sqrt, cube]')

            df[self.sample_list] = df_mat

        return df
    
    def _data_normalization(self, df: pd.DataFrame, normalize_method: str = None) -> pd.DataFrame:
        if normalize_method is None:
            print('normalize_method is not set, data normalization did not perform.')
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

    
    # set outlier to nan
    def _outlier_detection(self, df: pd.DataFrame, method: str = None, by_group:str=None) -> pd.DataFrame:
        from scipy.stats import zscore
        from scipy.spatial import distance
        from scipy.stats import chi2
        from statsmodels.discrete.count_model import ZeroInflatedPoisson
        from statsmodels.discrete.discrete_model import NegativeBinomial
        from statsmodels.tools.tools import add_constant

        df = df.copy()
        
        def get_group_dict(by_group:str = None):
            if by_group is None:
                return self.group_dict
            elif by_group == 'All Samples':
                return  {'All Samples': self.sample_list}
            else:
                return self._get_group_dict_from_meta(by_group)
        
        

        print(f'\n{self._get_current_time()} Start to detect outlier...')

        if method is None or method == 'None':
            print('outlier_method is not set, outlier detection did not perform.')
            return df

        df_mat = df[self.sample_list]
        groups_dict = get_group_dict(by_group)
        print(f'\nRow number before outlier detection: [{len(df_mat)}]')

        if method == 'half-zero':
            print('Outlier detection by [half-zero] (if half samples are 0 or half samples are not 0, set to nan)...')


            for key, cols in groups_dict.items():
                nonzero_count = (df_mat[cols] > 0).sum(axis=1)
                total_count = len(cols)
                nonzero_ratio = nonzero_count / total_count

                normal_rows = nonzero_count.isin([0, total_count])
                abnormal_rows_gt_half = (nonzero_ratio > 0.5) & ~normal_rows
                abnormal_rows_lt_half = (nonzero_ratio < 0.5) & ~normal_rows
                equal_rows = nonzero_ratio == 0.5

                df_mat.loc[abnormal_rows_gt_half, cols] = df_mat.loc[abnormal_rows_gt_half, cols].where(df_mat.loc[abnormal_rows_gt_half, cols] > 0, np.nan)
                df_mat.loc[abnormal_rows_lt_half, cols] = df_mat.loc[abnormal_rows_lt_half, cols].where(df_mat.loc[abnormal_rows_lt_half, cols] <= 0, np.nan)
                df_mat.loc[equal_rows, cols] = np.nan

                print(f'Group: [{key}], Samples: [{total_count}], Normal: [{normal_rows.sum()}], Abnormal: [{(abnormal_rows_gt_half | abnormal_rows_lt_half | equal_rows).sum()}],'
                    f'(Non-zero > 0.5: [{abnormal_rows_gt_half.sum()}], '
                    f'Zero > 0.5: [{abnormal_rows_lt_half.sum()}], '
                    f'Equal: [{equal_rows.sum()}]) Total Abnormal Ratio: [{((abnormal_rows_gt_half | abnormal_rows_lt_half | equal_rows).sum())/len(df_mat)*100:.2f}%]')

        elif method == 'zero-dominant':
            print('Outlier detection by [zero-dominant] (if half or more half samples are 0, set to nan)...')

            for key, cols in groups_dict.items():
                nonzero_count = (df_mat[cols] > 0).sum(axis=1)
                total_count = len(cols)
                nonzero_ratio = nonzero_count / total_count

                normal_rows = nonzero_count.isin([0, total_count])
                abnormal_rows_lt_half = (nonzero_ratio <= 0.5) & ~normal_rows

                df_mat.loc[abnormal_rows_lt_half, cols] = df_mat.loc[abnormal_rows_lt_half, cols].where(df_mat.loc[abnormal_rows_lt_half, cols] <= 0, np.nan)

                print(f'Group: [{key}], Samples: [{total_count}], Normal: [{normal_rows.sum()}], Abnormal: [{abnormal_rows_lt_half.sum()}], '
                    f'Zero > 0.5: [{abnormal_rows_lt_half.sum()}], Total Abnormal Ratio: [{abnormal_rows_lt_half.sum()/len(df_mat)*100:.2f}%]')



        elif method == "iqr":
            print('Outlier detection by [IQR] (if sample is out of 1.5*IQR, set to nan)...') 
            # calculate the IQR of each group
            for group, cols in groups_dict.items():
                q1 = df_mat[cols].quantile(0.25)
                q3 = df_mat[cols].quantile(0.75)
                iqr = q3 - q1
                outlier = (df_mat[cols] < (q1 - 1.5 * iqr)) | (df_mat[cols] > (q3 + 1.5 * iqr))
                # set the outlier to nan
                df_mat.loc[outlier.any(axis=1), cols] = np.nan
                print(f'Group: [{group}], Samples: [{len(cols)}], Outlier: [{outlier.any(axis=1).sum()} in {len(df_mat)} ({outlier.any(axis=1).sum()/len(df_mat)*100:.2f}%)]')
        elif method =='z-score':
            print('Outlier detection by [z-score] (if samples in a group are out of 3*std, set to nan)...')
            for group, cols in groups_dict.items():
                z = np.abs(zscore(df_mat[cols]))
                df_mat.loc[(z > 2.5).any(axis=1), cols] = np.nan
                print(f'Group: [{group}], Samples: [{len(cols)}], Outlier: [{(z > 3).any(axis=1).sum()} in {len(df_mat)} ({(z > 3).any(axis=1).sum()/len(df_mat)*100:.2f}%)]')

        elif method in {'zero-inflated-poisson', 'negative-binomial'}:
            print(f'Outlier detection by [{method}] (if the predicted value is less than 0.01, set to nan)...')
            for group, cols in groups_dict.items():
                # Concatenate all columns in the group into a single column
                data = df_mat[cols].values.flatten()
                data_const = add_constant(data)
                model = ZeroInflatedPoisson(endog=data, exog=data_const).fit() if method == 'zero-inflated-poisson' else NegativeBinomial(endog=data, exog=data_const).fit()
                # calculate the predicted value
                pred_prob = model.predict(data_const)

                # reshape pred_prob to match the original data shape
                pred_prob = pred_prob.reshape(-1, len(cols))

                # mark the outlier as nan
                for i, col in enumerate(cols):
                    df_mat.loc[pred_prob[:, i] < 0.01, col] = np.nan
                print(f'Group: [{group}], Outlier: [{(pred_prob < 0.01).sum()} in {len(data)} ({(pred_prob < 0.01).sum()/len(data)*100:.2f}%)]')

        elif method == 'mahalanobis-distance':
        #Compute the Mahalanobis Distance for each group
            print('Outlier detection by [mahalanobis] (if the Mahalanobis Distance is greater than the threshold(0.01), set to nan)...')
            for group, cols in groups_dict.items():
                # Get the data for this group
                data = df_mat[cols]

                # Compute the mean and covariance matrix
                mean = data.mean()
                cov = data.cov()
                inv_cov = np.linalg.inv(cov)

                # Compute the Mahalanobis distance for each data point
                mahalanobis_dist = data.apply(lambda x: distance.mahalanobis(x, mean, inv_cov), axis=1)

                # Compute the threshold for outlier detection (assuming a chi-square distribution)
                threshold = chi2.ppf((1-0.01), df=len(cols))  # 99% confidence

                # Mark the outliers as nan
                outliers = mahalanobis_dist > threshold
                df_mat.loc[outliers, cols] = np.nan

                print(f'Group: [{group}], Outlier: [{outliers.sum()} in {len(df_mat)} ({outliers.sum()/len(df_mat)*100:.2f}%)]')            


        else:
            raise ValueError(f'Invalid outlier method: {method}')

        df[self.sample_list] = df_mat
        # statistics the number
        num_row_with_outlier = df_mat.isnull().any(axis=1).sum()
        num_col_with_outlier = df_mat.isnull().any(axis=0).sum()
        num_nan = df_mat.isnull().sum().sum()
        print(f'\n[{num_nan}] values are set to NaN. in [{num_row_with_outlier}] rows and [{num_col_with_outlier}] columns.')

        print('\nRemove rows only contain NaN or 0 after outlier detection...')
        row_num_before = len(df)
        # remove rows in  df[self.sample_list] with all nan and all 0
        df = df[(df[self.sample_list] > 0).any(axis=1)]
        row_num_after = len(df)
        num_row_with_outlier_after = df[self.sample_list].isnull().any(axis=1).sum()
        print(f'Row Number: from [{row_num_before}] to [{row_num_after}] ({(row_num_after)/row_num_before*100:.2f}% left)')
        # print the number of row with nan
        if num_row_with_outlier_after > 0:
            print(f'The Number of rows still with nan: [{num_row_with_outlier_after}] in [{row_num_after}] ({num_row_with_outlier_after/row_num_after*100:.2f}%)')

        print(f'\n{self._get_current_time()} Outlier detection finished.\n')
        return df

    

    def _handle_missing_value(self, df: pd.DataFrame, method: str = 'drop+drop', by_group:str = None,df_original: pd.DataFrame = None) -> pd.DataFrame:
        from sklearn.experimental import enable_iterative_imputer
        from sklearn.impute import KNNImputer, IterativeImputer

        df = df.copy()
        
        def get_group_dict(by_group:str = None):
            if by_group is None:
                return self.group_dict
            elif by_group == 'All Samples':
                return  {'All Samples': self.sample_list}
            else:
                return self._get_group_dict_from_meta(by_group)
    
        print(f'\n{self._get_current_time()} Start to handle missing value...\n')

        df_mat = df[self.sample_list]
        df_mat.index = df.index

        if not df_mat.isnull().any().any():
            print('No missing value, skip outlier handling')
            return df

        method_list = method.split("+")
        method1, method2 = method_list[0], method_list[0] if len(method_list) == 1 else method_list[1]
        
        def fill_na_mean_median(args):
            df_group, fill_method = args
            df_group = df_group.copy()
            fill_func = lambda x: x.mean() if fill_method == 'mean' else x.median()

            # Only process rows with missing values
            missing_rows = df_group.isnull().any(axis=1)
            df_group.loc[missing_rows] = df_group[missing_rows].apply(lambda row: row.fillna(fill_func(row.dropna())), axis=1)

            return df_group

        def apply_imputer(df, cols, method):
            df_group = df.loc[:, cols].copy()
            if method == 'knn':
                imputer = KNNImputer(n_neighbors=5)
            elif method in {'regression', 'multiple'}:
                # make the results don't have negative values by setting min_value=0
                imputer = IterativeImputer(random_state=0 if method == 'multiple' else None, min_value=0)
            df_group.loc[:, cols] = imputer.fit_transform(df_group)
            return df_group

        def impute_method(df, method, by_group):
            df_mat = df[self.sample_list]
            # df_mat.index = df.index
            print(f'Fill NA by [{method}]...')
            # count the rows with missing value
            num_rows_with_missing_value = df_mat.isnull().any(axis=1).sum()
            print(f'Number of rows with NA before [{method}]: [{num_rows_with_missing_value} in {len(df_mat)} ({num_rows_with_missing_value/len(df_mat)*100:.2f}%)]')

            if method in {'knn', 'regression', 'multiple'}:
                if by_group == 'All Samples':
                    print(f'Fill NA by [{method}] on the [All Samples]...')
                    if method == 'knn':
                        imputer = KNNImputer(n_neighbors=5)
                    elif method in {'regression', 'multiple'}:
                        imputer = IterativeImputer(random_state=0 if method == 'multiple' else None)
                    df[self.sample_list] = pd.DataFrame(imputer.fit_transform(df_mat), columns=df_mat.columns, index=df.index)
                else: # by_group is True
                    group_dict = get_group_dict(by_group)
                    print(f'Fill NA by [{method}] within [{len(group_dict)}] groups...')
                    results = Parallel(n_jobs=-1)(delayed(apply_imputer)(df_mat, cols, method) for _, cols in group_dict.items())
                    df_mat_filled = pd.concat(results, axis=1)
                    df_mat_filled = df_mat_filled[df_mat.columns]
                    df[self.sample_list] = df_mat_filled

            elif method in {'mean', 'median'}:
                if by_group == 'All Samples':
                    print(f'Fill NA by [{method}] on the [All Samples]...')
                    df[self.sample_list] = df_mat.apply(lambda x: x.fillna(x.mean() if method == 'mean' else x.median()), axis=1)
                else:
                    group_dict = get_group_dict(by_group)
                    print(f'Fill NA by [{method}] within [{len(group_dict)}] groups...')
                    results = Parallel(n_jobs=-1)(
                        delayed(fill_na_mean_median)([df_mat.loc[:, cols], method]) 
                        for _, cols in group_dict.items()
                    )
                    # Ensure the order of results is the same as the original column order
                    df_mat_filled = pd.concat(results, axis=1)
                    df_mat_filled = df_mat_filled[df_mat.columns]
                    df[self.sample_list] = df_mat_filled
            
            elif method == 'original':
                print(f'Fill NA by {method}, keep the original data...')
                df = df_original[df_original.iloc[:, 0].isin(df.iloc[:, 0])]

            elif method == 'drop':
                print('NO HANDLING FOR MISSING VALUE, DROP ROWS WITH MISSING VALUE')
                df = df.dropna(subset=self.sample_list)
            else:
                raise ValueError(f'Invalid method: {method}')


            final_na_num = df[self.sample_list].isnull().any(axis=1).sum()
            if final_na_num > 0:
                print(f'There are still missing value in the data: [{final_na_num} in {len(df)} ({final_na_num/len(df)*100:.2f}%)]')
            else:
                print(f'No missing value after [{method}]')
            return df

        ### main function ###
        if method1 == 'drop':
            df = df.dropna(subset=self.sample_list)
        else:
            df = impute_method(df, method1, by_group)

        if df[self.sample_list].isnull().any().any():
            if method2 == 'drop':
                df = df.dropna(subset=self.sample_list)
            elif method1 != method2:
                print(f'\n\nFill NA by [{method2}] to handle the remaining missing value...')
                df = impute_method(df, method2,by_group)
        # still have missing value
        final_na_num = df[self.sample_list].isnull().any(axis=1).sum()
        if final_na_num > 0:
            print(f'Drop rows with missing value after [{method}]: [{final_na_num} in {len(df)} ({final_na_num/len(df)*100:.2f}%)]')
            df = df.dropna(subset=self.sample_list)
        print(f'Final number of rows after missing value handling: [{len(df)}]')
        print(f'\n{self._get_current_time()} Data processing finished.\n')

        return df




    def _handle_outlier(self, df: pd.DataFrame, detect_method: str = 'none',handle_method: str = 'drop+drop', detection_by_group:str=None, handling_by_group:str=None) -> pd.DataFrame:
        if self.group_list is None:
            raise ValueError('You must set set group before handling outlier')

        df_t = self._outlier_detection(df, method=detect_method, by_group=detection_by_group)
        df_t = self._handle_missing_value(df_t, method=handle_method, by_group=handling_by_group, df_original=df)

        return df_t

           

    def _data_preprocess(self, df: pd.DataFrame, normalize_method: str = None, 
                         transform_method: str = None, batch_list: list = None, 
                         outlier_detect_method: str = None, outlier_handle_method: str = None,
                         outlier_detect_by_group: str = None, outlier_handle_by_group: str = None, processing_order:list=None,
                         df_name:str=None) -> pd.DataFrame:
        df = df.copy()
        original_row_num = len(df)
        if processing_order is None:
            processing_order = ['outlier' ,'batch', 'transform', 'normalize']
        else:
            processing_order = processing_order
        # perform data processing in order
        for process in processing_order:
            if process == 'outlier':
                df = self._handle_outlier(df, detect_method=outlier_detect_method, handle_method=outlier_handle_method, detection_by_group = outlier_detect_by_group, handling_by_group=outlier_handle_by_group)
            elif process == 'batch':
                df = self._remove_batch_effect(df, batch_list)
            elif process == 'transform':
                df = self._data_transform(df, transform_method)
            elif process == 'normalize':
                df = self._data_normalization(df, normalize_method)
            else:
                raise ValueError('processing_order must be in [outlier, batch, transform, normalize]')
        print(f'\n{self._get_current_time()} -----Data preprocessing finished.-----\n')

        if df_name in {'peptide', 'taxa', 'func', 'taxa_func'}:
            left_row_num = len(df)
            self.outlier_status[df_name] = f'{left_row_num}/{original_row_num} ({left_row_num/original_row_num*100:.2f}%)'

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

        if df_type in ['taxa-func', 'func-taxa', 'taxa', 'func', 'peptide']:
            if df_type == 'taxa-func':
                df, primary, secondary = self.taxa_func_df, 'Taxon', self.func_name
            elif df_type == 'func-taxa':
                df, primary, secondary = self.func_taxa_df, self.func_name, 'Taxon'
            elif df_type == 'taxa':
                df, primary = self.taxa_df, 'Taxon'
            elif df_type == 'func':
                df, primary = self.func_df, self.func_name
            elif df_type == 'peptide':
                df, primary = self.peptide_df, 'Sequence'

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
        
    def get_stats_ttest(self, group_list: list = None, df_type: str = 'taxa-func') -> pd.DataFrame:

        group_list_all = sorted(set(self.get_meta_list(self.meta_name)))

        if group_list is None:
            group_list = group_list_all
        elif any(i not in group_list_all for i in group_list):
            raise ValueError(f"groups must be in {group_list_all}")
        if len(group_list) != 2:
            raise ValueError("groups must be 2")

        all_sample_list = [sample for group in group_list for sample in self.get_sample_list_in_a_group(group)]

        if df_type == 'taxa-func':
            df, primary, secondary = self.taxa_func_df, 'Taxon', self.func_name
        elif df_type == 'func-taxa':
            df, primary, secondary = self.func_taxa_df, self.func_name, 'Taxon'
        elif df_type == 'taxa':
            df, primary = self.taxa_df, 'Taxon'
        elif df_type == 'func':
            df, primary = self.func_df, self.func_name
        elif df_type == 'peptide':
            df, primary = self.peptide_df, 'Sequence'
        else:
            raise ValueError("df_type must be in ['taxa-func', 'func-taxa', 'taxa', 'func', 'peptide']")

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
    
    def get_intensity_matrix(self, func_name: str = None, taxon_name: str = None,
                             peptide_seq: str = None, sample_list: list = None) -> pd.DataFrame:
    # input: a taxon with its function, a function with its taxon,
    # and the peptides in the function or taxon
    # output: a matrix of the intensity of the taxon or function or peptide in each sample

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
        if sample_list is None:
            sample_list = self.sample_list
        elif any(i not in self.sample_list for i in sample_list):
            raise ValueError(
                f"sample_list must be in {self.sample_list}")
        # if groups is not None:
        #     group_list_all = self.group_list
        #     if any(i not in group_list_all for i in groups):
        #         raise ValueError(f"groups must be in {group_list_all}")
        #     groups = sorted(groups)
        #     sample_list = []
        #     for i in groups:
        #         sample_list += self.get_sample_list_in_a_group(i)
        # else:
        #     groups = self.group_list
        #     sample_list = self.sample_list

        # Get the intensity matrix of the samples
        dft = dft[sample_list]
        return dft

    
        # df = get_top_intensity(sw.taxa_df, top_num=50, method='freq')
    def get_top_intensity(self, df, top_num: int = 10, method: str = 'mean', sample_list: list = None):

        df = df[sample_list].copy() if sample_list else df.copy()
        df = self.replace_if_two_index(df)

        if method == 'freq':
            df['value'] = df.astype(bool).sum(axis=1)
        elif method == 'mean':
            df['value'] = df.mean(axis=1)
        elif method == 'sum':
            df['value'] = df.sum(axis=1)
            
        df = df.sort_values(by='value', ascending=False)
        df = df[:top_num].drop('value', axis=1)
        return df
    
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
    
    # input: df, df_type, top_num, show_stats_col
    # output: df
    # df_type: 'anova' or 'ttest' or 'log2fc'
    def get_top_intensity_matrix_of_test_res(self, df, df_type: str = None, top_num: int = 100, show_stats_cols: bool = False):

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

        dft = self.replace_if_two_index(dft)

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


        sample_list = []
        for i in group_list:
            sample = self.get_sample_list_in_a_group(i)
            sample_list += sample

        # Create intensity matrix
        df = df.copy()
        df = df[sample_list]
        df = self.replace_if_two_index(df)
        
        counts_df = df.T
        # make sure the max value is not larger than int32
        max_value = 2147483647
        if counts_df.max().max() > max_value:
            times = counts_df.max().max() / max_value
            divide = int(times) + 1
            counts_df = counts_df / divide
            print(f'Warning: the max value is [{counts_df.max().max()}], [{times}] times larger than int32, all values are divided by [{divide}]')
        else:
            print(f'The max value is [{counts_df.max().max()}], not larger than int32, no need to divide')
              
        counts_df = counts_df.astype(int)
        counts_df = counts_df.sort_index()


        # Create meta data
        meta_df = self.meta_df.copy()
        meta_df = meta_df[meta_df['Sample'].isin(sample_list)]

        meta_df.set_index('Sample', inplace=True)
        
        # ! Deseq2 would make mistake if the meta name and sample contain '_'
        # ! replace '_' with '-' in meta_df
        meta_df = meta_df.replace('_', '-', regex=True)
        columns = meta_df.columns
        meta_df.columns = [i.replace('_', '-') for i in columns]
        
        meta_df = meta_df.sort_index()
        

        dds = DeseqDataSet(
            counts=counts_df,
            metadata=meta_df,
            design_factors=self.meta_name.replace('_', '-'), # ! replace '_' with '-' in meta_name
            refit_cooks=True)
        dds.deseq2()
        
        try:
            stat_res = DeseqStats(dds, alpha=0.05, cooks_filter=True, independent_filter=True)
            stat_res.summary()
        except KeyError as e:
            if 'cooks' in str(e):
                print('cooks_filter is not available, use cooks_filter=False')
                stat_res = DeseqStats(dds, alpha=0.05, cooks_filter=False, independent_filter=True)
                stat_res.summary()
            else:
                raise e
        except Exception as e:
            raise e

        res = stat_res.results_df
        res_merged = pd.merge(res, df, left_index=True, right_index=True)


        # check order
        res_group = stat_res.LFC.columns[1]
        res_group_2 = stat_res.LFC.columns[1].split('_vs_')[1]
        input_group_2 = group_list[1].replace('_', '-')
        print(f'res_group_2: {res_group_2}')
        print(f'input_group_2: {input_group_2}')
        if res_group_2 == input_group_2:
            print(f'Res group order [{res_group}] is correct, keep original log2FoldChange values')
        else:
            res_merged["log2FoldChange"] = -res_merged["log2FoldChange"]
            print(f'Res group order [{res_group}] is incorrect, reverse log2FoldChange values')
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
            df = self._data_preprocess(df=df,df_name = 'peptide', **args_data_preprocess)
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
            df_func = self._data_preprocess(df=df_func,df_name = 'func', **args_data_preprocess)
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
            df_taxa = self._data_preprocess(df=df_taxa,df_name = 'taxa', **args_data_preprocess)
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
            dfc_processed = self._data_preprocess(df=dfc, df_name = 'peptide',**args_data_preprocess)
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
            df_taxa_func = self._data_preprocess(df=df_taxa_func,df_name = 'taxa_func', **args_data_preprocess)

        # df_func_taxa = dfc.groupby([func_name, 'Taxon'], as_index=True).sum(numeric_only=True)
        df_func_taxa = df_taxa_func.swaplevel().sort_index()


        print(f"Taxa-Function number: {df_taxa_func.shape[0]}")

        self.taxa_df = df_taxa
        self.func_df = df_func
        self.taxa_func_df = df_taxa_func
        self.func_taxa_df = df_func_taxa
        self.clean_df = dfc_with_peptides
        self.peptide_df = df_peptide
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
    
    def _get_current_time(self):
        import time
        return time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())