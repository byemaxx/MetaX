import pandas as pd
import sqlite3
import os


def get_time():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def download_file(url, save_dir):
    import requests
    file_name = url.split('/')[-1]
    print(f'{get_time()} Start downloading {file_name}...')
    save_path = os.path.join(save_dir, file_name)
    with open(save_path, "wb") as file:
        response = requests.get(url)
        file.write(response.content)
    print(f'{get_time()} {file_name} downloaded!\tSave path: {save_dir+file_name}')
    


def merge_dbcan(file_path):
    import tarfile
    from io import StringIO

    print(f'{get_time()} Start reading files...')

    tar = tarfile.open(file_path, "r:gz")
    dataframes = []

    for member in tar.getmembers():
        # check if the member is a file
        if member.isfile() and member.name.endswith('.txt'):
            # open file
            f = tar.extractfile(member)
            content = f.read().decode('utf-8')
            
            data = StringIO(content)
            df = pd.read_csv(data, sep='\t') 
            dataframes.append(df)
    
    print(f'{get_time()} Start concat files...')
    merged_df = pd.concat(dataframes)
    tar.close()

    new_cols = ['ID','dbcan_EC', 'dbcan_HMMER', 'dbcan_eCAMI', 'dbcan_DIAMOND', 'dbcan_NumOfTools']
    merged_df.columns = new_cols
    merged_df.drop(['dbcan_NumOfTools'], axis=1, inplace=True)
    merged_df['dbcan_HMMER'] = merged_df['dbcan_HMMER'].str.split('(').str[0]

    print(f'{get_time()} dbcan overview: {merged_df.shape}')
    
    return merged_df

def get_new_anno_df(file_path) -> pd.DataFrame:
    df = pd.read_csv(file_path, sep='\t')
    print(f'{get_time()} new annotation: {df.shape}')
    print(f'{get_time()} new annotation columns: {df.columns}, the first column will be used as ID')
    # rename the first column to ID
    df.rename(columns={df.columns[0]: 'ID'}, inplace=True)
    return df

def create_new_database(old_db_path, new_db_path, new_anno_df):
    # open the database of MGYG and link the merged_df to the database
    db_path = old_db_path
    output_path = new_db_path
    new_anno_df = new_anno_df

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # open id2annotation table and merge the new_anno_df by ID
    print(f'{get_time()} open id2annotation table...')
    # select 1000 rows for test
    # id2annotation = pd.read_sql_ID("SELECT * FROM id2annotation LIMIT 1000", conn)
    id2annotation = pd.read_sql_query("SELECT * FROM id2annotation", conn)
    print(f'{get_time()} merge id2annotation table...')
    new_df = pd.merge(id2annotation, new_anno_df, on='ID', how='left')
    new_df = new_df.fillna('-')
    new_df.set_index('ID', inplace=True)

    # save the new dataframe to a new database file
    new_conn = sqlite3.connect(output_path)
    print(f'{get_time()} write new id2annotation table to new database...')
    new_df.to_sql('id2annotation', new_conn, if_exists='replace', index=True)
    # copy the id2taxa table from old database to the new database
    id2taxa = pd.read_sql_query("SELECT * FROM id2taxa", conn)
    id2taxa.set_index('ID', inplace=True)
    print(f'{get_time()} write id2taxa table to new database...')
    id2taxa.to_sql('id2taxa', new_conn, if_exists='replace', index=True)
    # close the connection
    conn.close()
    new_conn.close()
    print(f'{get_time()} Done!')

def check_table_match(old_db_path, new_df):
    conn = sqlite3.connect(old_db_path)
    c = conn.cursor()
    new_df.rename(columns={new_df.columns[0]: 'ID'}, inplace=True)
    check_name = new_df['ID'].tolist()[0]
    # check if the check_name is in the old database
    c.execute("SELECT * FROM id2annotation WHERE ID = ?", (check_name,))
    result = c.fetchone()
    conn.close()
    if result:
        print(f'{get_time()} Matched!\t{check_name} is in the old database!')
        return True
    print(f'{get_time()} The old database does not match the new annotation file!\t{check_name} is not in the old database!')
    return False
    
def get_built_in_df(built_in_db_name) -> pd.DataFrame:
    # get the built-in database
    if built_in_db_name.split(' ')[0] == 'dbCAN':
        if built_in_db_name == 'dbCAN (HUMAN GUT)':
            url = "https://bcb.unl.edu/dbCAN_seq/download/HUMAN%20GUT/dbCAN_overview.tar.gz"
        elif built_in_db_name == 'dbCAN (COW RUMEN)':
            url = "https://bcb.unl.edu/dbCAN_seq/download/COW%20RUMEN/dbCAN_overview.tar.gz"
        elif built_in_db_name == "dbCAN (MARINE)":
            url = "https://bcb.unl.edu/dbCAN_seq/download/MARINE/dbCAN_overview.tar.gz"
        else:
            raise ValueError(f'Invalid built-in database name: {built_in_db_name}')
        # download the file to home directory MetaX
        # build directory if not exist
        home_dir = os.path.expanduser('~')
        save_dir = os.path.join(home_dir, 'MetaX')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        # download the file
        download_file(url, save_dir)
        # extract the file
        file_path = os.path.join(save_dir, 'dbCAN_overview.tar.gz')
        return merge_dbcan(file_path)
    elif built_in_db_name == 'CAZy':
        print(f'{get_time()} CAZy is not supported yet!')
        
        
        



def run_db_update(update_type, tsv_path, old_db_path, new_db_path,  built_in_db_name = None):
    try:
        if update_type == 'built-in':
            new_anno_df = get_built_in_df(built_in_db_name)
        elif update_type == 'custom':
            new_anno_df = get_new_anno_df(tsv_path)
        else:
            raise ValueError(f'Invalid type: {update_type}')
        
        if check_table_match(old_db_path, new_anno_df):
            create_new_database(old_db_path, new_db_path, new_anno_df)
    except Exception as e:
        print(f'{get_time()} Error: {e}')
        print(f'{get_time()} Failed!')
        


if __name__ == '__main__':
    print(f'{get_time()} Start...')
    
    update_type = 'built-in'
    update_type = 'custom'
    tsv_path = "overview.txt"
    old_db_path = "MetaX_HUGG.db"
    new_db_path = "MetaX_HUGG_new.db"
    built_in_db_name = 'dbCAN (HUMAN GUT)'
    
    run_db_update(update_type, tsv_path, old_db_path, new_db_path, built_in_db_name)
    
    
