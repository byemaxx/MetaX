# pep2taxafunc: Extract the taxonomic level and functions of each protein group
- Input: a list of protein names (e.g., ['MGYG00000001_1', 'MGYG000000])
- Output: a list of taxonomic levels and annotations of each protein group

## Changelog

- Date: 2023-01-17
  - Version: 0.21
  - Update: Change COG to eggNOG_OGs, COG_category, Description, Preferred_name, GOs, KEGG_ko, KEGG_Pathway, PFAMs and return their proportion of each annotation

- Date: 2023-02-16
  - Version: 0.22
  - Change: Output format to a dictionary



## Dependencies

- `collections`
- `sqlite3`

## Functions

- `open_eggnog_db(db_path)`: Open the database of eggNOG annotation of MGYG and return the connection.
- `query_taxon_from_db(conn, protein_list)`: Return a list of taxonomic levels of each protein.
- `find_LCA(taxa_list, threshold=1)`: Return the last common ancestor and its percentage.
- `query_protein_from_db(conn, protein_list)`: Return a dictionary of annotations of each protein.
- `stats_fun(re_dict)`: Find the most common annotation and its percentage.
- `create_dict_out(function_results, taxa_results)`: Return a dictionary of taxonomic level and annotation and their percentage.
- `proteins_to_taxa_func(protein_list: list, db_path: str, threshold=1) -> dict`: Main function to process the input list of proteins and return a dictionary of taxonomic level and annotation.


## Usage
### Import the necessary modules
```python
from collections import Counter
import sqlite3
```
### Test Data
```python
protein_list = [
    "pep0", "pep1", "pep2", "pep3", "pep4",
    "pep5", "pep6", "pep7", "pep8", "pep9",
    "pep10", "pep11", "pep12"
]

db_path = "path/to/your/database.db"
```
### Main usage example
```python
results = proteins_to_taxa_func(protein_list, db_path, threshold=1)
print(results)
```
