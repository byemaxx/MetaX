# TaxaFuncExplore Database Builder

This script is used to build the database for the TaxaFuncExplore tool. The database is created from the Unified Human Gastrointestinal Genome (UHGG) v2.0.1, which can be downloaded from the [European Molecular Biology Laboratory's European Bioinformatics Institute (EMBL-EBI) FTP site](http://ftp.ebi.ac.uk/pub/databases/metagenomics/mgnify_genomes/human-gut/v2.0.1/). The database contains two tables: `eggnog` and `mgyg2eggnog`.

## Usage

To run the script, you can use the following command-line arguments:

- `--auto`: Download and build the database automatically, saving it in the `TaxaFuncExplore_database` directory in the current working directory.
- `--save_dir`: Directory to save the database.
- `--db_name`: Set the name of the database.
- `--meta_path`: Path of the `genomes-all_metadata.tsv` file if you have already downloaded it.
- `--mgyg_dir`: Directory of EggNOG annotations of UHGG if you have already downloaded them.

## Functions

1. `download_mgyg2taxa(save_path)`: Download the `genomes-all_metadata.tsv` file if it does not already exist in the specified directory.
2. `build_mgyg2taxon_db(save_path, db_name, file_name = 'genomes-all_metadata.tsv', meta_path = None)`: Create the `mgyg2taxon` database and return a list of MGYG IDs.
3. `create_download_list(mgyg_list)`: Generate a list of URLs to download the `mgyg2eggnog` files.
4. `download_file(url, save_path)`: Download a file from the specified URL and save it to the given directory.
5. `download_mgyg2eggnog(down_list, save_path)`: Download the `mgyg2eggnog` files and save them in the specified directory.
6. `build_mgyg2eggnog_db(save_path, db_name, dir_name = 'mgyg2eggnog', mgyg_dir = None)`: Build the `mgyg2eggnog` database.
7. `query_download_list(db_path)`: Query the download list from the database.
8. `check_db(db_path)`: Check if the database exists and is complete.
9. `download_and_build_database(save_path, db_name, meta_path=None, mgyg_dir=None, time_start=None)`: Download and build the database, and print the total time taken.
10. `db_builder(args)`: Main function to build the database based on command-line arguments.

## Example Usage
```
python taxa_func_explore_db_builder.py --auto
```
This will download and build the database automatically, saving it in the `TaxaFuncExplore_database` directory in the current working directory.

