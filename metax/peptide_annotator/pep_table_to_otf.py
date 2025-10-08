# This script is used to annotate peptides with their corresponding proteins of a Table.
# input: peptide_table
# output: peptide_table with an additional column of proteins

# main steps:
# 1. load peptide_table and preprocess if necessary
# 2. annotate peptides with proteins
# 3. reduce proteins by genome ranking
# 4. save the annotated peptide_table or transfer to OTF annotator

#TODO:
# 1. add mutiple prefix options for intensity columns
# 2. add refine samples name function. e.g. D:/path/to/file/xxx.raw -> xxx


import sqlite3
import json
import pandas as pd
from tqdm import tqdm
import pathlib

if __name__ == "__main__":
    from get_genome_rank import GenomeRank
    from peptable_annotator import PeptideAnnotator

else:
    from .get_genome_rank import GenomeRank
    from .peptable_annotator import PeptideAnnotator

def query_peptide_proteins(db_file, peptide_list, chunk_size=10000, removed_genomes_set:set|None = None):
    """
    Query peptide to protein mapping from a database with progress tracking.
    
    Args:
        db_file (str): The file path to the SQLite database.
        peptide_list (list of str): A list of peptide sequences to query.
        chunk_size (int): The number of peptides to query in one batch (default: 10000).
        
    Returns:
        dict: A dictionary mapping peptide sequences to a semicolon-separated string of proteins.
    """
    
    peptide_proteins = {}

    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        for i in tqdm(range(0, len(peptide_list), chunk_size), desc="Querying database in chunks"):
            chunk = peptide_list[i:i + chunk_size]
            query = "SELECT peptide, proteins FROM peptide_proteins WHERE peptide IN ({})".format(
                ','.join(['?'] * len(chunk))
            )
            cursor.execute(query, chunk)
            rows = cursor.fetchall()

            for peptide, proteins_json in rows:  
                try:
                    proteins = json.loads(proteins_json)
                except json.JSONDecodeError:
                    peptide_proteins[peptide] = ""
                    continue
                if removed_genomes_set:
                    proteins = [p for p in proteins if p.split('_', 1)[0] not in removed_genomes_set]
                peptide_proteins[peptide] = ';'.join(proteins) if proteins else ""

    return peptide_proteins


class peptideProteinsMapper:
    def __init__(self, peptide_table_path, db_path, 
                 removed_genomes_set:set|None = None,
                 table_separator='\t',
                 peptide_col='Sequence', 
                 intensity_col_prefix='Intensity',
                 genome_cutoff_rank:int|None= None,   # if set, it will only get the top N genomes, otherwise use genome_peptide_coverage_cutoff
                 genome_peptide_coverage_cutoff:float|None = 0.97,
                 protein_peptide_coverage_cutoff:float|None = 1.0,
                 output_path=None,
                 temp_dir=None,
                 stop_after_genome_ranking=False,
                 continue_base_on_annotaied_peptide_table=False, # use genome annotated peptide table to continue the process, skip querying proteins
                 turn_point_method='auto', # 'auto', 'coverage', 'rank', or 'distinct_count'
                 turn_point_distinct_cutoff=3 # cutoff value for distinct_count method
                 ):

        self.peptide_table_path = peptide_table_path
        self.db_file = db_path
        self.removed_genomes_set = removed_genomes_set
        self.table_separator = table_separator
        self.peptide_col = peptide_col
        self.intensity_col_prefix = intensity_col_prefix
        self.genome_cutoff_rank = genome_cutoff_rank 
        self.genome_peptide_coverage_cutoff = genome_peptide_coverage_cutoff
        self.protein_peptide_coverage_cutoff = protein_peptide_coverage_cutoff
        self.output_path = output_path
        self.temp_dir = None
        self.stop_after_genome_ranking = stop_after_genome_ranking
        self.continue_base_on_annotaied_peptide_table = continue_base_on_annotaied_peptide_table
        self.turn_point_method = turn_point_method # 'auto', 'coverage', 'rank', or 'distinct_count'
        self.turn_point_distinct_cutoff = turn_point_distinct_cutoff # cutoff value for distinct_count method
        
        self.has_intensity = False
        self.protein_ranked_table = None
        self.genome_ranked_table = None
        self.final_peptide_table = None
        
        self.selected_proteins_num = 0
        self.selected_genomes_num = 0
        self.original_peptides_before_mapping = 0
        self.peptides_after_mapping = 0
        self.removed_peptides_no_matched = 0
        
        self.set_temp_dir(temp_dir)
        self.peptide_table = self.load_peptide_table()
    
    def load_peptide_table(self):
        print("Loading peptide table...")
        
        header_df = pd.read_csv(self.peptide_table_path, sep=self.table_separator, nrows=0)
        self._check_columns(header_df.columns)
        
        required_cols = [self.peptide_col]
        intensity_cols = [col for col in header_df.columns if col.startswith(self.intensity_col_prefix)]
        
        if self.continue_base_on_annotaied_peptide_table:
            required_cols.extend(['Genomes', 'Proteins'])
        
        required_cols.extend(intensity_cols)
        
        print(f"Reading columns: {required_cols}")
        
        self.peptide_table = pd.read_csv(self.peptide_table_path, sep=self.table_separator, usecols=required_cols)
        
        if intensity_cols:
            self.has_intensity = True
            print("Intensity columns found, will be kept in the output and used for genome ranking")
            self.sum_duplicates_peptides()
        else:
            print("Warning: Intensity columns not found")
            raise ValueError(f"The intensity columns you specified:[{self.intensity_col_prefix}] are not in the peptide_table, please check!")
        
        return self.peptide_table
    
    def _check_columns(self, columns):
        """Check if the necessary columns are in the peptide table."""
        if self.continue_base_on_annotaied_peptide_table:
            print("Continue base on annotated peptide table")
            print(f"Check if all the necessary columns are in the peptide table\
                \nPeptide column: [{self.peptide_col}]\
                \nIntensity columns prefix: [{self.intensity_col_prefix}]\
                \nGenomes column: [Genomes]\
                \nProteins column: [Proteins]")
            for col in [self.peptide_col, 'Genomes', 'Proteins']:
                if col not in columns:
                    raise ValueError(f"The peptide table should have a column named '{col}'")
        else:
            print(f"Check if all the necessary columns are in the peptide table\
                \nPeptide column: [{self.peptide_col}]\
                \nIntensity columns prefix: [{self.intensity_col_prefix}]")
            if self.peptide_col not in columns:
                raise ValueError(f"The peptide column you specified:[{self.peptide_col}] is not in the peptide_table, please check!")

        if not any([col.startswith(self.intensity_col_prefix) for col in columns]):
            raise ValueError(f"The intensity columns you specified:[{self.intensity_col_prefix}] are not in the peptide_table, please check!")

    def set_temp_dir(self, temp_dir):
        if temp_dir:
            # check if the temp dir valid
            temp_dir = pathlib.Path(temp_dir)
            if not temp_dir.is_dir():
                raise ValueError(f"Invalid temp dir path: {temp_dir}")
            self.temp_dir = temp_dir
            
        else:
            # create a temp dir in output path
            temp_dir = pathlib.Path(self.output_path).parent / 'metax_temp'
            temp_dir.mkdir(parents=True, exist_ok=True)
            self.temp_dir = temp_dir
    
    def sum_duplicates_peptides(self):
        # check if the peptides are unique, if not, combine the intensity columns, sum them up, if na , consider as 0
        # Get all intensity columns
        intensity_cols = [col for col in self.peptide_table.columns if col.startswith(self.intensity_col_prefix)]
        print(f"Found {len(intensity_cols)} intensity columns")

        # Check if peptides are unique
        duplicated_peptides = self.peptide_table[self.peptide_col].duplicated().sum()
        if duplicated_peptides > 0:
            print(f"Found {duplicated_peptides} duplicate peptide entries, combining their intensities")
            
            # Fill NA values with 0 in intensity columns
            self.peptide_table[intensity_cols] = self.peptide_table[intensity_cols].fillna(0)
            
            # Group by peptide and sum the intensity columns
            grouped_table = self.peptide_table.groupby(self.peptide_col)[intensity_cols].sum().reset_index()            
            
            # Get non-intensity columns
            non_intensity_cols = [col for col in self.peptide_table.columns 
                                    if not col.startswith(self.intensity_col_prefix) and col != self.peptide_col]
            
            # Keep the first occurrence of each peptide for other columns
            first_occurrence = self.peptide_table.drop_duplicates(subset=[self.peptide_col])[
                [self.peptide_col] + non_intensity_cols]
            
            # Merge back together
            self.peptide_table = pd.merge(grouped_table, first_occurrence, on=self.peptide_col)
            
            print(f"After combining duplicates: {len(self.peptide_table)} unique peptides")
        else:
            print("No duplicate peptides found, skipping combination of intensities")

    def annotate_peptides(self):
        """ Annotate peptides with proteins by querying the database. """
        print("Start annotating peptides with proteins")
        
        unique_peptides = self.peptide_table[self.peptide_col].drop_duplicates().tolist()

        peptide_proteins_dict = query_peptide_proteins(self.db_file, unique_peptides, removed_genomes_set=self.removed_genomes_set)

        self.peptide_table["Proteins"] = self.peptide_table[self.peptide_col].map(peptide_proteins_dict)

        original_count = len(self.peptide_table)
        self.original_peptides_before_mapping = original_count
        self.peptide_table = self.peptide_table[self.peptide_table["Proteins"].notna() & (self.peptide_table["Proteins"] != "")]
        removed_count = original_count - len(self.peptide_table)
        self.peptides_after_mapping = len(self.peptide_table)
        self.removed_peptides_no_matched = removed_count
        
        print(f"Original peptides: {original_count}, after filtering: {len(self.peptide_table)}")
        print(f"Removed peptides: {removed_count} due to no protein mapped in the database")

        return self.peptide_table

    def extract_genome_col(self, df):
        def extract_genome(proteins):
            if proteins in [None, '', 'NaN']:
                return ''
            proteins = proteins.split(';')
            genomes = []
            for protein in proteins:
                genome = protein.split('_')[0]
                genomes.append(genome)
            genomes = list(set(genomes))
            return ';'.join(genomes)

        df['Genomes'] = df['Proteins'].apply(extract_genome)
        return df
        
    def _update_cutoff_parameters_for_reporting(self, turn_point_method):
        if turn_point_method.lower() == 'auto':
            self.genome_cutoff_rank = "N/A"
            self.turn_point_distinct_cutoff = "N/A"
            self.genome_peptide_coverage_cutoff = "N/A"
        elif turn_point_method.lower() == 'coverage':
            self.genome_cutoff_rank = "N/A"
            self.turn_point_distinct_cutoff = "N/A"
        elif turn_point_method.lower() == 'rank':
            self.turn_point_distinct_cutoff = "N/A"
            self.genome_peptide_coverage_cutoff = "N/A"
        elif turn_point_method.lower() == 'distinct_count':
            self.genome_cutoff_rank = "N/A"
            self.genome_peptide_coverage_cutoff = "N/A"
        else:
            # warning already raised in calculate_genome_list
            pass
        
    def calculate_genome_list(self, df, turn_point_method="auto"):
        gr = GenomeRank(df = df, 
                                 peptide_column = self.peptide_col,
                                 genome_column = 'Genomes',
                                 genome_separator = ';')
        df_results_rank = gr.get_rank_covre_df(genome_rank_method='combined', 
                                                           weight_distinct=1, weight_peptide=0)
        df_weights = gr.df_combined[['Genomes', 'distinct_norm', 'peptide_norm', 'combined_score']]
        df_results_rank = df_results_rank.merge(df_weights, on='Genomes', how='left')
        # svaing the genome ranking table to temp dir
        # df_results_rank.to_csv(f'{self.output_path.replace(".tsv", "_genome_ranked.tsv")}', sep='\t', index=False)
        df_results_rank.to_csv(f'{self.temp_dir}/genome_ranked.tsv', sep='\t', index=False)
        self.genome_ranked_table = df_results_rank
        
        if turn_point_method.lower() == 'auto':
            window_size = 20
            std_threshold = 1
            print(f"Calculating turning point by rolling window: window_size={window_size}, std_threshold={std_threshold}")
            cutoff_index = gr._calculate_turning_point(df_results_rank, window_size, std_threshold)

        elif turn_point_method.lower() == 'coverage':
            if type(self.genome_peptide_coverage_cutoff) not in [float, int] or not (0 < self.genome_peptide_coverage_cutoff < 1): # type: ignore
                self.genome_peptide_coverage_cutoff = 0.97
                print(f"Warning: Invalid genome_peptide_coverage_cutoff: {self.genome_peptide_coverage_cutoff}, should be between 0 and 1. Using default value: 0.97")
                
            print(f"Calculating turning point by percentage cutoff: {self.genome_peptide_coverage_cutoff}")
            cutoff_index = df_results_rank[df_results_rank['coverage_ratio'] >= self.genome_peptide_coverage_cutoff].index[0]
            
        elif turn_point_method.lower() == 'rank' and type(self.genome_cutoff_rank) is int: 
            # make sure rank is less than total genomes, unless use Auto
            if self.genome_cutoff_rank > df_results_rank.shape[0]:
                raise ValueError(f"genome_cutoff_rank: {self.genome_cutoff_rank} is larger than total genomes found: {df_results_rank.shape[0]}, please check!")
            print(f"Get top {self.genome_cutoff_rank} genomes by rank")
            cutoff_index = self.genome_cutoff_rank - 1
            
        elif turn_point_method.lower() == 'distinct_count':
            cutoff_value = self.turn_point_distinct_cutoff
            print(f"Get top genomes with at least {cutoff_value} distinct peptides")
            cutoff_index = df_results_rank[df_results_rank['distinct_peptides_count'] >= cutoff_value].index[-1]
            
        else:
            raise ValueError(f"Invalid turn_point_method: {turn_point_method}, should be 'auto', 'coverage', 'rank', or 'distinct_count'")
        
        # Store the actually used parameters for reporting, set unused ones to 'N/A'
        self._update_cutoff_parameters_for_reporting(turn_point_method)
        
        selected_genomes = df_results_rank.loc[:cutoff_index]
        selected_genomes_list = selected_genomes['Genomes'].tolist()
        print(f'Original genomes: [{df_results_rank.shape[0]}]')
        print(f"The number of selected genomes: [{len(selected_genomes_list)}].\nThe last genome with coverage_ratio: {selected_genomes.iloc[-1]['coverage_ratio']}")
        self.selected_genomes_num = len(selected_genomes_list)
        
        return selected_genomes_list
    
    def calculate_protein_list(self, df):
        print("reducing proteins by genome ranking")
        gr = GenomeRank(df = df,
                                    peptide_column = self.peptide_col,
                                    genome_column = 'Proteins',
                                    genome_separator = ';')
        df_results_rank = gr.get_rank_covre_df(genome_rank_method='combined', iters=3)
        self.protein_ranked_table = df_results_rank
        cutoff_index = df_results_rank[df_results_rank['coverage_ratio'] >= self.protein_peptide_coverage_cutoff].index[0]
        selected_proteins = df_results_rank.loc[:cutoff_index]
        selected_proteins_list = selected_proteins['Proteins'].tolist()
        print(f'Original proteins: [{df_results_rank.shape[0]}]')
        print(f"The number of selected proteins: [{len(selected_proteins_list)}].\nThe last protein with coverage_ratio: {selected_proteins.iloc[-1]['coverage_ratio']}")
        self.selected_proteins_num = len(selected_proteins_list)
        
        return selected_proteins_list

    def reduce_proteins_by_genome(self, df, selected_genomes_list):
        print("Filtering proteins by selected genomes")
        original_peptides = df.shape[0]

        selected_genomes_set = set(selected_genomes_list)
        df['Proteins'] = df['Proteins'].astype(str).str.split(';')
        df['Proteins'] = df['Proteins'].apply(lambda proteins: ';'.join([p for p in proteins if p.split('_')[0] in selected_genomes_set]))
        
        df = df[df['Proteins'] != '']
        
        print(f"Original peptides: {original_peptides}, after filtering: {df.shape[0]}")
        print(f"Removed peptides: {original_peptides - df.shape[0]}, due to no protein left after filtering by selected genomes")
        print("-" * 20)

        if 'Genomes' in df.columns:
            df = df.drop(columns=['Genomes'])

        return df
    
    def reduce_proteins_by_mini_proteins_list(self, df, selected_proteins_list):
        print("Filtering proteins by selected proteins")
        original_peptides = df.shape[0]

        selected_proteins_set = set(selected_proteins_list)  
        df['Proteins'] = df['Proteins'].astype(str).str.split(';')
        df['Proteins'] = df['Proteins'].apply(lambda proteins: ';'.join([p for p in proteins if p in selected_proteins_set]))

        df = df[df['Proteins'] != '']
        
        print(f"Original peptides: {original_peptides}, after filtering: {df.shape[0]}")
        print("-" * 20)
        
        return df


    def process_peptides_to_proteins(self):# main function workflow
        if self.continue_base_on_annotaied_peptide_table:
            self.run_base_on_annotaied_peptide_table()
            return

        self.annotate_peptides()
        self.extract_genome_col(self.peptide_table)
        
        if self.stop_after_genome_ranking:
            print("Stopped after genome ranking")
            self.final_peptide_table = self.peptide_table
            self.calculate_genome_list(self.peptide_table, 
                                    turn_point_method=self.turn_point_method)
            #save the annotated peptide table to output path
            self.peptide_table.to_csv(self.output_path, sep='\t', index=False)
            return
        else:
            #save the annotated peptide table to temp dir
            self.peptide_table.to_csv(f'{self.temp_dir}/annotated_peptide_table.tsv', sep='\t', index=False)
            self.run_base_on_annotaied_peptide_table()


    def run_base_on_annotaied_peptide_table(self):
        selected_genomes_list = self.calculate_genome_list(self.peptide_table, 
                                                           turn_point_method=self.turn_point_method)
        self.final_peptide_table = self.reduce_proteins_by_genome(self.peptide_table, selected_genomes_list)
        selected_proteins_list = self.calculate_protein_list(self.final_peptide_table)
        self.final_peptide_table = self.reduce_proteins_by_mini_proteins_list(self.final_peptide_table, selected_proteins_list)
        return self.final_peptide_table


    def all_in_one(self, 
                   taxafunc_anno_db_path,
                   lca_threshold = 1,
                   genome_mode = True, 
                   distinct_genome_threshold = 1, # usually 3
                   exclude_protein_startwith = None, #Usually 'REV_;XXX_' 
                   protein_genome_separator = '_'
                   ): # run peptide to OTF
        
        if self.continue_base_on_annotaied_peptide_table:
            self.run_base_on_annotaied_peptide_table()
        else:
            self.process_peptides_to_proteins()
        
        # collect additional running information
        additional_running_info = {
            "peptideProteinsMapper": "Peptides directly annotated with proteins from a database",
            "Run time": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            "peptide_mapping_db": self.db_file,
            "peptide_col": self.peptide_col,
            "intensity_col_prefix": self.intensity_col_prefix,
            "protein_genome_separator": protein_genome_separator,
            "original_peptides_before_mapping": self.original_peptides_before_mapping,
            "peptides_after_mapping": self.peptides_after_mapping,
            "removed_peptides_no_matched": self.removed_peptides_no_matched,
            "genome_peptide_coverage_cutoff": self.genome_peptide_coverage_cutoff,
            "protein_peptide_coverage_cutoff": self.protein_peptide_coverage_cutoff,
            "turn_point_method": self.turn_point_method,
            "turn_point_distinct_cutoff": self.turn_point_distinct_cutoff,
            "genome_cutoff_rank": self.genome_cutoff_rank if self.turn_point_method.lower() in ['rank', 'distinct_count'] else "N/A",
            "total_genomes_found": len(self.genome_ranked_table) if self.genome_ranked_table is not None else "Unknown",
            "selected_genomes_num": self.selected_genomes_num,
            "total_proteins_found": len(self.protein_ranked_table) if self.protein_ranked_table is not None else "Unknown",
            "selected_proteins_num": self.selected_proteins_num,
            "continue_base_on_annotated_peptide_table": self.continue_base_on_annotaied_peptide_table,
            "stop_after_genome_ranking": self.stop_after_genome_ranking,
            "original_peptide_count": len(self.peptide_table) if hasattr(self, 'peptide_table') else "Unknown",
            "final_peptide_count": len(self.final_peptide_table) if hasattr(self, 'final_peptide_table') else "Unknown",
        }
        

        annotator = PeptideAnnotator(
            db_path=taxafunc_anno_db_path,
            peptide_path=None,
            peptide_df=self.final_peptide_table,
            output_path=self.output_path,
            threshold=lca_threshold,
            genome_mode=genome_mode,
            protein_separator=';',
            protein_genome_separator= protein_genome_separator,
            protein_col='Proteins',
            peptide_col=self.peptide_col,
            sample_col_prefix=self.intensity_col_prefix,
            distinct_genome_threshold=distinct_genome_threshold,
            exclude_protein_startwith = exclude_protein_startwith,
            additional_running_info=additional_running_info
        )
        annotator.run_annotate()
        print("OTF annotation finished")
        
        
if __name__ == "__main__":
    peptide_table_path = "C:/Users/Qing/Desktop/diann_res_test/report.pr_matrix_test.tsv"
    # peptide_table_path = "temp/annotated_peptide_table.tsv"
    db_path = "C:/Users/Qing/Desktop/UHGP/UHGP_digested_db/peptide_to_protein.db"
    
    ## test process_peptides_to_proteins
    # output_path = "anntated_report.pr_matrix.tsv"
    # peptide_mapper = peptideProteinsMapper(peptide_table_path=peptide_table_path, db_path=db_path, output_path=output_path,
    #                                        peptide_col='Stripped.Sequence', intensity_col_prefix="D:", table_separator='\t',
    #                                        genome_cutoff_rank=None,
    #                                         genome_peptide_coverage_cutoff=0.98, protein_peptide_coverage_cutoff=1,
    #                                         stop_after_genome_ranking=True, turn_point_method="Coverage",
    #                                         continue_base_on_annotaied_peptide_table=False)
    # peptide_mapper.process_peptides_to_proteins()
    # peptide_mapper.final_peptide_table.to_csv(output_path, sep='\t', index=False)
    # print("peptide annotation finished")
    
    # # test all_in_one
    taxafunc_anno_db_path = "C:/Users/Qing/Desktop/UHGP/MetaX_human-gut_v2.0.2_dacanadded_20250523.db"
    output_path ="C:/Users/Qing/Desktop/diann_res_test/otf.tsv"
    
    # set of genomes to be removed
    removed_genomes_set = set()
    removed_genomes_file_path = "C:/Users/Qing/OneDrive - University of Ottawa/code/TaxaFunc/MetaX/.local_tests/removed_genomes.txt"
    with open(removed_genomes_file_path) as f:
        for line in f:
            line = line.strip()
            if line:
                removed_genomes_set.add(line)
    print(len(removed_genomes_set), "genomes in the genome list")

    peptide_mapper = peptideProteinsMapper(peptide_table_path=peptide_table_path, db_path=db_path, output_path=output_path,
                                           removed_genomes_set=removed_genomes_set,
                                           peptide_col='Stripped.Sequence', intensity_col_prefix="D:", table_separator='\t',
                                           turn_point_method='Coverage',
                                           genome_cutoff_rank=None,
                                           turn_point_distinct_cutoff=5,
                                           genome_peptide_coverage_cutoff=0.97, 
                                           protein_peptide_coverage_cutoff=1,
                                           continue_base_on_annotaied_peptide_table=False)
    peptide_mapper.all_in_one(taxafunc_anno_db_path=taxafunc_anno_db_path)
    print("all in one finished")