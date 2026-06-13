# T-Test , ANOVA, Tukey HSD, DESeq2, limma
import pandas as pd
import numpy as np
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy.stats import f_oneway
from scipy.stats import ttest_ind
from tqdm.auto import tqdm
from scipy.stats import dunnett
from statsmodels.stats.multitest import multipletests
import re

class CrossTest:
    def __init__(self, tfa):
        self.tfa = tfa

    def _get_sample_columns(self, df):
        return [col for col in getattr(self.tfa, "sample_list", []) if col in df.columns]

    def prepare_limma_input(
        self,
        df,
        invert_transform=None,
        log2_transform=False,
        zero_to_nan=True,
    ):
        """
        Prepare dataframe for limma.
        Zeros will be treated as missing values and converted to NaN before limma runs.
        """
        df = df.copy()
        sample_cols = self._get_sample_columns(df)
        if not sample_cols:
            raise ValueError("No sample columns found in the dataframe.")
        if invert_transform is not None:
            df = self.tfa.invert_transform(df, invert_transform)
        if log2_transform:
            values = df.loc[:, sample_cols].apply(pd.to_numeric, errors="coerce")
            if (values < 0).any().any():
                raise ValueError("Cannot apply log2(x + 1) because negative values exist in the selected table.")
            df.loc[:, sample_cols] = np.log2(values + 1)
        if zero_to_nan:
            df.loc[:, sample_cols] = df.loc[:, sample_cols].apply(pd.to_numeric, errors="coerce").replace(0, np.nan)
        df.loc[:, sample_cols] = df.loc[:, sample_cols].replace([np.inf, -np.inf], np.nan)
        return df

    def prepare_deseq2_input(
        self,
        df,
        invert_transform=None,
        validate=True,
    ):
        df = df.copy()
        sample_cols = self._get_sample_columns(df)
        if not sample_cols:
            raise ValueError("No sample columns found in the dataframe.")
        if invert_transform is not None:
            df = self.tfa.invert_transform(df, invert_transform)
        df.loc[:, sample_cols] = df.loc[:, sample_cols].apply(pd.to_numeric, errors="coerce")
        df.loc[:, sample_cols] = df.loc[:, sample_cols].replace([np.inf, -np.inf], np.nan)
        if validate:
            if df.loc[:, sample_cols].isna().any().any():
                raise ValueError("Cannot run DESeq2 because NaN values exist in the sample columns.")
            if (df.loc[:, sample_cols] < 0).any().any():
                raise ValueError("Cannot run DESeq2 because negative values exist in the sample columns.")
        return df

    def convert_df_name_to_simple_name(self, name: str) -> str:
        name = name.lower()
        if name in ['taxa', 'taxon']:
            return 'taxa'
        elif name in ['func', 'function', 'functions']:
            return 'func'
        elif name in ['peptide', 'peptides']:
            return 'peptide'
        elif name in ['protein', 'proteins']:
            return 'protein'
        elif name in ['custom']:
            return 'custom'
        elif name in ['taxa-func', 'taxa-function', 'taxa-functions']:
            return 'taxa-func'
        elif name in ['func-taxa', 'function-taxa', 'functions-taxa']:
            return 'func-taxa'
        else:
            raise ValueError(f"df_type must be in ['taxa-func', 'func-taxa', 'taxa', 'func', 'peptide', 'custom'],\
                             but got [{name}]")

    def _get_df_primary_secondary(self, df_type: str):
        if df_type not in ['taxa-func', 'func-taxa', 'taxa', 'func', 'peptide', 'protein', 'custom']:
            raise ValueError(f"df_type must be in ['taxa-func', 'func-taxa', 'taxa', 'func', 'peptide', 'custom'],\
                             but got [{df_type}]")
        
        df, primary, secondary = None, None, None
        
        if df_type == 'taxa-func':
            df, primary, secondary = self.tfa.taxa_func_df, 'Taxon', self.tfa.func_name
        elif df_type == 'func-taxa':
            df, primary, secondary = self.tfa.func_taxa_df, self.tfa.func_name, 'Taxon'
        elif df_type == 'taxa':
            df, primary = self.tfa.taxa_df, 'Taxon'
        elif df_type == 'func':
            df, primary = self.tfa.func_df, self.tfa.func_name
        elif df_type == 'peptide':
            df, primary = self.tfa.peptide_df, self.tfa.peptide_col_name
        elif df_type == 'protein':
            df, primary = self.tfa.protein_df, self.tfa.protein_col_name
        elif df_type == 'custom':
            df, primary = self.tfa.custom_df, self.tfa.custom_col_name
            
        return df, primary, secondary
            


    def get_stats_anova(self, group_list: list|None = None, df_type:str = 'taxa-func', condition:list|None =None) -> pd.DataFrame:
        df_type = self.convert_df_name_to_simple_name(df_type)
        
        group_list_all = sorted(set(self.tfa.get_meta_list(self.tfa.meta_name)))

        if group_list is None:
            group_list = group_list_all
        elif any(i not in group_list_all for i in group_list):
            raise ValueError(f"groups must be in {group_list_all}")
        if len(group_list) <= 2:
            raise ValueError(
                "groups must be more than 2 for ANOVA test, please use t-test")

        all_sample_list = [sample for group in group_list for sample in self.tfa.get_sample_list_in_a_group(group, condition=condition)]

        df, primary, secondary = self._get_df_primary_secondary(df_type)
        
        if secondary is not None:
            print(f"--ANOVA test for {primary}-{secondary} in {group_list} with condition: {condition}--")
        else:
            print(f"--ANOVA test for {primary} in {group_list} with condition: {condition}--")

        res = {primary: [], "pvalue": [], "f-statistic": []}
        if df_type in ['taxa-func', 'func-taxa']:
            res[secondary] = []

        for row in tqdm(df.iterrows(), total=len(df)):
            primary_value = row[0]
            if df_type in ['taxa-func', 'func-taxa']:
                primary_value = row[0][0]
                secondary_value = row[0][1]
                res[secondary].append(secondary_value)

            res[primary].append(primary_value)

            list_for_anova = [row[1][self.tfa.get_sample_list_in_a_group(group, condition=condition)].to_list() for group in group_list]

            f, p = f_oneway(*list_for_anova)
            res["pvalue"].append(p)
            res["f-statistic"].append(f)

        res = pd.DataFrame(res)
        on_values = [primary]
        if df_type in ['taxa-func', 'func-taxa']:
            on_values.append(secondary)
        res_all = pd.merge(df, res, on=on_values)
        res_all.index = df.index
        # fill nan with 1 for pvalue
        res_all['pvalue'] = res_all['pvalue'].fillna(1)
        # adjust the pvalue as 'adj_pvalue'
        res_all['padj'] = multipletests(res_all['pvalue'], method='fdr_bh')[1]
        res_all = res_all[['pvalue', 'padj', 'f-statistic'] + all_sample_list]        
        return res_all
        
    def get_stats_ttest(self, group_list: list|None = None, df_type: str = 'taxa-func', condition:list|None =None) -> pd.DataFrame:
        df_type = self.convert_df_name_to_simple_name(df_type)

        group_list_all = sorted(set(self.tfa.get_meta_list(self.tfa.meta_name)))

        if group_list is None:
            group_list = group_list_all
        elif any(i not in group_list_all for i in group_list):
            raise ValueError(f"groups must be in {group_list_all}")
        if len(group_list) != 2:
            raise ValueError("groups must be 2")

        all_sample_list = [sample for group in group_list for sample in self.tfa.get_sample_list_in_a_group(group, condition=condition)]

        df, primary, secondary = self._get_df_primary_secondary(df_type)

        res = {primary: [], "pvalue": [], "t-statistic": []}
        
        if df_type in ['taxa-func', 'func-taxa']:
            print(f"t-test for {df_type} in {group_list}")
            res[secondary] = []
        else:
            print(f"t-test for {primary} in {group_list} with condition: {condition}")

        for row in tqdm(df.iterrows(), total=len(df)):
            primary_value = row[0]
            if df_type in ['taxa-func', 'func-taxa']:
                primary_value = row[0][0]
                secondary_value = row[0][1]
                res[secondary].append(secondary_value)

            res[primary].append(primary_value)

            list_for_ttest = [row[1][self.tfa.get_sample_list_in_a_group(group, condition=condition)].to_list() for group in group_list]
            # check if the sample size more than 1
            if any(len(i) < 2 for i in list_for_ttest):
                raise ValueError(f"sample size must be more than 1 for t-test")

            t, p = ttest_ind(*list_for_ttest)
            res["pvalue"].append(p)
            res["t-statistic"].append(t)

        res = pd.DataFrame(res)

        # print('reverse the t-statistic value due to the order of group_list is not correct')
        res['t-statistic'] = -res['t-statistic']
        on_values = [primary]
        if df_type in ['taxa-func', 'func-taxa']:
            on_values.append(secondary)
        res_all = pd.merge(df, res, on=on_values)
        res_all.index = df.index
        # fill nan with 1 for pvalue
        res_all['pvalue'] = res_all['pvalue'].fillna(1)
        res_all['padj'] = multipletests(res_all['pvalue'], method='fdr_bh')[1]
        res_all = res_all[['pvalue', 'padj', 't-statistic'] + all_sample_list]
        return res_all
    
    def get_stats_dunnett_test_against_control_with_conditon(self, control_group, condition, group_list:list|None =None, df_type: str = 'taxa-func') -> pd.DataFrame:
        df_type = self.convert_df_name_to_simple_name(df_type)
        
        meta_df = self.tfa.meta_df.copy()
        self.tfa.check_if_condition_valid(condition_meta=condition,  current_group_list=group_list)
        condition_list = meta_df[condition].unique()
        print(f'------------------ Start Comparisons Dunnett with Condition [{condition}]------------------')
        print(f'Condition List: {condition_list}')
        # only extract the row is condition in second_meta
        res_dict = {}
        for condition_group in condition_list:
            print(f'--Start for [{condition_group}] with condition: {condition}...')
            dft = self.get_stats_dunnett_test( control_group=control_group, condition=[condition, condition_group], group_list=group_list, df_type=df_type)
            res_dict[condition_group] = dft
            print(f'--Done for [{condition_group}] with condition: {condition}...')
        res_df = pd.concat(res_dict.values(), keys=res_dict.keys(), axis=1)
        print(f'\n------------------ Done for Comparisons Dunnett with Condition [{condition}]------------------\n')
        return res_df # a dataframe with 3 level columns index
            
            
    def get_stats_dunnett_test(self, control_group, group_list: list|None = None, df_type: str = 'taxa-func', condition:list|None =None) -> pd.DataFrame:
        df_type = self.convert_df_name_to_simple_name(df_type)

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
            # check if the control_group is in group_list
            if control_group in group_list:
                group_list.remove(control_group)
            # sort group_list incase the order is not correct for final result
            group_list = sorted(set(group_list))


        df, primary_index, secondary_index = self._get_df_primary_secondary(df_type)

        res_dict = {primary_index: [], "p_value": [], "t_statistic": []}

        if df_type in ['taxa-func', 'func-taxa']:
            print(f"Dunnett's test for {df_type} in {group_list} with condition: {condition}")
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


            test_dict = {group: row[1][self.tfa.get_sample_list_in_a_group(group, condition=condition)].to_list() for group in group_list}

            list_for_ttest = []
            for group, values in test_dict.items():
                # print(group, values)
                # check if the sample size at least 2
                if len(values) < 2:
                    output = f"Samples size must be more than 1 for Dunnett's test, but [{group}] has only {len(values)} sample"
                    if condition is not None:
                        output += f" with condition: {condition}"
                    raise ValueError(output)

                list_for_ttest.append(values)

            #! check if the sample size are the same is not necessary for Dunnett's test
            # if len(set([len(i) for i in list_for_ttest])) != 1:
            #     raise ValueError("sample size must be the same for Dunnett's test")

            dunnett_res = dunnett(*list_for_ttest, control=row[1][self.tfa.get_sample_list_in_a_group(control_group, condition=condition)].to_list())
            res_dict["p_value"].append(dunnett_res.pvalue)
            res_dict["t_statistic"].append(dunnett_res.statistic)


        res_df = pd.DataFrame(res_dict)
        if df_type in ['taxa-func', 'func-taxa']:
            # set multi-index
            res_df.set_index([primary_index, secondary_index], inplace=True)
        else:
            res_df.set_index(primary_index, inplace=True)

        # Separate p_value and t_statistic for each group
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

        # Combine pvalue and statistic into one dataframe
        res_df = pd.concat({'pvalue': res_df_pvalue, 'statistic': res_df_tstatistic}, axis=1)
        # Swap level for columns index
        res_df = res_df.swaplevel(axis=1).sort_index(axis=1)

        # Flatten all pvalues and apply correction
        res_df_pvalue_filled = res_df_pvalue.fillna(1)
        p_values_flat = res_df_pvalue_filled.values.flatten()
        _, p_values_corrected, _, _ = multipletests(p_values_flat, method='fdr_bh')
                
        # Reshape corrected pvalues back to the original shape
        p_values_corrected_reshaped = p_values_corrected.reshape(res_df_pvalue.shape)
        
        # Add corrected pvalues to the dataframe
        res_df_padj = pd.DataFrame(p_values_corrected_reshaped, index=res_df_pvalue.index, columns=res_df_pvalue.columns)
        
        # Merge corrected pvalues into the final result
        res_df = pd.concat({'padj': res_df_padj, 'pvalue': res_df_pvalue, 'statistic': res_df_tstatistic}, axis=1)
        
        # Swap levels and sort the columns
        res_df = res_df.swaplevel(axis=1).sort_index(axis=1)

        return res_df
        
    def get_stats_deseq2_against_control_with_conditon(
        self,
        df,
        control_group,
        condition,
        group_list=None,
        quiet=False,
        add_covariates: list[str] | None = None,
        input_prepared: bool = False,
    ) -> pd.DataFrame:
        """
        Run DESeq2 comparisons within each level of a given condition (stratified analysis).
        The condition is used for subsetting; covariates are applied within each condition level.
        """
        import warnings

        if not input_prepared:
            df = self.prepare_deseq2_input(df, validate=True)

        meta_df = self.tfa.meta_df.copy()

        # validate condition variable exists
        if condition not in meta_df.columns:
            raise KeyError(f"Condition '{condition}' not found in metadata. Available: {list(meta_df.columns)}")

        # unique levels to iterate
        condition_list = list(meta_df[condition].dropna().unique())
        print(f'------------------ Start Comparisons (stratified by [{condition}]) ------------------')
        print(f'Levels: {condition_list}')

        # sanitize covariates: drop the same variable as 'condition'
        covs = list(add_covariates) if add_covariates else None
        if covs and condition in covs:
            warnings.warn(
                f"[MetaX] '{condition}' is used for stratification and cannot be used as a covariate simultaneously; "
                f"removing it from add_covariates."
            )
            covs = [c for c in covs if c != condition]
        # optional: if after removal covs becomes empty, set to None for clarity
        if covs is not None and len(covs) == 0:
            covs = None

        # do the work per level
        res_dict = {}
        for cond_level in condition_list:
            print(f'-- Start level [{cond_level}] (condition: {condition}) --')
            # within-level subset is handled by 'condition=[condition, cond_level]' in the downstream call
            dft = self.get_stats_deseq2_against_control(
                df=df,
                control_group=control_group,
                group_list=group_list,
                concat_sample_to_result=True,
                quiet=quiet,
                condition=[condition, cond_level],
                add_covariates=covs,
                input_prepared=True,
            )
            if dft is not None and not dft.empty:
                res_dict[cond_level] = dft
            print(f'-- Done level [{cond_level}] --')

        # 3-level columns: (condition_level) × (group2) × (result_cols)
        if not res_dict:
            print(f"No valid DESeq2 results found across any levels for condition {condition}.")
            return pd.DataFrame()
            
        res_df = pd.concat(res_dict.values(), keys=res_dict.keys(), axis=1)
        print(f'------------------ Done (stratified by [{condition}]) ------------------')
        return res_df


    def _safe_name(self, s: str) -> str:
        """Make names formula-safe: replace '-' with '_' only for metadata names/levels."""
        return str(s).replace('-', '_')

    def _safe_design_token(self, s: str) -> str:
        """Create a stable, formula-friendly token for design matrix columns."""
        token = re.sub(r"\W+", "_", str(s)).strip("_")
        if not token:
            token = "level"
        if token[0].isdigit():
            token = f"x_{token}"
        return token

    def _require_inmoose_deseq2(self):
        try:
            from inmoose.deseq2 import DESeq, DESeqDataSet
        except ImportError as exc:
            raise ImportError(
                "InMoose is required for DESeq2 analysis. Install it with `pip install inmoose`."
            ) from exc
        return DESeq, DESeqDataSet

    def _require_inmoose_limma(self):
        try:
            from inmoose.limma import lmFit, contrasts_fit, eBayes, topTable
        except ImportError as exc:
            raise ImportError(
                "InMoose is required for limma analysis. Install it with `pip install inmoose`."
            ) from exc
        return lmFit, contrasts_fit, eBayes, topTable

    def _run_inmoose_deseq(self, DESeq, dds_factory, quiet=False):
        dds = dds_factory()
        try:
            return DESeq(dds, quiet=quiet)
        except NotImplementedError:
            print(
                "[DESeq2] InMoose local dispersion fallback is not implemented; "
                "retrying with fitType='mean'."
            )
            return DESeq(dds_factory(), quiet=quiet, fitType="mean")

    def _restore_limma_fit_column_names(self, fit, design_columns):
        design_columns = list(design_columns)
        for attr_name in ("coefficients", "stdev_unscaled"):
            value = getattr(fit, attr_name, None)
            if isinstance(value, pd.DataFrame) and value.shape[1] == len(design_columns):
                value.columns = design_columns

        cov = getattr(fit, "cov_coefficients", None)
        if isinstance(cov, pd.DataFrame) and cov.shape == (len(design_columns), len(design_columns)):
            cov.index = design_columns
            cov.columns = design_columns
        return fit

    def _run_inmoose_ebayes(self, eBayes, fit):
        try:
            return eBayes(fit)
        except KeyError as exc:
            if exc.args != (-2,):
                raise

            # InMoose can return a scalar df_prior=inf from squeezeVar. Its
            # eBayes then evaluates ~True as -2 and indexes a DataFrame column.
            # Broadcasting df_prior to per-feature values preserves the intended
            # row-mask semantics without patching the installed package.
            import importlib

            ebayes_module = importlib.import_module(eBayes.__module__)
            original_squeeze_var = ebayes_module.squeezeVar

            def squeeze_var_compat(*args, **kwargs):
                out = original_squeeze_var(*args, **kwargs)
                df_prior = out.get("df_prior")
                if np.isscalar(df_prior):
                    out["df_prior"] = np.repeat(df_prior, len(np.asarray(args[0])))
                return out

            ebayes_module.squeezeVar = squeeze_var_compat
            try:
                return eBayes(fit)
            finally:
                ebayes_module.squeezeVar = original_squeeze_var

    def _prepare_de_metadata(self, sample_list, group1, group2, add_covariates=None):
        meta_df = self.tfa.meta_df.copy()
        meta_df = meta_df[meta_df['Sample'].isin(sample_list)]
        meta_df.set_index('Sample', inplace=True)
        meta_df = meta_df.rename(columns=lambda c: c.replace('-', '_'))

        design_factor = self._safe_name(self.tfa.meta_name)
        if design_factor not in meta_df.columns:
            raise KeyError(
                f"Design factor '{design_factor}' not found in metadata columns: {list(meta_df.columns)}. "
                f"Original meta_name: '{self.tfa.meta_name}'. Make sure it matches a metadata column."
            )

        g1 = self._safe_name(group1)
        g2 = self._safe_name(group2)
        meta_df[design_factor] = meta_df[design_factor].astype(str).str.replace('-', '_', regex=False)
        meta_df[design_factor] = pd.Categorical(meta_df[design_factor], categories=[g1, g2])

        covs = []
        if add_covariates:
            covs = [self._safe_name(c) for c in add_covariates]
            for c_old, c_new in zip(add_covariates, covs):
                if c_new not in meta_df.columns and c_old in meta_df.columns:
                    meta_df.rename(columns={c_old: c_new}, inplace=True)
                if c_new not in meta_df.columns:
                    raise KeyError(f"Covariate '{c_old}' not found in metadata columns: {list(meta_df.columns)}")
                if not pd.api.types.is_numeric_dtype(meta_df[c_new]):
                    meta_df[c_new] = meta_df[c_new].astype(str).str.replace('-', '_', regex=False)
                    meta_df[c_new] = pd.Categorical(meta_df[c_new])

        return meta_df, design_factor, covs, g1, g2

    def _align_assay_and_metadata(self, assay_df, meta_df):
        assay_df = assay_df.sort_index()
        meta_df = meta_df.sort_index()
        if not assay_df.index.equals(meta_df.index):
            shared = assay_df.index.intersection(meta_df.index)
            assay_df = assay_df.loc[shared]
            meta_df = meta_df.loc[shared]
            if assay_df.shape[0] == 0:
                raise ValueError("No overlapping samples between assay data and metadata after alignment.")
        return assay_df, meta_df

    def _build_limma_design(self, meta_df, design_factor, covs, g1, g2):
        group_values = meta_df[design_factor].astype(str)
        group_columns = {
            level: f"group_{self._safe_design_token(level)}"
            for level in [g1, g2]
        }
        design_parts = []
        group_design = pd.DataFrame(index=meta_df.index)
        for level, col_name in group_columns.items():
            group_design[col_name] = (group_values == level).astype(float)
        design_parts.append(group_design)

        for cov in covs:
            values = meta_df[cov]
            if pd.api.types.is_numeric_dtype(values):
                cov_values = pd.to_numeric(values, errors="coerce")
                if cov_values.isna().any():
                    raise ValueError(f"Covariate '{cov}' contains non-numeric values after numeric conversion.")
                design_parts.append(pd.DataFrame({self._safe_design_token(cov): cov_values.astype(float)}, index=meta_df.index))
            else:
                dummies = pd.get_dummies(values.astype(str), prefix=self._safe_design_token(cov), drop_first=True, dtype=float)
                dummies.index = meta_df.index
                design_parts.append(dummies)

        design = pd.concat(design_parts, axis=1)
        contrast_name = f"{group_columns[g2]}_vs_{group_columns[g1]}"
        contrast = pd.DataFrame(0.0, index=design.columns, columns=[contrast_name])
        contrast.loc[group_columns[g2], contrast_name] = 1.0
        contrast.loc[group_columns[g1], contrast_name] = -1.0
        return design, contrast, contrast_name

    def _normalize_limma_results(
        self,
        res,
        dft,
        sample_list,
        concat_sample_to_result,
        group1_sample=None,
        group2_sample=None,
    ):
        res = pd.DataFrame(res).copy()
        rename_map = {}
        candidates = {
            "logFC": "log2FoldChange",
            "P.Value": "pvalue",
            "PValue": "pvalue",
            "p_value": "pvalue",
            "adj.P.Val": "padj",
            "adj_P_Val": "padj",
            "adj_pvalue": "padj",
            "FDR": "padj",
            "t": "stat",
            "T": "stat",
        }
        for old_name, new_name in candidates.items():
            if old_name in res.columns and new_name not in res.columns:
                rename_map[old_name] = new_name
        if rename_map:
            res.rename(columns=rename_map, inplace=True)

        if "baseMean" not in res.columns:
            res["baseMean"] = dft[sample_list].mean(axis=1)
        if "padj" not in res.columns and "pvalue" in res.columns:
            res["padj"] = multipletests(res["pvalue"].fillna(1), method="fdr_bh")[1]

        preferred = ["baseMean", "log2FoldChange", "stat", "pvalue", "padj"]
        ordered = [c for c in preferred if c in res.columns] + [c for c in res.columns if c not in preferred]
        res = res[ordered]

        if concat_sample_to_result:
            return pd.merge(res, dft[sample_list], left_index=True, right_index=True)
        return res

    def _normalize_deseq2_results(self, res):
        res = pd.DataFrame(res).copy()
        rename_map = {}
        candidates = {
            "logFC": "log2FoldChange",
            "log2FoldChange": "log2FoldChange",
            "lfcSE": "lfcSE",
            "P.Value": "pvalue",
            "PValue": "pvalue",
            "p_value": "pvalue",
            "adj.P.Val": "padj",
            "adj_P_Val": "padj",
            "adj_pvalue": "padj",
            "FDR": "padj",
        }
        for old_name, new_name in candidates.items():
            if old_name in res.columns and new_name not in res.columns:
                rename_map[old_name] = new_name
        if rename_map:
            res.rename(columns=rename_map, inplace=True)

        if "padj" not in res.columns and "pvalue" in res.columns:
            res["padj"] = multipletests(res["pvalue"].fillna(1), method="fdr_bh")[1]

        preferred = ["baseMean", "log2FoldChange", "lfcSE", "stat", "pvalue", "padj"]
        ordered = [c for c in preferred if c in res.columns] + [c for c in res.columns if c not in preferred]
        return res[ordered]

    def get_stats_deseq2_against_control(
        self,
        df,
        control_group,
        group_list: list | None = None,
        concat_sample_to_result: bool = False,
        quiet: bool = False,
        condition: list | None = None,
        add_covariates: list[str] | None = None,
        input_prepared: bool = False,
    ) -> pd.DataFrame:
        """
        Run DESeq2 for multiple group-vs-control comparisons and column-bind results.
        """
        all_group_list = sorted(set(self.tfa.group_list))
        if group_list is None:
            group_list = all_group_list

        if control_group not in all_group_list:
            raise ValueError(f"control_group must be in {all_group_list}")
        if any(i not in all_group_list for i in group_list):
            raise ValueError(f"groups must be in {all_group_list}")

        if control_group in group_list:
            group_list.remove(control_group)

        if not input_prepared:
            df = self.prepare_deseq2_input(df, validate=True)

        res_dict = {}

        for group2 in group_list:
            print(f'\n-------------Start to compare [{control_group}] and [{group2}]----------------\n')
            df_res = self.get_stats_deseq2(
                df=df,
                group1=control_group,
                group2=group2,
                concat_sample_to_result=concat_sample_to_result,
                quiet=quiet,
                condition=condition,
                add_covariates=add_covariates,
                input_prepared=True,
            )
            if df_res is not None:
                res_dict[group2] = df_res
            print(f'\n------------- Done for [{control_group}] and [{group2}]----------------\n')

        print('Concatenating results...')
        if not res_dict:
            print("No valid comparisons were performed.")
            return pd.DataFrame()
        combined_df = pd.concat(res_dict, axis=1)
        print('Done for all comparisons')

        return combined_df


    def get_stats_deseq2(
        self,
        df,
        group1,
        group2,
        concat_sample_to_result: bool = True,
        quiet: bool = False,
        condition: list | None = None,
        add_covariates: list[str] | None = None,
        input_prepared: bool = False,
    ) -> pd.DataFrame:
        """
        Run DESeq2 for group2 vs group1 using InMoose DESeq2 with formulaic design.
        The reported log2FoldChange is group2 / group1.

        Current InMoose backend supports categorical group2-vs-group1 contrasts with optional additive covariates. Continuous-term and interaction-specific tests are not currently supported.
        """
        print(f'\n--Running Deseq2 [{group1}] vs [{group2}] with condition: [{condition}]--')

        # Resolve sample lists
        group1_sample = self.tfa.get_sample_list_in_a_group(group1, condition=condition)
        group2_sample = self.tfa.get_sample_list_in_a_group(group2, condition=condition)
        sample_list = group1_sample + group2_sample

        print(f'group1 [{group1}]:\n{group1_sample}\n')
        print(f'group2 [{group2}]:\n{group2_sample}\n')

        if not group1_sample or not group2_sample:
            print(f"Skipping DESeq2 for [{group1}] vs [{group2}] because one of the groups has no samples under condition {condition}.")
            return None

        # Build intensity matrix for selected samples
        if not input_prepared:
            df = self.prepare_deseq2_input(df, validate=True)
            
        dft = df.copy()
        dft = dft[sample_list]
        dft = self.tfa.replace_if_two_index(dft)  # keep your original helper

        # counts: samples x features (int), with stable scaling → round → int
        counts_df = dft.T  # rows = samples, cols = features
        target_max = 1e6
        raw_max = float(np.nanmax(counts_df.values)) if counts_df.size else 0.0
        scale = max(raw_max / target_max, 1.0)
        if scale > 1.0:
            print(f'[Scaling] scale={scale:.3f} (max {raw_max:.3g} → target_max {target_max:.0f})')
        else:
            print(f'[Scaling] no scaling applied (max {raw_max:.3g} ≤ target_max {target_max:.0f})')
        counts_df = (counts_df / scale).round().astype(int)

        meta_df, design_factor, covs, g1, g2 = self._prepare_de_metadata(
            sample_list=sample_list,
            group1=group1,
            group2=group2,
            add_covariates=add_covariates,
        )
        counts_df, meta_df = self._align_assay_and_metadata(counts_df, meta_df)

        # Build formulaic design
        rhs_terms = covs + [design_factor]
        design_formula = "~" + " + ".join(rhs_terms) if rhs_terms else "~ 1"
        print(f"[Design] {design_formula}")

        DESeq, DESeqDataSet = self._require_inmoose_deseq2()

        def dds_factory():
            return DESeqDataSet(
                countData=counts_df,
                clinicalData=meta_df,
                design=design_formula
            )

        dds = self._run_inmoose_deseq(DESeq, dds_factory, quiet=quiet)

        contrast = [design_factor, g2, g1]
        print(f"Contrast used: {contrast}  => log2FoldChange = {g2} / {g1}")

        result_kwargs = {
            "contrast": contrast,
            "alpha": 0.05,
            "independentFiltering": True,
        }

        try:
            res = dds.results(**result_kwargs)
        except KeyError as e:
            if 'cooks' in str(e).lower():
                print('cooksCutoff is not available, use cooksCutoff=False')
                result_kwargs["cooksCutoff"] = False
                res = dds.results(**result_kwargs)
            else:
                raise e

        res = self._normalize_deseq2_results(res)

        # Optionally merge raw sample columns back for convenience
        if concat_sample_to_result:
            res_merged = pd.merge(res, dft, left_index=True, right_index=True)
        else:
            res_merged = res

        return res_merged

    def get_stats_limma_against_control_with_conditon(
        self,
        df,
        control_group,
        condition,
        group_list=None,
        quiet=False,
        add_covariates: list[str] | None = None,
    ) -> pd.DataFrame:
        """
        Run limma comparisons within each level of a given condition (stratified analysis).
        The output shape mirrors get_stats_deseq2_against_control_with_conditon.
        """
        import warnings

        meta_df = self.tfa.meta_df.copy()
        if condition not in meta_df.columns:
            raise KeyError(f"Condition '{condition}' not found in metadata. Available: {list(meta_df.columns)}")

        condition_list = list(meta_df[condition].dropna().unique())
        print(f'------------------ Start Limma Comparisons (stratified by [{condition}]) ------------------')
        print(f'Levels: {condition_list}')

        covs = list(add_covariates) if add_covariates else None
        if covs and condition in covs:
            warnings.warn(
                f"[MetaX] '{condition}' is used for stratification and cannot be used as a covariate simultaneously; "
                f"removing it from add_covariates."
            )
            covs = [c for c in covs if c != condition]
        if covs is not None and len(covs) == 0:
            covs = None

        res_dict = {}
        for cond_level in condition_list:
            print(f'-- Start limma level [{cond_level}] (condition: {condition}) --')
            dft = self.get_stats_limma_against_control(
                df=df,
                control_group=control_group,
                group_list=group_list,
                concat_sample_to_result=True,
                quiet=quiet,
                condition=[condition, cond_level],
                add_covariates=covs,
            )
            if dft is not None and not dft.empty:
                res_dict[cond_level] = dft
            print(f'-- Done limma level [{cond_level}] --')

        if not res_dict:
            print(f"No valid limma results found across any levels for condition {condition}.")
            return pd.DataFrame()

        res_df = pd.concat(res_dict.values(), keys=res_dict.keys(), axis=1)
        print(f'------------------ Done Limma (stratified by [{condition}]) ------------------')
        return res_df

    def get_stats_limma_against_control(
        self,
        df,
        control_group,
        group_list: list | None = None,
        concat_sample_to_result: bool = False,
        quiet: bool = False,
        condition: list | None = None,
        add_covariates: list[str] | None = None,
    ) -> pd.DataFrame:
        """
        Run limma for multiple group-vs-control comparisons and column-bind results.
        """
        all_group_list = sorted(set(self.tfa.group_list))
        if group_list is None:
            group_list = all_group_list
        else:
            group_list = list(group_list)

        if control_group not in all_group_list:
            raise ValueError(f"control_group must be in {all_group_list}")
        if any(i not in all_group_list for i in group_list):
            raise ValueError(f"groups must be in {all_group_list}")

        if control_group in group_list:
            group_list.remove(control_group)

        res_dict = {}
        for group2 in group_list:
            print(f'\n-------------Start limma compare [{control_group}] and [{group2}]----------------\n')
            df_res = self.get_stats_limma(
                df=df,
                group1=control_group,
                group2=group2,
                concat_sample_to_result=concat_sample_to_result,
                quiet=quiet,
                condition=condition,
                add_covariates=add_covariates,
            )
            if df_res is not None:
                res_dict[group2] = df_res
            print(f'\n------------- Done limma for [{control_group}] and [{group2}]----------------\n')

        print('Concatenating limma results...')
        if not res_dict:
            print("No valid limma comparisons were performed.")
            return pd.DataFrame()
        combined_df = pd.concat(res_dict, axis=1)
        print('Done for all limma comparisons')
        return combined_df

    def _filter_limma_rank_aware(self, dft, group1_sample, group2_sample, design):
        valid_g1 = dft[group1_sample].notna().sum(axis=1)
        valid_g2 = dft[group2_sample].notna().sum(axis=1)
        
        design_rank = np.linalg.matrix_rank(design.values)
        if design.shape[0] <= design_rank:
            raise ValueError("Not enough samples to fit the limma design matrix.")
            
        # Note: A global design-rank check is used here. 
        # Per-feature rank checking may be added later for sparse missingness patterns.
        valid_mask = (valid_g1 > 0) & (valid_g2 > 0) & (dft.notna().sum(axis=1) > design_rank)
        return dft[valid_mask]

    def get_stats_limma(
        self,
        df,
        group1,
        group2,
        concat_sample_to_result: bool = True,
        quiet: bool = False,
        condition: list | None = None,
        add_covariates: list[str] | None = None,
    ) -> pd.DataFrame:
        """
        Run limma for group2 vs group1 using InMoose.
        The input matrix is the current MetaX table as shown/selected by the GUI; use the GUI
        preprocessing controls to choose whether data should be log-transformed before limma.
        """
        print(f'\n--Running limma [{group1}] vs [{group2}] with condition: [{condition}]--')

        group1_sample = self.tfa.get_sample_list_in_a_group(group1, condition=condition)
        group2_sample = self.tfa.get_sample_list_in_a_group(group2, condition=condition)
        sample_list = group1_sample + group2_sample

        print(f'group1 [{group1}]:\n{group1_sample}\n')
        print(f'group2 [{group2}]:\n{group2_sample}\n')

        if not group1_sample or not group2_sample:
            print(f"Skipping limma for [{group1}] vs [{group2}] because one of the groups has no samples under condition {condition}.")
            return None

        dft = df.copy()
        dft = dft[sample_list]
        dft = self.tfa.replace_if_two_index(dft)
        dft = dft.apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
        
        # 保护机制：无论 GUI 是否传入 log 数据，都将 0 替换为 NaN 避免后续计算无意义的效应
        dft = dft.replace(0.0, np.nan)

        meta_df, design_factor, covs, g1, g2 = self._prepare_de_metadata(
            sample_list=sample_list,
            group1=group1,
            group2=group2,
            add_covariates=add_covariates,
        )

        design, contrast, contrast_name = self._build_limma_design(meta_df, design_factor, covs, g1, g2)
        print(f"[Limma design] columns={list(design.columns)}")
        print(f"[Limma contrast] {contrast_name}: {g2} / {g1}")

        # Filter out features that don't have enough valid samples to fit the model
        dft = self._filter_limma_rank_aware(dft, group1_sample, group2_sample, design)

        if dft.empty:
            print("No valid features left after filtering for missing values. Skipping limma.")
            return pd.DataFrame()

        expression_df = dft.T
        expression_df, meta_df = self._align_assay_and_metadata(expression_df, meta_df)
        dft = dft[expression_df.index]

        lmFit, contrasts_fit, eBayes, topTable = self._require_inmoose_limma()
        fit = lmFit(expression_df.T, design=design)
        fit = self._restore_limma_fit_column_names(fit, design.columns)
        fit = contrasts_fit(fit, contrast)
        fit = self._run_inmoose_ebayes(eBayes, fit)
        try:
            res = topTable(fit, coef=contrast_name, number=np.inf, sort_by="P")
        except (KeyError, ValueError, TypeError):
            res = topTable(fit, coef=0, number=np.inf, sort_by="P")

        if not quiet:
            print(f"limma returned {len(res)} rows.")

        return self._normalize_limma_results(
            res,
            dft,
            list(expression_df.index),
            concat_sample_to_result,
            group1_sample=group1_sample,
            group2_sample=group2_sample,
        )


    # Get the Tukey test result of a taxon or a function
    def get_stats_tukey_test(self, taxon_name: str|None =None, func_name: str|None =None, sum_all: bool=True, condition:list|None =None):
        # :param taxon_name: the taxon name
        # :param func_name: the function name
        # :return: the Tukey test result

        if sum_all:
            tukey_df = self.get_stats_tukey_test_sum(taxon_name=taxon_name, func_name=func_name, condition=condition)
        else:
            tukey_df = self.get_stats_tukey_test_each(taxon_name=taxon_name, func_name=func_name, condition=condition)

        return tukey_df
    
    def get_stats_tukey_test_each(self, taxon_name: str|None = None, func_name: str|None = None, condition:list|None =None):
        # Copy the dataframe and reset index
        df = self.tfa.taxa_func_df.copy()
        df = df.reset_index()

        # Filter based on taxon_name and func_name
        if taxon_name is not None and func_name is not None:
            # df = df[(df['Taxon'] == taxon_name) & (df[self.tfa.func_name] == func_name)]
            df = self.tfa.get_intensity_matrix( func_name=func_name, taxon_name=taxon_name, condition=condition)

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
                tukey_df[self.tfa.peptide_col_name] = row.name

            tukey_results = pd.concat([tukey_results, tukey_df], axis=0)
            print(tukey_results)
        # Return the combined Tukey test results
        return tukey_results

    def get_stats_tukey_test_sum(self, taxon_name: str|None=None, func_name: str|None=None, condition:list|None =None):
        # :param taxon_name: the taxon name
        # :param func_name: the function name
        # :return: the Tukey test result


        df = self.tfa.taxa_func_df.copy()
        df = df.reset_index()

        # Correct the logic for filtering the dataframe based on taxon_name and func_name
        if taxon_name is not None and func_name is not None:
            # df = df[(df['Taxon'] == taxon_name) & (df[self.tfa.func_name] == func_name)]
            # get peptide abundance for each sample
            df = self.tfa.GetMatrix.get_intensity_matrix( func_name=func_name, taxon_name=taxon_name, condition=condition)
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
    def get_stats_diff_taxa_but_func(self, group_list: list|None = None, p_value: float = 0.05,
                                     taxa_res_df: pd.DataFrame|None =None, 
                                     func_res_df: pd.DataFrame|None =None, 
                                     taxa_func_res_df: pd.DataFrame|None =None, 
                                     condition:list|None =None, p_type: str = 'padj'
                                     ) -> tuple:
        p_col_name = 'pvalue' if p_type == 'pvalue' else 'padj'
        print(f"Using [{p_col_name}] for filtering")
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
                print(f'--Calculating t-test for {group_list} with condition: {condition}--')
                df_taxa_test_res = self.get_stats_ttest(group_list=group_list, df_type='taxa', condition=condition)
                df_func_test_res = self.get_stats_ttest(group_list=group_list, df_type='func', condition=condition)
                df_taxa_func_test_res = self.get_stats_ttest(group_list=group_list, df_type='taxa-func', condition=condition)
            else: # if more than two groups, use ANOVA
                print(f'--Calculating ANOVA for {group_list} with condition: {condition}--')
                df_taxa_test_res = self.get_stats_anova(group_list=group_list, df_type='taxa', condition=condition)
                df_func_test_res = self.get_stats_anova(group_list=group_list, df_type='func', condition=condition)
                df_taxa_func_test_res = self.get_stats_anova(group_list=group_list, df_type='taxa-func', condition=condition)
        
        else:
            print("Using the given test result")
            df_taxa_test_res = taxa_res_df
            df_func_test_res = func_res_df
            df_taxa_func_test_res = taxa_func_res_df
        
        # check the p_value is between 0 and 1
        if p_value < 0 or p_value > 1:
            raise ValueError("p_value must be between 0 and 1")
        # 获取pvalue大于0.05的Taxon items
        not_significant_taxa_list = df_taxa_test_res[df_taxa_test_res[p_col_name] >= p_value].index.get_level_values('Taxon').tolist()
        significant_taxa_list = df_taxa_test_res[df_taxa_test_res[p_col_name] < p_value].index.get_level_values('Taxon').tolist()
        print(f"Under {p_col_name} = {p_value}: \n \
              Significant Taxa: [{len(significant_taxa_list)}], Not Significant Taxa: [{len(not_significant_taxa_list)}]")
        # 获取pvalue小于0.05的Function items
        not_significant_func_list = df_func_test_res[df_func_test_res[p_col_name] >= p_value].index.get_level_values(self.tfa.func_name).tolist()
        significant_func_list = df_func_test_res[df_func_test_res[p_col_name] < p_value].index.get_level_values(self.tfa.func_name).tolist()
        print(f"Under {p_col_name} = {p_value}: \n \
                Significant Function: [{len(significant_func_list)}], Not Significant Function: [{len(not_significant_func_list)}]")

        # 选择这些Taxon在df_taxa_func_test_res中的行 and pvalue < 0.05
        df_filtered_taxa_not_significant = df_taxa_func_test_res.loc[
            df_taxa_func_test_res.index.get_level_values('Taxon').isin(not_significant_taxa_list) & 
            (df_taxa_func_test_res[p_col_name] < p_value) & 
            (df_taxa_func_test_res.index.get_level_values(self.tfa.func_name).isin(significant_func_list))
                                                                     ]
        print(f"Taxa not significant but related function significant with {p_col_name} < {p_value}: [{len(df_filtered_taxa_not_significant)}]")
        df_filtered_func_not_significant = df_taxa_func_test_res.loc[
            df_taxa_func_test_res.index.get_level_values(self.tfa.func_name).isin(not_significant_func_list) & 
            (df_taxa_func_test_res[p_col_name] < p_value) &
            (df_taxa_func_test_res.index.get_level_values('Taxon').isin(significant_taxa_list))
            ]
        # reset_index for df_filtered_func_not_significant
        df_filtered_func_not_significant = df_filtered_func_not_significant.swaplevel(0, 1).sort_index()
        print(f"Function not significant but related taxa significant with {p_col_name} < {p_value}: [{len(df_filtered_func_not_significant)}]")
        
        print("Returning a tuple of two dataframesthe:\n \
            1. the taxa not significant but related function significant\n \
            2. the function not significant but related taxa significant")
        
        return (df_filtered_taxa_not_significant, df_filtered_func_not_significant)
    
    def extrcat_significant_stat_from_dunnett(self, df, p_value=0.05, p_type='padj'):
        """
        Extract significant statistical results from a Dunnett test.
        Parameters:
            df (pd.DataFrame): A multi-level DataFrame containing statistical results,
                               where the first level of columns represents different groups
                               and the second level contains statistical metrics.
            p_value (float, optional): The p-value threshold for significance. Default is 0.05.
            p_type (str, optional): 'padj' or 'pvalue'. Default is 'padj'.
        Returns:
            pd.DataFrame: A DataFrame containing only the significant statistics for each group,
                          with the first level of columns representing the groups and the second
                          level containing only the 'statistic' values.
        Raises:
            KeyError: If the specified p_type is not found in the DataFrame columns.
        """
        res_dict= {}
        for i in df.columns.levels[0]:
            df_i = df[i]
            df_i = df_i[df_i[p_type] < p_value]
            res_dict[i] = df_i
            print(f'Group: {i} | Number of significant taxa: {len(df_i)}')
        dft = pd.concat(res_dict, axis=1)
        # dft.columns = dft.columns.droplevel(1)
        print(f'Number of significant table: {len(dft)}')
        # only keep the levle 1 statistic column
        dft = dft.loc[:, (slice(None), 'statistic')]
        dft.columns = dft.columns.droplevel(1)

        return dft


    def extrcat_significant_fc_from_deseq2all(self, df, p_value=0.05, log2fc_min=1, log2fc_max=30, p_type='padj'):
        import pandas as pd
        p_type = 'padj' if p_type == 'padj' else 'pvalue'
        
        # extract p_type and log2FoldChange columns only 
        df_extrcted = df.loc[:, pd.IndexSlice[:, [p_type, 'log2FoldChange']]]

        res_dict = {}
        # remove 0 in the float number last digit

        for i in df_extrcted.columns.levels[0]:
            # print(f'Extracting [{i}] with (padj <= {padj}) and (log2fc >= {log2fc})')
            # extract i from multi-index
            df_i = df_extrcted[i]
            df_i = df_i.loc[(df_i[p_type] < p_value) & (abs(df_i['log2FoldChange']) >= log2fc_min) & (abs(df_i['log2FoldChange']) <= log2fc_max)]
            print(f"Group: [{i}] | Significant results: [{df_i.shape[0]}]    (up:{(df_i['log2FoldChange'] > 0).sum()} down:{(df_i['log2FoldChange'] < 0).sum()})")
            res_dict[i] = df_i
            
        dft = pd.concat(res_dict, axis=1)
        print(f"Total number of significant results: [{dft.shape[0]}]")
        # check if the dataframe is empty
        if dft.empty:
            print("ATTENTION:\nEmpty dataframe!\n")

        # only keep padj column
        dft = dft.loc[:, pd.IndexSlice[:, ['log2FoldChange']]]
        # rename column name
        dft.columns = dft.columns.droplevel(1)
        return dft
    
    # return a dict of 3 dataframe: df_all, df_no_na, df_same_trends
    def extrcat_significant_fc_from_all_3_levels(self, df, p_value=0.05, log2fc_min=1, log2fc_max=99,
                                                 p_type='padj', df_type:str='deseq2') -> dict:
        """
        Extracts significant fold change data from a multi-level DataFrame and categorizes it based on different filtering criteria.
        
        Parameters:
        -----------
        df : pd.DataFrame
            A multi-level DataFrame containing statistical data for different groups.
        
        p_value : float, optional, default=0.05
            The threshold for significance based on p-values. Only rows with p-values below this threshold will be considered significant.
        
        log2fc_min : float, optional, default=1
            The minimum log2 fold change to consider a row significant.
        
        log2fc_max : float, optional, default=99
            The maximum log2 fold change to consider a row significant.
        
        p_type : str, optional, default='padj'
            The type of p-value to use for filtering. Typically 'padj' or 'pvalue'.
        
        df_type : str, optional, default='deseq2'
            Specifies the type of statistical method used. Must be either 'dunnett' or 'deseq2'.
        
        Returns:
        --------
        dict
            A dictionary containing three DataFrames:
            - 'all_sig': DataFrame containing all significant rows across all groups, Non-significant values are replaced with NA.
            - 'half_same_trends': DataFrame containing rows where each group has the same trend (all positive or all negative non-NA values) 
            and at least 50% of the values are non-NA.
            - 'no_na': DataFrame containing rows with no NA values in each group.
            - 'same_trends': DataFrame containing rows with no NA values, and all values in each group follow the same trend (all positive or all negative).
        """
        def filter_rows_with_same_trends_and_half_na(group):
            non_na_count = group.notna().sum(axis=1)
            threshold = group.shape[1] / 2.0
            row_min = group.min(axis=1)
            row_max = group.max(axis=1)
            same_trend = (row_min > 0) | (row_max < 0)
            mask = same_trend & (non_na_count > threshold)
            return group[mask]
            
        # 筛选每行无NA且所有值同向的行
        def filter_rows(group):
            return group[((group > 0).all(axis=1)) | ((group < 0).all(axis=1))]
        
        res_df_dict = {}
        
        first_level_values = df.columns.get_level_values(0).unique()
        res_dict = {}
        for value in first_level_values:  # iterate over first level values
            sub_df = df[value]
            print(f"\nExtracting significant Stats from '{value}':")
            if df_type == 'dunnett':
                dft = self.extrcat_significant_stat_from_dunnett(sub_df, p_value=p_value, p_type=p_type)
            elif df_type in ['deseq2', 'limma']:
                dft = self.extrcat_significant_fc_from_deseq2all(sub_df, p_value=p_value, log2fc_min=log2fc_min, log2fc_max=log2fc_max, p_type=p_type)
            else:
                raise ValueError("df_type must be in ['dunnett', 'deseq2', 'limma']")
            
            res_dict[value] = dft
        df_combined = pd.concat(res_dict, axis=1)
        df_swapped = df_combined.swaplevel(axis=1)
        df_swapped = df_swapped.sort_index(axis=1)
        print(f"\nTotal number of all_siginificant: [{df_swapped.shape[0]}]")
        res_df_dict['all_sig'] = df_swapped
         
        df_half = pd.concat([filter_rows_with_same_trends_and_half_na(group) 
                             for _, group in df_swapped.groupby(level=0, axis=1)], axis=1)
        df_half = df_half.dropna(how='all')
        print(f"Total number of half_same_trends: [{df_half.shape[0]}]")
        res_df_dict['half_same_trends'] = df_half
        
        df_no_na = df_swapped.groupby(level=0, axis=1).apply(lambda x: x.dropna())
        df_no_na = df_no_na.droplevel(1, axis=1)
        print(f"Total number of no_na: [{df_no_na.shape[0]}]")
        res_df_dict['no_na'] = df_no_na

        df_same_trends = df_no_na.groupby(level=0, axis=1).apply(filter_rows)
        df_same_trends.columns = df_same_trends.columns.droplevel(1)
        print(f"Total number of same_trends: [{df_same_trends.shape[0]}]")
        res_df_dict['same_trends'] = df_same_trends
        
        return res_df_dict
