import sys,os
wdir = os.path.dirname(__file__)
sys.path.insert(1,wdir)
from create_finnmaps_db import create_edit_session_tables, execute_sql
print("Refreshing Edit Session Tables")
fm_db = os.path.join(os.path.dirname(wdir),"dbs/finnmaps.db")
check_sessions = execute_sql(fm_db,"SELECT * FROM edit_sessions",True)
check_added = execute_sql(fm_db,"SELECT * FROM added_places",True)
print(f"Existing Sessions: {str(check_sessions)}")
print(f"Existing Place Adds: {str(check_added)}")
num_sessions = len(check_sessions)
print(f"Total number of sessions currently tracked: {str(num_sessions)}")
if num_sessions > 500:
    print("Session table has grown too large, refreshing...")
    create_edit_session_tables(fm_db)
    print("refresh done")
