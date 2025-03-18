import pandas as pd
import os
import urllib.request

def download_kegg_files(save_path):
    try:
        url_map ='https://rest.kegg.jp/list/pathway'
        url_ko = 'https://rest.kegg.jp/list/pathway/ko'
        with open(os.path.join(save_path, 'pathway.tsv'), 'w') as f:
            for url in [url_map, url_ko]:
                response = urllib.request.urlopen(url)
                html = response.read().decode('utf-8')
                f.write(html)
                f.write('\n')
        print(f'pathway.tsv downloaded to {save_path}')
    except Exception as e:
        print('Error: download pathway.tsv failed!')
        print(e)
        
        
def download_kegg_module_files(save_path):
    url = "https://rest.kegg.jp/list/module/"
    try:
        urllib.request.urlretrieve(url, os.path.join(save_path, 'module.tsv'))
        print(f'ko.tsv downloaded to {save_path}')
    except Exception as e:
        print('Error: download ko.tsv failed!')
        print(e)


def download_ec_files(save_path):
    try:
        url = "https://ftp.expasy.org/databases/enzyme/enzyme.dat"
        urllib.request.urlretrieve(url, os.path.join(save_path, 'enzyme.dat'))
        print(f'enzyme.dat downloaded to {save_path}')
    except Exception as e:
        print('Error: download enzyme.dat failed!')
        print(e)
        
def download_ko_files(save_path):
    url = "https://rest.kegg.jp/list/ko"
    try:
        urllib.request.urlretrieve(url, os.path.join(save_path, 'ko.tsv'))
        print(f'ko.tsv downloaded to {save_path}')
    except Exception as e:
        print('Error: download ko.tsv failed!')
        print(e)
    

def parse_dat_file(file_path):
    if not os.path.exists(file_path):
        print(f'{file_path} does not exist!\nTry to download the file from https://ftp.expasy.org/databases/enzyme/enzyme.dat')
        download_ec_files(os.path.dirname(file_path))
        
    with open(file_path, 'r') as file:
        data = []
        record = {'EC_ID': None,  'EC_AN': None, 'EC_DE': None, 'EC_CA': [], 'EC_CC': []}
        cc_line = ''
        ca_line = ''
        for line in file:
            if line.startswith('ID'):
                record['EC_ID'] = line[3:].strip()
            elif line.startswith('DE'):
                record['EC_DE'] = line[3:].strip()
            elif line.startswith('AN'):
                record['EC_AN'] = line[3:].strip()
            elif line.startswith('CC'):
                # Check if this line starts a new CC field
                if line.startswith('CC   -!- '):
                    # If there's a previous CC field, add it to the record
                    if cc_line:
                        record['EC_CC'].append(cc_line)
                    # Start a new CC field
                    cc_line = line[9:].strip()
                else:
                    # If this line continues the current CC field, append it
                    cc_line += ' ' + line[3:].strip()
            elif line.startswith('CA'):
                # Check if this line starts a new CA field
                if line.startswith('CA   -!- '):
                    # If there's a previous CA field, add it to the record
                    if ca_line:
                        record['EC_CA'].append(ca_line)
                    # Start a new CA field
                    ca_line = line[9:].strip()
                else:
                    # If this line continues the current CA field, append it
                    ca_line += ' ' + line[3:].strip()
            elif line.startswith('//'):
                # End of record, add the last CC and CA field to the record
                if cc_line:
                    record['EC_CC'].append(cc_line)
                if ca_line:
                    record['EC_CA'].append(ca_line)
                # Add the record to data
                data.append(record)
                # Start a new record
                record = {'EC_ID': None,  'EC_AN': None, 'EC_DE': None, 'EC_CA': [], 'EC_CC': []}
                cc_line = ''
                ca_line = ''
        df = pd.DataFrame(data)
        # Join the 'EC_CC' and 'EC_CA' entries with '-!-' as the separator
        df['EC_CC'] = df['EC_CC'].apply(lambda x: '-!-'.join(x))
        df['EC_CA'] = df['EC_CA'].apply(lambda x: '-!-'.join(x))
        
        df.replace('', '-', inplace=True)
        df.fillna('-', inplace=True)
        # drop the row EC_ID == '-'
        df = df[df['EC_ID'] != '-']
        df.set_index('EC_ID', inplace=True)
        return df

def get_ec_dict():
    script_path = os.path.dirname(os.path.realpath(__file__))
    dat_path = os.path.join(script_path, '../data/enzyme.dat')
    df = parse_dat_file(dat_path)
    return df.to_dict(orient='index')
    
def get_pathway_dict():
    script_path = os.path.dirname(os.path.realpath(__file__))
    dat_path = os.path.join(script_path, '../data/pathway.tsv')
    if not os.path.exists(dat_path):
        print(f'{dat_path} does not exist!\nTry to download the file from https://rest.kegg.jp/list/pathway')
        download_kegg_files(os.path.dirname(dat_path))
        
    # create a dictionary of pathway IDs and names
    pathway_dict = {}
    with open(dat_path, 'r') as f:
        for line in f:
            if line.startswith('ko') or line.startswith('map'):
                line = line.strip().split('\t')
                pathway_dict[line[0]] = line[1]
    return pathway_dict


def lookup_and_join_for_EC(ec_nums: list, ec_dict:dict, column_name: str) -> str:
    """
    Look up values for each EC number and join them
    
    Args:
        ec_nums: List of EC numbers
        column_name: Name of column to look up in ec_dict
        
    Returns:
        Joined string of lookup values
    """
    values = []
    processed_nums = set()  # Track processed numbers to avoid recursion
    
    for ec_num in ec_nums:
        if ec_num in processed_nums:
            continue
            
        processed_nums.add(ec_num)
        res = ec_dict[ec_num][column_name]
        
        if res.startswith('Transferred entry:'):
            # Handle transferred entries
            new_ec_nums = res.split(':')[1].strip('.').replace(' ', '').split('and')
            # Add new numbers if not already processed
            new_nums = [num for num in new_ec_nums if num not in processed_nums]
            if new_nums:
                res = lookup_and_join_for_EC(new_nums, ec_dict, column_name)
                if res != '-':
                    values.append(res)
        else:
            values.append(res)
            
    # Process results
    if not values or all(value == '-' for value in values):
        return '-'
        
    # Remove duplicates and empty values
    values = list(dict.fromkeys(val for val in values if val != '-'))
    return ' | '.join(values)


def add_ec_name_to_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add EC name columns to dataframe by converting EC numbers to their corresponding information
    
    Args:
        df (pd.DataFrame): Input dataframe containing EC numbers
        
    Returns:
        pd.DataFrame: DataFrame with added EC name columns
    """

    # Check if EC column exists
    if 'EC' not in df.columns:
        print('EC column does not exist!, return the original dataframe')
        return df

    # Create result dataframe
    result_df = df.copy()
    
    # Get EC dictionary
    ec_dict = get_ec_dict()
    
    # Define target columns
    ec_columns = ['EC_DE', 'EC_AN', 'EC_CC', 'EC_CA']
    
    # Create mask for valid EC rows
    mask_EC = ~result_df['EC'].isin(['not_found', '-'])

    # Process valid EC entries
    for i, row in result_df[mask_EC].iterrows():
        ec_nums = row['EC'].split(',')
        for column_name in ec_columns:
            result_df.at[i, column_name] = lookup_and_join_for_EC(ec_nums,ec_dict, column_name)

    # Set default value for invalid entries
    result_df.loc[~mask_EC, ec_columns] = '-'

    # Handle property columns
    for column_name in ec_columns:
        prop_column = f'EC_{column_name}_prop'
        if prop_column in result_df.columns:
            result_df[prop_column] = result_df['EC_prop']
            
    # Fill NA values only for EC columns
    for col in ec_columns:
        result_df[col] = result_df[col].fillna('-')
        result_df[col] = result_df[col].replace('', '-')
            
    print("Add EC columns to df successfully!")
    return result_df

def add_pathway_name_to_df(df: pd.DataFrame, kppe_id:bool = False) -> pd.DataFrame:
    def query_kegg(id_str, pathway_dict, kppe_id=False):
        id_list = id_str.split(',')
        if id_list[0] == 'not_found':
            return 'not_found'
        pathway_list = []
        for id in id_list:
            if id in pathway_dict:
                if kppe_id:
                    pathway_list.append(f'{id}:{pathway_dict[id]}')
                else:
                    pathway_list.append(pathway_dict[id])
        # remove duplicates
        pathway_list = list(dict.fromkeys(pathway_list))
        if len(pathway_list) == 0:
            return '-'
        
        # join the list into a string
        pathway_list = '|'.join(pathway_list)
        return pathway_list
    
    # check if the column 'KEGG_Pathway' exists
    if 'KEGG_Pathway' not in df.columns:
        print('KEGG_Pathway column does not exist!, return the original dataframe')
        return df
    
    #! fill the missing pathway names if necessary
    # df['KEGG_Pathway'] = df['KEGG_Pathway'].fillna('not_found')

    pathway_dict = get_pathway_dict()
    df.loc[:, 'KEGG_Pathway_name'] = df['KEGG_Pathway'].apply(lambda x: query_kegg(x, pathway_dict, kppe_id))
    if 'KEGG_Pathway_prop' in df.columns:
        df.loc[:, 'KEGG_Pathway_name_prop'] = df['KEGG_Pathway_prop']    
    print("Add KEGG_Pathway_name to df successfully!")
    return df


def query_kegg_items(id_str: str, id_to_name_dict: dict, split_char: str = ',', id_split_char: str = ':') -> str:
    """
    Convert KEGG IDs to their corresponding names
    
    Args:
        id_str: String containing KEGG IDs separated by split_char
        id_to_name_dict: Dictionary mapping IDs to names
        split_char: Separator character between IDs, defaults to comma
    
    Returns:
        str: String of converted names joined by '|'
    """
    if not id_str or not isinstance(id_str, str):
        return '-'
    
    name_set = set()
    
    id_list = id_str.split(split_char)
    
    for kegg_id in id_list:
        if kegg_id in ('not_found', '-'):
            name_set.add('-')
            continue
            
        try:
            if id_split_char:
                _, id_part = kegg_id.split(':', 1)
            else:
                id_part = kegg_id
            name = id_to_name_dict.get(id_part, '-')
            if name != '-':
                name_set.add(f'{id_part}:{name}')
        except ValueError:
            name_set.add('-')
    
    return next(iter(name_set)) if len(name_set) == 1 else '|'.join(name_set)


def add_ko_name_to_df(df: pd.DataFrame) -> pd.DataFrame:
    # check if the column 'KEGG_ko' exists
    if 'KEGG_ko' not in df.columns:
        print('KEGG_ko column does not exist!, return the original dataframe')
        return df
    
    # read ko.tsv
    script_path = os.path.dirname(os.path.realpath(__file__))
    ko_path = os.path.join(script_path, '../data/ko.tsv')
    if not os.path.exists(ko_path):
        print(f'{ko_path} does not exist!\nTry to download the file from https://rest.kegg.jp/list/ko')
        download_ko_files(os.path.dirname(ko_path))
    ko_dict = {}
    with open(ko_path, 'r') as f:
        for line in f:
            line = line.strip().split('\t')
            ko_dict[line[0]] = line[1]
    
    df.loc[:, 'KEGG_ko_name'] = df['KEGG_ko'].apply(lambda x: query_kegg_items(x, ko_dict))
    if 'KEGG_ko_prop' in df.columns:
        df.loc[:, 'KEGG_ko_name_prop'] = df['KEGG_ko_prop']
    print("Add KEGG_ko_name to df successfully!")
    return df

def add_kegg_module_to_df(df: pd.DataFrame) -> pd.DataFrame:
    # check if the column 'KEGG_ko' exists
    if 'KEGG_Module' not in df.columns:
        print('KEGG_Module column does not exist!, return the original dataframe')
        return df
    
    # read ko.tsv
    script_path = os.path.dirname(os.path.realpath(__file__))
    module_path = os.path.join(script_path, '../data/module.tsv')
    if not os.path.exists(module_path):
        print(f'{module_path} does not exist!\nTry to download the file from https://rest.kegg.jp/list/module')
        download_kegg_module_files(os.path.dirname(module_path))
    module_dict = {}
    with open(module_path, 'r') as f:
        for line in f:
            line = line.strip().split('\t')
            module_dict[line[0]] = line[1]
    
    df.loc[:, 'KEGG_module_name'] = df['KEGG_Module'].apply(lambda x: query_kegg_items(x, module_dict, split_char=',', id_split_char=''))
    if 'KEGG_Module_prop' in df.columns:
        df.loc[:, 'KEGG_module_name_prop'] = df['KEGG_Module_prop']
    print("Add KEGG_module_name to df successfully!")
    return df
    
    
    

# if __name__ == '__main__':
#     df_path = "MetaX/data/example_data/Example_OTF.tsv"
#     df = pd.read_csv(df_path, sep='\t')
#     df = add_pathway_name_to_df(df, kppe_id=True)
#     df = add_ec_name_to_df(df)
#     df = add_ko_name_to_df(df)
#     df = add_kegg_module_to_df(df)
#     df.to_csv("11.tsv", sep='\t', index=False)