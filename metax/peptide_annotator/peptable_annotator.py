# This script is used to call the function proteins_to_taxa_func in pep2taxafunc.py
# input: table of final peptides from MetaLab_MAG
# output: table of final peptides with taxonomic and functional information

from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import re
from tqdm import tqdm
import time
import argparse
import os

if __name__ == '__main__':

    from pep2taxafunc import proteins_to_taxa_func
    from convert_id_to_name import add_pathway_name_to_df, add_ec_name_to_df, add_ko_name_to_df
else:
    from .pep2taxafunc import proteins_to_taxa_func
    from .convert_id_to_name import add_pathway_name_to_df, add_ec_name_to_df, add_ko_name_to_df

# run the function proteins_to_taxa_func
def run_pep2taxafunc(proteins, db_path, threshold, genome_mode) -> dict:
    protein_list = str(proteins).split(';')
    #print(protein_list)
    try:
        re = proteins_to_taxa_func(
            protein_list=protein_list,
            db_path=db_path,
            threshold=threshold,
            genome_mode=genome_mode,
        )
    except Exception as e:
        re = {}
        print(f"Error: {protein_list}")
        print(e)
    return re


def stat_length(seq): # count the length of peptide sequence
    pattern = re.compile(r'\(.*?\)')
    return len(re.sub(pattern, '', seq))

def count_protein(proteins): # count the number of proteins in a protein group
    return len(proteins.split(';'))

def apply_run(row, db_path, threshold, genome_mode) -> dict:
    result = run_pep2taxafunc(row, db_path, threshold, genome_mode)
    return result


def add_additional_columns(df):
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
        

def run_2_result(df, db_path, threshold, genome_mode):
    tqdm.pandas()
    df_t = df.copy()
    # print('Counting protein number and peptide length...')
    # df_t['protein_count'] = df_t.loc[:, 'Proteins'].progress_apply(count_protein)
    # df_t['peptide_length'] = df_t.iloc[:,0].progress_apply(stat_length)
    print('Running proteins_to_taxa_func...')
    
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(apply_run, protein, db_path, threshold, genome_mode) for protein in df_t['Proteins']]
        results = [future.result() for future in tqdm(futures, total=len(futures))]

    # convert the results to dataframe
    df_t0 = pd.DataFrame(results, index=df_t.index)
    # try to add pathway name and EC name
    df_t0 = add_additional_columns(df_t0)
    # add the columns of None and None_prop
    df_t0['None'] = 'none'
    df_t0['None_prop'] = '1.0'
    
    
    # change the column names of 'Description'	'Description_prop' to 'eggNOG_Description'	'eggNOG_Description_prop'
    if 'Description' in df_t0.columns:
        df_t0.rename(columns={'Description':'eggNOG_Description', 'Description_prop':'eggNOG_Description_prop'}, inplace=True)
    if 'Preferred_name' in df_t0.columns:
        df_t0.rename(columns={'Preferred_name':'Gene', 'Preferred_name_prop':'Gene_prop'}, inplace=True)
    else:
        print('Warning: column name "Description" does not exist!, skip renaming...')
        
    df_t = pd.concat([df_t, df_t0], axis=1) # concatenate the annotation results to the original dataframe
    # reorder the columns
    cols = df_t.columns.tolist()
    sample_cols = [col for col in cols if col.startswith('Intensity_')]
    for col in sample_cols:
        cols.remove(col)
        cols.append(col)
    df_t = df_t.reindex(columns=cols)
    return df_t

def save_result(df, output_path):
    dir_path = os.path.dirname(output_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f'Output directory did not exist, created: {dir_path}')
    
    if os.path.exists(output_path):
        counter = 1
        base_name = os.path.splitext(os.path.basename(output_path))[0]  # get base name without extension
        ext = os.path.splitext(output_path)[-1]
        new_output_path = os.path.join(dir_path, f'{base_name}_{counter}{ext}')
        while os.path.exists(new_output_path):
            counter += 1
            new_output_path = os.path.join(dir_path, f'{base_name}_{counter}{ext}')
        output_path = new_output_path
        print(f'Output file already exists, saved as: {output_path}')
    
    df.to_csv(output_path, sep='\t', index=False)
    print(f'Output file: {output_path}')
    print(f'Output shape: {df.shape}')

def remove_human(df):
    print('Removing human proteins...')
    print(f'Original shape: {df.shape}')
    df = df[~df['Proteins'].str.contains('HUMAN')]
    print(f'After removing human proteins: {df.shape}')
    return df

def remove_reversed(df):
    print('Removing reversed proteins...')
    print(f'Original shape: {df.shape}')
    df = df[~df['Proteins'].str.contains('REV_')]
    print(f'After removing reversed proteins: {df.shape}')
    return df

def peptableAnnotate(final_peptides_path, output_path, db_path, threshold=1.0, genome_mode=True):
    threshold = round(float(threshold), 4) # round to 4 decimal places to avoid float precision problem
    print('Start running Peptide Annotator...')
    print(f'Input file: {final_peptides_path}')
    print(f'Database: {db_path}')
    print(f'Threshold: {threshold}')
    print(f'Genome mode: {genome_mode}')
    print(f'Output file: {output_path}')
    print('-----------------------------------')
    
    # check if the input file exists
    if not os.path.exists(final_peptides_path):
        raise FileNotFoundError(f'Input file not found: {final_peptides_path}')
    if not os.path.exists(db_path):
        raise FileNotFoundError(f'Database file not found: {db_path}')
    
    df = pd.read_csv(final_peptides_path, sep='\t')
    # df = df[:10] #! for testing
    # modify the column names
    df.columns = [col.replace(' ','_') for col in df.columns]
    
    # filter the peptides with intensity 0 in all samples
    print(f'Original shape: {df.shape}')
    df = df.loc[:, ['Sequence', 'Proteins'] + [col for col in df.columns if col.startswith('Intensity_')]]
    print(f'After filtering Intensity 0 in all samples and removing other columns: {df.shape}')
    
    # remove human proteins and reversed proteins
    # df = remove_human(df)
    df = remove_reversed(df)
    
    # run the function proteins_to_taxa_func
    df_res = run_2_result(df,db_path, threshold, genome_mode)
    
    save_result(df_res, output_path)
    
    return df_res
    
    
# if __name__ == '__main__':
#     final_peptides_path = 'C:/Users/Qing/Desktop/Example_final_peptide.tsv'
#     output_path = 'C:/Users/Qing/Desktop/1.tsv'
#     db_path = 'C:/Users/Qing/Desktop/MetaX_Suite/metaX_dev_files/MetaX-human-gut_20231211.db'
#     threshold = 1
#     t0 = time.time()
#     peptableAnnotate(final_peptides_path, output_path, db_path, threshold, genome_mode=True)
#     print(f'Running time: {time.time() - t0} seconds')
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Peptides to Taxa and Function')
    parser.add_argument('-i', '--input', help='Input file path (final_peptide.tsv of MetaLab)', required=True)
    parser.add_argument('-o', '--output', help='Output file path', required=True)
    parser.add_argument('-d', '--database', help='Database path', required=True)
    parser.add_argument('-t', '--threshold', help='Threshold of the proportion of taxa in a protein group', default=1.0)
    parser.add_argument('--genome_mode', help='Whether to use genome mode', action='store_true')
    args = parser.parse_args()
    
    t0 = time.time()
    peptableAnnotate(args.input, args.output, args.database, args.threshold, args.genome_mode)
    print(f'Running time: {time.time() - t0} seconds')
