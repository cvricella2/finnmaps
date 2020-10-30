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
