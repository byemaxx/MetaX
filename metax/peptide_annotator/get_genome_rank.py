import pandas as pd
from tqdm import tqdm
from collections import defaultdict



class GenomeRank:
    def __init__(self, df, peptide_column,  genome_column, genome_separator):
        self.df = df
        self.peptide_column = peptide_column
        self.genome_column = genome_column
        self.genome_separator = genome_separator
        self._remove_empty_genomes(df, genome_column)
        self.df_results_by_rank = None
        self.target_to_peptides = None
        self.df_combined = None
    
    
    def _remove_empty_genomes(self, df, genome_column):
        na_count = df[genome_column].isna().sum()
        if na_count > 0:
            print(f"Removing {na_count} rows with empty genomes")
            df = df[df[genome_column].notna()]
            print(f"After removing empty genomes: {df.shape}")
        return df
        
    def _create_target_to_peptides(self, df, peptide_column, target_column, protein_separator):
        """
        Create a dictionary mapping targets to peptides.

        """
        # df = self.df.loc[:, [self.column_map['peptide'], self.column_map['target']]]
        df = df.loc[:, [peptide_column, target_column]]
        target_to_peptides = defaultdict(set)

        for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Creating target to peptides mapping"):
            # sequence = row[self.column_map['peptide']]
            sequence = row[peptide_column]
            # targets = row[self.column_map['target']].split(self.protein_separator)
            targets = row[target_column].split(protein_separator)
            for target in targets:
                target_to_peptides[target].add(sequence)
        
        self.target_to_peptides = target_to_peptides
        return target_to_peptides


    def _get_distinct_genomes(self, df, genome_column, genome_separator) -> pd.DataFrame:
        # count distinct peptides for each genome
        dft = df.loc[:, [genome_column]]
        dft['count'] = dft[genome_column].apply(lambda x: len(x.split(genome_separator)))
        df_genome_distinct = dft[[genome_column, 'count']].astype({'count': 'int'})
        df_genome_distinct = df_genome_distinct[df_genome_distinct['count'] == 1]
        df_genome_distinct = df_genome_distinct.groupby(genome_column).size().sort_values(ascending=False).reset_index(name='distinct_count')
        
        # set 0 for genomes with no distinct peptides
        all_genomes = set(df[genome_column].str.split(genome_separator).explode().unique())
        distinct_genomes = set(df_genome_distinct[genome_column])
        missing_genomes = all_genomes - distinct_genomes
        
        # create a DataFrame for missing genomes
        df_missing = pd.DataFrame({genome_column: list(missing_genomes), 'distinct_count': 0})
        
        # concatenate the two DataFrames
        df_genome_distinct = pd.concat([df_genome_distinct, df_missing], ignore_index=True)
        return df_genome_distinct


    def _calculate_peptide_counts(self):
        peptide_counts = {target: len(peptides) for target, peptides in self.target_to_peptides.items()}
        df_peptide_counts = pd.DataFrame(list(peptide_counts.items()), columns=[self.genome_column, 'peptide_count'])
        # sort by peptide count in descending order
        df_peptide_counts = df_peptide_counts.sort_values(by='peptide_count', ascending=False).reset_index(drop=True)
        return df_peptide_counts

    def _calculate_genome_coverage(self, genome_rank_list, target_to_peptides):
        unique_peptides = set()
        cumulative_counts = []
        new_counts = []

        for target in genome_rank_list:
            peptides = target_to_peptides[target]
            # Calculate new peptides that are not in the unique_peptides set
            new_peptides = peptides - unique_peptides
            unique_peptides.update(new_peptides)
            # Append counts
            cumulative_counts.append(len(unique_peptides))
            new_counts.append(len(new_peptides))

        df_results_by_rank = pd.DataFrame({
            self.genome_column: genome_rank_list,
            'cumulative_peptides': cumulative_counts,
            'added_peptides': new_counts,
        })
        df_results_by_rank['coverage_ratio'] = df_results_by_rank['cumulative_peptides'] / len(unique_peptides)
        # df_results_rank_by_distinct['peptide_in_target'] = df_results_rank_by_distinct['Target'].apply(lambda x: len(target_to_peptides[x]))
        return df_results_by_rank

    def _calculate_turning_point(self, df_results_by_rank, window_size = 20, std_threshold = 1):
        rolling_std = df_results_by_rank['cumulative_peptides'].rolling(window=window_size).std()
        std_threshold = rolling_std.mean() * std_threshold
        # print(f"Threshold: {std_threshold}")
        turning_point_idx = (rolling_std[rolling_std < std_threshold].index[0]
                            if (rolling_std < std_threshold).any() else None)

        print(f"Turning point index: {turning_point_idx}")
        return turning_point_idx

    
    def _calculate_combined_rank(self, df_genome_distinct, df_peptide_counts, weight_distinct=0.9, weight_peptide=0.1):
        # Normalize counts for distinct and peptide counts
        df_genome_distinct['distinct_score'] = df_genome_distinct['distinct_count'] / df_genome_distinct['distinct_count'].max()
        df_peptide_counts['peptide_score'] = df_peptide_counts['peptide_count'] / df_peptide_counts['peptide_count'].max()
        
        # Merge the two DataFrames on the genome column
        df_combined = pd.merge(df_genome_distinct[[self.genome_column, 'distinct_score']], 
                               df_peptide_counts[[self.genome_column, 'peptide_score']], 
                               on=self.genome_column, how='outer').fillna(0)

        # Calculate combined score with weights
        df_combined['combined_score'] = df_combined['distinct_score'] * weight_distinct + df_combined['peptide_score'] * weight_peptide

        # remove genome not in distinct genome list
        # print(f'Number of genomes before filtering: {df_combined.shape[0]}')
        # df_combined = df_combined[df_combined['distinct_score'] > 0]
        # print(f'Number of genomes with distinct peptides: {df_combined.shape[0]}')
        
        
        # Sort genomes by combined score in descending order
        df_combined = df_combined.sort_values(by='combined_score', ascending=False).reset_index(drop=True)
        self.df_combined = df_combined
        return df_combined
    
    
    def get_rank_covre_df(self, genome_rank_method='combined', weight_distinct=0.9, weight_peptide=0.1):
        print(f"Calculating genome coverage using [{genome_rank_method}] method")
        
        target_to_peptides = self._create_target_to_peptides(self.df, self.peptide_column, self.genome_column, self.genome_separator)
        
        if genome_rank_method == 'distinct_number':
            df_genome_distinct = self._get_distinct_genomes(self.df, self.genome_column, self.genome_separator)
            genome_rank_list = df_genome_distinct[self.genome_column].tolist()
        elif genome_rank_method == 'peptide_number':
            genome_rank_list = sorted(target_to_peptides.keys(), key=lambda x: len(target_to_peptides[x]), reverse=True)
        elif genome_rank_method == 'combined':
            print(f"weight_distinct={weight_distinct}, weight_peptide={weight_peptide}")
            df_genome_distinct = self._get_distinct_genomes(self.df, self.genome_column, self.genome_separator)
            df_peptide_counts = self._calculate_peptide_counts()
            df_combined = self._calculate_combined_rank(df_genome_distinct, df_peptide_counts, weight_distinct, weight_peptide)
            genome_rank_list = df_combined[self.genome_column].tolist()
        else:
            raise ValueError("Invalid genome_rank_method")
        
        print("1st round for genome coverage")
        df_results_by_rank = self._calculate_genome_coverage(genome_rank_list, target_to_peptides)
        # use "add_peptides" as the rank
        print("2nd round for genome coverage")
        df_results_by_rank.sort_values(by='added_peptides', ascending=False, inplace=True)
        new_genome_rank_list = df_results_by_rank[self.genome_column].tolist()
        df_results_by_rank = self._calculate_genome_coverage(new_genome_rank_list, target_to_peptides)
        # again use "add_peptides" as the rank
        print("3rd round for genome coverage")
        df_results_by_rank.sort_values(by='added_peptides', ascending=False, inplace=True)
        new_genome_rank_list = df_results_by_rank[self.genome_column].tolist()
        df_results_by_rank = self._calculate_genome_coverage(new_genome_rank_list, target_to_peptides)
        self.df_results_by_rank = df_results_by_rank
        return df_results_by_rank
    
    
    def get_rank_list_by_distinct_number(self):
        if self.df_results_by_rank is None:
            df_results_by_rank = self.get_rank_covre_df()
        df_results_by_rank = self.df_results_by_rank
        genome_rank_list = df_results_by_rank[self.genome_column].tolist()
        return genome_rank_list
    
    def get_rank_list_by_peptide_number(self):
        if self.target_to_peptides is None:
            self._create_target_to_peptides(self.df, self.peptide_column, self.genome_column, self.genome_separator)
        target_to_peptides = self.target_to_peptides
        genome_rank_list = sorted(target_to_peptides.keys(), key=lambda x: len(target_to_peptides[x]), reverse=True)
        return genome_rank_list        
        
    
    def get_turning_point(self, df_results_by_rank=None,window_size = 20, std_threshold = 1):
        df_results_by_rank = df_results_by_rank if df_results_by_rank is not None else self.df_results_by_rank
        if self.df_results_by_rank is None:
            raise ValueError("Please call get_rank_covre_df() first")
        
        turning_point_idx = self._calculate_turning_point(self.df_results_by_rank, window_size, std_threshold)
        return turning_point_idx
    

# if __name__ == '__main__':
#     dft = pd.read_csv('test_data/diann_res_annotation.tsv', sep='\t')
#     # dft = dft.head(10000)
#     gr = GenomeRank(dft, 'Stripped.Sequence', 'uhgp_genomes', ';')
#     df_results_rank_by_distinct = gr.get_rank_covre_df(genome_rank_method='combined')
#     turning_point_idx = gr.get_turning_point()
    

    
