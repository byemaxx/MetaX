import logging
import pandas as pd
import numpy as np
from numba import njit
import os

# Setup logging
LOGGER = logging.getLogger(__name__)

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

setup_logging()

def check_whether_to_copy_numpy_arrays_derived_from_pandas():
    try:
        _manipulate_numpy_array_without_copy()
        return False
    except:
        LOGGER.info("Some numpy arrays derived from pandas will be copied.")
        return True

def _manipulate_numpy_array_without_copy():
    # Test whether numpy arrays derived from pandas are views or copies
    protein_profile_df = pd.DataFrame(
        {
            "ProteinA": [10, 20, 30, 40],
            "ProteinB": [15, 25, 35, 45],
            "ProteinC": [20, 30, 40, 50],
        },
        index=["Sample1", "Sample2", "Sample3", "Sample4"],
    )
    protein_profile_df = protein_profile_df.iloc[1:3]
    protein_profile_numpy = protein_profile_df.to_numpy(copy=False)
    protein_profile_numpy[0] = protein_profile_numpy[0] + 2

def sort_input_df_by_protein_id(data_df, protein_id):
    return data_df.sort_values(by=protein_id, ignore_index=True)

def remove_potential_quant_id_duplicates(data_df: pd.DataFrame, quant_id):
    before_drop = len(data_df)
    data_df = data_df.drop_duplicates(subset=quant_id, keep="first")
    after_drop = len(data_df)
    if before_drop != after_drop:
        entries_removed = before_drop - after_drop
        LOGGER.warning(
            f"Duplicate quant_ids detected. {entries_removed} rows removed from input df."
        )
    return data_df

def index_and_log_transform_input_df(data_df, protein_id, quant_id):
    data_df = data_df.set_index([protein_id, quant_id])
    return np.log2(data_df.replace(0, np.nan))

def remove_allnan_rows_input_df(data_df):
    return data_df.dropna(axis=0, how="all")

# NormalizationManager and related classes
class NormalizationManager:
    def __init__(self, complete_dataframe, num_samples_quadratic=100):
        self.complete_dataframe = complete_dataframe
        self._num_samples_quadratic = num_samples_quadratic
        self._run_normalization()

    def _run_normalization(self):
        self._check_no_duplicate_rows()
        if len(self.complete_dataframe.index) <= self._num_samples_quadratic:
            self.complete_dataframe = self.normalization_function(self.complete_dataframe)
        else:
            self._normalize_large_dataset()

    def _check_no_duplicate_rows(self):
        if self.complete_dataframe.index.duplicated().any():
            raise ValueError(
                "There are duplicate rows in the input dataframe. Ensure that there are no duplicate quant_id/ion values."
            )

    def _normalize_large_dataset(self):
        self._determine_subset_rows()
        self._normalize_quadratic_subset()
        self._create_reference_sample()
        self._shift_remaining_rows()

    def _determine_subset_rows(self):
        self._sorted_rows = self.complete_dataframe.index[
            np.argsort(self.complete_dataframe.isna().sum(axis=1))
        ]
        self._quadratic_subset_rows = self._sorted_rows[: self._num_samples_quadratic]
        self._linear_subset_rows = self.complete_dataframe.index.difference(
            self._quadratic_subset_rows
        )

    def _normalize_quadratic_subset(self):
        quadratic_subset_dataframe = self.complete_dataframe.loc[self._quadratic_subset_rows]
        self.complete_dataframe.loc[self._quadratic_subset_rows, :] = self.normalization_function(quadratic_subset_dataframe)

    def _create_reference_sample(self):
        quadratic_subset_dataframe = self.complete_dataframe.loc[self._quadratic_subset_rows]
        self._merged_reference_sample = quadratic_subset_dataframe.median(axis=0)

    def _shift_remaining_rows(self):
        linear_subset_dataframe = self.complete_dataframe.loc[self._linear_subset_rows]
        linear_shifted_dataframe = SampleShifterLinear(
            linear_subset_dataframe, self._merged_reference_sample
        ).ion_dataframe
        self.complete_dataframe.loc[self._linear_subset_rows, :] = linear_shifted_dataframe

class NormalizationManagerSamplesOnSelectedProteins(NormalizationManager):
    def __init__(
        self,
        complete_dataframe,
        num_samples_quadratic,
        selected_proteins_file=None,
        copy_numpy_arrays=False,
    ):
        complete_dataframe = complete_dataframe.T
        self.normalization_function = self._normalization_function
        self._selected_proteins_file = selected_proteins_file
        self._selected_protein_groups = None
        self._copy_numpy_arrays = copy_numpy_arrays
        self._adapt_selected_proteins_to_protein_groups(complete_dataframe)
        super().__init__(complete_dataframe, num_samples_quadratic)
        self.complete_dataframe = self.complete_dataframe.T

    def _adapt_selected_proteins_to_protein_groups(self, df):
        if self._selected_proteins_file is not None:
            LOGGER.info("Normalizing only selected proteins")
            selected_proteins = pd.read_csv(
                self._selected_proteins_file, header=None, sep="\t"
            )[0].to_list()
            protein2proteingroup_mapping = {
                protein: protein_group
                for protein_group in df.columns.get_level_values(0).to_list()
                for protein in protein_group.split(";")
            }
            existing_selected_proteins = [
                protein
                for protein in selected_proteins
                if protein in protein2proteingroup_mapping.keys()
            ]
            self._selected_protein_groups = [
                protein2proteingroup_mapping[protein]
                for protein in existing_selected_proteins
            ]

    def _normalization_function(self, ion_dataframe):
        if self._selected_protein_groups is not None:
            ion_dataframe_selected = ion_dataframe.loc[:, self._selected_protein_groups]
            sample2shift = get_normfacts(ion_dataframe_selected.to_numpy())
        else:
            ion_dataframe_selected = ion_dataframe
            sample2shift = get_normfacts(
                drop_nas_if_possible(ion_dataframe_selected).to_numpy()
            )

        df_c_normed = pd.DataFrame(
            apply_sampleshifts(
                ion_dataframe.to_numpy(copy=self._copy_numpy_arrays), sample2shift
            ),
            index=ion_dataframe.index,
            columns=ion_dataframe.columns,
        )
        return df_c_normed

def drop_nas_if_possible(df):
    df_nonans = df.dropna(axis=1)
    fraction_nonans = len(df_nonans.columns) / len(df.columns)
    if len(df_nonans.columns) < 1000 or fraction_nonans < 0.001:
        LOGGER.info(
            "Too few values for normalization without missing values. Including missing values"
        )
        return df
    else:
        return df_nonans

def get_normfacts(samples):
    set_samples_with_only_single_intensity_to_nan(samples)
    num_samples = samples.shape[0]
    mergedsamples = np.copy(samples)
    sampleidx2shift = dict(zip(range(num_samples), np.zeros(num_samples)))
    sampleidx2counts = dict(zip(range(num_samples), np.ones(num_samples)))
    sampleidx2anchoridx = {}
    exclusion_set = set()
    distance_matrix = create_distance_matrix(samples)
    variance_matrix = create_distance_matrix(samples, metric="variance")
    exclude_unconnected_samples(distance_matrix)
    exclude_unconnected_samples(variance_matrix)

    for rep in range(num_samples - 1):
        anchor_idx, shift_idx, min_distance = get_bestmatch_pair(
            distance_matrix, variance_matrix, sampleidx2counts
        )

        if anchor_idx is None:
            break
        sampleidx2anchoridx.update({shift_idx: anchor_idx})
        sampleidx2shift.update({shift_idx: min_distance})
        exclusion_set.add(shift_idx)

        anchor_sample = mergedsamples[anchor_idx]
        shift_sample = samples[shift_idx]
        shifted_sample = shift_sample + min_distance

        merged_sample = merge_distribs(
            anchor_sample,
            shifted_sample,
            sampleidx2counts[anchor_idx],
            sampleidx2counts[shift_idx],
        )
        mergedsamples[anchor_idx] = merged_sample

        update_distance_matrix(
            variance_matrix, mergedsamples, anchor_idx, shift_idx, metric="variance"
        )
        update_distance_matrix(distance_matrix, mergedsamples, anchor_idx, shift_idx)

        sampleidx2counts[anchor_idx] += 1

    sampleidx2totalshift = {}
    for i in exclusion_set:
        shift = get_total_shift(sampleidx2anchoridx, sampleidx2shift, i)
        sampleidx2totalshift[i] = shift
    return sampleidx2totalshift

def set_samples_with_only_single_intensity_to_nan(samples):
    for idx in range(len(samples)):
        sample = samples[idx]
        if sum(~np.isnan(sample)) < 2:
            sample[:] = np.nan

def apply_sampleshifts(samples, sampleidx2shift):
    for idx in sampleidx2shift.keys():
        samples[idx] = samples[idx] + sampleidx2shift.get(idx)
    return samples

def exclude_unconnected_samples(distance_matrix):
    if distance_matrix.shape[0] < 2:
        return
    unconnected_sample_idxs = get_unconnected_sample_idxs(distance_matrix)
    distance_matrix[unconnected_sample_idxs, :] = np.inf
    distance_matrix[:, unconnected_sample_idxs] = np.inf

def get_unconnected_sample_idxs(lower_matrix):
    full_matrix = convert_lower_to_full_matrix(lower_matrix)
    sums = np.sum(np.isfinite(full_matrix), axis=1)
    starting_sample = np.argmax(sums)
    num_samples = full_matrix.shape[0]

    connected_samples = np.zeros(num_samples, dtype=np.bool_)
    check_connected_traces(full_matrix, starting_sample, connected_samples)
    unconnected_samples = np.where(~connected_samples)[0]
    return unconnected_samples

def convert_lower_to_full_matrix(lower_matrix):
    full_matrix = np.copy(lower_matrix)
    rows, cols = np.where((lower_matrix != np.inf))
    full_matrix[cols, rows] = lower_matrix[rows, cols]
    return full_matrix

@njit
def check_connected_traces(matrix, trace_idx, visited):
    neighbors = np.where(matrix[trace_idx] != np.inf)[0]
    for neighbor in neighbors:
        if not visited[neighbor]:
            visited[neighbor] = True
            check_connected_traces(matrix, neighbor, visited)

def create_distance_matrix(samples, metric="median"):
    num_samples = samples.shape[0]
    distance_matrix = np.full((num_samples, num_samples), np.inf)
    for i in range(num_samples):
        for j in range(i + 1, num_samples):
            distance_matrix[i, j] = calc_distance(metric, samples[i], samples[j])

    return distance_matrix

def calc_distance(metric, samples_1, samples_2):
    res = None

    if metric == "median":
        res = calc_nanmedian(get_fcdistrib(samples_1, samples_2))
    if metric == "variance":
        fcdist = get_fcdistrib(samples_1, samples_2)
        res = calc_nanvar(fcdist)
    if res is None:
        raise Exception(f"Distance metric {metric} not implemented")
    if np.isnan(res):
        return np.inf
    else:
        return res

@njit
def calc_nanvar(fcdist):
    return np.nanvar(fcdist)

@njit
def calc_nanmedian(fcdist):
    return np.nanmedian(fcdist)

def get_bestmatch_pair(distance_matrix, variance_matrix, sample2counts):
    i, j = np.unravel_index(
        np.argmin(variance_matrix, axis=None), variance_matrix.shape
    )
    min_distance = distance_matrix[i, j]
    if min_distance == np.inf:
        return None, None, None
    anchor_idx, shift_idx, min_distance = determine_anchor_and_shift_sample(
        sample2counts, i, j, min_distance
    )
    return anchor_idx, shift_idx, min_distance

def determine_anchor_and_shift_sample(sample2counts, i_min, j_min, min_distance):
    counts_i = sample2counts[i_min]
    counts_j = sample2counts[j_min]
    anchor_idx = i_min if counts_i >= counts_j else j_min
    shift_idx = j_min if anchor_idx == i_min else i_min
    flip = 1 if anchor_idx == i_min else -1
    return anchor_idx, shift_idx, flip * min_distance

def merge_distribs(anchor_distrib, shifted_distrib, counts_anchor_distrib, counts_shifted_distrib):
    res = np.zeros(len(anchor_distrib))

    nans_anchor = np.isnan(anchor_distrib)
    nans_shifted = np.isnan(shifted_distrib)
    nans_anchor_and_shifted = nans_anchor & nans_shifted
    nans_only_anchor = nans_anchor & ~nans_shifted
    nans_only_shifted = nans_shifted & ~nans_anchor
    no_nans = ~nans_anchor & ~nans_shifted

    idx_anchor_and_shifted = np.where(nans_anchor_and_shifted)
    idx_only_anchor = np.where(nans_only_anchor)
    idx_only_shifted = np.where(nans_only_shifted)
    idx_no_nans = np.where(no_nans)

    res[idx_anchor_and_shifted] = np.nan
    res[idx_only_anchor] = shifted_distrib[idx_only_anchor]
    res[idx_only_shifted] = anchor_distrib[idx_only_shifted]
    res[idx_no_nans] = (
        anchor_distrib[idx_no_nans] * counts_anchor_distrib
        + shifted_distrib[idx_no_nans] * counts_shifted_distrib
    ) / (counts_anchor_distrib + counts_shifted_distrib)
    return res

def update_distance_matrix(distance_matrix, merged_samples, merged_sample_idx, shift_idx, metric="median"):
    for i in range(0, merged_sample_idx):
        if distance_matrix[i, merged_sample_idx] == np.inf:
            continue
        distance = calc_distance(metric, merged_samples[i], merged_samples[merged_sample_idx])
        distance_matrix[i, merged_sample_idx] = distance

    for j in range(merged_sample_idx + 1, merged_samples.shape[0]):
        if distance_matrix[merged_sample_idx, j] == np.inf:
            continue
        distance = calc_distance(metric, merged_samples[merged_sample_idx], merged_samples[j])
        distance_matrix[merged_sample_idx, j] = distance

    distance_matrix[shift_idx] = np.inf
    distance_matrix[:, shift_idx] = np.inf

def get_fcdistrib(logvals_rep1, logvals_rep2):
    dist = np.subtract(logvals_rep1, logvals_rep2)
    return dist

def get_total_shift(sampleidx2anchoridx, sample2shift, sample_idx):
    total_shift = 0.0

    while True:
        total_shift += sample2shift[sample_idx]
        if sample_idx not in sampleidx2anchoridx:
            break
        sample_idx = sampleidx2anchoridx[sample_idx]

    return total_shift

class SampleShifterLinear:
    def __init__(self, ion_dataframe, reference_intensities):
        self.ion_dataframe = ion_dataframe
        self._reference_intensities = reference_intensities.to_numpy()
        self._shift_columns_to_reference_sample()

    def _shift_columns_to_reference_sample(self):
        num_rows = self.ion_dataframe.shape[0]
        for row_idx in range(num_rows):
            distance_to_reference = self._calc_distance(
                samples_1=self._reference_intensities, samples_2=self.ion_dataframe.iloc[row_idx, :].to_numpy()
            )
            self.ion_dataframe.iloc[row_idx, :] += distance_to_reference

    @staticmethod
    def _calc_distance(samples_1, samples_2):
        distrib = get_fcdistrib(samples_1, samples_2)
        is_all_nan = np.all(np.isnan(distrib))
        if is_all_nan:
            return np.nan
        else:
            return np.nanmedian(distrib)

def estimate_protein_intensities(
    normed_df,
    min_nonan,
    num_samples_quadratic,
    num_cores,
    compile_normalized_ion_table,
    log_processed_proteins,
    protein_id,
    quant_id,
):
    allprots = list(normed_df.index.get_level_values(0).unique())
    LOGGER.info(f"{len(allprots)} LFQ-Objects total")

    list_of_tuple_w_protein_profiles_and_shifted_peptides = get_list_of_tuple_w_protein_profiles_and_shifted_peptides(
        normed_df,
        num_samples_quadratic,
        min_nonan,
        num_cores,
        log_processed_proteins,

    )

    protein_df = get_protein_dataframe_from_list_of_protein_profiles(
        list_of_tuple_w_protein_profiles_and_shifted_peptides=list_of_tuple_w_protein_profiles_and_shifted_peptides,
        normed_df=normed_df,
        protein_id=protein_id,
    )
    if compile_normalized_ion_table:
        ion_df = get_ion_intensity_dataframe_from_list_of_shifted_peptides(
            list_of_tuple_w_protein_profiles_and_shifted_peptides,
            column_names=normed_df.columns,
            protein_id=protein_id,
            quant_id=quant_id,
        )
    else:
        ion_df = None

    return protein_df, ion_df

def get_list_of_tuple_w_protein_profiles_and_shifted_peptides(
    normed_df,
    num_samples_quadratic,
    min_nonan,
    num_cores,
    log_processed_proteins,

):
    input_specification_tuplelist = get_input_specification_tuplelist_idx__df__num_samples_quadratic__min_nonan(
        normed_df, num_samples_quadratic, min_nonan
    )

    if num_cores is not None and num_cores > 1:
        import multiprocessing
        pool = multiprocessing.Pool(num_cores)
        args = [
            (
                idx,
                peptide_intensity_df,
                num_samples_quadratic,
                min_nonan,
                log_processed_proteins
            )
            for idx, peptide_intensity_df, num_samples_quadratic, min_nonan in input_specification_tuplelist
        ]
        results = pool.starmap(calculate_peptide_and_protein_intensities, args)
        pool.close()
        pool.join()
    else:
        # Process sequentially
        results = [
            calculate_peptide_and_protein_intensities(
                idx,
                peptide_intensity_df,
                num_samples_quadratic,
                min_nonan,
                log_processed_proteins,

            )
            for idx, peptide_intensity_df, num_samples_quadratic, min_nonan in input_specification_tuplelist
        ]

    return results

def get_input_specification_tuplelist_idx__df__num_samples_quadratic__min_nonan(
    normed_df, num_samples_quadratic, min_nonan
):
    list_of_normed_dfs = get_normed_dfs(normed_df)
    return [
        (idx, df, num_samples_quadratic, min_nonan)
        for idx, df in enumerate(list_of_normed_dfs)
    ]

def get_normed_dfs(normed_df):
    protein_names = normed_df.index.get_level_values(0).to_numpy()
    ion_names = normed_df.index.get_level_values(1).to_numpy()
    normed_array = normed_df.to_numpy()
    indices_of_proteinname_switch = find_nameswitch_indices(protein_names)
    results_list = [
        get_subdf(normed_array, indices_of_proteinname_switch, idx, protein_names, ion_names, normed_df.columns)
        for idx in range(len(indices_of_proteinname_switch) - 1)
    ]

    return results_list

def find_nameswitch_indices(arr):
    change_indices = np.where(arr[:-1] != arr[1:])[0] + 1

    start_indices = np.insert(change_indices, 0, 0)

    start_indices = np.append(start_indices, len(arr))

    return start_indices

def get_subdf(normed_array, indices_of_proteinname_switch, idx, protein_names, ion_names, columns):
    start_switch = indices_of_proteinname_switch[idx]
    end_switch = indices_of_proteinname_switch[idx + 1]
    sub_array = normed_array[start_switch:end_switch]
    index_sub_array = pd.MultiIndex.from_arrays(
        [protein_names[start_switch:end_switch], ion_names[start_switch:end_switch]],
        names=["protein_id", "quant_id"],
    )
    return pd.DataFrame(sub_array, index=index_sub_array, columns=columns)

def calculate_peptide_and_protein_intensities(
    idx,
    peptide_intensity_df,
    num_samples_quadratic,
    min_nonan,
    log_processed_proteins,

):
    if (idx % 100 == 0) and log_processed_proteins:
        LOGGER.info(f"Processing LFQ object {idx}")

    if len(peptide_intensity_df.index) > 1:
        peptide_intensity_df = ProtvalCutter(
            peptide_intensity_df, maximum_df_length=100
        ).get_dataframe()

    summed_pepint = np.nansum(2 ** peptide_intensity_df)

    if peptide_intensity_df.shape[1] < 2:
        shifted_peptides = peptide_intensity_df
    else:
        shifted_peptides = NormalizationManagerProtein(
            peptide_intensity_df, num_samples_quadratic=num_samples_quadratic
        ).complete_dataframe

    protein_profile = get_protein_profile_from_shifted_peptides(
        shifted_peptides, summed_pepint, min_nonan
    )

    return protein_profile, shifted_peptides

class ProtvalCutter:
    def __init__(self, protvals_df, maximum_df_length=100):
        self._protvals_df = protvals_df
        self._maximum_df_length = maximum_df_length

    def get_dataframe(self):
        if len(self._protvals_df.index) > self._maximum_df_length:
            sorted_idx = self._protvals_df.isna().sum(axis=1).sort_values().index[: self._maximum_df_length]
            return self._protvals_df.loc[sorted_idx]
        else:
            return self._protvals_df

class NormalizationManagerProtein(NormalizationManager):
    def __init__(self, complete_dataframe, num_samples_quadratic):
        self.normalization_function = normalize_ion_profiles
        super().__init__(complete_dataframe, num_samples_quadratic)

def normalize_ion_profiles(protein_profile_df):
    protein_profile_numpy = protein_profile_df.to_numpy()
    sample2shift = get_normfacts(protein_profile_numpy)
    df_normed = pd.DataFrame(
        apply_sampleshifts(protein_profile_numpy, sample2shift),
        index=protein_profile_df.index,
        columns=protein_profile_df.columns,
    )
    return df_normed

def get_protein_profile_from_shifted_peptides(normalized_peptide_profile_df, summed_pepints, min_nonan):
    intens_vec = []
    for sample in normalized_peptide_profile_df.columns:
        reps = normalized_peptide_profile_df.loc[:, sample].to_numpy()
        nonan_elems = sum(~np.isnan(reps))
        if nonan_elems >= min_nonan:
            intens_vec.append(np.nanmedian(reps))
        else:
            intens_vec.append(np.nan)
    intens_vec = np.array(intens_vec)
    summed_intensity = np.nansum(2 ** intens_vec)
    if summed_intensity == 0:
        return None
    intens_conversion_factor = summed_pepints / summed_intensity
    scaled_vec = intens_vec + np.log2(intens_conversion_factor)
    return scaled_vec

def get_protein_dataframe_from_list_of_protein_profiles(
    list_of_tuple_w_protein_profiles_and_shifted_peptides, normed_df, protein_id
):
    index_list = []
    profile_list = []

    list_of_protein_profiles = [x[0] for x in list_of_tuple_w_protein_profiles_and_shifted_peptides]
    allprots = [
        x[1].index.get_level_values(0)[0] for x in list_of_tuple_w_protein_profiles_and_shifted_peptides
    ]

    for idx in range(len(allprots)):
        if list_of_protein_profiles[idx] is None:
            continue
        index_list.append(allprots[idx])
        profile_list.append(list_of_protein_profiles[idx])

    index_for_protein_df = pd.Index(data=index_list, name=protein_id)
    protein_df = 2 ** pd.DataFrame(
        profile_list, index=index_for_protein_df, columns=normed_df.columns
    )
    protein_df = protein_df.replace(np.nan, 0)
    protein_df = protein_df.reset_index()
    return protein_df

def get_ion_intensity_dataframe_from_list_of_shifted_peptides(
    list_of_tuple_w_protein_profiles_and_shifted_peptides, column_names, protein_id, quant_id
):
    ion_names = []
    ion_vals = []
    protein_names = []
    for idx in range(len(list_of_tuple_w_protein_profiles_and_shifted_peptides)):
        ion_df = list_of_tuple_w_protein_profiles_and_shifted_peptides[idx][1]
        protein_name = ion_df.index.get_level_values(0)[0]
        ion_names += ion_df.index.get_level_values(1).tolist()
        ion_vals.append(ion_df.to_numpy())
        protein_names.extend([protein_name] * len(ion_df.index))
    merged_ions = 2 ** np.concatenate(ion_vals)
    merged_ions = np.nan_to_num(merged_ions)
    ion_df = pd.DataFrame(merged_ions)
    ion_df.columns = column_names
    ion_df[quant_id] = ion_names
    ion_df[protein_id] = protein_names
    ion_df = ion_df.set_index([protein_id, quant_id])
    return ion_df


def is_numeric_matrix(df):
    # mark non-numeric values as NaN
    numeric_df = df.apply(pd.to_numeric, errors='coerce')
    # check if nan values are present
    return numeric_df.notna().all().all()


def run_normalization(
            input_df: pd.DataFrame,
            number_of_quadratic_samples: int = 100
       ):
    '''
    Normalize the input DataFrame.
    Args:
        input_df (pd.DataFrame): A matrix of intensities.Columns are samples, index is items to be normalized.
        number_of_quadratic_samples (int, optional): How many samples are used to create the anchor intensity trace. Increasing might marginally increase performance at the cost of runtime
    Returns:
        pd.DataFrame: The normalized DataFrame.
    '''
    # chcek if only numbers are in the dataframe
    if not is_numeric_matrix(input_df):
        raise ValueError("Input DataFrame contains non-numeric values. Make sure to the items column is set as index.")
    
    copy_numpy_arrays = check_whether_to_copy_numpy_arrays_derived_from_pandas()
    input_df = np.log2(input_df.replace(0, np.nan)) # type: ignore
    input_df = input_df.dropna(axis=0, how="all")
    
    LOGGER.info("Performing sample normalization.")
    input_df = NormalizationManagerSamplesOnSelectedProteins(
        input_df,
        num_samples_quadratic=number_of_quadratic_samples,
        selected_proteins_file=None,
        copy_numpy_arrays=copy_numpy_arrays,
    ).complete_dataframe
    # restore log2 values
    input_df = 2 ** input_df
    # fill NaNs with 0
    input_df = input_df.fillna(0)
    
    return input_df

def run_lfq(
    input_df,
    protein_id: str = "protein",
    quant_id: str = "ion",
    min_nonan: int = 1,
    number_of_quadratic_samples: int = 100,
    maximum_number_of_quadratic_ions_to_use_per_protein: int = 10,
    log_processed_proteins: bool = True,
    compile_normalized_ion_table: bool = True,
    num_cores: int|None = None,
    use_multiprocessing: bool = False,
):
    copy_numpy_arrays = check_whether_to_copy_numpy_arrays_derived_from_pandas()

    input_df = sort_input_df_by_protein_id(input_df, protein_id)
    input_df = remove_potential_quant_id_duplicates(input_df, quant_id)
    input_df = index_and_log_transform_input_df(input_df, protein_id, quant_id)
    input_df = remove_allnan_rows_input_df(input_df)
    LOGGER.info(f"Starting LFQ analysis for [{protein_id}].")
    LOGGER.info("Performing sample normalization.")
    input_df = NormalizationManagerSamplesOnSelectedProteins(
        input_df,
        num_samples_quadratic=number_of_quadratic_samples,
        selected_proteins_file=None,
        copy_numpy_arrays=copy_numpy_arrays,
    ).complete_dataframe

    LOGGER.info("Estimating LFQ intensities.")
    if use_multiprocessing and num_cores is None:
        num_cores = os.cpu_count()
        LOGGER.info(f"{num_cores} cores for multiprocessing.")
    elif not use_multiprocessing:
        LOGGER.info("Multiprocessing disabled.")
        num_cores = 1

    protein_df, ion_df = estimate_protein_intensities(
        input_df,
        min_nonan=min_nonan,
        num_samples_quadratic=maximum_number_of_quadratic_ions_to_use_per_protein,
        num_cores=num_cores,
        compile_normalized_ion_table=compile_normalized_ion_table,
        log_processed_proteins=log_processed_proteins,
        protein_id=protein_id,
        quant_id=quant_id,
    )
    LOGGER.info(f'LFQ analysis for [{protein_id}] completed.')
    return protein_df, ion_df

if __name__ == "__main__":
    import time
    t1 = time.time()
    current_dir = os.path.dirname(os.path.realpath(__file__))
    df_path = os.path.join(current_dir, "../../../local_tests/peptide_for_protein.tsv")
    df = pd.read_csv(df_path, sep="\t")

    # protein_df = df.drop(columns=["Proteins"])
    # protein_df.set_index("Sequence", inplace=True)
    # print(protein_df.head())
    # df1 = run_normalization(protein_df)
    
    protein_df, ion_df = run_lfq(
        df,
        protein_id="Proteins",
        quant_id="Sequence",
        min_nonan=1,
        number_of_quadratic_samples=500,
        maximum_number_of_quadratic_ions_to_use_per_protein=10,
        num_cores=None,
        use_multiprocessing=True
    )
    
    print(protein_df.shape)
    print(protein_df.head())
    t2 = time.time()
    print(f"Time: {t2-t1:.4f} s")
