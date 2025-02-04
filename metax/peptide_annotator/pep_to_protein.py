# This script is used to map peptides to proteins of built database
# e.g. VAGDKFDEAISTYVK -> {MGYG000000546_02430, MGYG000000076_00704}

import sqlite3
import json
        
def query_peptide_proteins(db_file, peptide_list):
    """
    Query peptide to protein mapping from a database.
    This function connects to a SQLite database, executes a query to retrieve
    the mapping of peptides to proteins, and returns the results as a dictionary.
    Args:
        db_file (str): The file path to the SQLite database.
        peptide_list (list of str): A list of peptide sequences to query.
    Returns:
        dict: A dictionary where the keys are peptide sequences and the values
              are sets of protein identifiers associated with each peptide.
    """

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    query = "SELECT peptide, proteins FROM peptide_proteins WHERE peptide IN ({seq})".format(
        seq=','.join('?' for _ in peptide_list))

    cursor.execute(query, peptide_list)
    rows = cursor.fetchall()
    conn.close()
    
    # Convert JSON-encoded to Dict
    peptide_proteins = {peptide: (set(json.loads(proteins))) for peptide, proteins, in rows}
    return peptide_proteins




if __name__ == "__main__":
    peptide_to_query = ["TGAFFPSLLK", "TGAFFPSLLKIVNFNLNYR", "QALGMIETK" ]
    result = query_peptide_proteins(db_file="Z:/Qing/Projects/UHGP/peptide_to_protein.db", 
                                    peptide_list=peptide_to_query)
    print("result:",)
    for peptide, proteins in result.items():
        print(len(proteins))
        print(peptide)
        print(list(proteins)[:10]) 
