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


def generate_token(username,password,expiration=60):
        data = {'username':username,
            'password': password,
            'referer' : 'https://www.arcgis.com',
            'f': 'json',
            'expiration':expiration}
        url  = 'https://www.arcgis.com/sharing/rest/generateToken'
        jres = requests.post(url, data=data, verify=True).json()
        return jres['token']

def query_layer(feature,layer,token,where_clause,out_fields,return_geom):

    url = ("https://services1.arcgis.com/0cYxNkh7FJosf1xi/ArcGIS/rest"
           "/services/{}/FeatureServer/{}/query").format(feature,layer)

    data = {'f':'json',
            'token':token,
            'where':where_clause,
            'outFields':out_fields,
            'returnGeometry':return_geom}

    jres = requests.post(url, data = data, verify = True).json()

    return jres

def edit_layer(feature,layer,token,adds="",updates="", deletes="",
               gdb_version="",return_edit="false",rollback="true",use_global_id="false",
               attachments="",session_id="",use_prev_edit="false",datum_trans=""):

    """ Operation adds, updates, and deletes features of the target
        feature layer or table. For more info on any of this methods args
        see here: https://developers.arcgis.com/rest/services-reference/
        apply-edits-feature-service-layer-.htm
        Args:
            feature: the feature to apply edits
            layer: layer of the feature to apply edits
            adds(optional): Features to add to the layer of interest.
              format should be feature object format that the REST API
              returns.
            updates(optional): Features to update in the layer of interest.
              format should be the feature object format that the REST API
              returns.
            deletes(optional): Object IDs of features/records to be deleted.
            gdb_version(optional): The version to apply edits. Used for
              versioned data.
            return_edit(optional): If "true" response will return time edits
              were supplied in the editMoment key. Default is "false"
            rollback(optional): Specifies whether the edits should be applied
              if the operation fails. If "false" the server will apply any
              successful edits, even if some failed; the REST API supplies
              "true" by default.
            use_global_id(optional): If "true" features and attachments are
              identified by global id instead of object id or attachtment
              id. REST API uses "false" by default.
            attachments(optional): Add, update or delete attachments.
            session_id(optional): Used if working on versioned data. GUID
              value that is supplied at the beginning of an edit session,
              and used throughout.
            use_prev_edit(optional): Used to apply the edits with the same
              edit moment as the previous set of edits. Allows an editor
              to apply a block edits partially, do another task, and then
              complete the block of edits. Set to "true" to use.
            datum_trans(optional): Supplies a datum transformation while
              projecting geometries in the results when "outSR" is
              different than the layer's spatial reference.
              https://developers.arcgis.com/rest/services-reference/
              project.htm
          Returns:
            The result of the edits. Results are grouped by type of edit
            each group contains an array of edit result objects.
            Example:
                "addResults" : [
                  {
                    "objectId" : 3700,
                    "globalId" : "{93BADD75-B2B7-497a-99F0-6E89B09C9C8E}",
                    "success" : true
                  },
                  {
                    "objectId" : -1,
                    "globalId" : "{9B395A2F-2A97-443f-8A32-0EDCC031226B}",
                    "success" : false,
                    "error" : {
                      "code" : 100,
                      "description" : "Provided Geometry does not have Z Value(s).", }
                  }
                  ]
             """


    url = ("https://services1.arcgis.com/0cYxNkh7FJosf1xi/ArcGIS/rest"
               "/services/{}/FeatureServer/{}/applyEdits").format(feature,layer)

    data = {
            'f':'json',
            'token':token,
            'adds':adds,
            'updates':updates,
            'deletes':deletes,
            'gdbVersion':gdb_version,
            'returnEditMoment':return_edit,
            'rollbackOnFailure':rollback,
            'useGlobalIds':use_global_id,
            'attachments':attachments,
            'sessionID':session_id,
            'usePreviousEditMoment':use_prev_edit,
            'datumTransformation':datum_trans
            }

    jres = requests.post(url,data = data,verify = True).json()

    return jres

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
        adds = {{"geom":{"x":coords[0],"y":[coords[1]}},
        ]}
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
