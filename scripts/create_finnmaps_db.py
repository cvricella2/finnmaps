import sqlite3,os
from sqlite3 import Error

def create_db(db_file):
    """
    Creates a sqlite database, the connection is closed after creation.
    Returns early if a database already exists at the given location.

    Args:
        db_file (str): A full path (unless already in the target directory) 
          to create the database e.g. r"c:\mydb.db"
    """   
    db_exists = os.path.exists(db_file)
    if db_exists:
        raise Exception("Database already exists in specified directory.")
    else:
        conn = sqlite3.connect(db_file)
        if conn:conn.close()

def check_table_exists(db_file,table_name):
    """
    Checks if a table exists in the specified database file

    Args:
        db_file (str): A full path (unless already in the target directory) 
          to the database file e.g. r"c:\mydb.db"
        table_name (str): Name of table to check in the database.

    Returns:
        [bool]: A bool indicated if the table exists
    """    
    conn = sqlite3.connect(db_file)
    table_exists = False
    sql = f""" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table_name}'"""
    cursor = conn.cursor()
    cursor.execute(sql)
    if cursor.fetchone()[0]==1:table_exists = True
    conn.close()
    return table_exists

def execute_sql(db_file,sql):
    """
    Connects to the database file and executes a query, the query is commited 
    and the connection closed.

    Args:
        db_file ([type]): [description]
        sql ([type]): [description]
    """    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    wdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    os.chdir(wdir)
    db_file="finnmaps.db"
    table_name="user_info"
    print(f"Creating {db_file} at {wdir}")
    # No data type for datetimes in sqlite,
    # instead use integer to store as unix time.
    create_table_sql = f""" CREATE TABLE IF NOT EXISTS {table_name} (
                                        name text,
                                        email text,
                                        phone_number text
                                    ); """
    create_db(db_file)
    print(f"Creating {table_name} in {db_file}")
    execute_sql(db_file,create_table_sql)
    if not check_table_exists(db_file,table_name):
        raise Error(f"{table_name} was not created")
