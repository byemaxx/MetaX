import pandas as pd
from .reComBat import reComBat
import numpy as np
from joblib import Parallel, delayed



class DataPreprocessing:
    """
    A class for preprocessing data including batch effect removal, data transformation, normalization, and outlier handling.

    `Attributes`:
        - tfa (object): An object containing metadata and sample list information.

    `Methods`:
       -  _data_preprocess(df, normalize_method=None, transform_method=None, batch_meta=None, outlier_detect_method=None, outlier_handle_method=None, outlier_detect_by_group=None, outlier_handle_by_group=None, processing_order=None, df_name=None)

    """


    def __init__(self, tfa):
        self.tfa = tfa
        
        
    # data pre-processing for multi-tables
    def _remove_batch_effect(self, df: pd.DataFrame= None, batch_meta: str =None) -> pd.DataFrame:
        df = df.copy()
        #check if len df is less than 2
        if len(df) < 2:
            print('ATTENTION: df has less than 2 rows, Batch effect removal did not perform.')
            return df
        if df is not None and batch_meta is not None and batch_meta != 'None':
            print(f'Remove batch effect by [{batch_meta}]...')
            batch_list = self.tfa.meta_df[batch_meta].tolist()
            df_samples = df[self.tfa.sample_list]
            df_samples += 1

            # display(df_samples.head())

            batch  = pd.Series(index=df_samples.columns, data=batch_list)
            # display(batch.head())
            # print(Counter(batch))

            combat = reComBat()
            df_corrected = combat.fit_transform(df_samples.T, batch).T

            df_corrected = np.where(df_corrected < 2, 0, df_corrected)
            df[self.tfa.sample_list] = df_corrected

        elif batch_meta is None or batch_meta == 'None':
            print('batch_meta is not set, Batch effect removal did not perform.')
        else:
            print('df and batch_meta are not set, Batch effect removal did not perform.')
        return df
            
    
    def _data_transform(self, df: pd.DataFrame, transform_method: str = None) -> pd.DataFrame:
        if transform_method is None:
            print('transform_method is not set, data transform did not perform.')
        else:
            df_mat = df[self.tfa.sample_list]
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

            df[self.tfa.sample_list] = df_mat

        return df
    
    def _data_normalization(self, df: pd.DataFrame, normalize_method: str = None) -> pd.DataFrame:
        if normalize_method is None:
            print('normalize_method is not set, data normalization did not perform.')
        else:
            df = df.copy()
            df_mat = df[self.tfa.sample_list]

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
                print(f'Data normalized by [{normalize_method}]')
            else:
                raise ValueError('normalize_method must be in [None, mean, sum, minmax, zscore]')

            # shift values by their absolute minimum to ensure all values are non-negative
            df_mat = df_mat - df_mat.min()

            df[self.tfa.sample_list] = df_mat

        return df

    def get_group_dict(self, by_group:str = None):
        if by_group is None:
            if self.tfa.group_list is None:
                raise ValueError('You must set set group before handling outlier if you do not set by_group')
            return self.tfa.group_dict
        elif by_group == 'All Samples':
            return  {'All Samples': self.tfa.sample_list}
        else:
            return self.tfa._get_group_dict_from_meta(by_group)
    
    # set outlier to nan
    def _outlier_detection(self, df: pd.DataFrame, method: str = None, by_group:str=None) -> pd.DataFrame:
        from scipy.stats import zscore
        from scipy.spatial import distance
        from scipy.stats import chi2
        from statsmodels.discrete.count_model import ZeroInflatedPoisson
        from statsmodels.discrete.discrete_model import NegativeBinomial
        from statsmodels.tools.tools import add_constant

        df = df.copy()
        
        
        

        print(f'\n{self._get_current_time()} Start to detect outlier...')

        if method is None or method in['None', 'missing-value', 'none']:
            print('outlier_method is not set, outlier detection did not perform.')
            return df

        df_mat = df[self.tfa.sample_list]
        groups_dict = self.get_group_dict(by_group)
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
            raise ValueError(f'Invalid outlier method: {method}\nMust be in [none, missing-value, half-zero, zero-dominant, iqr, z-score, zero-inflated-poisson, negative-binomial, mahalanobis-distance]')

        df[self.tfa.sample_list] = df_mat
        # statistics the number
        num_row_with_outlier = df_mat.isnull().any(axis=1).sum()
        num_col_with_outlier = df_mat.isnull().any(axis=0).sum()
        num_nan = df_mat.isnull().sum().sum()
        print(f'\n[{num_nan}] values are set to NaN. in [{num_row_with_outlier}] rows and [{num_col_with_outlier}] columns.')

        print('\nRemove rows only contain NaN or 0 after outlier detection...')
        row_num_before = len(df)
        # remove rows in  df[self.tfa.sample_list] with all nan and all 0
        df = df[(df[self.tfa.sample_list] > 0).any(axis=1)]
        row_num_after = len(df)
        num_row_with_outlier_after = df[self.tfa.sample_list].isnull().any(axis=1).sum()
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
        
    
        print(f'\n{self._get_current_time()} Start to handle missing value...\n')

        df_mat = df[self.tfa.sample_list]
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
            df_mat = df[self.tfa.sample_list]
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
                    df[self.tfa.sample_list] = pd.DataFrame(imputer.fit_transform(df_mat), columns=df_mat.columns, index=df.index)
                else: # by_group is True
                    group_dict = self.get_group_dict(by_group)
                    print(f'Fill NA by [{method}] within [{len(group_dict)}] groups...')
                    results = Parallel(n_jobs=-1)(delayed(apply_imputer)(df_mat, cols, method) for _, cols in group_dict.items())
                    df_mat_filled = pd.concat(results, axis=1)
                    df_mat_filled = df_mat_filled[df_mat.columns]
                    df[self.tfa.sample_list] = df_mat_filled

            elif method in {'mean', 'median'}:
                if by_group == 'All Samples':
                    print(f'Fill NA by [{method}] on the [All Samples]...')
                    df[self.tfa.sample_list] = df_mat.apply(lambda x: x.fillna(x.mean() if method == 'mean' else x.median()), axis=1)
                else:
                    group_dict = self.get_group_dict(by_group)
                    print(f'Fill NA by [{method}] within [{len(group_dict)}] groups...')
                    results = Parallel(n_jobs=-1)(
                        delayed(fill_na_mean_median)([df_mat.loc[:, cols], method]) 
                        for _, cols in group_dict.items()
                    )
                    # Ensure the order of results is the same as the original column order
                    df_mat_filled = pd.concat(results, axis=1)
                    df_mat_filled = df_mat_filled[df_mat.columns]
                    df[self.tfa.sample_list] = df_mat_filled
            
            elif method == 'original':
                print(f'Fill NA by {method}, keep the original data...')
                df = df_original[df_original.iloc[:, 0].isin(df.iloc[:, 0])]

            elif method == 'drop':
                print('NO HANDLING FOR MISSING VALUE, DROP ROWS WITH MISSING VALUE')
                df = df.dropna(subset=self.tfa.sample_list)
            else:
                raise ValueError(f'Invalid method: {method}')


            final_na_num = df[self.tfa.sample_list].isnull().any(axis=1).sum()
            if final_na_num > 0:
                print(f'There are still missing value in the data: [{final_na_num} in {len(df)} ({final_na_num/len(df)*100:.2f}%)]')
            else:
                print(f'No missing value after [{method}]')
            return df

        ### main function ###
        if method1 == 'drop':
            df = df.dropna(subset=self.tfa.sample_list)
        else:
            df = impute_method(df, method1, by_group)

        if df[self.tfa.sample_list].isnull().any().any():
            if method2 == 'drop':
                df = df.dropna(subset=self.tfa.sample_list)
            elif method1 != method2:
                print(f'\n\nFill NA by [{method2}] to handle the remaining missing value...')
                df = impute_method(df, method2,by_group)
        # still have missing value
        final_na_num = df[self.tfa.sample_list].isnull().any(axis=1).sum()
        if final_na_num > 0:
            print(f'Drop rows with missing value after [{method}]: [{final_na_num} in {len(df)} ({final_na_num/len(df)*100:.2f}%)]')
            df = df.dropna(subset=self.tfa.sample_list)
        print(f'Final number of rows after missing value handling: [{len(df)}]')
        print(f'\n{self._get_current_time()} Data processing finished.\n')

        return df




    def _handle_outlier(self, df: pd.DataFrame, detect_method: str = 'none',handle_method: str = 'drop+drop', detection_by_group:str=None, handling_by_group:str=None) -> pd.DataFrame:
        # if self.tfa.group_list is None:
        #     raise ValueError('You must set set group before handling outlier')

        df_t = self._outlier_detection(df, method=detect_method, by_group=detection_by_group)
        df_t = self._handle_missing_value(df_t, method=handle_method, by_group=handling_by_group, df_original=df)

        return df_t

    def _get_current_time(self):
        import time
        return time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())

    def _data_preprocess(self, df: pd.DataFrame, normalize_method: str = None, 
                         transform_method: str = None, batch_meta: str =None,
                         outlier_detect_method: str = None, outlier_handle_method: str = None,
                         outlier_detect_by_group: str = None, outlier_handle_by_group: str = None, processing_order:list=None,
                         df_name:str=None) -> pd.DataFrame:
        """
        ## `_data_preprocess` Method

        Processes the given DataFrame by applying normalization, transformation, batch effect removal, and outlier handling in a specified order.

        ### Parameters:

        - `df` (`pd.DataFrame`):  
        The DataFrame to be processed.

        - `normalize_method` (`str`, optional):  
        Method used for data normalization. Options include:
            - `None`: No normalization.
            - `mean`: Mean normalization.
            - `sum`: Sum normalization.
            - `minmax`: Min-max normalization.
            - `zscore`: Z-score normalization.
            - `pareto`: Pareto scaling.

        - `transform_method` (`str`, optional):  
        Method used for data transformation. Options include:
            - `None`: No transformation.
            - `log10`: Log10 transformation.
            - `log2`: Log2 transformation.
            - `sqrt`: Square root transformation.
            - `cube`: Cube root transformation.

        - `batch_meta` (`str`, optional):  
        Column name for batch metadata, used for batch effect removal.

        - `outlier_detect_method` (`str`, optional):  
        Method for outlier detection. Options include:
            - `none`: No outlier detection.
            - `missing-value`: Detect missing values.
            - `half-zero`: Detect outliers based on half-zero criteria.
            - `zero-dominant`: Detect outliers based on zero-dominance.
            - `iqr`: Interquartile range method.
            - `z-score`: Z-score method.
            - `zero-inflated-poisson`: Zero-inflated Poisson distribution method.
            - `negative-binomial`: Negative binomial distribution method.
            - `mahalanobis-distance`: Mahalanobis distance method.

        - `outlier_handle_method` (`str`, optional):  
        Method for handling outliers, specified as methods separated by +. Options include:
            - `drop`: Drop rows with outliers.
            - `mean`: Fill with mean.
            - `median`: Fill with median.
            - `knn`: K-nearest neighbors imputation.
            - `regression`: Regression imputation.
            - `multiple`: Multiple imputation.
            - `original`: Keep original data unchanged.

        - `outlier_detect_by_group` (`str`, optional):  
        Column name for grouping samples for outlier detection.

        - `outlier_handle_by_group` (`str`, optional):  
        Column name for grouping samples for outlier handling.

        - `processing_order` (`list of following str`, optional):  
        Order of processing steps to apply. Options include:
            - `outlier`: Outlier handling.
            - `batch`: Batch effect removal.
            - `transform`: Data transformation.
            - `normalize`: Data normalization.

        - `df_name` (`str`, optional):  
        Name of the DataFrame for status tracking. Options include:
            - `peptide`
            - `taxa`
            - `func`
            - `taxa_func`
            - `protein`
            - `custom`

        ### Returns:

        - `pd.DataFrame`:  
        The processed DataFrame after applying the specified preprocessing steps.
        """
        
        
        df = df.copy()
        original_row_num = len(df)
        if processing_order is None:
            processing_order = ['outlier' , 'transform', 'normalize', 'batch']
        else:
            processing_order = processing_order
        # perform data processing in order
        for process in processing_order:
            if process == 'outlier':
                df = self._handle_outlier(df, detect_method=outlier_detect_method, handle_method=outlier_handle_method, detection_by_group = outlier_detect_by_group, handling_by_group=outlier_handle_by_group)
            elif process == 'batch':
                df = self._remove_batch_effect(df, batch_meta)
            elif process == 'transform':
                df = self._data_transform(df, transform_method)
            elif process == 'normalize':
                df = self._data_normalization(df, normalize_method)
            else:
                raise ValueError('processing_order must be in [outlier, batch, transform, normalize]')
        print(f'\n{self._get_current_time()} -----Data preprocessing finished.-----\n')

        if df_name in {'peptide', 'taxa', 'func', 'taxa_func', 'protein', 'custom'}:
            left_row_num = len(df)
            # self.tfa.outlier_status[df_name] = f'{left_row_num}/{original_row_num} ({left_row_num/original_row_num*100:.2f}%)'
            self.tfa.outlier_status[df_name] = f'{left_row_num} ({left_row_num/original_row_num*100:.2f}%)'

        return df
    