from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import re
from tqdm import tqdm
import time
import os
import threading
import sqlite3
if __name__ == '__main__':
    from pep_to_taxafunc import Pep2TaxaFunc
    from convert_id_to_name import add_pathway_name_to_df, add_ec_name_to_df, add_ko_name_to_df
else:
    from .pep_to_taxafunc import Pep2TaxaFunc
    from .convert_id_to_name import add_pathway_name_to_df, add_ec_name_to_df, add_ko_name_to_df
    
    
class PeptideAnnotator:
    def __init__(self, db_path:str, peptide_path: str, output_path: str,
                 threshold=1.0, genome_mode=True, protein_separator=';', protein_genome_separator = '_',
                 protein_col='Proteins', peptide_col='Sequence', sample_col_prefix='Intensity',
                 distinct_genome_threshold:int=0, exclude_protein_contains:str='REV_'):

        self.db_path = db_path
        self.peptide_path = peptide_path
        self.output_path = output_path
        
        self.threshold = round(float(threshold), 4)
        self.genome_mode = genome_mode
        self.protein_separator = protein_separator # the separator between proteins in the proteins group column
        self.protein_genome_separator = protein_genome_separator # the separator between protein and genome in each protein ID
        self.protein_col = protein_col
        self.peptide_col = peptide_col
        self.sample_col_prefix = sample_col_prefix.strip()
        self.distinct_genome_threshold = distinct_genome_threshold
        self.exclude_protein_contains = exclude_protein_contains
        
        self.thread_local = threading.local()
        
    def get_connection(self):
        if not hasattr(self.thread_local, "conn"):
            self.thread_local.conn = sqlite3.connect(self.db_path)
        return self.thread_local.conn

    def get_pep2taxafunc(self):
        if not hasattr(self.thread_local, "p2tf"):
            self.thread_local.p2tf = Pep2TaxaFunc(
                threshold=self.threshold,
                genome_mode=self.genome_mode,
                conn=self.get_connection(),
                protein_genome_separator = self.protein_genome_separator
            )
        return self.thread_local.p2tf

    def stat_length(self, seq):
        pattern = re.compile(r'\(.*?\)')
        return len(re.sub(pattern, '', seq))

    def count_protein(self, proteins):
        return len(proteins.split(self.protein_separator))

    def run_pep2taxafunc(self, row) -> dict:
        protein_list = str(row).split(self.protein_separator)
        result = {}
        try:
            p2tf = self.get_pep2taxafunc()
            result = p2tf.proteins_to_taxa_func(protein_list)
        except Exception as e:
            print(f"Error: {protein_list}")
            print(e)
        return result

    def add_additional_columns(self, df):
        try:
            print("Trying to add 'EC_DE', 'EC_AN', 'EC_CC' and 'EC_CA' to the dataframe...")
            df = add_ec_name_to_df(df)
        except Exception as e:
            print('Error: add additional EC columns failed!')
            print(e)
        
        try:
            print("Trying to add 'KEGG_Pathway_name' to the dataframe...")
            df = add_pathway_name_to_df(df)
        except Exception as e:
            print('Error: add additional KEGG_Pathway_name column failed!')
            print(e)

        try:
            print("Trying to add 'KO_name' to the dataframe...")
            df = add_ko_name_to_df(df)
        except Exception as e:
            print('Error: add additional KO_name column failed!')
            print(e)
        
        return df

    def run_2_result(self, df):
        tqdm.pandas()
        df_t = df.copy()
        df_t.rename(columns={self.peptide_col: 'Sequence'}, inplace=True)
        print('Running proteins_to_taxa_func...')
        
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.run_pep2taxafunc, protein) for protein in df_t[self.protein_col]]
            results = [future.result() for future in tqdm(futures, total=len(futures))]

        df_t0 = pd.DataFrame(results, index=df_t.index)
        df_t0 = self.add_additional_columns(df_t0)
        df_t0['None_func'] = 'none_func'
        df_t0['None_func_prop'] = '1.0'
        
        if 'Description' in df_t0.columns:
            df_t0.rename(columns={'Description': 'eggNOG_Description', 'Description_prop': 'eggNOG_Description_prop'}, inplace=True)
        if 'Preferred_name' in df_t0.columns:
            df_t0.rename(columns={'Preferred_name': 'Gene', 'Preferred_name_prop': 'Gene_prop'}, inplace=True)
        else:
            print('Warning: column name "Description" does not exist!, skip renaming...')
            
        df_t = pd.concat([df_t, df_t0], axis=1)
        cols = df_t.columns.tolist()
        sample_cols = [col for col in cols if col.startswith('Intensity_')]
        for col in sample_cols:
            cols.remove(col)
            cols.append(col)
        df_t = df_t.reindex(columns=cols)
        return df_t

    def save_result(self, df):
        dir_path = os.path.dirname(self.output_path)
        if dir_path == '':
            dir_path = '.'
            
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f'Output directory did not exist, created: {dir_path}')
        
        if os.path.exists(self.output_path):
            import datetime
            counter = 1
            base_name = os.path.splitext(os.path.basename(self.output_path))[0]
            ext = os.path.splitext(self.output_path)[-1]
            new_output_path = os.path.join(dir_path, f'{base_name}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}{ext}')
            
            while os.path.exists(new_output_path):
                counter += 1
                new_output_path = os.path.join(dir_path, f'{base_name}_{counter}{ext}')
            self.output_path = new_output_path
            print(f'Output file already exists, saved as: {self.output_path}')
        
        df.to_csv(self.output_path, sep='\t', index=False)
        print(f'Output file: {self.output_path}')
        print(f'Output shape: {df.shape}')


    def exclude_proteins(self, df):
        print(f'Removing reversed proteins containing [{self.exclude_protein_contains}]...')
        try:
            df = df[~df[self.protein_col].str.contains(self.exclude_protein_contains)]
            print(f'After removing reversed proteins: {df.shape}')
        except Exception as e:
            print('Error: removing reversed proteins failed!')
            print(e)
            
        return df
    
    def extract_genome_from_protein(self, protein:str):
        pro_list = protein.split(self.protein_separator)
        genome_list = [pro.split(self.protein_genome_separator)[0] for pro in pro_list]
        genome = set(genome_list)
        genome = ';'.join(genome)
        return genome
    
    def get_genome_list_by_distinct_pep_num(self, df):
        print('Calculating distinct peptides number for each genome...')
        df_t = df[[self.peptide_col, self.protein_col]].copy()
        df_t['genome'] = df_t[self.protein_col].apply(self.extract_genome_from_protein)
        df_t['genome_count'] = df_t['genome'].apply(lambda x: len(x.split(';')))
        df_distinct = df_t.loc[df_t['genome_count'] == 1, ['genome', 'genome_count']]
        df_distinct = df_distinct.groupby('genome').count().reset_index()
        genome_list = df_distinct.loc[df_distinct['genome_count'] >= self.distinct_genome_threshold, 'genome'].tolist()
        print(f'Total genomes: {df_distinct.shape[0]}, genomes with distinct peptides >= {self.distinct_genome_threshold}: [{len(genome_list)}]')
        return genome_list
    
    def remove_proteins_not_in_genome_list(self, protein_str, genome_list):
        pro_list = protein_str.split(self.protein_separator)
        pro_list = [pro for pro in pro_list if pro.split(self.protein_genome_separator)[0] in genome_list]
        return ';'.join(pro_list)
    
    def filter_genome_with_distinct_pep_num(self, df):
        if self.distinct_genome_threshold < 1:
            return df
        
        print(f'Filtering genomes less than [{self.distinct_genome_threshold}] distinct peptides...')
        original_num = df.shape[0]
        genome_list = self.get_genome_list_by_distinct_pep_num(df)
        df[self.protein_col] = df[self.protein_col].apply(lambda x: self.remove_proteins_not_in_genome_list(x, genome_list))
        # remove rows with empty proteins
        df = df[df[self.protein_col].str.len() > 0]
        print(f'Peptides number: from [{original_num}] -> [{df.shape[0]}] after filtering genomes with distinct peptides')
        return df
        
    def rename_columns(self, df):
        # remove the prefix of the peptide, protein and sample prefix columns
        # to standardize the column names avoiding the error in the OTF Analyzer
        cols = df.columns.tolist()
        cols = [col.replace(self.peptide_col, 'Sequence') for col in cols]
        cols = [col.replace(self.protein_col, 'Proteins') for col in cols]
        cols = [col.replace(self.sample_col_prefix, 'Intensity_') for col in cols]
        # replace the "Intensity__" to "Intensity_" if there are any
        cols = [col.replace('Intensity__', 'Intensity_') for col in cols]
        df.columns = cols
        return df

    def run_annotate(self):
        print('Start running Peptide Annotator...')
        print(f'Input file: {self.peptide_path}')
        print(f'Database: {self.db_path}')
        print(f'Threshold: {self.threshold}')
        print(f'Genome mode: {self.genome_mode}')
        print(f'Output file: {self.output_path}')
        print('-----------------------------------')
        
        if not os.path.exists(self.peptide_path):
            raise FileNotFoundError(f'Input file not found: {self.peptide_path}')
        
        df = pd.read_csv(self.peptide_path, sep='\t')
        df.columns = [col.replace(' ', '_') for col in df.columns]
        
        print(f'Original shape: {df.shape}')
        # extract the peptide sequence, protein accessions and sample columns from the dataframe
        intensity_cols = [col for col in df.columns if col.startswith(self.sample_col_prefix)]
        # remove the columns only containing self.sample_col_prefix, rather than starting with self.sample_col_prefix
        intensity_cols = [col for col in intensity_cols if col != self.sample_col_prefix]
        df = df.loc[:, [self.peptide_col, self.protein_col] + intensity_cols]
        
        print(f'After filtering Intensity 0 in all samples and removing other columns: {df.shape}')
        
        df = self.exclude_proteins(df)
        
        df = self.filter_genome_with_distinct_pep_num(df)
        
        df_res = self.run_2_result(df)
        
        df_res = self.rename_columns(df_res)
        
        self.save_result(df_res)
        
        return df_res

if __name__ == '__main__':
    current_path = os.path.dirname(os.path.abspath(__file__))
    # db_path = 'UHGP.db'
    db_path = os.path.join(current_path, '../../local_tests/UHGP.db')
    # final_peptides_path = 'peptide.tsv'
    final_peptides_path = os.path.join(current_path, '../data/example_data/Example_final_peptide.tsv')
    output_path = 'OTF.tsv'
    threshold = 1
    t0 = time.time()

    annotator = PeptideAnnotator(
        db_path=db_path,
        peptide_path=final_peptides_path,
        output_path=output_path,
        threshold=threshold,
        genome_mode=True,
        protein_separator=';',
        protein_genome_separator = '_',
        protein_col='Proteins',
        peptide_col='Sequence',
        sample_col_prefix='Intensity',
        distinct_genome_threshold=3,
        
    )
    annotator.run_annotate()

    print(f'Running time: {time.time() - t0} seconds')