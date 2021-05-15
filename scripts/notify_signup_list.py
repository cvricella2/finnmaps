import smtplib, ssl
import os,sqlite3,re
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText


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
    

wdir = os.path.dirname(__file__)
fm_db = os.path.join(os.path.dirname(wdir),"dbs/finnmaps.db")
port = 465
password = "@phineas2021S"

context = ssl.create_default_context()

carriers = ["txt.att.net", "tmomail.net", "vtext.com", "messaging.sprintpcs.com", "vmobl.com", 
"mst5.tracfone.com", "mymetropcs.com", "sms.myboostmobile.com", "sms.cricketwireless.net", 
"text.republicwireless.com", "msg.fi.google.com"]

users = execute_sql(fm_db,"SELECT * FROM user_info",True)

msg = MIMEText("""https://finnmaps.org has recieved an update!\n\nThere's now new art, helpful alerts, a new help\info widget, and improved adding & deleting tools""")

with smtplib.SMTP_SSL("smtp.gmail.com",port,context=context) as server:
    server.login("finnmapsdotorg@gmail.com",password)

    for row in users:
        name = row[0]
        email = row[1]
        number = row[2]
        if number != 'None':
            for carrier in carriers:
                format_num = "".join(re.findall(r'\b\d+\b',number))
                print(f"Sending Message to {row[0]} at {format_num} for {carrier}") 
                server.sendmail("finnmapsdotorg@gmail.com",f"{format_num}@{carrier}",msg=msg.as_string())
        else:
            msg['Subject'] = 'Finn Maps Update'
            server.sendmail("finnmapsdotorg@gmail.com",email,msg=msg.as_string())
