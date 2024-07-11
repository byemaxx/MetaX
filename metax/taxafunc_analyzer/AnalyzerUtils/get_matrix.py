import pandas as pd

class GetMatrix:
    def __init__(self, tfa):
        self.tfa = tfa
        
    def get_intensity_matrix(self, func_name: str = None, taxon_name: str = None,
                             peptide_seq: str = None, sample_list: list = None, condition:list = None) -> pd.DataFrame:
        # input: a taxon with its function, a function with its taxon,
        # and the peptides in the function or taxon
        # output: a matrix of the intensity of the taxon or function or peptide in each sample
        # `peptide_seq` (str, optional): when `taxon_name` and `func_name` are both None, extract the intensity matrix of the peptide. Defaults to None.
        
        if condition is not None:
            sample_list = self.tfa.get_sample_list_for_group_list(condition=condition)
        
        if func_name is not None:
            dft = self.tfa.func_taxa_df.copy()
            dft.reset_index(inplace=True)

            if taxon_name is None:
                dft = dft[dft[self.tfa.func_name] == func_name]
                dft.set_index('Taxon', inplace=True)
            if taxon_name is not None:
                dft = self.tfa.clean_df[(self.tfa.clean_df['Taxon'] == taxon_name) & (
                    self.tfa.clean_df[self.tfa.func_name] == func_name)]
                dft.set_index(self.tfa.peptide_col_name, inplace=True)

        elif taxon_name is not None and peptide_seq is None:
            dft = self.tfa.func_taxa_df.copy()
            dft.reset_index(inplace=True)
            dft = dft[dft['Taxon'] == taxon_name]
            dft.set_index(self.tfa.func_name, inplace=True)

        elif peptide_seq is not None and taxon_name is None:
            dft = self.tfa.original_df[self.tfa.original_df[self.tfa.peptide_col_name] == peptide_seq]
            dft.set_index(self.tfa.peptide_col_name, inplace=True)

        else:
            raise ValueError(
                "Please input either func_name or taxon_name or peptide_seq")

        # Create the samples list of groups
        if sample_list is None:
            sample_list = self.tfa.sample_list
        elif any(i not in self.tfa.sample_list for i in sample_list):
            raise ValueError(
                f"sample_list must be in {self.tfa.sample_list}")

        dft = dft[sample_list]
        return dft
    
        # df = get_top_intensity(sw.taxa_df, top_num=50, method='freq')
    def get_top_intensity(self, df, top_num: int = 10, method: str = 'mean', sample_list: list = None):
        """
        Returns the top intensity values from a DataFrame based on a specified method.

        Args:
            `df` (pandas.DataFrame): The input DataFrame.
            `top_num` (int, optional): The number of top intensity values to return. Defaults to 10.
            `method` (str, optional): The method used to calculate intensity values. 
                Options: ['freq', 'mean', 'sum']. Defaults to 'mean'.
            `sample_list` (list, optional): A list of column names to consider for intensity calculation. 
                If None, all columns in the DataFrame will be used. Defaults to None.

        Returns:
            pandas.DataFrame: The DataFrame containing the top intensity values.

        """
        df = df[sample_list].copy() if sample_list else df.copy()
        df = self.tfa.replace_if_two_index(df)

        if method == 'freq':
            df['value'] = df.astype(bool).sum(axis=1)
        elif method == 'mean':
            df['value'] = df.mean(axis=1)
        elif method == 'sum':
            df['value'] = df.sum(axis=1)
            
        df = df.sort_values(by='value', ascending=False)
        df = df[:top_num].drop('value', axis=1)
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

        dft = self.tfa.replace_if_two_index(dft)

        if show_stats_cols:
            dft = dft.head(top_num)
        else:
            if df_type == 'log2fc':
                dft = dft.drop(df.columns[:6], axis=1)
            elif df_type in {'ttest', 'anova'}:
                dft = dft.drop(df.columns[:2], axis=1)

            dft = dft.head(top_num)

        return dft