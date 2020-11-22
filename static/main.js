//TO DO:
// server side python scripts
// add new layer to house finns current location
// Adjust styling of editior
// republish layer on agol, publish user information table sep. So it can't be viewed or edited.


require([
  "esri/views/MapView",
  "esri/Map",
  "esri/layers/FeatureLayer",
  "esri/widgets/Expand",
  "esri/widgets/Legend",
  "esri/widgets/Home",
  "esri/core/watchUtils"
],
  function(MapView,Map,FeatureLayer,Expand,Legend,Home,watchUtils) {

    // Variables in global scope used throughout Application-----------------------
    let addPlace = false;
    let deletePlace = false;
    let highlight;

    const headerTitle = document.getElementById("headerTitle");
    const headerSubTitle = document.getElementById('headerSubTitle');
    const visitInfo = document.getElementById("visitInfo");
    const visitAttachments = document.getElementById("visitAttachments");
    const nextVisitButton = document.getElementById("nextVisit");
    const nextAttachButton = document.getElementById("nextAttach");
    const visitHeader = document.getElementById("visitHeader");
    const placeInfo = document.getElementById("placeInfo");
    const signupWidget = document.getElementById("signupWidget");
    const submitFormBtn = document.getElementById("submitFormBtn");
    const submitForm = document.getElementsByName("submitForm")[0];
    const openForm = document.getElementById("openForm");
    const closeForm = document.getElementById("closeForm");
    const overlay = document.getElementById("overlay");
    const number_field = document.getElementById("phone_number");
    const editForm = document.getElementsByName("editForm")[0];
    const editWidget = document.getElementById("editWidget");
    const editWidgetBtn = document.getElementById("editWidgetBtn");
    //const deleteBtn = document.getElementById("deleteBtn");
    const closeEditWidget = document.getElementById("closeEditWidget");
    const editWidgetExpand = document.createElement("aside");
    const visitDate = document.createElement("span");
    const noImgVid = document.createElement("p");
    const noParagraph = document.createElement("p");
    const rankText = document.createElement("span");

    editWidgetExpand.id = "editWidgetContainer";
    editWidgetExpand.className = "esri-icon-map-pin esri-widget--button";
    editWidgetExpand.setAttribute("title", "Add Places For Finn To Visit");
    noImgVid.className = "sidebarNoInfo";
    noParagraph.className = "sidebarNoInfo";
    visitDate.id = "visitDate";
    rankText.id = "finnRank";
    rankText.innerHTML = "Finn Ranking: ";
    noParagraph.innerHTML = "Finn Didin't Record Any Information " +
                            "Yet About This Visit!";
    noImgVid.innerHTML = "Finn Didin't Take Any Photos or Videos " +
                         "During This Visit!";
    
    // Reset all the forms when the page shows
    window.addEventListener("pageshow", function(){
      let forms = document.getElementsByTagName('form');
      for (form of forms) {form.reset()}
  });

// Define functions------------------------------------------------------------

    /** Clears the sidebar if anywhere different is clicked on the map from
    the last click */
     function clearSideBar() {
       visitAttachments.innerHTML = " ";
       visitInfo.innerHTML = " ";
       nextVisitButton.style.display = "none";
       nextAttachButton.style.display = "none";
       visitHeader.innerHTML = " ";
       visitDate.innerHTML = " ";
       placeInfo.innerHTML = " ";
     };


    /** initializes the sidebar when a Finn place is clicked on the map */
     function updateSidebar(relatedData) {
       visitHeader.style.display = 'flex';
       visitHeader.appendChild(visitDate);
       let relatedDataKeys = Object.keys(relatedData)
       // If related data is empty let the user no by displaying
       // noImgVid and noParagraph elements. This will happen if
       // There are no related features to query when this function is
       // called by queryRelatedFetures().
       // Then return.
       if (relatedDataKeys.length === 0) {
         visitAttachments.append(noImgVid);
         visitInfo.append(noParagraph);
         return
       } else {
         let attachments = relatedData[relatedDataKeys[0]].attachments
         if (!(attachments.length === 0)) {
           visitAttachments.append(attachments[0]);
         } else {
           visitAttachments.append(noImgVid);
         }
       }
       visitInfo.append(relatedData[relatedDataKeys[0]].visit_paragraph);
       nextVisitButton.style.display = "block";
       nextAttachButton.style.display = "block";
       visitDate.innerHTML = relatedData[relatedDataKeys[0]].date_of_visit;
     };


    /** nextVisit() controls how the user clicks through visits associated with each Finn Place.
     * It's triggered when a user clicks on the "nextVisitButton" which is creatd with the
     * updateSidebar() function.
     * @param {object} relatedData - the relatedData object created by queryRelatedFetures()
     */
     function nextVisit(relatedData) {
       // Initialize the various variables needed to render the relevant visit information.
       // the index variables current_idx and next_idx exist to ensure the proper visit information
       // is displayed and that the user doesn't step outside of the index range. If the next_idx
       // is equal to the number of available keys we know that we are at the end of the array and
       // need to go back tot he start.
       let visit_paragraph = visitInfo.children[0]
       let visit_attachment = visitAttachments.children[0]
       let relatedDataKeys = Object.keys(relatedData);
       // current_idx tells nextVisit where in the array of visit info stored in relatedData
       // the index position is currently at (i.e. before we got to the next visit)
       let current_idx = relatedDataKeys.indexOf(`${visit_paragraph.id}`)
       // We know that we want to go to the next index position in the array
       // so increment by one.
       let next_idx = current_idx + 1
       // Then this if ensures that if we are going to be outside the index range
       // on the next visit, go back to the first position (i.e. 0)
       if (relatedDataKeys.length === next_idx) { next_idx = 0 }
       let visit = relatedData[relatedDataKeys[next_idx]]
       visit_paragraph.replaceWith(visit.visit_paragraph);
       visitDate.innerHTML = visit.date_of_visit;
       // One last check, need to make sure we actually have attachments for the current visit.
       // if not then the noImgVid element stores some text to let the user know.
       if(!(visit.attachments.length === 0)) {
          visit_attachment.replaceWith(visit.attachments[0]);
       } else {
         visit_attachment.replaceWith(noImgVid);
       }
     }


     function nextAttach(relatedData) {
       let visit_paragraph = visitInfo.children[0]
       let current_oid = parseInt(visit_paragraph.id);
       let visit_attachment = visitAttachments.children[0]
       let relatedDataKeys = Object.keys(relatedData);
       let current_idx = relatedDataKeys.indexOf(`${visit_paragraph.id}`)
       let attachments = relatedData[current_oid].attachments;
       if(!(attachments.length === 0)){
         let attach_idx = attachments.indexOf(visit_attachment);

         if(attach_idx + 1 === attachments.length) {
              visit_attachment.replaceWith(attachments[0])
         } else {
              visit_attachment.replaceWith(attachments[attach_idx+1])
            };
       }
     }


     function addRankStars (ranking) {
         let breakpoint = 1;
         if (ranking) {
           visitHeader.appendChild(rankText);
           for (x of Array(ranking).keys()) {
             let span = document.createElement("span")
             span.className = "rankStar"
             span.innerHTML = "&#9733"
             visitHeader.appendChild(span)
             if (breakpoint === ranking ) {
               break
             }
             breakpoint++;
           }
         }
     }


     function createSidebar(screenPoint) {
       relatedData = {};
       view.hitTest(screenPoint).then(function(response){
         if(response.results.length === 0) {
           // Remove highlight if anywhere on map is clicked.
           if (highlight) {highlight.remove();}
           headerTitle.innerHTML = "Finn Maps";
           headerSubTitle.innerHTML = "Click any of the points on the map to view details on Finn's many Adventures!";
           visitHeader.style.display = "none";
           return
         }
         let graphic = response.results[0].graphic
         // Highlights feature when clicked, removes highlight if
         // new feature is clicked.
         view.whenLayerView(graphic.layer).then(function(layerView){
           if (highlight) {
             highlight.remove();
          }
         console.log("Highlighting")
         highlight = layerView.highlight(graphic);
         });
         headerTitle.innerHTML = graphic.attributes.name;
         placeInfo.innerHTML = graphic.attributes.comment;
         headerSubTitle.innerHTML = "";
         addRankStars(graphic.attributes.finn_rank);
         return graphic.attributes.OBJECTID
       }).then(function(objectId) {
           // Query the for the related features for the features ids found
           return finnPlaces.queryRelatedFeatures({
             outFields: ["OBJECTID","date_of_visit","ticks_found","num_ticks_found","note","Photos And Files"],
             relationshipId: finnPlaces.relationships[0].id,
             objectIds: objectId
           });
         }).then(function (relatedFeatureSetByObjectId) {
           let relatedFeatureSetKeys = Object.keys(relatedFeatureSetByObjectId);
           if (relatedFeatureSetKeys.length === 0){
             updateSidebar(relatedData);
           } else {
           relatedFeatureSetKeys.forEach(function(objectId) {
             // get the attributes of the FeatureSet
             const relatedFeatureSet = relatedFeatureSetByObjectId[objectId];
             // Map over the feature set to create an object containing visit data for for each
             // visit related to a point clicked on the map. For the first instance of a visit
             // add an element to the DOM containing it.
             relatedFeatureSet.features.map(function (feature) {

               let visit_date = feature.attributes.date_of_visit;
               let date = new Date(visit_date)
               let formatted_date = `${date.getFullYear()}-${date.getMonth()+1}-${date.getDate()}`;
               let oid = feature.attributes.OBJECTID
               let ticks_found = feature.attributes.ticks_found
               let num_ticks_found = feature.attributes.num_ticks_found
               let note = feature.attributes.note

               relatedData[oid] = {date_of_visit:formatted_date,
                                  ticks_found:ticks_found,
                                  num_ticks_found:num_ticks_found,
                                  note:note,
                                  attachments:[]};

               let visit_paragraph = document.createElement("p")
               visit_paragraph.id = feature.attributes.OBJECTID
               visit_paragraph.innerHTML = feature.attributes.note
               relatedData[feature.attributes.OBJECTID].visit_paragraph = visit_paragraph;
             });

             let relatedDataKeys = Object.keys(relatedData);
             // Get the attachments for each related feature
             relatedDataKeys.forEach(function(objectId) {
               visitData.queryAttachments({
                 //apparently ios videos somehow go from mov to quicktime
                 attachmentTypes: ["image/jpeg","video/mp4","video/quicktime"],
                 objectIds:objectId
               }).then(function(attachmentIds){
                 let attach_num = 1;
                 Object.keys(attachmentIds).forEach(function(id){
                   const attachments = attachmentIds[id];
                   attachments.forEach(function(attachment){
                     let contentType = attachment.contentType;
                     if ((contentType === "video/mp4" || contentType === "video/quicktime")){
                       ele_type = "video";
                     }else{
                       ele_type = "img";
                     }
                     let ele = document.createElement(ele_type)
                     if (ele_type === "video"){ele.controls = true}
                     ele.className = "queryImg";
                     ele.id = `visitAttach${attach_num}`;
                     attach_num++
                     ele.src = attachment.url
                     relatedData[id].attachments.push(ele);
                   })
                 })
               })
             })
            setTimeout(function(){updateSidebar(relatedData)},1000);
         })
       }
        }).catch(function(error){
          console.log(error);
        });
       };
  
  /**  All the stuff that should be done after an edit is made 
   * @param msg Alert message for user after edit.
  */
  function editComplete(msg,coord){
    //deletePlace = false;
    addPlace = false;
    if (highlight) {
      highlight.remove();
    }
    let div = document.createElement("div");
    div.className = "eventMsg";
    div.classList.add("elementToFadeInAndOut");
    div.classList.add("esri-component");
    div.classList.add("esri-widget");
    div.innerHTML=`<p> ${msg} </p>`;
    let innerView = document.getElementsByClassName("esri-ui-inner-container")[0];
    innerView.append(div);
    setTimeout(function(){
      innerView.removeChild(div);
      finnPlaces.refresh();
      view.goTo({
        target:coord,
        zoom:view.zoom+2
      })
    }, 2000);
  }

// Set up map and view---------------------------------------------------------
  var map = new Map({
    basemap:"osm"
  });

  var view = new MapView({
    map: map,
    container: "viewDiv",
    center: [-72.991659,40.902234],
    zoom:9
  });

  const root_url = "https://services2.arcgis.com/O48sbyo4drQXsscH/arcgis/rest/" +
                   "services/Finn_Maps_HFS_Public/FeatureServer";
  let finnPlaces = new FeatureLayer({
    url:`${root_url}/0`
  });
  let visitData = new FeatureLayer({
    url:`${root_url}/1`
  });
  let finnLastLocation = new FeatureLayer({
    url:'https://services2.arcgis.com/O48sbyo4drQXsscH/arcgis/rest/services/finn_last_location/FeatureServer/0'
  });

  finnPlaces.outFields = ["*"]

  const legend = new Legend({
    view: view,
    layerInfos: [{
      layer: finnPlaces,
      title: " "
    },
    {layer:finnLastLocation,title:"Finn's Last Reported Location"}]
  });

  const homeWidget = new Home({
    view: view
  });

  const legendExpand = new Expand({
    expandIconClass: "esri-icon-key",
    view: view,
    content: legend,
    mode:"auto",
    expandTooltip:"Open Map Key",
    collapseTooltip:"Close Map Key"
  });

// Add stuff to the map and view
  view.ui.add(editWidgetExpand, "bottom-right");
  view.ui.add(legendExpand, "top-right");
  view.ui.add(homeWidget,"bottom-left");
  map.add(finnPlaces);
  map.add(finnLastLocation);

// All the DOM events are defined below----------------------------------------

// Below are all DOM events for the sidebar
 view.on("click", function (event) {
   if (deletePlace === false){
     console.log(deletePlace);
     clearSideBar()
     createSidebar(event);
   }
 });

 nextVisitButton.addEventListener("click", function(event){
   nextVisit(relatedData);
 });

 nextAttachButton.addEventListener("click", function(event){
   nextAttach(relatedData);
  });

// Below are all DOM events for the sign up form
 number_field.addEventListener("input", function(){
    let filter_value = number_field.value.replace('+1 ', '').match(/\d*/g).join('');
    number_field.value = filter_value.replace(/(\d{0,3})\-?(\d{0,3})\-?(\d{0,4}).*/,'$1-$2-$3')
                                     .replace(/\-+$/, '')
                                     .replace(/(\d{3})\-?(\d{3})\-?(\d{4})/,'+1 $1-$2-$3')
  });

  openForm.addEventListener("click", function(event){
    signupWidget.style.display = "flex";
    overlay.style.display= "block";
  });

  submitFormBtn.addEventListener("click", function(event){
    let name = document.getElementById("name").value
    let email = document.getElementById("email").value
    let phone_number = document.getElementById("phone_number").value
    let data = {'name':name,'email':email,'phone_number':phone_number}
    data = JSON.stringify(data);
    $.ajax({
      type:"POST",
      url: "/signupform",
      data:data,
      contentType:"application/json",
      dataType:"json"
    })
    submitForm.reset();
    signupWidget.style.display = "none";
    overlay.style.display = "none";
  });

  closeForm.addEventListener("click", function(event){
    signupWidget.style.display = "none";
    overlay.style.display = "none";
    submitForm.reset();
  });

// Below is all DOM events for the editing widget
  editWidgetExpand.addEventListener("click",function(){
    editWidget.style.display = "flex";
    overlay.style.display= "block";
    editForm.reset();
  });

  editWidgetBtn.addEventListener("click",function(){
    addPlace = true;
    editWidget.style.display = "none";
    overlay.style.display= "none";
  })

  //deleteBtn.addEventListener("click",function(){
    //deletePlace = true;
    //editWidget.style.display = "none";
    //overlay.style.display= "none";
    //editForm.reset();
  //})

  watchUtils.whenTrue(view, "navigating", function () {
    finnPlaces.refresh();
  });

  view.on("click",function(evt){
    let pt = view.toMap({ x: evt.x, y: evt.y })
    var coord = [pt.longitude,pt.latitude]
    console.log(coord)
    //if (deletePlace === true) {
      //view.hitTest(evt).then(function (response) {
        //let result = response.results;
        //if (result === 0){
          //console.log("Nothing to delete here.")
          //return 
        //}
        //let attributes = response.results[0].graphic.attributes;
        //let oid = attributes.OBJECTID;
        //let placeName = attributes.name;
        //let deleteAttributes = [oid,placeName]
        //return deleteAttributes
      //}).then(function(deleteAttributes){
        //let data = {'oid':deleteAttributes[0]}
        //let msg = `${deleteAttributes[1]} was deleted! 🐶`
        //data = JSON.stringify(data);
        //$.ajax({
          //type:"POST",
          //url: "finnmaps/deleteplace",
          //data:data,
          //contentType:"application/json",
          //complete:editComplete(msg,coord)
        //})
      //}).catch(function(error){
        //console.log(error);
      //})
    //}

    if (addPlace === true) {
      let placeName = document.getElementById("placeName").value
      let placeType = document.getElementById("placeTypeList").value
      let msg = `Added ${placeName} 🐶`;
      let data = {'name':placeName,'type':placeType,'coord':coord}
      data = JSON.stringify(data);
      $.ajax({
        type:"POST",
        url: "/addplace",
        data:data,
        contentType:"application/json",
        dataType:"json",
        complete: editComplete(msg,coord)
      })
    }
  });

  closeEditWidget.addEventListener("click",function(){
    editWidget.style.display = "none";
    overlay.style.display= "none";
    editForm.reset();
  });

});
