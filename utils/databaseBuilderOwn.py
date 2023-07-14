import pandas as pd
import sqlite3


def check_anno_table(df):

    # check if the table at least has 2 columns
    if df.shape[1] < 2:
        print('The annotation table has less than 2 columns')
        return False
    # Check if the first column is unique
    if not df.iloc[:, 0].is_unique:
        print('The first column of the annotation table is not unique')
        return False
    else:
        return True

def check_taxa_table(df):

    # check if the table is 2 columns
    if df.shape[1] > 2:
        print('The taxa table should only have 2 columns')
        return False
    elif df.shape[1] < 2:
        print('The taxa only has 1 column')
        return False
    # Check if the first column is unique
    if not df.iloc[:, 0].is_unique:
        print('The first column of the taxa table is not unique')
        return False
    # check the format of the taxa "d__Bacteria;p__Firmicutes;c__Bacilli;o__Erysipelotrichales;f__Erysipelotrichaceae;g__Bulleidia;s__Bulleidia moorei"
    taxa = df.iloc[1, 1]
    if not taxa.startswith('d__'):
        print('The taxa does not start with d__')
        return False
    # check if the taxa separated by ;
    if ';' not in taxa:
        print('The taxa is not separated by ;')
        return False
    else:
        return True
    
def read_annotation_table(anno_path):
    df = pd.read_csv(anno_path, sep='\t')
    if check_anno_table(df):
        # rename the first column to ID
        df.columns = ['ID'] + list(df.columns[1:])
        df.set_index('ID', inplace=True)
        df.fillna('-', inplace=True)
        return df
    else:
        raise ValueError('The annotation table is not in the correct format')

def check_complete_taxa(df):
    def complete_taxa(taxa, all_categories):
        taxa_splitted = taxa.split(';')
        while len(taxa_splitted) < len(all_categories):
            taxa_splitted.append(all_categories[len(taxa_splitted)])
        return ';'.join(taxa_splitted)
    
    all_categories = ["d__", "p__", "c__", "o__", "f__", "g__", "s__"]
    # Remove trailing semicolon if it exists
    df.iloc[:, 1] = df.iloc[:, 1].apply(lambda x: x.rstrip(';') if x.endswith(';') else x)
    # Only apply complete_taxa function if the number of semicolons is less than 6
    df.iloc[:, 1] = df.iloc[:, 1].apply(lambda x: complete_taxa(x, all_categories) if x.count(';') < len(all_categories) - 1 else x)
    # rename the first column to ID, the second column to taxa
    return df

def read_taxa_table(taxa_path):
    df = pd.read_csv(taxa_path, sep='\t')
    if check_taxa_table(df):
        df = check_complete_taxa(df)
        df.columns = ['ID', 'taxa']
        df.set_index('ID', inplace=True)
        return df
    else:
        raise ValueError('The taxa table is not in the correct format')


def build_db(anno_path, taxa_path, db_path):
    anno_df = read_annotation_table(anno_path)
    taxa_df = read_taxa_table(taxa_path)
    print('Start building the database...')
    conn = sqlite3.connect(db_path)
    # save the annotation table to the database as id2annotation
    anno_df.to_sql('id2annotation', conn, if_exists='replace')
    taxa_df.to_sql('id2taxa', conn, if_exists='replace')
    conn.close()
    print('Database built successfully')
    
if __name__ == '__main__':
    import time
    start = time.time()
    anno_path = "C:/Users/Qing/Desktop/111/MGYG000000001_eggNOG.tsv"
    taxa_path = "C:/Users/Qing/Desktop/111/test_taxa.tsv"
    db_path = "C:/Users/Qing/Desktop/111/test_db.db"
    build_db(anno_path, taxa_path, db_path)
    print(time.time() - start)