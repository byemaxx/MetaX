# T-Test , ANOVA, Tukey HSD, Deseq2
import pandas as pd
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy.stats import f_oneway
from scipy.stats import ttest_ind
from tqdm.auto import tqdm
from pydeseq2.ds import DeseqStats
from pydeseq2.dds import DeseqDataSet

class CrossTest:
    def __init__(self, tfa):
        self.tfa = tfa


    def get_stats_anova(self, group_list: list = None, df_type:str = 'taxa-func') -> pd.DataFrame:
        group_list_all = sorted(set(self.tfa.get_meta_list(self.tfa.meta_name)))

        if group_list is None:
            group_list = group_list_all
        elif any(i not in group_list_all for i in group_list):
            raise ValueError(f"groups must be in {group_list_all}")
        if len(group_list) <= 2:
            raise ValueError(
                "groups must be more than 2 for ANOVA test, please use t-test")

        all_sample_list = [sample for group in group_list for sample in self.tfa.get_sample_list_in_a_group(group)]

        if df_type in ['taxa-func', 'func-taxa', 'taxa', 'func', 'peptide']:
            if df_type == 'taxa-func':
                df, primary, secondary = self.tfa.taxa_func_df, 'Taxon', self.tfa.func_name
            elif df_type == 'func-taxa':
                df, primary, secondary = self.tfa.func_taxa_df, self.tfa.func_name, 'Taxon'
            elif df_type == 'taxa':
                df, primary = self.tfa.taxa_df, 'Taxon'
            elif df_type == 'func':
                df, primary = self.tfa.func_df, self.tfa.func_name
            elif df_type == 'peptide':
                df, primary = self.tfa.peptide_df, 'Sequence'

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

                list_for_anova = [row[1][self.tfa.get_sample_list_in_a_group(group)].to_list() for group in group_list]

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

        group_list_all = sorted(set(self.tfa.get_meta_list(self.tfa.meta_name)))

        if group_list is None:
            group_list = group_list_all
        elif any(i not in group_list_all for i in group_list):
            raise ValueError(f"groups must be in {group_list_all}")
        if len(group_list) != 2:
            raise ValueError("groups must be 2")

        all_sample_list = [sample for group in group_list for sample in self.tfa.get_sample_list_in_a_group(group)]

        if df_type == 'taxa-func':
            df, primary, secondary = self.tfa.taxa_func_df, 'Taxon', self.tfa.func_name
        elif df_type == 'func-taxa':
            df, primary, secondary = self.tfa.func_taxa_df, self.tfa.func_name, 'Taxon'
        elif df_type == 'taxa':
            df, primary = self.tfa.taxa_df, 'Taxon'
        elif df_type == 'func':
            df, primary = self.tfa.func_df, self.tfa.func_name
        elif df_type == 'peptide':
            df, primary = self.tfa.peptide_df, 'Sequence'
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

            list_for_ttest = [row[1][self.tfa.get_sample_list_in_a_group(group)].to_list() for group in group_list]
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
    

    def get_stats_deseq2(self, df, group_list: list):

        sample_list = []
        for i in group_list:
            sample = self.tfa.get_sample_list_in_a_group(i)
            sample_list += sample

        # Create intensity matrix
        df = df.copy()
        df = df[sample_list]
        df = self.tfa.replace_if_two_index(df)
        
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
        meta_df = self.tfa.meta_df.copy()
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
            design_factors=self.tfa.meta_name.replace('_', '-'), # ! replace '_' with '-' in meta_name
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
    def get_stats_tukey_test(self, taxon_name: str=None, func_name: str=None, sum_all: bool=True):
        # :param taxon_name: the taxon name
        # :param func_name: the function name
        # :return: the Tukey test result

        if sum_all:
            tukey_df = self.get_stats_tukey_test_sum(taxon_name=taxon_name, func_name=func_name)
        else:
            tukey_df = self.get_stats_tukey_test_each(taxon_name=taxon_name, func_name=func_name)

        return tukey_df
    
    def get_stats_tukey_test_each(self, taxon_name: str = None, func_name: str = None):
        # Copy the dataframe and reset index
        df = self.tfa.taxa_func_df.copy()
        df = df.reset_index()

        # Filter based on taxon_name and func_name
        if taxon_name is not None and func_name is not None:
            # df = df[(df['Taxon'] == taxon_name) & (df[self.tfa.func_name] == func_name)]
            df = self.tfa.get_intensity_matrix( func_name=func_name, taxon_name=taxon_name)

        elif taxon_name is not None:
            df = df[df['Taxon'] == taxon_name]
        elif func_name is not None:
            df = df[df[self.tfa.func_name] == func_name]
        else:
            raise ValueError("Please input the taxon name or the function name or both of them")
        if df.empty:
            raise ValueError("Got empty dataframe, please check the taxon name or the function name")

        # Initialize DataFrame to store Tukey test results
        tukey_results = pd.DataFrame()

        # Iterate over each row (function or taxon)
        for _, row in df.iterrows():
            Group = []
            Value = []

            # Extract group and value for each sample
            for sample in self.tfa.sample_list:
                group = self.tfa.meta_df[self.tfa.meta_df['Sample'] == sample][self.tfa.meta_name].values[0]
                value = row[sample]
                Group.append(group)
                Value.append(value)

            # Create a new DataFrame for the current row and perform Tukey's test
            new_df = pd.DataFrame({'Group': Group, 'Value': Value})
            tukey_result = pairwise_tukeyhsd(new_df["Value"], new_df["Group"])

            # Convert Tukey test result to DataFrame and add to the results
            tukey_df = pd.DataFrame(data=tukey_result._results_table.data[1:], columns=tukey_result._results_table.data[0])
            tukey_df['significant'] = tukey_df['reject'].apply(lambda x: 'Yes' if x else 'No')

            # Add column based on input parameters
            if taxon_name and not func_name:
                tukey_df['Function'] = row[self.tfa.func_name]
            elif func_name and not taxon_name:
                tukey_df['Taxa'] = row['Taxon']
            elif taxon_name and func_name:
                # tukey_df['seq'] = row['Seq']
                tukey_df['Sequence'] = row.name

            tukey_results = pd.concat([tukey_results, tukey_df], axis=0)
            print(tukey_results)
        # Return the combined Tukey test results
        return tukey_results

    def get_stats_tukey_test_sum(self, taxon_name: str=None, func_name: str=None):
        # :param taxon_name: the taxon name
        # :param func_name: the function name
        # :return: the Tukey test result


        df = self.tfa.taxa_func_df.copy()
        df = df.reset_index()

        # Correct the logic for filtering the dataframe based on taxon_name and func_name
        if taxon_name is not None and func_name is not None:
            # df = df[(df['Taxon'] == taxon_name) & (df[self.tfa.func_name] == func_name)]
            # get peptide abundance for each sample
            df = self.tfa.get_intensity_matrix( func_name=func_name, taxon_name=taxon_name)
        elif taxon_name is not None:
            df = df[df['Taxon'] == taxon_name]
        elif func_name is not None:
            df = df[df[self.tfa.func_name] == func_name]
        else:
            raise ValueError(
                "Please input the taxon name or the function name or both of them")
        if df.empty:
            raise ValueError(
                "Got empty dataframe, please check the taxon name or the function name")

        df = df[self.tfa.sample_list]
        #summarize the data to one row
        df = df.agg(['sum'])

        Group = []
        Value = []

        for sample in self.tfa.sample_list:
            group = self.tfa.meta_df[self.tfa.meta_df['Sample']
                                 == sample][self.tfa.meta_name].values[0]
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