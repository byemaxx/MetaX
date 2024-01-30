# This file is used to sum the protein intensity for each sample
# Method: razor or anti-razor
# By sample: True or False
# Output: a dataframe with protein as index and sample as columns
############################################## 
# USAGE:
# from utils.AnalyzerUtils.SumProteinIntensity import SumProteinIntensity
# out = SumProteinIntensity(sw)
# df1 = out.sum_protein_intensity(method='razor', by_sample=False, rank_method='count')
# df2 = out.sum_protein_intensity(method='razor', by_sample=False, rank_method='shared')
# df3 = out.sum_protein_intensity(method='razor', by_sample=False, rank_method='unique')
# df4 = out.sum_protein_intensity(method='anti-razor')
##############################################

import pandas as pd

class SumProteinIntensity:
    def __init__(self, taxa_func_analyzer):
        self.tfa = taxa_func_analyzer
        self.res_intensity_dict = {} #store all sample to output
        self.rank_dict = {} #store the rank of protein intensity for each sample temporarily
        self.rank_method = None
        self.extract_col_name = [self.tfa.peptide_col_name, self.tfa.protein_col_name] + self.tfa.sample_list
        self.df = self.tfa.original_df.loc[:,self.extract_col_name]
        self._init_dicts()

            
    def sum_protein_intensity(self, method='razor', by_sample=False, rank_method='unique_counts'):

        if method not in ['razor', 'anti-razor']:
            raise ValueError('Method must in ["razor", "anti-razor"]')
        if rank_method not in ['shared_intensity', 'all_counts', 'unique_counts', 'unique_intensity']:
            raise ValueError('Rank method must in ["shared_intensity", "all_counts", "unique_counts", "unique_intensity"]')
        
        self.rank_method = rank_method
        
        if method == 'razor':
            print(f"\n-------------Start to sum protein intensity using method: [{method}]  by_sample: [{by_sample}] rank_method: [{rank_method}]-------------")   
            # make a dict to count the intensity of each protein, intensity sahred by peptides will be divided by the number of peptides
            if by_sample:
                for sample in self.tfa.sample_list:
                    # update the dict for each sample
                    print(f'Creating protein rank dict for [{sample}] by shared intensity', end='\r')
                    self._update_protein_rank_dict(sample_name = sample, rank_method = rank_method)
                    self._sum_protein_razor(sample, by_sample)
                    
            else: # without sample
                # only need to create the dict once
                print(f'Creating protein rank dict for all samples by [{rank_method}]', end='\r')
                # sample_name set as '_all_samples'
                self._update_protein_rank_dict(sample_name = None, rank_method = rank_method)
 
                for sample in self.tfa.sample_list:
                    self._sum_protein_razor(sample, by_sample)
                    
        
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

    
    def _init_dicts(self):
        for sample in self.tfa.sample_list:
            self.res_intensity_dict[sample] = {}
            self.rank_dict[sample] = {}
            self.rank_dict['_all_samples'] = {}
            

    def _update_protein_rank_dict(self, sample_name = None, rank_method = None):
        
        def update_by_intesity(df, sample_name=sample_name, method=rank_method):
            for row in df.itertuples():
                proteins = row[1].split(';')
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
            intensity = intensity/len(protein_list)
            for protein in protein_list:
                if protein in self.res_intensity_dict[sample_name].keys():
                    self.res_intensity_dict[sample_name][protein] += intensity
                else:
                    self.res_intensity_dict[sample_name][protein] = intensity
                    
                    
    def _sum_protein_razor(self, sample_name:str, by_sample=False):
        # print in one line
        print(f'Asigning protein intensity for [{sample_name}]', end='\r')
        df = self.df.loc[:,[ self.tfa.protein_col_name, sample_name]]

        for row in df.itertuples():
            proteins = row[1].split(';')
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

        for row in df.itertuples():
            proteins = row[1].split(';')
            intensity = row[2]
            self._update_output_dict(proteins, sample_name, intensity)



