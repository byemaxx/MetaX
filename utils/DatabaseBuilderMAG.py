# This script is used to build the database for the MetaX tool 
# database from: Unified Human Gastrointestinal Genome (UHGG) v2.0.1
# database ftp: http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-gut/v2.0.1/
# need to download: 
#   1. the MGYG to EggNOG mapping files in the data folder
#   2. the MGYG to Taxa mapping file 

# output:
# A SQLite database with two tables: 1. eggnog 2. id2annotation in one database
# 
# change log:
# 2023-06-07: add database for chicken-gut, cow-rumen, human-oral, marine, non-model-fish-gut, pig-gut, zebrafish-fecal


import argparse
import pandas as pd
import sqlite3
import os
import urllib.request
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing



def download_mgyg2taxa(save_path, db_type = "human-gut"):
    url_dict = {
                "chicken-gut": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/chicken-gut/v1.0.1/genomes-all_metadata.tsv",
                "cow-rumen": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/cow-rumen/v1.0.1/genomes-all_metadata.tsv",
                "honeybee-gut": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/honeybee-gut/v1.0.1/genomes-all_metadata.tsv",
                "human-gut": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-gut/v2.0.2/genomes-all_metadata.tsv",
                "human-oral": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-oral/v1.0.1/genomes-all_metadata.tsv",
                "human-vaginal": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-vaginal/v1.0/genomes-all_metadata.tsv",
                "marine": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/marine/v1.0/genomes-all_metadata.tsv",
                "mouse-gut": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/mouse-gut/v1.0/genomes-all_metadata.tsv",
                "non-model-fish-gut": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/non-model-fish-gut/v2.0/genomes-all_metadata.tsv",
                "pig-gut": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/pig-gut/v1.0/genomes-all_metadata.tsv",
                "zebrafish-fecal": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/zebrafish-fecal/v1.0/genomes-all_metadata.tsv"                
                }

    if not os.path.exists(save_path):
        os.makedirs(save_path)
    url = url_dict[db_type]
    file_name = url.split('/')[-1]
    path = os.path.join(save_path, file_name)
    
    if os.path.exists(path):
        print(f"{file_name} already exists. Skip downloading.")
        return
    print(f"Downloading genomes-all_metadata.tsv from {url}...")
    with tqdm(unit='B', unit_scale=True, miniters=1, desc=file_name) as t:
        urllib.request.urlretrieve(url, path, reporthook=lambda x, y, z: t.update(y))
        print(f"{file_name} downloaded.")


# Create id2taxa database and return a list of MGYG IDs
def build_id2taxa_db(save_path, db_name, file_name = 'genomes-all_metadata.tsv', meta_path = None):
    if meta_path is None:
        df = pd.read_csv(os.path.join(save_path, file_name), sep='\t', header=0, index_col=0)
    else:
        df = pd.read_csv(meta_path, sep='\t', header=0, index_col=0)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    df = df[['Species_rep', 'Lineage']]
    # rename the columns
    df.columns = ['ID', 'Taxa']
    df = df.drop_duplicates()
    df.set_index('ID', inplace=True)
    db_path = os.path.join(save_path, db_name)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    table_name = "id2taxa"
    query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
    result = c.execute(query).fetchall()
    
    if len(result) > 0:
        print(f"{table_name} already exists in db. Skip building.")
    else:
    
        df.to_sql("id2taxa", conn, index= True, if_exists= 'replace')
        
        print("id2taxa database built completely.")
    return df.index.tolist()


def create_download_list(mgyg_list, db_type = "human-gut"):
    url_dict = {
                "chicken-gut": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/chicken-gut/v1.0.1/species_catalogue",
                "cow-rumen": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/cow-rumen/v1.0.1/species_catalogue",
                "honeybee-gut": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/honeybee-gut/v1.0.1/species_catalogue",
                "human-gut": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-gut/v2.0.2/species_catalogue",
                "human-oral": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-oral/v1.0.1/species_catalogue",
                "human-vaginal": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-vaginal/v1.0/species_catalogue",
                "marine": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/marine/v1.0/species_catalogue",
                "mouse-gut": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/mouse-gut/v1.0/species_catalogue",
                "non-model-fish-gut": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/non-model-fish-gut/v2.0/species_catalogue",
                "pig-gut": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/pig-gut/v1.0/species_catalogue",
                "zebrafish-fecal": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/zebrafish-fecal/v1.0/species_catalogue",
                
                
                
                }
    url = url_dict[db_type]
    url_list = []
    for i in mgyg_list:
        group = i.split(".")[0] if "." in i else i
        id_group = "MGYG000" + group[-6:-2]
        url_list.append(f"{url}/{id_group}/{i}/genome/{i}_eggNOG.tsv")
    return url_list



def download_file(url, save_path):
    file_name = url.split('/')[-1]
    with urllib.request.urlopen(url) as response, open(os.path.join(save_path, file_name), 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    return file_name


def download_id2annotation(down_list, save_path):
    dir_name = 'id2annotation'
    os.makedirs(os.path.join(save_path, dir_name), exist_ok=True)
    
    need_download_list = []
    for url in down_list:
        file_name = url.split('/')[-1]
        if not os.path.exists(os.path.join(save_path, dir_name, file_name)):
            need_download_list.append(url)
        else:
            print(f"{file_name} already exists. Skip downloading.", end='\r')
            
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download_file, url, os.path.join(save_path, dir_name)) for url in need_download_list]
        with tqdm(total=len(need_download_list), desc="Downloading") as pbar:
            for future in as_completed(futures):
                result = future.result()
                pbar.update(1)
                pbar.set_postfix_str(result)
    print("Annotation files downloaded completely.")


def read_file(args):
    file_path = args[0]
    return pd.read_csv(file_path, sep='\t', header=0, index_col= None)


#! 会引发重复加载 主程序动画的问题, 有待解决
def build_id2annotation_db(save_path, db_name, dir_name = 'id2annotation', mgyg_dir = None):
    

    if mgyg_dir is None:
        file_list = os.listdir(os.path.join(save_path, dir_name))
        path = os.path.join(save_path, dir_name)
    else:
        file_list = os.listdir(mgyg_dir)
        path = mgyg_dir

    with multiprocessing.Pool() as pool:
        df_list = list(tqdm(pool.imap(read_file, [(os.path.join(path, f),) for f in file_list]), desc='Loading annotation files', total=len(file_list)))
    
    print("Concatenating annotation files...")
    df = pd.concat(df_list, ignore_index=True)
    df = df.drop_duplicates()
    df = df.rename(columns=lambda x: x.replace('#', ''))
    #rename the first column to ID
    df.rename(columns={df.columns[0]: "ID"}, inplace=True)
    # drop cols with no annotation info
    drop_list = ['seed_ortholog', 'evalue', 'score']
    columns_exist = all(col in df.columns for col in drop_list)
    if columns_exist:
        df.drop(drop_list, axis=1, inplace=True)
    else:
        print(f"Columns {drop_list} not found. Skip dropping.")

    df.set_index('ID', inplace=True)
    print("Annotation files concatenated completely.")

    # df.to_csv(os.path.join(save_path, 'id2annotation.tsv'), sep='\t')

    # Check if table exists
    conn = sqlite3.connect(os.path.join(save_path, db_name))
    c = conn.cursor()
    table_name = "id2annotation"
    query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
    result = c.execute(query).fetchall()

    # If table exists, skip building else build
    if len(result) > 0:
        print(f"{table_name} already exists in db. Skip building.")
    else:
        print("id2annotation database building...")
        df.to_sql("id2annotation", conn, index=True, if_exists='replace')
        print("id2annotation database built completely.")

def query_download_list(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    sql = "SELECT DISTINCT Species_rep FROM id2taxa"
    result = c.execute(sql).fetchall()
    return [i[0] for i in result]



def check_db(db_path):
    if not os.path.exists(db_path):
        return "no db"

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='id2taxa';"
    sql2 = "SELECT name FROM sqlite_master WHERE type='table' AND name='id2annotation';"
    result = c.execute(sql).fetchall()
    result2 = c.execute(sql2).fetchall()
    if len(result) == 0:
        return "no id2taxa"
    else:
        return "no id2annotation" if len(result2) == 0 else "all exists"

def download_and_build_database(save_path, db_name, db_type, meta_path=None, mgyg_dir=None):
    db_path = os.path.join(save_path, db_name)
    status = check_db(db_path)

    if status in ["no db", "no id2taxa"]:
        if meta_path is None:
            download_mgyg2taxa(save_path, db_type)
        mgyg_list = build_id2taxa_db(save_path, db_name, meta_path= meta_path)
        down_list = create_download_list(mgyg_list, db_type)
        if mgyg_dir is None:
            download_id2annotation(down_list, save_path)
        build_id2annotation_db(save_path, db_name, mgyg_dir=mgyg_dir)


    elif status == "no id2annotation":
        print("The database already exists. Skip building id2taxa.")
        down_list = create_download_list(query_download_list(db_path), db_type)
        if mgyg_dir is None:
            download_id2annotation(down_list, save_path)
        build_id2annotation_db(save_path, db_name, mgyg_dir=mgyg_dir)

    else:
        print("The database already exists and complete. Skip building.")


# ### debug ###
# if __name__ == "__main__":
#     save_path = "C:/Users/ZAL/Desktop"
#     db_name = "MetaX.db"
#     db_type = "non-model-fish-gut"
#     download_and_build_database(save_path, db_name, db_type)

# ### debug ###

def build_db(args):
    if args.auto:
        # set the default save path and db name
        save_path = os.path.abspath('MetaX_database')
        db_name = 'MetaX.db'
        db_type = 'human-gut'
        
        print('The data will be downloaded and built automatically.')
        print(f'The database will be saved at:\n {os.path.join(save_path, db_name)}\n')
        download_and_build_database(save_path, db_name, db_type)
    
    if args.auto and args.db_type:
        save_path = os.path.abspath('MetaX_database')
        db_name = 'MetaX.db'
        
        print('The data will be downloaded and built automatically.')
        print(f'The database will be saved at:\n {os.path.join(save_path, db_name)}\n')
        download_and_build_database(save_path, db_name, db_type)


    elif args.meta_path and args.mgyg_dir and args.save_dir and args.db_name and args.db_type:
        save_path = os.path.abspath(args.save_dir)
        db_name = args.db_name
        meta_path = os.path.abspath(args.meta_path)
        mgyg_dir = os.path.abspath(args.mgyg_dir)
        print(f'The path of genomes-all_metadata.tsv is:\n {meta_path}\n')
        print(f'The directory of eggNOG annotation is:\n {mgyg_dir}\n')
        print(f'The path of database you want to save is:\n {save_path}\n')
        print(f'The name of database you want to save is:\n {db_name}\n')
        download_and_build_database(save_path, db_name, db_type, meta_path=meta_path, mgyg_dir=mgyg_dir)

    elif args.save_dir and args.db_name and args.db_type:
        save_path = os.path.abspath(args.save_dir)
        db_name = args.db_name
        print(f'The path of database you want to save is:\n {save_path}\n')
        print(f'The name of database you want to save is:\n {db_name}\n')
        print("The data will be downloaded automatically.")
        download_and_build_database(save_path, db_name, db_type)
            
    else:
        parser.print_help()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Download Annotation of MGnify and create database for MetaX tool.')

    parser.add_argument('--auto', action='store_true',
                        help='download and build the database automatically and save it in MetaX_database in the current directory')

    parser.add_argument('--save_dir', metavar='PATH', type=str,
                        # default="123",
                        help='directory to save the database')
    parser.add_argument('--db_name', metavar='PATH', type=str,
                        # default="11.db",
                       help='set the name of the database')

    parser.add_argument('--meta_path', metavar='PATH', type=str,
                        # default= "test_download\genomes-all_metadata.tsv",
                        help='path of the genomes-all_metadata.tsv if you already downloaded')
    parser.add_argument('--mgyg_dir', metavar='PATH', type=str,
                        # default= "test_download\id2annotation",
                        help='directory of eggNOG annotation of UHGG if you already downloaded')
    parser.add_argument('--db_type', metavar='PATH', type=str,default="human-gut",
                        help='The db type for download. (human-gut,human-oral, chicken-gut, cow-rumen,	marine, non-model-fish-gut, pig-gut, zebrafish-fecal)')

    args = parser.parse_args()
    


    build_db(args)

