from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import re
from tqdm import tqdm
import time
import os
import threading
import sqlite3
from datetime import datetime


try:
    from ..utils.version import __version__
    from .proteins_to_taxafunc import Pep2TaxaFunc
    from .convert_id_to_name import add_pathway_name_to_df, add_ec_name_to_df, add_ko_name_to_df, add_kegg_module_to_df, add_go_name_to_df
except ImportError:
    print("ImportError occurred, trying alternative imports...")
    __version__ = "Test version"
    from proteins_to_taxafunc import Pep2TaxaFunc
    from convert_id_to_name import add_pathway_name_to_df, add_ec_name_to_df, add_ko_name_to_df, add_kegg_module_to_df, add_go_name_to_df

        
class PeptideAnnotator:
    """
    A class to annotate peptides with taxonomic and functional information.
    Attributes:
        db_path (str): Path to the database file.
        peptide_path (str): Path to the input peptide file.
        output_path (str): Path to the output file.
        threshold (float): Threshold value for annotation.
        genome_mode (bool): Flag to indicate genome mode.
        protein_separator (str): Separator between proteins in the proteins group column.
        protein_genome_separator (str): Separator between protein and genome in each protein ID.
        protein_col (str): Column name for proteins.
        peptide_col (str): Column name for peptides.
        sample_col_prefix (str): Prefix for sample columns.
        distinct_genome_threshold (int): Threshold for distinct genome count.
        exclude_protein_startwith (str): Prefix for proteins to exclude.
        peptide_df (pd.DataFrame|None): DataFrame containing peptides, if provided.
        additional_running_info (dict): Additional information for the run.

    Methods:
        run_annotate():
            Runs the entire annotation process and returns the annotated dataframe.
    """
    def __init__(self, db_path:str,  output_path: str,
                 threshold=1.0, genome_mode=True, protein_separator=';', protein_genome_separator = '_',
                 protein_col='Proteins', peptide_col='Sequence', sample_col_prefix='Intensity',
                 distinct_genome_threshold:int=0, exclude_protein_startwith:str='REV_',
                 peptide_path: str|None= None,peptide_df: pd.DataFrame|None=None,
                 additional_running_info: dict=None, duplicate_peptide_handling_mode: str='sum'):
        self.db_path = db_path
        self.peptide_path = peptide_path
        self.peptide_df = peptide_df
        self.output_path = output_path
        
        self.threshold = round(float(threshold), 4)
        self.genome_mode = genome_mode
        self.protein_separator = protein_separator # the separator between proteins in the proteins group column
        self.protein_genome_separator = protein_genome_separator # the separator between protein and genome in each protein ID
        self.protein_col = protein_col
        self.peptide_col = peptide_col
        self.sample_col_prefix = sample_col_prefix.strip()
        self.distinct_genome_threshold = distinct_genome_threshold
        self.exclude_protein_startwith = exclude_protein_startwith
        self.duplicate_peptide_handling_mode = duplicate_peptide_handling_mode  # 'first', 'sum', 'max', 'min', 'mean', 'keep'
        
        self.thread_local = threading.local()
        self.start_time = datetime.now()
        self.additional_running_info = additional_running_info if additional_running_info else {}
        
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
            
        try:
            print("Trying to add 'KEGG_Module' to the dataframe...")
            df = add_kegg_module_to_df(df)
        except Exception as e:
            print('Error: add additional KEGG_Module column failed!')
            print(e)
        
        try:
            print("Trying to add 'GO_name' to the dataframe...")
            df = add_go_name_to_df(df)
        except Exception as e:
            print('Error: add additional GO_name column failed!')
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

    def get_metadata(self):
        """get metadata for the running"""
        metadata = {
            "software": "MetaX (PeptideAnnotator)",
            "version": __version__,
            "run_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "parameters": {
                "database_path": os.path.abspath(self.db_path),
                "input_peptide_path": os.path.abspath(self.peptide_path) if self.peptide_path else "DataFrame_input",
                "threshold": self.threshold,
                "genome_mode": self.genome_mode,
                "distinct_genome_threshold": self.distinct_genome_threshold,
                "exclude_protein_startwith": self.exclude_protein_startwith
            }
        }
        if self.additional_running_info:
            metadata["additional_info"] = self.additional_running_info
            
        return metadata

    def save_result(self, df):
        dir_path = os.path.dirname(self.output_path)
        if dir_path == '':
            dir_path = '.'
            
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f'Output directory did not exist, created: {dir_path}')
        
        if os.path.exists(self.output_path):
            counter = 1
            base_name = os.path.splitext(os.path.basename(self.output_path))[0]
            ext = os.path.splitext(self.output_path)[-1]
            new_output_path = os.path.join(dir_path, f'{base_name}_{pd.Timestamp.now().strftime("%Y%m%d%H%M%S")}{ext}')
            
            while os.path.exists(new_output_path):
                counter += 1
                new_output_path = os.path.join(dir_path, f'{base_name}_{counter}{ext}')
            self.output_path = new_output_path
            print(f'Output file already exists, saved as: {self.output_path}')
        
        # get metadata for the running
        metadata = self.get_metadata()
        completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        processing_duration = str(datetime.now() - self.start_time).split('.')[0]
        
        # save the dataframe to the output file (clean TSV without comments)
        print('Saving result dataframe to output file...')
        df.to_csv(self.output_path, sep='\t', index=False)
        
        # save metadata to a separate info file
        base_path = os.path.splitext(self.output_path)[0]
        info_path = f"{base_path}_info.txt"
        with open(info_path, 'w', encoding='utf-8') as f:
            f.write("MetaX PeptideAnnotator Results\n")
            if 'additional_info' in metadata:
                f.write("="*50 + "\n")
                for key, value in metadata['additional_info'].items():
                    f.write(f"{key}: {value}\n")
            f.write("="*50 + "\n")
            f.write(f"Software: {metadata['software']} v{metadata['version']}\n")
            f.write(f"Run time: {metadata['run_time']}\n")
            f.write(f"Completion time: {completion_time}\n")
            f.write(f"Processing duration: {processing_duration}\n")
            f.write(f"Input: {metadata['parameters']['input_peptide_path']}\n")
            f.write(f"Database: {metadata['parameters']['database_path']}\n")
            f.write(f"Threshold: {metadata['parameters']['threshold']}\n")
            f.write(f"Genome mode: {metadata['parameters']['genome_mode']}\n")
            f.write(f"Distinct genome threshold: {metadata['parameters']['distinct_genome_threshold']}\n")
            f.write(f"Exclude proteins: {metadata['parameters']['exclude_protein_startwith']}\n")
            f.write(f"Result: {df.shape[0]} rows × {df.shape[1]} columns\n")
        
        print(f'Output file: {self.output_path}')
        print(f'Info file: {info_path}')
        print(f'Output shape: {df.shape}')


    def exclude_proteins(self, df):
        if not self.exclude_protein_startwith:
            return df
        print(f'Removing proteins name start with [{self.exclude_protein_startwith}]...')
        try:
            exclude_list = [excl.strip() for excl in self.exclude_protein_startwith.split(';') if excl.strip()]
            if not exclude_list:
                print('No proteins to exclude.')
                return df
            
            # check each protein in the string separated by protein_separator
            mask = df[self.protein_col].str.split(self.protein_separator).apply(
                lambda proteins: any(p.strip().startswith(tuple(exclude_list)) for p in proteins)
            )
            df = df[~mask]
            print(f'After removing exclude proteins: {df.shape}')
        except Exception as e:
            print('Error: removing exclude proteins failed!')
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

        # replace the prefix of the sample columns to "Intensity" if there are not
        if not self.sample_col_prefix.lower().startswith('intensity'):
            cols = [
                f"Intensity_{col}"
                if col.startswith(self.sample_col_prefix) and not col.lower().startswith('intensity')
                else col
                for col in cols
            ]
        # replace the "Intensity__" to "Intensity_" if there are any
        cols = [col.replace('Intensity__', 'Intensity_') for col in cols]
        df.columns = cols
        return df
    
    def handle_duplicate_peptides(self, df):
        row_count = df.shape[0]
        # 统计 [protein, peptide] 组合的唯一数
        try:
            unique_pair_count = df[[self.protein_col, self.peptide_col]].drop_duplicates().shape[0]
        except KeyError:
            print('Warning: protein or peptide column not found when checking duplicates.')
            return df

        if row_count == unique_pair_count:
            print('No duplicate peptides found.')
            return df

        sample_cols = [col for col in df.columns if col.startswith(self.sample_col_prefix)]

        # 无样本列或选择 'first' 时，直接保留首条
        if self.duplicate_peptide_handling_mode == 'first' or len(sample_cols) == 0:
            if len(sample_cols) == 0 and self.duplicate_peptide_handling_mode != 'first':
                print('No sample columns detected, fallback to "first".')
            df = df.drop_duplicates(subset=[self.protein_col, self.peptide_col], keep='first')
            print(f'Handling duplicate peptides with mode [first]: from [{row_count}] -> [{df.shape[0]}]')
            return df

        # 确保样本列为数值，避免聚合时报错
        df[sample_cols] = df[sample_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

        group_keys = [self.protein_col, self.peptide_col]
        mode = self.duplicate_peptide_handling_mode

        if mode == 'sum':
            df = df.groupby(group_keys, as_index=False)[sample_cols].sum()
        elif mode == 'max':
            df = df.groupby(group_keys, as_index=False)[sample_cols].max()
        elif mode == 'min':
            df = df.groupby(group_keys, as_index=False)[sample_cols].min()
        elif mode == 'mean':
            df = df.groupby(group_keys, as_index=False)[sample_cols].mean()
        elif mode == 'keep':  # 保留全部，不做处理, 仅在代码中使用, GUI中不提供该选项
            print(f'Handling duplicate peptides with mode [keep]: from [{row_count}] -> [{df.shape[0]}]')
            return df
        else:
            print(f'Warning: Unknown duplicate_peptide_handling_mode [{mode}], no handling applied.')
            print(f'Handling duplicate peptides with mode [keep]: from [{row_count}] -> [{df.shape[0]}]')
            return df

        print(f'Handling duplicate peptides with mode [{mode}]: from [{row_count}] -> [{df.shape[0]}]')
        return df

    def run_annotate(self):
        print('Start running Peptide Annotator...')
        if self.peptide_df is not None:
            print(f'Peptide Table was provided with shape: {self.peptide_df.shape}')
        else:
            print(f'Input file: {self.peptide_path}')
        print(f'Database: {self.db_path}')
        print(f'Threshold: {self.threshold}')
        print(f'Genome mode: {self.genome_mode}')
        print(f'Output file: {self.output_path}')
        print('-----------------------------------')
        
        if self.peptide_df is not None:
            print('Using provided peptide table...')
            df = self.peptide_df
        else:
            print('Reading peptide table from file...')
            if not os.path.exists(self.peptide_path):
                raise FileNotFoundError(f'Input file not found: {self.peptide_path}')
            
            df = pd.read_csv(self.peptide_path, sep='\t')
            df.columns = [col.replace(' ', '_') for col in df.columns]
            print(f'Original peptide table shape: {df.shape}')
            
        print(f"Removing columns only containing [{self.sample_col_prefix}] rather than starting with [{self.sample_col_prefix}]...")
        # extract the peptide sequence, protein accessions and sample columns from the dataframe
        intensity_cols = [col for col in df.columns if col.startswith(self.sample_col_prefix)]
        # remove the columns only containing self.sample_col_prefix, rather than starting with self.sample_col_prefix
        intensity_cols = [col for col in intensity_cols if col != self.sample_col_prefix]
        df = df.loc[:, [self.peptide_col, self.protein_col] + intensity_cols]
        # remove the rows with empty protein column
        print("Removing rows with empty protein column if there are...")
        df = df[df[self.protein_col].str.len() > 0]
        print("Removing rows with 0 or NaN in all samples...")
        df = df.loc[df[intensity_cols].sum(axis=1) > 0]
        
        print(f'After filtering columns and rows, the peptide table shape: {df.shape}')
        
        df = self.handle_duplicate_peptides(df)
        
        df = self.exclude_proteins(df)
        
        df = self.filter_genome_with_distinct_pep_num(df)
        
        df_res = self.run_2_result(df)
        
        df_res = self.rename_columns(df_res)
        
        self.save_result(df_res)
        
        return df_res

if __name__ == '__main__':
    current_path = os.path.dirname(os.path.abspath(__file__))
    # db_path = 'UHGP.db'
    db_path = os.path.join(current_path, '../../.local_tests/UHGP.db')
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
        exclude_protein_startwith='REV_;XXX_' # separated by ';'
        
    )
    annotator.run_annotate()

    print(f'Running time: {time.time() - t0} seconds')