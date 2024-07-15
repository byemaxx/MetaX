# This script is used to convert the MetaLab 2.3 results to OTF table.
# input: 
#   peptide_file: maxquant_search/combined/txt/peptides_report.txt -> for the pep2pro_dict 
#   pepTaxa_file: maxquant_search/taxonomy_analysis/BuiltIn.pepTaxa.csv -> for the peptide taxonomy and intensity
#   functions_file: maxquant_search/functional_annotation/functions.tsv
# output:
#   - OTF.tsv

import pandas as pd
from tqdm import tqdm
from typing import Optional, Dict, List
from collections import Counter
import os

class MetaLab2OTF:
    def __init__(self, peptide_file, pepTaxa_file, functions_file, save_path: Optional[str] = None):
        self.peptide_file = peptide_file
        self.pepTaxa_file = pepTaxa_file
        self.functions_file = functions_file
        self.save_path = save_path
        self.check_files()
        
        self.pep2pro_dict: Dict[str, List[str]] = {} # AAAAAPEAPVCIGR: ['HT14A_GL0083014', 'V1.CD54-0_GL0054240']
        self.pepTaxa_df: Optional[pd.DataFrame] = None # peptide taxonomy dataframe
        self.df_anno: Optional[pd.DataFrame] = None # protein annotation dataframe, index is the protein name, each column is a function
        self.func_list: List[str] = []
        self.anno_protein_list: List[str] = []
        
        
        
    def check_files(self):
        files = [self.peptide_file, self.pepTaxa_file, self.functions_file]
        for file in files:
            if not os.path.isfile(file):
                raise FileNotFoundError(f'{file} is not found!')
        print('All files are found!')
        
        # check the save_path parent directory exists
        if self.save_path:
            save_dir = os.path.dirname(self.save_path)
            if not os.path.isdir(save_dir):
                # create the directory if it does not exist
                os.makedirs(save_dir)
                print(f'Created the directory: {save_dir}')
                
        
    def create_pep2pro_dict(self):
        print('Creating the peptide to proteins dictionary...')
        df = pd.read_csv(self.peptide_file, sep='\t')

        # # Split the proteins by ';'
        df['Proteins'] = df['Proteins'].str.split(';')

        # set the index to the peptide sequence and convert the dataframe to a dictionary
        self.pep2pro_dict = df.set_index('Sequence')['Proteins'].to_dict()

        print(f'Total number of peptides: {len(self.pep2pro_dict)}')
        

        
    # Format taxonomy column
    def format_taxonomy(self, row):
        # use row.get('column_name', '')  to return '' if the column is not found or empty
        taxon =  f"d__{row['Superkingdom']}|p__{row['Phylum']}|c__{row['Class']}|o__{row['Order']}|f__{row['Family']}|g__{row['Genus']}|s__{row['Species']}"
        taxon = taxon.replace('nan', '')
        return taxon
                    
    def create_pepTaxa_df(self):
        '''
        Process a CSV file containing peptide taxonomy data and transform it into a
        simplified DataFrame with essential `taxonomy`, `rank information` and `intensity values`.
        
        input:
    
            | Peptide id | Sequence           | LCA             | Rank    | Superkingdom | Kingdom | Phylum       | Class       | Order        | Family         | Genus      | Species          |LFQ intensity F1| 
            |------------|--------------------|-----------------|---------|--------------|---------|--------------|-------------|--------------|----------------|------------|------------------|----------------| 
            | 1          | AAAAAKDVIELAK      | Bacteroides     | Genus   | Bacteria     |         | Bacteroidetes| Bacteroidia | Bacteroidales| Bacteroidaceae | Bacteroides|                  |100             |
            | 2          | AAAAAPEAPVCIGR     | Blautia sp. YL58| Species | Bacteria     |         | Firmicutes   | Clostridia  | Eubacteriales| Lachnospiraceae| Blautia    | Blautia sp. YL58 |0               |
            | 3          | AAAAAQHHLYGTTSGK   | Bacteroides     | Genus   | Bacteria     |         | Bacteroidetes| Bacteroidia | Bacteroidales| Bacteroidaceae | Bacteroides|                  |200             |
                    
        return:
            
            taxa_df:
            | Sequence            | LCA_level | Taxon                                                 | Taxon_prop |Intensity F1| ...
            |---------------------|-----------|-------------------------------------------------------|------------|------------|----
            | 0	AAAAAKDVIELAK     | genus     | d__Bacteria|p__Bacteroidetes|c__Bacteroidia|o_...     | 1          |100         | ...
            | 1	AAAAAPEAPVCIGR    | species   | d__Bacteria|p__Firmicutes|c__Clostridia|o__Eub...     | 1          |0           | ...
            | 2	AAAAAQHHLYGTTSGK  | genus     | d__Bacteria|p__Bacteroidetes|c__Bacteroidia|o_...     | 1          |200         | ...
            
        '''
        print('Reading the peptide taxonomy file...')
        
        pepTaxa_df = pd.read_csv(self.pepTaxa_file)
        print(f'The number of peptides: {len(pepTaxa_df)}')
        
        
        # create a df with only taxonomy information
        rank_df = pepTaxa_df[['Rank']].value_counts().reset_index()
        rank_df.columns = ['Rank', 'Count']
        rank_df['Percentage'] = rank_df['Count'] / rank_df['Count'].sum() * 100
        print(rank_df) # print the rank distribution

        extract_list = ['Sequence', 'Rank', 'Superkingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']
        samples_list = [col for col in pepTaxa_df.columns if "LFQ intensity" in col]
        extract_list += samples_list

        df_pep_taxa = pepTaxa_df[extract_list]

        # Process each row to format the taxonomy information
        tqdm.pandas(desc="Formatting taxonomy")
        df_pep_taxa = df_pep_taxa.copy() # use copy to avoid SettingWithCopyWarning

        df_pep_taxa.loc[:, 'Taxon'] = df_pep_taxa.progress_apply(self.format_taxonomy, axis=1)
        df_pep_taxa.loc[:, 'LCA_level'] = df_pep_taxa['Rank'].apply(lambda x: x.lower().replace('superkingdom', 'domain'))
        df_pep_taxa.drop(columns=['Rank', 'Superkingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species'], inplace=True)
        df_pep_taxa.loc[:, 'Taxon_prop'] = 1
        
        # move samples to the end
        df_pep_taxa = df_pep_taxa[['Sequence', 'LCA_level', 'Taxon', 'Taxon_prop'] + samples_list]
        df_pep_taxa.columns =  [col.replace("LFQ intensity", "Intensity") for col in df_pep_taxa.columns]
        
        self.pepTaxa_df = df_pep_taxa
        print('Peptide taxonomy dataframe is created!')
    
    
    def create_df_anno(self):
        '''
        Read the functional annotation file and return a DataFrame with the protein name as the index, each column is a function.
        '''
        print('Reading the functions file...')
        df_anno = pd.read_csv(self.functions_file, sep='\t')
        df_anno.set_index('Name', inplace=True) # "Name" is the protein name

        df_anno.columns
        
        extract_list = [
            'Preferred name', 'Gene_Ontology_id', 'Gene_Ontology_name', 
            'Gene_Ontology_namespace', 'EC_id', 'EC_de',
            'EC_an', 'EC_ca', 'KEGG_ko', 'KEGG_Pathway_Entry', 'KEGG_Pathway_Name',
            'KEGG_Module', 'KEGG_Reaction', 'KEGG_rclass', 'BRITE', 'KEGG_TC',
            'CAZy', 'BiGG_Reaction', 'COG accession', 'COG category', 'COG name',
            'NOG accession', 'NOG category', 'NOG name'
       ]
        
        # check if the columns are in the dataframe
        available_columns = [col for col in extract_list if col in df_anno.columns]
        self.func_list = available_columns
        
        # print(f'Etracting the following columns: {available_columns}')
        df_anno = df_anno[available_columns]
        print(f'The number of proteins: {len(df_anno)}')
        self.df_anno = df_anno
        self.anno_protein_list = df_anno.index.tolist()
    

    def get_func_dict(self, protein_list):
        df_anno = self.df_anno
        funcs = self.func_list # save as local variable to avoid multiple lookups in the loop

        func_dict = {func: [] for func in funcs}

        for protein in protein_list:
            if protein in df_anno.index:
                for func in funcs:
                    func_query_result = df_anno.at[protein, func]
                    func_dict[func].append(func_query_result if pd.notnull(func_query_result) else '-')
            else:
                for func in funcs:
                    func_dict[func].append('-')

        return func_dict

    # find the most common annotation and its percentage
    def stats_fun(self, func_dict):
        '''
        input:
            re_dict: {'Preferred name': ['tccB'], 'Gene_Ontology_id': [nan], ...}
        return:
            {'Preferred name': ('tccB', 1.0), 'Gene_Ontology_id': (nan, 1.0), ...}
        '''
        stats = {}
        for func_type, anno_list in func_dict.items():
            count = Counter(anno_list)
            most_common, count_most_common = count.most_common(1)[0]
            stats[func_type] = (most_common, count_most_common / len(anno_list))
        return stats



    def get_func_res_dict_from_pep(self, pep_seq: str):
        protein_list = self.pep2pro_dict.get(pep_seq, [])
        func_dict = self.get_func_dict(protein_list)
        function_results =  self.stats_fun(func_dict)
        
        re_out = {'Proteins': ";".join(protein_list)}
        for function, (result, proportion) in function_results.items():
            re_out[function] = result
            re_out[f'{function}_prop'] = proportion
        
        return re_out
    
    

    def run_pep2taxafunc(self) -> pd.DataFrame:
        def anno_func_by_row(row):
            peptide = row.Sequence
            func_dict = self.get_func_res_dict_from_pep(peptide)
            return pd.Series(func_dict)
        
        print('Processing peptides to taxonomy and functional annotation...')
        df_pep_taxa = self.pepTaxa_df.copy()
        # df_pep_taxa = df_pep_taxa.head(2000)
        
        tqdm.pandas(desc="Processing peptides")
        df_func_re = df_pep_taxa.progress_apply(anno_func_by_row, axis=1, result_type='expand')

        print('Merging the final dataframe...')
        # replace the space with underscore
        df_func_re.columns = df_func_re.columns.str.replace(' ', '_')
        # fill the NaN values with '-'
        df_func_re.fillna('-', inplace=True)

        # merge the peptide intensity dataframe with the functional annotation dataframe
        
        df_re = pd.concat([df_pep_taxa, df_func_re], axis=1)

        return df_re
    
    def main(self, save_path: Optional[str] = None):
        self.create_pep2pro_dict()
        self.create_pepTaxa_df()
        self.create_df_anno()
        df_re = self.run_pep2taxafunc()
        save_path = save_path if save_path else self.save_path # if save_path is not provided, use the default save_path
        if save_path:
            df_re.to_csv(save_path, sep='\t', index=False)
            print(f'OTFs table is saved to: {save_path}')
        return df_re
        
if __name__ == '__main__':
    path = "./Maxquant_workflow"
    pepTaxa_file = f"{path}/maxquant_search/taxonomy_analysis/BuiltIn.pepTaxa.csv"
    peptide_file = f"{path}/maxquant_search/combined/txt/peptides_report.txt"
    functions_file = f"{path}/maxquant_search/functional_annotation/functions.tsv"
    save_path = f"{path}/OTF.tsv"
    
    m2o = MetaLab2OTF(peptide_file, pepTaxa_file, functions_file, save_path)
    m2o.main()