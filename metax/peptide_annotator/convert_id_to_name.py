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

def add_ec_name_to_df(df: pd.DataFrame) -> pd.DataFrame:
    def lookup_and_join(ec_nums, column_name):
    # For each EC number, lookup the corresponding value in the given column of df
        values = []
        for ec_num in ec_nums:
            res = ec_dict[ec_num][column_name]
            if res.startswith('Transferred entry:'):
                new_ec_nums = res.split(':')[1].strip('.').replace(' ', '').split('and')
                ec_nums.extend(new_ec_nums)
                # Lookup and join the corresponding values, and store the result in the new column
                res = lookup_and_join(new_ec_nums, column_name)
                values.append(res)
                # Just append the "Transferred entry" text instead of looking up again
                # values.append('Transferred entry: ' + ', '.join(new_ec_nums))
            else:
                values.append(res)
        if all(value == '-' for value in values):
            return '-'
        # Remove duplicates
        values = list(dict.fromkeys(values))
        # remove '-'
        values = [value for value in values if value != '-']
        return ' | '.join(values)

    # check if the column 'EC' exists
    if 'EC' not in df.columns:
        print('EC column does not exist!, return the original dataframe')
        return df

    ec_dict = get_ec_dict()
    # Create a mask for rows where 'EC' is not "not_found"
    mask_EC = ~df['EC'].isin(['not_found', '-'])

    # For each row in df where 'EC' is not "not_found"
    for i, row in df[mask_EC].iterrows():
        # Split the 'EC' value into multiple EC numbers
        ec_nums = row['EC'].split(',')
        # And for each column to be added
        for column_name in ['EC_DE', 'EC_AN', 'EC_CC', 'EC_CA']:
            # Lookup and join the corresponding values, and store the result in the new column
            df.at[i, column_name] = lookup_and_join(ec_nums, column_name)

    # For rows where 'EC' is "not_found", set the new columns' values to "-"
    df.loc[~mask_EC, ['EC_DE', 'EC_AN', 'EC_CC', 'EC_CA']] = '-'

    # Set the new '_prop' columns' values to the values in the 'EC_prop' column
    df['EC_DE_prop'] = df['EC_prop']
    df['EC_AN_prop'] = df['EC_prop']
    df['EC_CC_prop'] = df['EC_prop']
    df['EC_CA_prop'] = df['EC_prop']
    df.fillna('-', inplace=True)
    df.replace('', '-', inplace=True)
    print("Add EC columns to df successfully!")
    return df

def add_pathway_name_to_df(df: pd.DataFrame) -> pd.DataFrame:
    def query_kegg(id_str, pathway_dict):
        id_list = id_str.split(',')
        if id_list[0] == 'not_found':
            return 'not_found'
        pathway_list = []
        for id in id_list:
            if id in pathway_dict:
                pathway_list.append(pathway_dict[id])
        # remove duplicates
        pathway_list = list(set(pathway_list))
        if len(pathway_list) == 0:
            return '-'
        
        # join the list into a string
        pathway_list = '|'.join(pathway_list)
        return pathway_list
    
    # check if the column 'KEGG_Pathway' exists
    if 'KEGG_Pathway' not in df.columns:
        print('KEGG_Pathway column does not exist!, return the original dataframe')
        return df

    pathway_dict = get_pathway_dict()
    df.loc[:, 'KEGG_Pathway_name'] = df['KEGG_Pathway'].apply(lambda x: query_kegg(x, pathway_dict))
    df.loc[:, 'KEGG_Pathway_name_prop'] = df['KEGG_Pathway_prop']    
    print("Add KEGG_Pathway_name to df successfully!")
    return df

def add_ko_name_to_df(df: pd.DataFrame) -> pd.DataFrame:
    def query_ko(id_str, ko_dict):
        id_list = id_str.split(',')
        ko_list = []
        for ko_id in id_list:
            if ko_id in ['not_found', '-']:
                ko_list.append('-')
            else:
                ko_id = ko_id.split(':')[1]
                ko_name = ko_dict.get(ko_id, '-')
                ko_list.append(f'{ko_id}:{ko_name}')
        # join the list into a string
        ko_name_str = '|'.join(ko_list)
        return ko_name_str
        
        
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
    
    df.loc[:, 'KEGG_ko_name'] = df['KEGG_ko'].apply(lambda x: query_ko(x, ko_dict))
    df.loc[:, 'KEGG_ko_name_prop'] = df['KEGG_ko_prop']
    print("Add KEGG_ko_name to df successfully!")
    return df
    
    
    

# if __name__ == '__main__':
#     df_path = "MetaX/data/example_data/Example_OTF.tsv"
#     df = pd.read_csv(df_path, sep='\t')
#     df = add_pathway_name_to_df(df)
#     df = add_ec_name_to_df(df)
#     df = add_ko_name_to_df(df)
#     df.to_csv("11.tsv", sep='\t', index=False)