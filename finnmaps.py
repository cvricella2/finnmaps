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
import os,sqlite3,json,phonenumbers
from email_validator import validate_email, EmailNotValidError
from phonenumbers.phonenumberutil import NumberParseException
from arcgis.gis import GIS
from arcgis import geometry,features
import sys

sys.path.insert(0,'/var/www/html/finnmaps')


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
    except Exception as e:
        print(e)
        return ''


def add_feature(coords,fl,placename,placetype):
    try:
        geom=geometry.Point(coords)
        feature = features.Feature(geometry=geom,
                                   attributes={'name':placename,'type':placetype})
        resp = fl.edit_features(adds=[feature])
        print(resp)
    except Exception as e:
        print(e)


def delete_feature(oid,fl):
    """ Deletes a feature using the arcgis for python api"""
    try:
        resp = fl.edit_features(deletes=[oid])
        print(resp)
    except Exception as e:
        print(e)


def init_gis(username,password,portal_url,hfs_id):
    """Connect to the GIS, get the relevant HFS, return needed feature layer"""
    print("Connecting to GIS portal")
    gis = GIS(portal_url,username,password)
    print("Finished Connecting...Connecting to HFS")
    hfs = gis.content.get(hfs_id)
    fl = hfs.layers[0]
    return fl

def add_user(db_file,sql):
    db = sqlite3.connect(db_file)
    cur = db.cursor()
    cur.execute(sql)
    db.commit()
    db.close()
    print("User Added")

wdir = os.path.dirname(__file__)
place_layer = init_gis("cvgeospatial","@phineas16S","https://cvgeospatial.maps.arcgis.com","704707d94dd64cb48045b1b7d96bdf26")
app = Bottle()

@app.route('/static/<filename:path>')
def send_css(filename):
    return static_file(filename, root=os.path.join(wdir,'static'))

@app.route('/static/<filename:path>')
def send_js(filename):
    return static_file(filename, root=os.path.join(wdir,'static'))

@app.route('/')
def serve_index():
    return template("./views/index.tpl")

@app.route('/signupform',method="POST")
def form_handler():
    jres = request.json
    # Strip out whitespace to help validate submissions
    name,email,number = jres['name'],jres['email'],jres['phone_number']

    valid_email = check_email(email)
    valid_number = check_number(number)

    # to sign up must atleast give a name or email.
    sql = f"insert into user_info values ('{name}','{valid_email}','{valid_number}')"
    if valid_email or valid_number:
        add_user("finnmaps.db",sql)
    else:
        print("Somethings not right, try again")

@app.route('/addplace',method="POST")
def add_place():
    jres = request.json
    coord = jres['coord']
    name = jres['name']
    type = jres['type']
    print(str(coord) + "," + name + "," + type)
    add_feature(coord,place_layer,name,type)

@app.route('/deleteplace',method="POST")
def delete_place():
    jres = request.json
    oid = jres['oid']
    delete_feature(oid,place_layer)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
