# This file is used to sum the protein intensity for each sample
# Method: razor, anti-razor or rank
# By sample: True or False
# Output: a dataframe with protein as index and sample as columns
############################################## 
# USAGE:
# from utils.AnalyzerUtils.SumProteinIntensity import SumProteinIntensity
# out = SumProteinIntensity(sw)
# df0 = out.sum_protein_intensity(method='razor')
# df1 = out.sum_protein_intensity(method='rank', by_sample=False, rank_method='all_counts')
# df2 = out.sum_protein_intensity(method='rank', by_sample=False, rank_method='shared_intensity')
# df3 = out.sum_protein_intensity(method='rank', by_sample=False, rank_method='unique_counts')
# df4 = out.sum_protein_intensity(method='anti-razor')
##############################################

from collections import defaultdict
import pandas as pd
from tqdm import tqdm
from .razor_sum import RazorSum


class SumProteinIntensity:
    def __init__(self, taxa_func_analyzer, df=None, peptide_num_threshold=1, protein_separator=';'):
        self.tfa = taxa_func_analyzer
        self.res_intensity_dict = {}  # store all sample to output
        self.rank_dict = {}  # store the rank of protein intensity for each sample temporarily
        self.rank_method = None  # only used for rank method
        self.extract_col_name = [self.tfa.peptide_col_name, self.tfa.protein_col_name] + self.tfa.sample_list
        self.df = self.tfa.original_df.loc[:, self.extract_col_name] if df is None else df.loc[:, self.extract_col_name]
        self._init_dicts()
        self.greedy_method = None  # only used for razor method
        self.share_intensity = False
        self.__multi_target_count = 0
        self.peptide_num_threshold = peptide_num_threshold # the protein must have at least 3 peptides to be considered as a target
        self.protein_separator = protein_separator

        
    def check_protein_col(self):
        # if any NA, '', or empty in the protein column, raise error
        if self.df[self.tfa.protein_col_name].isnull().values.any():
            raise ValueError(f'There are NA values in {self.tfa.protein_col_name} column')

        if (self.df[self.tfa.protein_col_name].str.strip() == '').any():
            raise ValueError(f'There are empty values in {self.tfa.protein_col_name} column')
    
    def get_razor_pep_df(self, greedy_method='heap'):
        razor_integrator = RazorSum(df=self.df, 
                            column_map={
                                        'peptide': self.tfa.peptide_col_name,
                                        'target': self.tfa.protein_col_name,
                                        'sample_list': self.tfa.sample_list,
                                    }, 
                            peptide_num_threshold=self.peptide_num_threshold, 
                            share_intensity=self.share_intensity, 
                            greedy_method=greedy_method,
                            protein_separator= self.protein_separator)
        df = razor_integrator.get_razor_pep_df(greedy_method = greedy_method)
        return df
    
    def sum_protein_intensity(self, method='razor', by_sample=False, rank_method='unique_counts',
                              greedy_method='heap', peptide_num_threshold=None, quant_method: str = 'sum'):
        '''
        method: str, default 'razor'
            options: ['razor', 'anti-razor', 'rank']
        by_sample: bool, default False. only used for `rank` method
            if True, calculate the protein set for each sample, then sum the intensity
        rank_method: str, default 'shared_intensity'. only used for `rank` method
            options: ['shared_intensity', 'all_counts', 'unique_counts', 'unique_intensity']
        greedy_method: str, default 'heap'. only used for `razor` method
            options: ['greedy', 'heap']
        peptide_num_threshold: int, default None
            the protein must have at least 3 peptides to be considered as a target
        quant_method: str, default 'sum'
            options: ['sum', 'lfq']
        '''
        if method not in ['razor', 'anti-razor', 'rank']:
            raise ValueError('Method must in ["razor", "anti-razor", "rank"]')
        if rank_method not in ['shared_intensity', 'all_counts', 'unique_counts', 'unique_intensity']:
            raise ValueError('Rank method must in ["shared_intensity", "all_counts", "unique_counts", "unique_intensity"]')
        if greedy_method not in ['greedy', 'heap']:
            raise ValueError('Greedy method must in ["greedy", "heap"]')
        if peptide_num_threshold is not None:
            self.peptide_num_threshold = peptide_num_threshold
        
        # remove the protein with less than the threshold of peptides
        # use teh methood in RazorSum
        razor_integrator = RazorSum(df=self.df, 
                                    column_map={
                                                'peptide': self.tfa.peptide_col_name,
                                                'target': self.tfa.protein_col_name,
                                                'sample_list': self.tfa.sample_list,
                                            }, 
                                    peptide_num_threshold=self.peptide_num_threshold, 
                                    share_intensity=self.share_intensity, 
                                    greedy_method=greedy_method,
                                    protein_separator= self.protein_separator)
        
        self.rank_method = rank_method
        self.check_protein_col()
        
        self.df = razor_integrator.remove_protein_less_than_threshold()
        self.tfa.peptide_num_used['protein'] = len(self.df)
        
        if method == 'rank':
            print(f"\n-------------Start to sum protein intensity using method: [{method}]  by_sample: [{by_sample}] rank_method: [{rank_method}]-------------")   
            # make a dict to count the intensity of each protein, intensity sahred by peptides will be divided by the number of peptides
            if by_sample:
                for sample in self.tfa.sample_list:
                    # update the dict for each sample
                    print(f'Creating protein rank dict for [{sample}] by shared intensity', end='\r')
                    self._update_protein_rank_dict(sample_name = sample, rank_method = rank_method)
                    self._sum_protein_rank(sample, by_sample)
                    
            else: # without sample
                # only need to create the dict once
                print(f'Creating protein rank dict for all samples by [{rank_method}]', end='\r')
                # sample_name set as '_all_samples'
                self._update_protein_rank_dict(sample_name = None, rank_method = rank_method)
 
                for sample in self.tfa.sample_list:
                    self._sum_protein_rank(sample, by_sample)
        elif method == 'razor':
            print('start to sum protein intensity using method: [razor]')
            if quant_method == 'sum':
                razor_integrator.peptide_num_threshold = 1 # set the threshold to 1, to avoid run filter again
                res_df = razor_integrator.sum_protein_intensity(greedy_method=greedy_method)
            elif quant_method == 'lfq':
                from .lfq import run_lfq
                df_pep = razor_integrator.get_razor_pep_df(greedy_method = greedy_method)
                df_pep.drop(columns=['Proteins_group'], inplace=True)
                df_protein, _ = run_lfq(df_pep, protein_id=self.tfa.protein_col_name, quant_id=self.tfa.peptide_col_name)
                res_df = df_protein.set_index(self.tfa.protein_col_name)
                #add a column of all peptide of the protein
                res_df['peptides'] = res_df.index.map(lambda x: ';'.join(razor_integrator.filtered_target_to_peptides[x]))
                # add a column of the peptide number of the protein
                res_df['peptide_num'] = res_df.index.map(lambda x: len(razor_integrator.filtered_target_to_peptides[x]))
                # move teh 2 columns to the front
                res_df = res_df[['peptides', 'peptide_num'] + [col for col in res_df.columns if col not in ['peptides', 'peptide_num']]]
                
            return res_df       
        
        elif method == 'anti-razor':
            print(f"\n-------------Start to sum protein intensity using method: [{method}]  by_sample: [True] rank_method: [Shared]-------------")
            for sample in self.tfa.sample_list:
                self._sum_protein_anti_razor(sample)
        

        
        res_df= pd.DataFrame.from_dict(self.res_intensity_dict)
        # fill na with 0
        res_df.fillna(0, inplace=True)
        # set index name
        res_df.index.name = self.tfa.protein_col_name
        
        print(f'\nTotal number of proteins: {len(res_df)}\n')
        # check i any row is all 0, if yes, remove it
        if (res_df == 0).all(axis=1).any():
            res_df = res_df[~(res_df == 0).all(axis=1)]
            print(f'After removing, total number of proteins: {len(res_df)}\n')
        print("-------------Finish summing protein intensity.-------------\n")
        
        return res_df

    # razor method
    def find_minimum_protein_set(self, peptides, protein_to_peptides):
        protein_to_peptides_copy = protein_to_peptides.copy()
        print(f'Current target number: {len(protein_to_peptides)}')
        peptides_to_cover = set(peptides)
        selected_proteins = set()
        method = self.greedy_method
        
        if method == 'greedy':
            print('Start creating protein dict for "Set Cover Problem" with [Greedy] Approximation Algorithm')
            with tqdm(total=len(peptides_to_cover), desc="Covering peptides") as pbar:
                while peptides_to_cover:
                    best_protein = None
                    peptides_covered_by_best = set()
                    for protein, covered_peptides in protein_to_peptides_copy.items():
                        covered = peptides_to_cover & covered_peptides
                        if len(covered) > len(peptides_covered_by_best):
                            best_protein = protein
                            peptides_covered_by_best = covered

                    if not best_protein:
                        break

                    selected_proteins.add(best_protein)
                    peptides_to_cover -= peptides_covered_by_best
                    protein_to_peptides_copy.pop(best_protein)  # remove the protein from the dict to speed up the process
                    pbar.update(len(peptides_covered_by_best))
        elif method == 'heap':
            import heapq
            print('Start creating protein dict for "Set Cover Problem" with [Heap Optimization] of Greedy Approximation Algorithm')
            protein_coverage = {protein: covered_peptides & peptides_to_cover 
                                for protein, covered_peptides in protein_to_peptides_copy.items()}
            protein_heap = [(-len(covered), protein) for protein, covered in protein_coverage.items()]
            heapq.heapify(protein_heap)

            with tqdm(total=len(peptides_to_cover), desc="Covering peptides") as pbar:
                while peptides_to_cover:
                    while protein_heap:
                        max_covered, best_protein = heapq.heappop(protein_heap)
                        if best_protein in protein_coverage:
                            peptides_covered_by_best = protein_coverage.pop(best_protein)
                            break

                    if not best_protein or not peptides_covered_by_best:
                        break

                    selected_proteins.add(best_protein)
                    peptides_to_cover -= peptides_covered_by_best
                    pbar.update(len(peptides_covered_by_best))

                    # update other proteins' coverage
                    for protein in list(protein_coverage.keys()):
                        if protein_coverage[protein] & peptides_covered_by_best:
                            protein_coverage[protein] -= peptides_covered_by_best
                            heapq.heappush(protein_heap, (-len(protein_coverage[protein]), protein))
                            if not protein_coverage[protein]:
                                del protein_coverage[protein]
        else:
            raise ValueError(f"Invalid greedy method: {method}. Must be ['greedy' or 'heap']")
        
        print(f'Minium target number: {len(selected_proteins)}')
        return selected_proteins
    
    def _create_pep_to_protein_razor(self) -> dict:
        """
        Create a dictionary mapping peptides to proteins based on a minimum protein set.

        Returns:
            dict: A dictionary mapping peptides to proteins.
            key: peptide
            value: a list of proteins
        """
        
        df = self.df.loc[:, [self.tfa.peptide_col_name, self.tfa.protein_col_name]]
        # Create a dictionary mapping proteins to peptides
        protein_to_peptides = defaultdict(set)
        peptides = set(df[self.tfa.peptide_col_name])

        separator = self.protein_separator
        for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Creating protein to peptides mapping"):
            sequence = row[self.tfa.peptide_col_name]
            proteins = row[self.tfa.protein_col_name].split(separator)
            for protein in proteins:
                protein_to_peptides[protein].add(sequence)

        mini_protein_set = self.find_minimum_protein_set(peptides, protein_to_peptides)
        
        # remove the proteins not in the mini_protein_set from the protein_to_peptides
        filtered_protein_to_peptides = {protein: protein_to_peptides[protein] for protein in mini_protein_set}
        # Assign each peptide to the protein that contains it with the highest peptide count
        print('Assigning peptides to proteins')
        peptide_to_protein = defaultdict(list)
        for peptide in tqdm(peptides, desc="Assigning peptides to proteins"):
            possible_proteins = [protein for protein, peps in filtered_protein_to_peptides.items() if peptide in peps]
            if possible_proteins:
                # 找到包含该肽最多的蛋白质
                max_protein_count = max(len(filtered_protein_to_peptides[protein]) for protein in possible_proteins)
                best_proteins = [protein for protein in possible_proteins if len(filtered_protein_to_peptides[protein]) == max_protein_count]
                peptide_to_protein[peptide].extend(best_proteins)
        
        return peptide_to_protein
    
    def _sum_protein_razor(self, peptide_to_protein: dict):
        
        for sample in tqdm(self.tfa.sample_list):
            print(f'Assigning protein intensity for [{sample}]')
            df = self.df.loc[:,[ self.tfa.peptide_col_name, sample]]
            # create a dict to store the intensity of each peptide
            df.set_index(self.tfa.peptide_col_name, inplace=True)
            peptide_intensity_dict = df.to_dict()[sample]
            for peptide, proteins in peptide_to_protein.items():
                intensity = peptide_intensity_dict[peptide]
                self._update_output_dict(proteins, sample, intensity)
            

        
    def _init_dicts(self):
        for sample in self.tfa.sample_list:
            self.res_intensity_dict[sample] = {}
            self.rank_dict[sample] = {}
            self.rank_dict['_all_samples'] = {}
            

    def _update_protein_rank_dict(self, sample_name = None, rank_method = None):
        
        def update_by_intesity(df, sample_name=sample_name, method=rank_method):
            separator = self.protein_separator

            for row in df.itertuples():
                proteins = row[1].split(separator)
                shared_times = len(proteins)

                if method == 'shared_intensity':
                    shared_intensity = row[2]/shared_times
                elif method == 'all_counts':
                    shared_intensity = 1
                elif method == 'unique_counts':
                    if shared_times == 1:
                        shared_intensity = 1
                    else:   
                        shared_intensity = 0
                elif method == 'unique_intensity':
                    if shared_times == 1:
                        shared_intensity = row[2]
                    else:   
                        shared_intensity = 0
                    
                for protein in proteins:
                    if protein in self.rank_dict[sample_name].keys():
                        self.rank_dict[sample_name][protein] += shared_intensity
                    else:
                        self.rank_dict[sample_name][protein] = shared_intensity
            
        
        if sample_name is None:
            sample_name = '_all_samples'
            df = self.df.loc[:,[ self.tfa.protein_col_name ]]
            if 'intensity' in self.rank_method:
                df['intensity'] = self.df[self.tfa.sample_list].sum(axis=1)
            else: # count
                df['peptide_count'] = 1
            # rank method:[shared, count, unique]
            update_by_intesity(df, sample_name, method=rank_method)

                            
        else: 
            df = self.df.loc[:,[ self.tfa.protein_col_name, sample_name ]]
            update_by_intesity(df, sample_name, method=rank_method)
        
                            


    def _update_output_dict(self, protein_list: list, sample_name:str, intensity:float):
        if len(protein_list) == 1:
            protein = protein_list[0]
            if protein in self.res_intensity_dict[sample_name].keys():
                self.res_intensity_dict[sample_name][protein] += intensity
            else:
                self.res_intensity_dict[sample_name][protein] = intensity
        else:
            if self.share_intensity:
                intensity = intensity/len(protein_list)
                for protein in protein_list:
                    self.res_intensity_dict.setdefault(sample_name, {}).setdefault(protein, 0)
                    self.res_intensity_dict[sample_name][protein] += intensity
            else:
                self.__multi_target_count += 1
                protein = protein_list[0]
                self.res_intensity_dict.setdefault(sample_name, {}).setdefault(protein, 0)
                self.res_intensity_dict[sample_name][protein] += intensity
                
                
                
                    
    def _sum_protein_rank(self, sample_name:str, by_sample=False):
        # print in one line
        print(f'Asigning protein intensity for [{sample_name}]', end='\r')
        df = self.df.loc[:,[ self.tfa.protein_col_name, sample_name]]
        separator = self.protein_separator

        for row in df.itertuples():
            proteins = row[1].split(separator)
            intensity = row[2]
            if len(proteins) == 1:
                self._update_output_dict(proteins, sample_name, intensity)

            else: 
                # check which protein has the highest intensity, then use this protein as the representative protein
                # extract sub dict for these proteins
                if by_sample:
                    sub_dict = {key: self.rank_dict[sample_name][key] for key in proteins}
                else:
                    sub_dict = {key: self.rank_dict['_all_samples'][key] for key in proteins}
                    
                    
                    
                max_value = max(sub_dict.values())  
                max_proteins = [protein for protein, value in sub_dict.items() if value == max_value]  # find the protein with the highest intensity                
                self._update_output_dict(max_proteins, sample_name, intensity)

        
    def _sum_protein_anti_razor(self, sample_name:str):
        print(f'Creating protein intensity dict for [{sample_name}]', end='\r')
        df = self.df.loc[:,[ self.tfa.protein_col_name, sample_name]]
        self.share_intensity = True
        separator = self.protein_separator
        for row in df.itertuples():
            proteins = row[1].split(separator)
            intensity = row[2]
            self._update_output_dict(proteins, sample_name, intensity)