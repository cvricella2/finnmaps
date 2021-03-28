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


def execute_sql(db_file,sql,return_result=False):
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
    if return_result:
        result = cursor.fetchall()
        conn.close()
        return result
    conn.close()
    

if __name__ == "__main__":
    wdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    db_file= os.path.join(wdir,"dbs/finnmaps.db")
    print(wdir)

    user_sql = """ 
                CREATE TABLE IF NOT EXISTS user_info (
                name text,
                email text,
                phone_number text);

               """

    session_sql = """
                  CREATE TABLE IF NOT EXISTS edit_sessions (
                  key text unique primary key);
                  
                  """

    added_sql = """
                CREATE TABLE IF NOT EXISTS added_places (
                oid integer, key text);
                
                """

    tables = {"user_info":user_sql,"edit_sessions":session_sql,"added_places":added_sql}
    
    if not os.path.exists(db_file):
        print("Database file does not exist, creating it")
        create_db(db_file)

    else: print("Database already exists, file not created")
 
    for table,sql in tables.items():
        # No data type for datetimes in sqlite,
        # instead use integer to store as unix time.
        if not check_table_exists(db_file,table):
            print(f"{table} does not exist, creating it using: {sql}")
            execute_sql(db_file,sql)
        else: print(f"{table} already exists, not created")

