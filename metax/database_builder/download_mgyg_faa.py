# -*- coding: utf-8 -*-
import pandas as pd
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

def get_mgyg_list(meta_path):
    try:
        df = pd.read_csv(meta_path, sep='\t', header=0)
        if 'Species_rep' not in df.columns:
            raise ValueError("Invalid metadata file format: 'Species_rep' column not found")
        return df['Species_rep'].unique().tolist()
    except Exception as e:
        print(f"Failed to read metadata file: {str(e)}")
        raise

def create_download_list(mgyg_list, db_type = "human-gut"):
    if db_type not in DB_URLS:
        raise ValueError(f"Unsupported database type: {db_type}")
        
    db_info = DB_URLS[db_type]
    base_url = f"{db_info['base_url']}/{db_info['catalogue']}"
    url_list = []
    
    for i in mgyg_list:
        try:
            group = i.split(".")[0] if "." in i else i
            id_group = "MGYG000" + group[-6:-2]
            url_list.append(f"{base_url}/{id_group}/{i}/genome/{i}.faa")
        except Exception as e:
            print(f"Error processing MGYG ID {i}: {str(e)}")
            continue
    return url_list

def download_faa_files(down_list, save_path):
    dir_name = 'faa_files'
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
    print("FAA files download completed.")

def run_download(save_path = "./mouse-gut", db_type = "mouse-gut"):
    try:
        print(f'Files will be saved to: {save_path}')
        print(f'Files will be saved to: {save_path}')
        print(f'Database type: {db_type}')
        
        # Download metadata file
        meta_path = download_mgyg2taxa(save_path, db_type)
        
        # Get MGYG list
        mgyg_list = get_mgyg_list(meta_path)
        print(f"Found {len(mgyg_list)} MGYG IDs")
        
        # Create download list
        down_list = create_download_list(mgyg_list, db_type)
        print(f"Preparing to download {len(down_list)} FAA files")
        
        # Download FAA files
        download_faa_files(down_list, save_path)
        
    except Exception as e:
        print(f"\nProgram execution error: {str(e)}")
        raise

if __name__ == "__main__":
    run_download(save_path="./mouse-gut", db_type="mouse-gut")