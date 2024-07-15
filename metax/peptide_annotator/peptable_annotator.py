from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import re
from tqdm import tqdm
import time
import os
import threading
import sqlite3
if __name__ == '__main__':
    from pep2taxafunc import Pep2TaxaFunc
    from convert_id_to_name import add_pathway_name_to_df, add_ec_name_to_df, add_ko_name_to_df
else:
    from .pep2taxafunc import Pep2TaxaFunc
    from .convert_id_to_name import add_pathway_name_to_df, add_ec_name_to_df, add_ko_name_to_df
    
    
class PeptideAnnotator:
    def __init__(self, db_path:str, peptide_path: str, output_path: str,
                 threshold=1.0, genome_mode=True, protein_separator=';', 
                 protein_col='Proteins', peptide_col='Sequence', sample_col_prefix='Intensity_'):

        self.db_path = db_path
        self.peptide_path = peptide_path
        self.output_path = output_path
        
        self.threshold = round(float(threshold), 4)
        self.genome_mode = genome_mode
        self.protein_separator = protein_separator
        self.protein_col = protein_col
        self.peptide_col = peptide_col
        self.sample_col_prefix = sample_col_prefix
        
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
        print('Running proteins_to_taxa_func...')
        
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.run_pep2taxafunc, protein) for protein in df_t[self.protein_col]]
            results = [future.result() for future in tqdm(futures, total=len(futures))]

        df_t0 = pd.DataFrame(results, index=df_t.index)
        df_t0 = self.add_additional_columns(df_t0)
        df_t0['None'] = 'none'
        df_t0['None_prop'] = '1.0'
        
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


    def remove_reversed(self, df):
        print('Removing reversed proteins...')
        print(f'Original shape: {df.shape}')
        try:
            df = df[~df['Proteins'].str.contains('REV_')]
            print(f'After removing reversed proteins: {df.shape}')
        except Exception as e:
            print('Error: removing reversed proteins failed!')
            print(e)
            
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
        # exxtract the peptide sequence, protein accessions and sample columns from the dataframe
        df = df.loc[:, [self.peptide_col, self.protein_col] + [col for col in df.columns if col.startswith(self.sample_col_prefix)]]
        
        print(f'After filtering Intensity 0 in all samples and removing other columns: {df.shape}')
        
        df = self.remove_reversed(df)
        
        df_res = self.run_2_result(df)
        
        self.save_result(df_res)
        
        return df_res

if __name__ == '__main__':
    final_peptides_path = 'C:/Users/max/Desktop/MetaX_Suite/MetaX/metax/metax/data/example_data/Example_final_peptide.tsv'
    output_path = 'C:/Users/max/Desktop/Example_OTF.tsv'
    db_path = 'C:/Users/max/Desktop/MetaX_Suite/MetaX-human-gut-new.db'
    threshold = 1
    t0 = time.time()

    annotator = PeptideAnnotator(
        db_path=db_path,
        peptide_path=final_peptides_path,
        output_path=output_path,
        threshold=threshold,
        genome_mode=True,
        protein_separator=';',
        protein_col='Proteins',
        peptide_col='Sequence',
        sample_col_prefix='Intensity_'
        
    )
    annotator.run_annotate()

    print(f'Running time: {time.time() - t0} seconds')