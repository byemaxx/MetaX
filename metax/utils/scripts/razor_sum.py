from collections import defaultdict
import pandas as pd
from tqdm import tqdm


class RazorSum:
    def __init__(self, df, column_map):
        self.df = df
        self.column_map = column_map
        self.res_intensity_dict = {}  # store all sample to output
        self.greedy_method = None  # only used for razor method
        self.mini_target_set = None
        self.filtered_target_to_peptides = None
        self.share_intensity = False
        self.__multi_target_count = 0


    def sum_protein_intensity(self, greedy_method='heap'):
        self.greedy_method = greedy_method
        print('Start to sum protein intensity using method: [razor]')
        if column_map['sample_list'] is None or len(column_map['sample_list']) == 0:
            raise ValueError('Please provide [sample_list] in column_map for sum, e.g. ["Sample1", "Sample2", "Sample3"]')
        # only extract the peptide and target columns
        extract_cols = [self.column_map['peptide'], self.column_map['target']] + self.column_map['sample_list']
        self.df = self.df.loc[:, extract_cols]
        
        pep_to_target = self._create_pep_to_target_razor()
        self._sum_target_intensity(pep_to_target)
        
        # show summary
        print(f"Total peptides count: {len(pep_to_target)}")
        self.__multi_target_count = self.__multi_target_count/len(sample_list)
        print(f"Multi-target peptides count: {self.__multi_target_count} ({self.__multi_target_count / len(pep_to_target) * 100:.2f}%)")

        
        res_df = pd.DataFrame.from_dict(self.res_intensity_dict)
        res_df.fillna(0, inplace=True)
        res_df.index.name = 'Target'
        
        print('Finish summing protein intensity')
        
        return res_df
    
    def get_mini_target_set(self, greedy_method='heap'):
        self.greedy_method = greedy_method
        print('Start to get minimum target set using method: [razor]')
        # only extract the peptide and target columns
        extract_cols = [self.column_map['peptide'], self.column_map['target']] + self.column_map['sample_list'] if self.column_map['sample_list'] else []
        # if NA in target column, or '', raise error
        if self.df[self.column_map['target']].isna().any() or '' in self.df[self.column_map['target']].values:
            raise ValueError(f'NA or empty value in target column: {self.column_map["target"]}')
        
        self.df = self.df.loc[:, extract_cols]
        df = self.df.loc[:, [self.column_map['peptide'], self.column_map['target']]]
        peptides = set(df[self.column_map['peptide']])
        target_to_peptides = self._create_target_to_peptides()
        mini_target_set = self.find_minimum_target_set(peptides, target_to_peptides)
        filtered_target_to_peptides = {target: target_to_peptides[target] for target in mini_target_set}
        self.mini_target_set = mini_target_set
        self.filtered_target_to_peptides = filtered_target_to_peptides
        return self.mini_target_set

    def _create_pep_to_target_razor(self):
        """
        Create a dictionary mapping peptides to targets based on a minimum target set.

        Returns:
            dict: A dictionary mapping peptides to targets.
            key: peptide
            value: a list of targets
        """
        self.get_mini_target_set(self.greedy_method)
        
        peptides = set(self.df[self.column_map['peptide']])
        filtered_target_to_peptides = self.filtered_target_to_peptides
        
        peptide_to_target = defaultdict(list)
        for peptide in tqdm(peptides, desc="Assigning peptides to targets"):
            possible_targets = [target for target, peps in filtered_target_to_peptides.items() if peptide in peps]
            if possible_targets:
                max_target_count = max(len(filtered_target_to_peptides[target]) for target in possible_targets)
                best_targets = [target for target in possible_targets if len(filtered_target_to_peptides[target]) == max_target_count]
                peptide_to_target[peptide].extend(best_targets)
        
        return peptide_to_target
    
    def _create_target_to_peptides(self):
        """
        Create a dictionary mapping targets to peptides.
        e.g. {'target1': {'peptide1', 'peptide2'}, 'target2': {'peptide1', 'peptide3'}}
        
        """
        df = self.df.loc[:, [self.column_map['peptide'], self.column_map['target']]]
        target_to_peptides = defaultdict(set)

        for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Creating target to peptides mapping"):
            sequence = row[self.column_map['peptide']]
            targets = row[self.column_map['target']].split(';')
            for target in targets:
                target_to_peptides[target].add(sequence)
                
        return target_to_peptides

    def _sum_target_intensity(self, peptide_to_target):
        for sample in tqdm(self.column_map['sample_list'], desc="Summing intensity"):
            df_sample = self.df.loc[:, [self.column_map['peptide'], sample]]
            df_sample.set_index(self.column_map['peptide'], inplace=True)
            peptide_intensity_dict = df_sample.to_dict()[sample]
            for peptide, targets in peptide_to_target.items():
                intensity = peptide_intensity_dict.get(peptide, 0)
                self._update_output_dict(targets, sample, intensity)
        

    def find_minimum_target_set(self, peptides, target_to_peptides):
        target_to_peptides_copy = target_to_peptides.copy()
        # print current target number
        print(f'Current target number: {len(target_to_peptides_copy)}')
        peptides_to_cover = set(peptides)
        selected_targets = set()
        method = self.greedy_method

        if method == 'greedy':
            print('Start creating protein dict for "Set Cover Problem" with Greedy Approximation Algorithm')
            with tqdm(total=len(peptides_to_cover), desc="Covering peptides") as pbar:
                while peptides_to_cover:
                    best_protein = None
                    peptides_covered_by_best = set()
                    for protein, covered_peptides in target_to_peptides_copy.items():
                        covered = peptides_to_cover & covered_peptides
                        if len(covered) > len(peptides_covered_by_best):
                            best_protein = protein
                            peptides_covered_by_best = covered

                    if not best_protein:
                        break

                    selected_targets.add(best_protein)
                    peptides_to_cover -= peptides_covered_by_best
                    target_to_peptides_copy.pop(best_protein)  # remove the protein from the dict to speed up the process
                    pbar.update(len(peptides_covered_by_best))
        elif method == 'heap':
            import heapq
            target_coverage = {target: covered_peptides & peptides_to_cover 
                            for target, covered_peptides in target_to_peptides_copy.items()}
            target_heap = [(-len(covered), target) for target, covered in target_coverage.items()]
            heapq.heapify(target_heap)

            with tqdm(total=len(peptides_to_cover), desc="Covering peptides") as pbar:
                while peptides_to_cover:
                    while target_heap:
                        max_covered, best_target = heapq.heappop(target_heap)
                        if best_target in target_coverage:
                            peptides_covered_by_best = target_coverage.pop(best_target)
                            break

                    if not best_target or not peptides_covered_by_best:
                        break

                    selected_targets.add(best_target)
                    peptides_to_cover -= peptides_covered_by_best
                    pbar.update(len(peptides_covered_by_best))

                    for target in list(target_coverage.keys()):
                        if target_coverage[target] & peptides_covered_by_best:
                            target_coverage[target] -= peptides_covered_by_best
                            heapq.heappush(target_heap, (-len(target_coverage[target]), target))
                            if not target_coverage[target]:
                                del target_coverage[target]
        else:
            raise ValueError(f"Invalid greedy method: {method}. Must be ['greedy' or 'heap']")
        
        
        print(f'Minium target number: {len(selected_targets)}')
        return selected_targets

    def _update_output_dict(self, target_list, sample_name, intensity):
        if len(target_list) == 1:
            target = target_list[0]
            self.res_intensity_dict.setdefault(sample_name, {}).setdefault(target, 0)
            self.res_intensity_dict[sample_name][target] += intensity
        else:
            if self.share_intensity:
                intensity /= len(target_list)
                for target in target_list:
                    self.res_intensity_dict.setdefault(sample_name, {}).setdefault(target, 0)
                    self.res_intensity_dict[sample_name][target] += intensity

            else: # assign the intensity to the 1st target
                self.__multi_target_count += 1
                target = target_list[0]
                self.res_intensity_dict.setdefault(sample_name, {}).setdefault(target, 0)
                self.res_intensity_dict[sample_name][target] += intensity

# Example usage:
# Assuming df is your pandas dataframe and column_map is your dictionary
if __name__ == '__main__':
    df = pd.read_csv('OTF.tsv', sep='\t')
    df_meta = pd.read_csv('meta.txt', sep='\t')
    sample_list = df_meta['Samples'].unique().tolist()
    sample_list = ["Intensity_" + sample for sample in sample_list]
    
    column_map = {
        'peptide': 'Sequence',
        'target': 'Proteins',
        'sample_list': sample_list  # ['Sample1', 'Sample2', 'Sample3']
    }
    sia = RazorSum(df, column_map)
    
    res_df = sia.sum_protein_intensity(greedy_method='heap')
    res_df.to_csv('razor_protein_intensity.tsv', sep='\t')

    # or get minimum target set only
    # mini_target_set = sia.get_mini_target_set(greedy_method='heap')

