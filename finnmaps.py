#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 19:37:30 2020

@author: cvric

"""
from bottle import Bottle,template,request,static_file,response
import os,sqlite3,json,phonenumbers,logging,sys,uuid,requests,smtplib,ssl,re
from email_validator import validate_email, EmailNotValidError
from phonenumbers.phonenumberutil import NumberParseException
from configparser import ConfigParser
from arcgis  import GIS
from arcgis import geometry,features
from email.mime.text import MIMEText
import time


wdir = os.path.dirname(__file__)
config_file = os.path.join(wdir,"config.ini")
config = ConfigParser()
config.read(config_file)
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
sh_out = logging.StreamHandler(sys.stderr)
sh_out.setLevel(logging.INFO)
sh_out.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(sh_out)
logger.info("APP RUNNING")


class SubmitError(Exception):
    """ Raised when a user makes an invalid submission to a form """
    pass

def check_email(email):
    """ Checks an email to see if it's 'valid' it does not test if this email is actually
        reachable, just if the address would be valid"""
    try:
        logger.info("Checking email...")
        valid = validate_email(email)
        return valid.email
    except EmailNotValidError as e:
        logger.warning(e)


def notify_users(sender_email,password,db_file,msg_body,url="https://finnmaps.org"):

    context = ssl.create_default_context()

    carriers = ["txt.att.net", "tmomail.net", "vzwpix.com", "messaging.sprintpcs.com", "vmobl.com", 
    "mst5.tracfone.com", "mymetropcs.com", "sms.myboostmobile.com", "sms.cricketwireless.net", 
    "text.republicwireless.com", "msg.fi.google.com"]

    users = execute_sql(db_file,"SELECT * FROM user_info",True)

    with smtplib.SMTP_SSL("smtp.gmail.com",465,context=context) as server:
        server.login(sender_email,password)

        for row in users:
            name = row[0]
            email = row[1]
            number = row[2]
            full_msg = f"Hi {name},\n{msg_body}\nCheck it out at: {url}"
            msg = MIMEText(full_msg)
            if number != 'None':
                for carrier in carriers:
                    format_num = "".join(re.findall(r'\b\d+\b',number))
                    print(f"Sending Message to {row[0]} at {format_num} for {carrier}") 
                    server.sendmail(sender_email,f"{format_num}@{carrier}",msg=msg.as_string())
            else:
                msg['Subject'] = 'Finn Maps Update'
                server.sendmail(sender_email,email,msg=msg.as_string())


def get_token(username,password,expiration=60):

    """ Generate a token for AGOL """

    data = {
        'f': 'json',
        'username': username,
        'password': password,
        'referer' : 'https://www.arcgis.com',
        'expiration': expiration
        }

    url  = 'https://www.arcgis.com/sharing/rest/generateToken'
    jres = requests.post(url, data=data, verify = True).json()
    return jres['token']



def check_number(number,region=None):
    """ Checks if a phone number is actually a phone number, it does not test if it's reachable"""
    try:
        logger.info("Checking phone number...")
        pn_obj = phonenumbers.parse(number,region)
        pn_format = phonenumbers.PhoneNumberFormat.NATIONAL
        nice_num = phonenumbers.format_number(pn_obj,pn_format)
        return nice_num
    except NumberParseException as e:
        logger.warning(e)


def add_feature(coords,fl,placename,placetype):
    """ Add feature using the arcgis for python api"""
    geom=geometry.Point(coords)
    feature = features.Feature(geometry=geom,
                               attributes={'name':placename,'type':placetype})
    resp = fl.edit_features(adds=[feature])
    logger.info(resp)
    return resp['addResults'][0]['objectId']


def delete_feature(oid,fl):
    """ Deletes a feature using the arcgis for python api"""
    logger.info(f"Deleting feature with OBJECTID: {str(oid)}")
    resp = fl.edit_features(deletes=[oid])
    logger.info(resp)
   

def init_gis(username,password,portal_url,hfl_id):
    """Connect to the GIS, get the relevant HFS, return needed feature layer"""
    logger.info("Connecting to GIS portal")
    gis = GIS(portal_url,username,password)
    logger.info("Finished Connecting...Getting the HFL")
    hfl = gis.content.get(hfl_id)
    fl = hfl.layers[0]
    visit_table = hfl.tables[0]
    return fl,visit_table


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


def check_session(db_file):
    """ Gets the current session used by the client if it exists, if not a new session key is created and added
        to the finn maps database.
    """
    key = request.get_cookie("sessionid")
    result = execute_sql(db_file,f"SELECT key FROM edit_sessions WHERE key='{key}'",return_result=True)
    if result:
        logger.info(f"Returning User With Key: {key}")
        return True
        
    key = str(uuid.uuid4())
    execute_sql(db_file,f"INSERT INTO edit_sessions VALUES ('{key}')")
    response.set_cookie("sessionid",key,max_age=31540000)
    logger.info(f"Adding new session with key: {key}")
    return False
    


def user_owns_place(db_file,key,oid):
    """ Checks if a user (key) owns/added the given feature (oid) """
    check_sql = f"SELECT oid FROM added_places WHERE key = '{key}' and oid = {oid}"
    result = execute_sql(db_file,check_sql,True)
    if result:
        return True
    return False


logger.info(f"Working Directory is {wdir}")
agol_user = config.get("GIS_VAR","agol_user")
agol_pw = config.get("GIS_VAR","agol_pw")
agol_url = config.get("GIS_VAR","agol_url")
notify_email = config.get("EMAIL_VAR","notify_email")
email_pw = config.get("EMAIL_VAR","email_pw")
finnmaps_hfl_id = config.get("GIS_VAR","hfl_id")
gis_content = init_gis(agol_user,agol_pw,agol_url,finnmaps_hfl_id)
place_layer = gis_content[0]
visit_table = gis_content[1]
fm_db = os.path.join(wdir,"dbs/finnmaps.db")

application = Bottle()

@application.route('/static/main.css')
def send_css():
    logger.info("CSS Sent")
    return static_file('main.css', root=os.path.join(wdir,'static'))

@application.route('/static/main.js')
def send_js():
    logger.info("JS Sent")
    return static_file('main.js', root=os.path.join(wdir,'static'))

@application.route('/static/img/<filename>')
def send_img(filename):
    return static_file(filename, root=os.path.join(wdir,'static/img'))

@application.route('/')
def send_index():
    logger.info("Index Sent")
    info = {"center":[-72.991659,40.902234],"zoom":10,"place_name":'null',"default":'true'}
    if request.query:
        info = {"center":request.query.center,"zoom":request.query.zoom,
                "place_name":requests.utils.quote(request.query.place_name),"default":'false'}
    else:
        logger.info("No Query")
    info["have_session"] = check_session(fm_db)
    return template(os.path.join(wdir,"views/index.tpl"),info)

@application.route('/signupform',method="POST")
def form_handler():
    try:
        logger.info("User submitted sign up form, getting their info...")
        jres = request.json
        name,email,number = jres['name'],jres['email'],jres['phone_number']
        valid_email = check_email(email)
        valid_number = check_number(number)
        response.set_header('Content-Type','application/json')

        # to sign up must atleast give a name or email.
        if valid_email or valid_number:
            sql = f"insert into user_info values ('{name}','{valid_email}','{valid_number}')"
            logger.info("Adding user...")
            execute_sql(fm_db,sql)
            logger.info("User added")
            return json.dumps({"message": "Application Submitted"})
        else:
            response.status = 400
            logger.info("No valid number or email submitted, user not added")
            return json.dumps({"message": "Application Failed"})
    except Exception:
        logger.error("",exc_info=True)


@application.route('/addplace',method="POST")
def add_place():
    jres = request.json
    coord = jres['coord']
    name = jres['name']
    place_type = jres['type']
    response.set_header('Content-Type','application/json')
    if place_type and name:
        logger.info(str(coord) + "," + name + "," + place_type)
        oid = add_feature(coord,place_layer,name,place_type)
        key = request.get_cookie("sessionid")
        execute_sql(fm_db,f"INSERT INTO added_places VALUES ({oid},'{key}')")
        return json.dumps({"message": "Add Successful"})
    else:
        response.status = 400
        return json.dumps({"message": "Add Failed, Must Enter Both a Valid Place Type and Name"})


@application.route('/deleteplace',method="POST")
def delete_place():
    ip = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR')
    admin_ip = ['192.168.1.13']
    logger.info(f"Client's IP is {ip}")
    jres = request.json
    oid = jres['oid']
    key = request.get_cookie("sessionid")
    logger.info( f"User owns place? {str(user_owns_place(fm_db,key,oid))}")
    logger.info( f"User is admin? {str(ip in admin_ip)}")
    response.set_header('Content-Type','application/json')
    if user_owns_place(fm_db,key,oid) or ip in admin_ip:
        delete_feature(oid,place_layer)
        return json.dumps({'message':'Delete Successful'})
    else:
        response.status = 400
        return json.dumps({'message':'Delete Failed'})


@application.route('/1a6bd1eb-9c11-49f3-bd1c-4c1cd1801085', method="POST")
def agol_webhook():
    logger.info("Web Hook Route Hit")
    try:
        token = get_token(agol_user,agol_pw,expiration=5)
        jres = request.json
        logger.info(jres)
        change_url = requests.utils.unquote(jres[0]['changesUrl'])
        logger.info(change_url)
        change_params = {
            'f': 'json',
            'token': token,
            'outSR': 4326,
            'includeRelated':"true"
            }
        change_jres = requests.post(url=change_url,data=change_params,verify=True).json()
        status_url = change_jres['statusUrl'] + f"?token={token}&f=json"
        logger.info(status_url)
        result_url = ''
        while result_url == '':
            status = requests.get(url=status_url).json()
            result_url = status['resultUrl']
            logger.info("awaiting results url")
            time.sleep(5)

        result_url = result_url + f"?token={token}&f=json"
        result = requests.get(url=result_url).json()

        # Unpack result from the webhook payload:
        # we know we want the visit table, it has id == 1
        # it seems the the ids are one to one with the their position in the list (ids start at 0 for layers and tables in ArcGIS)
        # So we get the edits, get the visit table, it's features, and the visit id for what was added
        visit_id = result['edits'][1]['features']['adds'][0]['attributes']['visit_id']

        # Next we query the places layer and visit table and find the layer finn visit based on the visit_id
        # we get a count of the number of visits in the table, if its one or less we know it's a new place and notifyt he users
        query_resp = place_layer.query(where=f"GlobalId = '{visit_id}' ",out_fields='name,ESRIGNSS_LONGITUDE,ESRIGNSS_LATITUDE')
        num_visits = visit_table.query(where=f"visit_id = '{visit_id}'",return_count_only=True)
        if num_visits <= 1:
            feature = query_resp.features[0]
            # Remove any trailing or leading spaces and convert any inbetween spaces to a "+"
            # The browser will interpret this as a space 
            visit_place = feature.attributes['name'].strip().replace(" ","+")
            coords = [feature.attributes['ESRIGNSS_LONGITUDE'],feature.attributes['ESRIGNSS_LATITUDE']]
            coords = str(coords).replace(" ","") # get rid of space in list, will mess up the get request
            query_url = f"https://finnmaps.org/?center={coords}&zoom=15&place_name={visit_place}"
            # put the spaces back in the for the user message
            user_msg = f"Finn explored {visit_place.replace('+',' ')} for the first time"

            # Lastly we query the user table and notify everyone on the list that finn just visited the named place
            # add any additional info
            notify_users(notify_email,email_pw,fm_db,user_msg,query_url)
        else:
            logger.info("Finn already visited this place, not notifying users")

    except:
        logger.error("",exc_info=True)

if __name__ == '__main__':
    application.run(port=80)
    #application.run(host="0.0.0.0")