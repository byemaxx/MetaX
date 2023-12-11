# T-Test , ANOVA, Tukey HSD, Deseq2
import pandas as pd
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy.stats import f_oneway
from scipy.stats import ttest_ind
from tqdm.auto import tqdm
from pydeseq2.ds import DeseqStats
from pydeseq2.dds import DeseqDataSet
from scipy.stats import dunnett

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

        secondary = None # give a default value to prevent error when print
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
            else:
                raise ValueError("df_type must be in ['taxa-func', 'func-taxa', 'taxa', 'func', 'peptide']")
            
            if secondary is not None:
                print(f"ANOVA test for {primary}-{secondary} in {group_list}")
            else:
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

        secondary = None # give a default value to prevent error when print
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

        res = {primary: [], "P-value": [], "t-statistic": []}
        
        if df_type in ['taxa-func', 'func-taxa']:
            print(f"t-test for {df_type} in {group_list}")
            res[secondary] = []
        else:
            print(f"t-test for {primary} in {group_list}")

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
    
    
    def get_stats_dunnett_test(self, control_group, group_list: list = None, df_type: str = 'taxa-func') -> pd.DataFrame:
        group_list_all = sorted(set(self.tfa.get_meta_list(self.tfa.meta_name)))
        #! Output a dataframe with (p_value, t_statistic) for each group
        # check if the control_group is in group_list_all
        if control_group not in group_list_all:
            raise ValueError(f"control_group must be in {group_list_all}")

        if group_list is None:
            group_list = group_list_all
            group_list.remove(control_group)
        else:
            # check if the group_list is in group_list_all
            if any(i not in group_list_all for i in group_list):
                raise ValueError(f"groups must be in {group_list_all}")
            # sort group_list incase the order is not correct for final result
            group_list = sorted(set(group_list))
            
         
   
        secondary_index = None # give a default value to prevent error when print
        if df_type == 'taxa-func':
            df, primary_index, secondary_index = self.tfa.taxa_func_df, 'Taxon', self.tfa.func_name
        elif df_type == 'func-taxa':
            df, primary_index, secondary_index = self.tfa.func_taxa_df, self.tfa.func_name, 'Taxon'
        elif df_type == 'taxa':
            df, primary_index = self.tfa.taxa_df, 'Taxon'
        elif df_type == 'func':
            df, primary_index = self.tfa.func_df, self.tfa.func_name
        elif df_type == 'peptide':
            df, primary_index = self.tfa.peptide_df, 'Sequence'
        else:
            raise ValueError("df_type must be in ['taxa-func', 'func-taxa', 'taxa', 'func', 'peptide']")

        res_dict = {primary_index: [], "p_value": [], "t_statistic": []}
        
        if df_type in ['taxa-func', 'func-taxa']:
            print(f"Dunnett's test for {df_type} in {group_list}")
            res_dict[secondary_index] = []
        else:
            print(f"Dunnett's test for {primary_index} in {group_list}")
        print(f"control group: {control_group}")
        
        print(f"primary index: {primary_index}", f"secondary index: {secondary_index}", sep='\n')
        
        # extract head 10 rows for test
        # df = df.head(10)
        
        # start dunnett for each row
        for row in tqdm(df.iterrows(), total=len(df)):
            # row[0] is the index, row[1] is the row data
            primary_value = row[0]
            if df_type in ['taxa-func', 'func-taxa']: # if the df is taxa-func or func-taxa, the index is a tuple
                primary_value = row[0][0]
                secondary_value = row[0][1]
                res_dict[secondary_index].append(secondary_value)
            # else the index is a string, and the secondary is empty
            
            res_dict[primary_index].append(primary_value)
            

           
            test_dict = {group: row[1][self.tfa.get_sample_list_in_a_group(group)].to_list() for group in group_list}

            list_for_ttest = []
            for group, values in test_dict.items():
                # print(group, values)
                # check if the sample size at least 2
                if len(values) < 2:
                    raise ValueError(f"sample size must be more than 1 for Dunnett's test, but {group} has only {len(values)} sample(s)")                
                list_for_ttest.append(values)
                
            #! check if the sample size are the same is not necessary for Dunnett's test
            # if len(set([len(i) for i in list_for_ttest])) != 1:
            #     raise ValueError("sample size must be the same for Dunnett's test")
                
            
            dunnett_res = dunnett(*list_for_ttest, control=row[1][self.tfa.get_sample_list_in_a_group(control_group)].to_list())
            res_dict["p_value"].append(dunnett_res.pvalue)
            res_dict["t_statistic"].append(dunnett_res.statistic)
            

        
        res_df = pd.DataFrame(res_dict)
        if df_type in ['taxa-func', 'func-taxa']:
            # set multi-index
            res_df.set_index([primary_index, secondary_index], inplace=True)
        else:
            res_df.set_index(primary_index, inplace=True)
            
        
        res_df_pvalue = res_df.copy()
        res_df_pvalue.drop(columns=['t_statistic'], inplace=True)
        for index, group_name in enumerate(group_list):
            res_df_pvalue[group_name] = res_df_pvalue['p_value'].apply(lambda x: x[index])
        res_df_pvalue.drop(columns=['p_value'], inplace=True)
        
        res_df_tstatistic = res_df.copy()
        res_df_tstatistic.drop(columns=['p_value'], inplace=True)
        for index, group_name in enumerate(group_list):
            res_df_tstatistic[group_name] = res_df_tstatistic['t_statistic'].apply(lambda x: x[index])
        res_df_tstatistic.drop(columns=['t_statistic'], inplace=True)
        
        res_df_pvalue.columns = [i + '(p_value)' for i in res_df_pvalue.columns]
        res_df_tstatistic.columns = [i + '(t_statistic)' for i in res_df_tstatistic.columns]
        
        # merge two dataframe
        res_df = pd.concat([res_df_pvalue, res_df_tstatistic], axis=1)
        # sort the columns
        res_df = res_df.reindex(sorted(res_df.columns), axis=1)
        
        

        # res_df_dict = {'p_value': res_df_pvalue, 't_statistic': res_df_tstatistic}
        
        return res_df
            
            
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
    
    
    # find out the items that are not significant in taxa but significant in function, and vice versa
    def get_stats_diff_taxa_but_func(self, group_list: list = None, p_value: float = 0.05,
                                     taxa_res_df: pd.DataFrame =None, func_res_df: pd.DataFrame=None, taxa_func_res_df: pd.DataFrame=None) -> tuple:
        
        # calculate the test result if not given
        if taxa_res_df is None or func_res_df is None or taxa_func_res_df is None:
            print("No test result given, calculating the test result first")
            # if group_list is None, use all groups
            if group_list is None:
                group_list = sorted(set(self.tfa.get_meta_list(self.tfa.meta_name)))
                
            # if len(group_list) less than 2, raise error
            if len(group_list) < 2:
                raise ValueError("groups must be more than 1")
            
            if len(group_list) == 2: # if only two groups, use t-test
                df_taxa_test_res = self.get_stats_ttest(group_list=group_list, df_type='taxa')
                df_func_test_res = self.get_stats_ttest(group_list=group_list, df_type='func')
                df_taxa_func_test_res = self.get_stats_ttest(group_list=group_list, df_type='taxa-func')
            else: # if more than two groups, use ANOVA
                df_taxa_test_res = self.get_stats_anova(group_list=group_list, df_type='taxa')
                df_func_test_res = self.get_stats_anova(group_list=group_list, df_type='func')
                df_taxa_func_test_res = self.get_stats_anova(group_list=group_list, df_type='taxa-func')
        
        else:
            print("Using the given test result")
            df_taxa_test_res = taxa_res_df
            df_func_test_res = func_res_df
            df_taxa_func_test_res = taxa_func_res_df
        
        # check the p_value is between 0 and 1
        if p_value < 0 or p_value > 1:
            raise ValueError("p_value must be between 0 and 1")
        # 获取p-value大于0.05的Taxon条目
        not_significant_taxa = df_taxa_test_res[df_taxa_test_res['P-value'] >= p_value].index.get_level_values('Taxon').tolist()
        print(f"Under P-value = {p_value}: \n \
              Significant Taxa: [{len(df_taxa_test_res) - len(not_significant_taxa)}], Not Significant Taxa: [{len(not_significant_taxa)}]")
        not_significant_func = df_func_test_res[df_func_test_res['P-value'] >= p_value].index.get_level_values(self.tfa.func_name).tolist()
        print(f"Under P-value = {p_value}: \n \
                Significant Function: [{len(df_func_test_res) - len(not_significant_func)}], Not Significant Function: [{len(not_significant_func)}]")

        # 选择这些Taxon在df_taxa_func_test_res中的行 and P-value < 0.05
        df_filtered_taxa_not_significant = df_taxa_func_test_res.loc[df_taxa_func_test_res.index.get_level_values('Taxon').isin(not_significant_taxa) & (df_taxa_func_test_res['P-value'] < p_value)]
        print(f"Taxa not significant but related function significant Under P-value = {p_value}: [{len(df_filtered_taxa_not_significant)}]")
        df_filtered_func_not_significant = df_taxa_func_test_res.loc[df_taxa_func_test_res.index.get_level_values(self.tfa.func_name).isin(not_significant_func) & (df_taxa_func_test_res['P-value'] < p_value)]
        # reset_index for df_filtered_func_not_significant
        df_filtered_func_not_significant = df_filtered_func_not_significant.swaplevel(0, 1).sort_index()
        print(f"Function not significant but related taxa significant Under P-value = {p_value}: [{len(df_filtered_func_not_significant)}]")
        
        print("Returning a tuple of two dataframesthe:\n \
            1. the taxa not significant but related function significant\n \
            2. the function not significant but related taxa significant")
        
        return (df_filtered_taxa_not_significant, df_filtered_func_not_significant)

