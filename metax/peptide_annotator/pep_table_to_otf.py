# This script is used to annotate peptides with their corresponding proteins of a Table.
# input: peptide_table
# output: peptide_table with an additional column of proteins

# main steps:
# 1. load peptide_table and preprocess if necessary
# 2. annotate peptides with proteins
# 3. reduce proteins by genome ranking
# 4. save the annotated peptide_table or transfer to OTF annotator

import sqlite3
import json
import pandas as pd
from tqdm import tqdm
if __name__ == "__main__":
    from get_genome_rank import GenomeRank
    from peptable_annotator import PeptideAnnotator

else:
    from .get_genome_rank import GenomeRank
    from .peptable_annotator import PeptideAnnotator

def query_peptide_proteins(db_file, peptide_list, chunk_size=10000):
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
            for peptide, proteins_json in tqdm(rows, desc="Processing peptide mappings", leave=False):
                try:
                    proteins = json.loads(proteins_json)  # decode JSON string
                    peptide_proteins[peptide] = ";".join(proteins)  # join proteins with semicolon
                except json.JSONDecodeError:
                    peptide_proteins[peptide] = ""  # empty string if JSON decoding fails

    return peptide_proteins


class peptideProteinsMapper:
    def __init__(self, peptide_table_path, db_path, 
                 table_separator='\t',
                 peptide_col='Sequence', 
                 intensity_col_prefix='Intensity',
                 peptide_coverage_cutoff=0.95,
                 output_path=None
                 ):

        self.peptide_table_path = peptide_table_path
        self.db_file = db_path
        self.table_separator = table_separator
        self.peptide_col = peptide_col
        self.intensity_col_prefix = intensity_col_prefix
        self.peptide_coverage_cutoff = peptide_coverage_cutoff
        self.output_path = output_path
        
        self.has_intensity = False
        
        self.peptide_table = self.load_peptide_table()
        self.genome_ranked_table = None
        self.final_peptide_table = None
        
        
    def load_peptide_table(self):
        # load peptide_table
        self.peptide_table = pd.read_csv(self.peptide_table_path, sep=self.table_separator)
        # check if peptide_col and intensity_col_prefix are in the peptide_table
        if self.peptide_col not in self.peptide_table.columns:
            raise ValueError(f"The peptide column you specified:[{self.peptide_col}] is not in the peptide_table, please check!")
        if any([col.startswith(self.intensity_col_prefix) for col in self.peptide_table.columns]):
            self.has_intensity = True
            print("Intensity columns found, will be kept in the output and used for genome ranking")
        else:
            print("Warning: Intensity columns not found")
            raise ValueError(f"The intensity columns you specified:[{self.intensity_col_prefix}] are not in the peptide_table, please check!")
        return self.peptide_table
    

    def annotate_peptides(self):
        """ Annotate peptides with proteins by querying the database. """
        print("Start annotating peptides with proteins")
        
        unique_peptides = self.peptide_table[self.peptide_col].drop_duplicates().tolist()

        peptide_proteins_dict = query_peptide_proteins(self.db_file, unique_peptides)

        self.peptide_table["Proteins"] = self.peptide_table[self.peptide_col].map(peptide_proteins_dict)

        original_count = len(self.peptide_table)
        self.peptide_table = self.peptide_table[self.peptide_table["Proteins"].notna() & (self.peptide_table["Proteins"] != "")]
        removed_count = original_count - len(self.peptide_table)
        
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
        
    def calculate_genome_list(self, df):
        gr = GenomeRank(df = df, 
                                 peptide_column = self.peptide_col,
                                 genome_column = 'Genomes',
                                 genome_separator = ';')
        df_results_rank_by_distinct = gr.get_rank_covre_df(genome_rank_method='combined', 
                                                           weight_distinct=0.9, weight_peptide=0.1)
        self.genome_ranked_table = df_results_rank_by_distinct
        # cutoff indes is  "coverage_ratio" > peptide_coverage_cutoff
        cutoff_index = df_results_rank_by_distinct[df_results_rank_by_distinct['coverage_ratio'] >= self.peptide_coverage_cutoff].index[0]
        selected_genomes = df_results_rank_by_distinct.loc[:cutoff_index]
        selected_genomes_list = selected_genomes['Genomes'].tolist()
        print(f"The number of selected genomes: {len(selected_genomes_list)}.\nThe last genome with coverage_ratio: {selected_genomes.iloc[-1]['coverage_ratio']}")
        return selected_genomes_list
    
    def reduce_proteins(self, df, selected_genomes_list):
        # remove prteins that are not in the keep_genomes of "proteins" in df
        def filter_proteins(proteins, keep_genomes):
            if proteins == '':
                return ''
            proteins = proteins.split(';')
            proteins = [protein for protein in proteins if protein.split('_')[0] in keep_genomes]
            return ';'.join(proteins)
        print("filtering proteins by selected genomes")
        original_peptides = df.shape[0]
        df['Proteins'] = df['Proteins'].apply(filter_proteins, args=(selected_genomes_list,))
        df = df[df['Proteins'] != '']
        print(f"original peptides: {original_peptides}, after filtering: {df.shape[0]}")
        print(f"Removed peptides: {original_peptides - df.shape[0]}, due to no protein left after filtering by selected genomes")
        # remove the genome column
        df = df.drop(columns=['Genomes'])
        return df
    
    
    def process_peptides_to_proteins(self):# main function workflow
        self.annotate_peptides()
        self.extract_genome_col(self.peptide_table)
        selected_genomes_list = self.calculate_genome_list(self.peptide_table)
        self.final_peptide_table = self.reduce_proteins(self.peptide_table, selected_genomes_list)
        return self.final_peptide_table


    def all_in_one(self, 
                   taxafunc_anno_db_path,
                   lca_threshold = 1,
                   genome_mode = True, 
                   distinct_genome_threshold = 1, # usually 3
                   exclude_protein_startwith = None, #Usually 'REV_;XXX_' 
                   protein_genome_separator = '_'
                   ): # run peptide to OTF
        self.process_peptides_to_proteins()
        

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
            exclude_protein_startwith = exclude_protein_startwith 
            
        )
        annotator.run_annotate()
        print("OTF annotation finished")
        
        
if __name__ == "__main__":
    peptide_table_path = "/report.pr_matrix.tsv"
    db_path = "peptide_to_protein.db"
    
    ## test process_peptides_to_proteins
    # output_path = "anntated_report.pr_matrix.tsv"
    # peptide_mapper = peptideProteinsMapper(peptide_table_path=peptide_table_path, db_path=db_path, output_path=output_path,
    #                                        peptide_col='Stripped.Sequence', intensity_col_prefix="D:", table_separator='\t')
    # peptide_mapper.process_peptides_to_proteins()
    # peptide_mapper.final_peptide_table.to_csv(output_path, sep='\t', index=False)
    # print("peptide annotation finished")
    
    # # test all_in_one
    taxafunc_anno_db_path = "MetaX-human-gut_20231211.db"
    output_path = "all_in_one_report.pr_matrix.tsv"
    peptide_mapper = peptideProteinsMapper(peptide_table_path=peptide_table_path, db_path=db_path, output_path=output_path,
                                           peptide_col='Stripped.Sequence', intensity_col_prefix="D:", table_separator='\t')
    peptide_mapper.all_in_one(taxafunc_anno_db_path=taxafunc_anno_db_path)
    print("all in one finished")