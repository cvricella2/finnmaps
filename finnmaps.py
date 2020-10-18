# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 19:37:30 2020

@author: cvric
"""
from bottle import Bottle,template,request,static_file
import os,sqlite3,json,phonenumbers
from email_validator import validate_email, EmailNotValidError
from phonenumbers.phonenumberutil import NumberParseException
from arcgis.gis import GIS
from arcgis import geometry,features


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

app = Bottle()
wdir = os.path.dirname(__file__)
db = sqlite3.connect("finnmaps.db")
cur = db.cursor()
username = "cvgeospatial"
password = "@phineas16S"
portal_url = "https://cvgeospatial.maps.arcgis.com"
gis = GIS(portal_url,username,password)
finnmaps_hfs = gis.content.get("704707d94dd64cb48045b1b7d96bdf26")
place_layer = finnmaps_hfs.layers[0]

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
        print(sql)
        cur.execute(sql)
        db.commit()
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


if __name__ == '__main__':
    print(wdir)
    app.run(debug=True,reloader=True)
