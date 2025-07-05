# -*- coding: utf-8 -*-
# This script is used to build the database for the MetaX tool 
# Database source: Unified Human Gastrointestinal Genome (UHGG) v2.0.1
# Database ftp: http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-gut/v2.0.1/
# Required downloads: 
#   1. MGYG to EggNOG mapping files in the data folder
#   2. MGYG to Taxa mapping file 

# Output:
# A SQLite database with two tables: 1. eggnog 2. id2annotation in one database

import argparse
import pandas as pd
import sqlite3
import os
import urllib.request
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from urllib.error import URLError, HTTPError

# Combined URL dictionary for all database types
DB_URLS = {
    "chicken-gut": {
        "base_url": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/chicken-gut/v1.0.1",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue"
    },
    "cow-rumen": {
        "base_url": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/cow-rumen/v1.0.1",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue"
    },
    "honeybee-gut": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/honeybee-gut/v1.0.1",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue"
    },
    "human-gut": {
        "base_url": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-gut/v2.0.2",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue"
    },
    "human-oral": {
        "base_url": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-oral/v1.0.1",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue"
    },
    "human-vaginal": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-vaginal/v1.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue"
    },
    "marine": {
        "base_url": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/marine/v2.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue"
    },
    "mouse-gut": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/mouse-gut/v1.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue"
    },
    "non-model-fish-gut": {
        "base_url": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/non-model-fish-gut/v2.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue"
    },
    "pig-gut": {
        "base_url": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/pig-gut/v1.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue"
    },
    "sheep-rumen": {
        "base_url": "https://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/sheep-rumen/v1.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue"
    },
    "zebrafish-fecal": {
        "base_url": "http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/zebrafish-fecal/v1.0",
        "metadata": "genomes-all_metadata.tsv",
        "catalogue": "species_catalogue"
    }
}

def download_with_retry(url, save_path, max_retries=3, retry_delay=5):
    """Download function with retry mechanism"""
    file_name = url.split('/')[-1]
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(url, timeout=30) as response, open(os.path.join(save_path, file_name), 'wb') as out_file:
                data = response.read()
                out_file.write(data)
            return file_name
        except (URLError, HTTPError) as e:
            if attempt < max_retries - 1:
                print(f"\nDownload failed for {file_name}, retrying in {retry_delay} seconds... (Error: {str(e)})")
                time.sleep(retry_delay)
            else:
                print(f"\nDownload failed for {file_name}, maximum retries reached.")
                return None
        except Exception as e:
            print(f"\nUnknown error occurred while downloading {file_name}: {str(e)}")
            return None

def download_mgyg2taxa(save_path, db_type = "human-gut"):
    """Download metadata file for the specified database type"""
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    if db_type not in DB_URLS:
        raise ValueError(f"Unsupported database type: {db_type}")
        
    db_info = DB_URLS[db_type]
    url = f"{db_info['base_url']}/{db_info['metadata']}"
    file_name = db_info['metadata']
    path = os.path.join(save_path, file_name)
    
    if os.path.exists(path):
        print(f"{file_name} already exists, skipping download.")
        return path
        
    print(f"Downloading genomes-all_metadata.tsv from {url}...")
    with tqdm(unit='B', unit_scale=True, miniters=1, desc=file_name) as t:
        try:
            urllib.request.urlretrieve(url, path, reporthook=lambda x, y, z: t.update(y))
            print(f"{file_name} download completed.")
        except Exception as e:
            print(f"\nDownload failed for {file_name}: {str(e)}")
            if os.path.exists(path):
                os.remove(path)
            raise
    return path

def build_id2taxa_db(save_path, db_name, file_name = 'genomes-all_metadata.tsv', meta_path = None):
    """Build id2taxa database and return a list of MGYG IDs"""
    try:
        if meta_path is None:
            df = pd.read_csv(os.path.join(save_path, file_name), sep='\t', header=0)
        else:
            df = pd.read_csv(meta_path, sep='\t', header=0)
            
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        df = df[['Species_rep', 'Lineage']]
        df.columns = ['ID', 'Taxa']
        df = df.drop_duplicates()
        df.set_index('ID', inplace=True)
        
        db_path = os.path.join(save_path, db_name)
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        table_name = "id2taxa"
        
        # Check if table exists
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        result = c.execute(query).fetchall()
        
        if len(result) > 0:
            print(f"{table_name} already exists in db, skipping.")
        else:
            df.to_sql("id2taxa", conn, index=True, if_exists='replace')
            print("id2taxa database built successfully.")
            
        return df.index.tolist()
        
    except Exception as e:
        print(f"Error building id2taxa database: {str(e)}")
        raise

def create_download_list(mgyg_list, db_type = "human-gut"):
    """Create list of download URLs for eggNOG files"""
    if db_type not in DB_URLS:
        raise ValueError(f"Unsupported database type: {db_type}")
        
    db_info = DB_URLS[db_type]
    base_url = f"{db_info['base_url']}/{db_info['catalogue']}"
    url_list = []
    
    for i in mgyg_list:
        try:
            group = i.split(".")[0] if "." in i else i
            id_group = "MGYG000" + group[-6:-2]
            url_list.append(f"{base_url}/{id_group}/{i}/genome/{i}_eggNOG.tsv")
        except Exception as e:
            print(f"Error processing MGYG ID {i}: {str(e)}")
            continue
    return url_list

def download_id2annotation(down_list, save_path):
    """Download eggNOG annotation files"""
    dir_name = 'id2annotation'
    os.makedirs(os.path.join(save_path, dir_name), exist_ok=True)
    
    need_download_list = []
    for url in down_list:
        file_name = url.split('/')[-1]
        if not os.path.exists(os.path.join(save_path, dir_name, file_name)):
            need_download_list.append(url)
        else:
            print(f"{file_name} already exists, skipping download.", end='\r')
    
    if not need_download_list:
        print("\nAll files already downloaded.")
        return
            
    print(f"\nStarting download of {len(need_download_list)} files...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download_with_retry, url, os.path.join(save_path, dir_name)) for url in need_download_list]
        with tqdm(total=len(need_download_list), desc="Downloading") as pbar:
            for future in as_completed(futures):
                result = future.result()
                if result:
                    pbar.update(1)
                    pbar.set_postfix_str(result)
    print("Annotation files download completed.")

def read_file(args):
    """Read and process a single annotation file"""
    file_path = args[0]
    try:
        # Files should already be validated, so we can read directly
        df = pd.read_csv(file_path, sep='\t', header=0, index_col=None)
        
        # Check if the dataframe is empty
        if df.empty:
            print(f"Warning: File {file_path} contains no data after reading.")
            return None
            
        return df
        
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        # Since files are pre-validated, any error here is unexpected
        raise

def validate_annotation_files(file_list, path):
    """Validate annotation files and return list of valid files"""
    valid_files = []
    invalid_files = []
    
    for f in file_list:
        file_path = os.path.join(path, f)
        try:
            if not os.path.exists(file_path):
                invalid_files.append(f"File does not exist: {f}")
                continue
            
            if os.path.getsize(file_path) == 0:
                invalid_files.append(f"Empty file: {f}")
                continue
            
            # Try to read the first few lines to check if it's a valid TSV
            with open(file_path, 'r', encoding='utf-8') as test_file:
                first_line = test_file.readline().strip()
                if not first_line or '\t' not in first_line:
                    invalid_files.append(f"Invalid TSV format: {f}")
                    continue
            
            valid_files.append(f)
            
        except Exception as e:
            invalid_files.append(f"Error checking {f}: {str(e)}")
    
    # If there are invalid files, raise an error with detailed information
    if invalid_files:
        error_msg = f"Found {len(invalid_files)} invalid annotation files out of {len(file_list)} total files:\n"
        for invalid in invalid_files[:20]:  # Show first 20 invalid files
            error_msg += f"  - {invalid}\n"
        if len(invalid_files) > 20:
            error_msg += f"  ... and {len(invalid_files) - 20} more invalid files\n"
        
        error_msg += f"\nValid files: {len(valid_files)}/{len(file_list)}\n"
        error_msg += "\nPlease check and re-download the invalid files before proceeding.\n"
        error_msg += "You can:\n"
        error_msg += "1. Delete the invalid files and re-run the download process\n"
        error_msg += "2. Check your internet connection and retry downloading\n"
        error_msg += "3. Verify the file URLs are accessible"
        
        raise ValueError(error_msg)
    
    print(f"All files are valid: {len(valid_files)}/{len(file_list)}")
    return valid_files

def build_id2annotation_db(save_path, db_name, dir_name = 'id2annotation', mgyg_dir = None):
    """Build id2annotation database from downloaded files"""
    try:
        if mgyg_dir is None:
            file_list = os.listdir(os.path.join(save_path, dir_name))
            path = os.path.join(save_path, dir_name)
        else:
            file_list = os.listdir(mgyg_dir)
            path = mgyg_dir

        print("Validating annotation files...")
        valid_files = validate_annotation_files(file_list, path)
        
        # If we reach here, all files are valid
        print("Loading annotation files...")
        with ThreadPoolExecutor() as executor:
            df_list = []
            futures = [executor.submit(read_file, (os.path.join(path, f),)) for f in valid_files]
            with tqdm(total=len(valid_files), desc="Processing files") as pbar:
                for future in as_completed(futures):
                    result = future.result()
                    pbar.update(1)
                    if result is not None:  # Only add non-None results
                        df_list.append(result)
        
        if not df_list:
            raise ValueError("No valid annotation data could be loaded from the files.")
        
        print(f"Successfully loaded {len(df_list)} annotation files.")
        
        print("Concatenating annotation files...")
        df = pd.concat(df_list, ignore_index=True)
        df = df.drop_duplicates()
        df = df.rename(columns=lambda x: x.replace('#', ''))
        df.rename(columns={df.columns[0]: "ID"}, inplace=True)
        
        # Drop columns with no annotation info
        drop_list = ['seed_ortholog', 'evalue', 'score']
        columns_exist = all(col in df.columns for col in drop_list)
        if columns_exist:
            df.drop(drop_list, axis=1, inplace=True)
        else:
            print(f"Columns {drop_list} not found, skipping drop.")

        df.set_index('ID', inplace=True)
        print("Annotation files concatenated successfully.")

        # Check if table exists
        conn = sqlite3.connect(os.path.join(save_path, db_name))
        c = conn.cursor()
        table_name = "id2annotation"
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        result = c.execute(query).fetchall()

        if len(result) > 0:
            print(f"{table_name} already exists in db, skipping.")
        else:
            print("Building id2annotation database...")
            df.to_sql("id2annotation", conn, index=True, if_exists='replace')
            print("id2annotation database built successfully.")
            
    except Exception as e:
        print(f"Error building id2annotation database: {str(e)}")
        raise

def query_download_list(db_path):
    """Query existing database for MGYG IDs"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Check what columns exist in the id2taxa table
        pragma_sql = "PRAGMA table_info(id2taxa)"
        columns_info = c.execute(pragma_sql).fetchall()
        column_names = [col[1] for col in columns_info]
        
        # Try ID first (our standard), then Species_rep (for compatibility)
        if 'ID' in column_names:
            sql = "SELECT DISTINCT ID FROM id2taxa"
        elif 'Species_rep' in column_names:
            sql = "SELECT DISTINCT Species_rep FROM id2taxa"
        else:
            raise ValueError(f"Neither 'ID' nor 'Species_rep' column found in id2taxa table. Available columns: {column_names}")
        
        result = c.execute(sql).fetchall()
        return [i[0] for i in result]
    except Exception as e:
        print(f"Error querying database: {str(e)}")
        raise

def check_db(db_path):
    """Check database status and return status string"""
    if not os.path.exists(db_path):
        return "no db"

    try:
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
    except Exception as e:
        print(f"Error checking database: {str(e)}")
        raise

def download_and_build_database(save_path, db_name, db_type, meta_path=None, mgyg_dir=None):
    """Main function to download and build the database"""
    try:
        db_path = os.path.join(save_path, db_name)
        status = check_db(db_path)

        if status in ["no db", "no id2taxa"]:
            if meta_path is None:
                download_mgyg2taxa(save_path, db_type)
            mgyg_list = build_id2taxa_db(save_path, db_name, meta_path=meta_path)
            down_list = create_download_list(mgyg_list, db_type)
            if mgyg_dir is None:
                download_id2annotation(down_list, save_path)
            build_id2annotation_db(save_path, db_name, mgyg_dir=mgyg_dir)

        elif status == "no id2annotation":
            print("Database already exists, skipping id2taxa build.")
            down_list = create_download_list(query_download_list(db_path), db_type)
            if mgyg_dir is None:
                download_id2annotation(down_list, save_path)
            build_id2annotation_db(save_path, db_name, mgyg_dir=mgyg_dir)

        else:
            print("Database already exists and complete, skipping build.")
            
    except Exception as e:
        print(f"Error in database build process: {str(e)}")
        raise

def build_db(args):
    """Build database based on command line arguments"""
    try:
        if args.auto:
            # Set default parameters
            save_path = os.path.abspath('MetaX_database')
            db_name = 'MetaX.db'
            db_type = args.db_type if args.db_type else 'human-gut'
            
            print('Data will be downloaded and built automatically.')
            print(f'Database will be saved at:\n {os.path.join(save_path, db_name)}\n')
            download_and_build_database(save_path, db_name, db_type)
        
        elif args.meta_path and args.mgyg_dir and args.save_dir and args.db_name and args.db_type:
            save_path = os.path.abspath(args.save_dir)
            db_name = args.db_name
            meta_path = os.path.abspath(args.meta_path)
            mgyg_dir = os.path.abspath(args.mgyg_dir)
            
            print(f'Path of genomes-all_metadata.tsv:\n {meta_path}\n')
            print(f'Directory of eggNOG annotation:\n {mgyg_dir}\n')
            print(f'Database save path:\n {save_path}\n')
            print(f'Database name:\n {db_name}\n')
            
            download_and_build_database(save_path, db_name, args.db_type, meta_path=meta_path, mgyg_dir=mgyg_dir)

        elif args.save_dir and args.db_name and args.db_type:
            save_path = os.path.abspath(args.save_dir)
            db_name = args.db_name
            
            print(f'Database save path:\n {save_path}\n')
            print(f'Database name:\n {db_name}\n')
            print("Data will be downloaded automatically.")
            
            download_and_build_database(save_path, db_name, args.db_type)
                
        else:
            parser.print_help()
            
    except Exception as e:
        print(f"Error in build process: {str(e)}")
        raise

if __name__ == "__main__":
    # download_and_build_database(
    #     save_path = os.path.abspath('C:/Users/Qing/Desktop/test'),
    #     db_name = 'MetaX.db',
    #     db_type = 'sheep-rumen'
    # )
    parser = argparse.ArgumentParser(
        description='Download Annotation of MGnify and create database for MetaX tool.')

    parser.add_argument('--auto', action='store_true',
                        help='Download and build the database automatically and save it in MetaX_database in the current directory')

    parser.add_argument('--save_dir', metavar='PATH', type=str,
                        help='Directory to save the database')
    parser.add_argument('--db_name', metavar='PATH', type=str,
                       help='Set the name of the database')

    parser.add_argument('--meta_path', metavar='PATH', type=str,
                        help='Path of the genomes-all_metadata.tsv if already downloaded')
    parser.add_argument('--mgyg_dir', metavar='PATH', type=str,
                        help='Directory of eggNOG annotation of UHGG if already downloaded')
    parser.add_argument('--db_type', metavar='TYPE', type=str, default="human-gut",
                        help='Database type (human-gut, human-oral, chicken-gut, cow-rumen, marine, non-model-fish-gut, pig-gut, zebrafish-fecal)')

    args = parser.parse_args()
    build_db(args)

