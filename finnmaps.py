#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 19:37:30 2020

@author: cvric

TO DO:
- Add tick numbers to sidebar heading
- Add empty stars to finn ranking for when it's less than 5 stars
- Try to improve rendering of sidebar so content loads together
- Figure out if possible to install arcgis on python anywhere; if not rewrite editing functions to use rest api instead.
- Add layer on AGOL to store finns last reported location
- Script to notify users who sign up
- Ios script to update finn last reported location layer on AGOL
- Get app working on python anywhere; redirect domain to personal site
"""
from bottle import Bottle,template,request,static_file,response
import os,sqlite3,json,phonenumbers,logging,sys,uuid
from email_validator import validate_email, EmailNotValidError
from phonenumbers.phonenumberutil import NumberParseException
from configparser import ConfigParser
from arcgis  import GIS
from arcgis import geometry,features


wdir = os.path.dirname(__file__)
config_file = os.path.join(wdir,"config.ini")
config = ConfigParser()
config.read(config_file)
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
sh_out = logging.StreamHandler(sys.stdout)
sh_out.setLevel(logging.DEBUG)
sh_out.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
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
    return fl


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
finnmaps_hfl_id = config.get("GIS_VAR","hfl_id")
place_layer = init_gis(agol_user,agol_pw,agol_url,finnmaps_hfl_id)
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
    has_session = check_session(fm_db)
    if has_session:
        return template(os.path.join(wdir,"views/index.tpl"))
    return template(os.path.join(wdir,"views/index_first_visit.tpl"))

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
            return json.dumps({"message": "Application Failed"})
            logger.info("No valid number or email submitted, user not added")
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



if __name__ == '__main__':
    application.run(host="0.0.0.0")