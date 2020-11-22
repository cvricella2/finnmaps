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
from bottle import Bottle,template,request,static_file
import os,sqlite3,json,phonenumbers,logging,sys
from email_validator import validate_email, EmailNotValidError
from phonenumbers.phonenumberutil import NumberParseException
from configparser import ConfigParser
from arcgis  import GIS
from arcgis import geometry,features

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)
logger.addHandler(sh)
logger.info("APP RUNNING")

#sys.path.remove('/var/www/finnmaps/fmvenv/lib64/python3.6/site-packages/IPython/extensions')
logger.info(sys.path)

class SubmitError(Exception):
    """ Raised when a user makes an invalid submission to a form """
    pass

def check_email(email):
    try:
        valid = validate_email(email)
        return valid.email
    except Exception as e:
        print(e)
        return ''


def check_number(number,region=None):
    try:
        pn_obj = phonenumbers.parse(number,region)
        pn_format = phonenumbers.PhoneNumberFormat.NATIONAL
        nice_num = phonenumbers.format_number(pn_obj,pn_format)
        return nice_num
    except:
        raise SubmitError("Failed to add number")


def add_feature(coords,fl,placename,placetype):
    try:
        geom=geometry.Point(coords)
        feature = features.Feature(geometry=geom,
                                   attributes={'name':placename,'type':placetype})
        resp = fl.edit_features(adds=[feature])
        print(resp)
    except:
        raise SubmitError("Failed to Add Feature")


def delete_feature(oid,fl):
    """ Deletes a feature using the arcgis for python api"""
    try:
        logger.info("Deleting {} feature".format(str(oid)))
        resp = fl.edit_features(deletes=[oid])
        logger.info(resp)
    except Exception as e:
        logger.error("",exc_info=True)


def init_gis(username,password,portal_url,hfl_id):
    """Connect to the GIS, get the relevant HFS, return needed feature layer"""
    logger.info("Connecting to GIS portal")
    gis = GIS(portal_url,username,password)
    logger.info("Finished Connecting...Connecting to HFL")
    hfl = gis.content.get(hfl_id)
    fl = hfl.layers[0]
    return fl

def add_user(db_file,sql):
    db = sqlite3.connect(db_file)
    cur = db.cursor()
    cur.execute(sql)
    db.commit()
    db.close()
    print("User Added")


wdir = os.path.dirname(__file__)
logger.info(f"Working Directory is {wdir}")
logger.info(f"Working Directory is {wdir}")
config_file = os.path.join(wdir,"config.ini")
config = ConfigParser()
config.read(config_file)
agol_user = config.get("GIS_VAR","agol_user")
agol_pw = config.get("GIS_VAR","agol_pw")
agol_url = config.get("GIS_VAR","agol_url")
finnmaps_hfl_id = config.get("GIS_VAR","hfl_id")
place_layer = init_gis(agol_user,agol_pw,agol_url,finnmaps_hfl_id)
application = Bottle()

@application.route('/static/main.css')
def send_css():
    return static_file('main.css', root=os.path.join(wdir,'static'))

@application.route('/static/main.js')
def send_js():
    return static_file('main.js', root=os.path.join(wdir,'static'))

@application.route('/')
def send_index():
    return template(os.path.join(wdir,"views/index.tpl"))

@application.route('/signupform',method="POST")
def form_handler():
    fm_db = os.path.join(wdir,"finnmaps.db")
    jres = request.json
    # Strip out whitespace to help validate submissions
    name,email,number = jres['name'],jres['email'],jres['phone_number']

    valid_email = check_email(email)
    valid_number = check_number(number)

    # to sign up must atleast give a name or email.
    sql = f"insert into user_info values ('{name}','{valid_email}','{valid_number}')"
    if valid_email or valid_number:
        add_user(fm_db,sql)
    else:
        print("Somethings not right, try again")

@application.route('/addplace',method="POST")
def add_place():
    jres = request.json
    coord = jres['coord']
    name = jres['name']
    type = jres['type']
    print(str(coord) + "," + name + "," + type)
    add_feature(coord,place_layer,name,type)

@application.route('/deleteplace',method="POST")
def delete_place():
    jres = request.json
    oid = jres['oid']
    logger.info("Delete Route Hit")
    delete_feature(oid,place_layer)




if __name__ == '__main__':
    application.run()
