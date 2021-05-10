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
  "esri/core/watchUtils",
  "esri/widgets/Search"
],
  function(MapView,Map,FeatureLayer,Expand,Legend,Home,watchUtils,Search) {

    // Variables in global scope used throughout Application-----------------------

    function createAlert(msg,bgColor,fontColor,parent,destroyOld=true,addCloseBtn=true,closeBtnColor="red"){
      
      if (destroyOld){
        let oldAlerts = document.getElementsByClassName("alertContainer");
        for (let alert of oldAlerts){
          alert.remove();
        }
      }

      const alertContainer = document.createElement("aside");
      const parentContainer = document.getElementById(parent);
  
      alertContainer.className = "alertContainer";
      alertContainer.style.backgroundColor = bgColor;
      
      if (addCloseBtn){
          const closeBtn = document.createElement("span");
          closeBtn.className = "alertCloseBtn"
          closeBtn.innerHTML = "&times";
          console.log(closeBtnColor);
          closeBtn.style.color = closeBtnColor;
          alertContainer.appendChild(closeBtn);
          closeBtn.addEventListener("click", function () {
          alertContainer.style.display = "none";
       })
      }

      const alertMsg = document.createElement("p");
      alertMsg.innerHTML = msg;
      alertMsg.style.color = fontColor;
      alertContainer.appendChild(alertMsg);

      parentContainer.appendChild(alertContainer);
      alertContainer.style.display ="flex";

      return alertContainer

    }  

    let addPlace = false;
    let deletePlace = false;
    let visited = true;
    let highlight;
    const imgDir = "./static/img"
    const placeTypeConfig = {"Village Park":1,
                             "Town Park":2,
                             "County Park":3,
                             "State Park":4,
                             "National Park":5,
                             "Preserve":6,
                             "Eatery":7,
                             "Store":8,
                             "Monument":9,
                             "Residence":10,
                             "Other":11}
    let placeTypeVal = "";

    const headerTitle = document.getElementById("headerTitle");
    const headerSubTitle = document.getElementById('headerSubTitle');
    const headerImg = document.getElementById('headerImg');
    const visitInfo = document.getElementById("visitInfo");
    const visitAttachments = document.getElementById("visitAttachments");
    const nextVisitButton = document.getElementById("nextVisit");
    const prevVisitButton = document.getElementById("prevVisit");
    const nextAttachButton = document.getElementById("nextAttach");
    const prevAttachButton = document.getElementById("prevAttach");
    const visitHeader = document.getElementById("visitHeader");
    const placeInfo = document.getElementById("placeInfo");
    const signupWidget = document.getElementById("signupWidget");
    const submitFormBtn = document.getElementById("submitFormBtn");
    const submitForm = document.getElementsByName("submitForm")[0];
    const openForm = document.getElementById("openForm");
    const closeForm = document.getElementById("closeForm");
    const overlay = document.getElementById("overlay");
    const numberField = document.getElementById("phone_number");
    const editForm = document.getElementsByName("editForm")[0];
    const editWidget = document.getElementById("editWidget");
    const editWidgetBtn = document.getElementById("editWidgetBtn");
    const deleteBtn = document.getElementById("deleteBtn");
    const closeEditWidget = document.getElementById("closeEditWidget");
    const editWidgetExpand = document.createElement("aside");
    const visitDate = document.createElement("span");
    const noImgVid = document.createElement("p");
    const noParagraph = document.createElement("p");
    const notVisited = document.createElement("p");
    const rankText = document.createElement("span");
    const placeTypeDropdown = document.getElementById("placeTypeDropdown")
    const placeTypeInput = document.getElementById("placeTypeInput")
    const helpWidget = document.createElement("div")


    editWidgetExpand.id = "editWidgetContainer";
    editWidgetExpand.className = "esri-icon-map-pin esri-widget--button";
    editWidgetExpand.setAttribute("title", "Open Place Edit Widget");
    noImgVid.className = "sidebarNoInfo";
    noParagraph.className = "sidebarNoInfo";
    notVisited.className = "sidebarNoInfo"
    visitDate.id = "visitDate";
    rankText.id = "finnRank";
    rankText.innerHTML = "Finn Ranking: ";
    noParagraph.innerHTML = "Finn Didin't Record Any Information " +
                            "Yet About This Visit!";
    noImgVid.innerHTML = "Finn Didin't Take Any Photos or Videos " +
                         "During This Visit!";
    notVisited.innerHTML = "<b>Finn Hasn't Visited Here Yet!</b>"
    helpWidget.className = "esri-widget esri-widget--panel";
    helpWidget.innerHTML = `<h2 style="text-align:center;"> Finn Maps How To </h2>
                            <h3 style="text-align:center; text-decoration:underline;">Map Operations</h3>
                            <h4 style="text-align:center;">Navigating</h4>
                            <ul>
                              <li>On desktop left click, hold and drag to move the map. On mobile the same can be accomplished by touching, holding and draging</li>
                              <li>You can zoom in and out using your mouse wheel, by double clicking on the map, or using "+" "-" keys.
                              On mobile, zooming can be accomplished by pinching the fingers together to zoom in, or apart to zoom out.
                              Zooming can also be done via the zoom widget located in the top left corner ("+" and "-" buttons) on both
                              mobile and desktop. </li>
                              <li>Click the home widget, in the bottom left corner to zoom the map out to where it started</li>
                            </ul>
                            <h4 style="text-align:center;">Searching</h4>
                            <ul>
                              <li>You can search for a specific address, a Finn Place or your current location using the search widget. The search widget is located in the bottom left,
                              click the magnifying glass to open it. Once clicked you'll see an option to "Use current location" which will zoom to where you're currently located. Type in any address to zoom there
                              related suggestions will pop-up, you can also change what is searched first by clicking the small arrow to the left of the search bar.</li>
                            </ul>
                            <h4 style = "text-align:center;">Viewing Finn Places</h4>
                            <ul>
                              <li>Click on one of the green and white icons (Finn Places) to view information about what Finn has done there. This will update the sidebar</li>
                              <li>The sidebar has information about the place itself (at the top), Finn's visit (center), and a footer with a clickable link that brings up a form (bottom)</li>
                              <li>The visit information contains all the data that we record every time finn visits a place, if there are multiple visits you can scroll through them by
                                  clicking "Previous" or "Next" visit buttons above the photo or video. Visits sometimes also have multiple photos or videos to view, you can scroll through these in the same fashion,
                                  by clicking the "Previous" or "Next" buttons found below the photo or video. 
                              <li>Lastly clicking on the link to stay up to date with finn will bring up a form to fill out. Please read the disclaimer before you submit it.</li>
                           </ul>
                           <h3 style="text-align:center; text-decoration:underline;">Adding and Deleting Places</h3>
                           <p style="text-align:center;">Click the pin in the lower right corner</p>
                           <h4 style="text-align:center;">Adding Places</h4>
                            <ol>
                              <li>Fill out the form fields, both are required</li>
                              <li>Click "Add Place" this will close the widget and alert you that editing is enabled</li>
                              <li>You can now click anywhere on the map to add the place, you will be alerted when it's complete</li>
                           </ol>
                           <h4 style="text-align:center;">Deleting Places</h4>
                             <ol>
                               <li>Click "Delete Place" this will close the widget and alert you that editing is enabled</li>
                               <li>
                               To delete a place, you just need to click it; however you can only delete places you yourself have added.
                               If you're are private browsing, this will be limited to your current session.
                               </li>
                            </ol>
                           `;
    
    // Reset all the forms when the page shows
    window.addEventListener("pageshow", function(){
      let forms = document.getElementsByTagName('form');
      for (form of forms) {form.reset()}
  });

// Define functions------------------------------------------------------------

    /** Clears the sidebar if anywhere different is clicked on the map from
    the last click */
     function clearSidebar() {
       visitAttachments.innerHTML = " ";
       visitInfo.innerHTML = " ";
       nextVisitButton.style.display = "none";
       prevVisitButton.style.display = "none";
       nextAttachButton.style.display = "none";
       prevAttachButton.style.display = "none";
       visitHeader.innerHTML = " ";
       visitDate.innerHTML = " ";
       placeInfo.innerHTML = " ";
     };


    /** initializes the sidebar when a Finn place is clicked on the map */
     function updateSidebar(relatedData) {
       visitHeader.style.display = 'flex';
       visitHeader.appendChild(visitDate);
       let relatedDataKeys = Object.keys(relatedData)
       // If related data is empty let the user know by displaying
       // noImgVid and noParagraph elements. This will happen if
       // There are no related features to query when this function is
       // called by queryRelatedFetures().
       // Then return.
       if (!(visited)) {
         visitInfo.append(notVisited);
         return
       }
       
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
       visitInfo.append(relatedData[relatedDataKeys[0]].tick_info);
       visitInfo.append(relatedData[relatedDataKeys[0]].visit_paragraph);
       nextVisitButton.style.display = "inline-flex";
       prevVisitButton.style.display = "inline-flex";
       nextAttachButton.style.display = "inline-flex";
       prevAttachButton.style.display = "inline-flex";
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
       // need to go back to the start.
       let visit_paragraph = visitInfo.children[1]
       let tick_info = visitInfo.children[0]
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
       tick_info.replaceWith(visit.tick_info);
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


     function prevVisit(relatedData) {
      // Initialize the various variables needed to render the relevant visit information.
      // the index variables current_idx and next_idx exist to ensure the proper visit information
      // is displayed and that the user doesn't step outside of the index range. If the next_idx
      // is equal to the number of available keys we know that we are at the end of the array and
      // need to go back to the start.
      let visit_paragraph = visitInfo.children[1]
      let tick_info = visitInfo.children[0]
      let visit_attachment = visitAttachments.children[0]
      let relatedDataKeys = Object.keys(relatedData);
      // current_idx tells nextVisit where in the array of visit info stored in relatedData
      // the index position is currently at (i.e. before we got to the next visit)
      let current_idx = relatedDataKeys.indexOf(`${visit_paragraph.id}`)
      // We know that we want to go to the next index position in the array
      // so increment by one.
      let next_idx = current_idx - 1
      // Then this if ensures that if we are going to be outside the index range
      // on the next visit, go back to the first position (i.e. 0)
      if (current_idx === 0) { next_idx = 0 }
      let visit = relatedData[relatedDataKeys[next_idx]]
      tick_info.replaceWith(visit.tick_info);
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

     function prevAttach(relatedData) {
      let visit_paragraph = visitInfo.children[0]
      let current_oid = parseInt(visit_paragraph.id);
      let visit_attachment = visitAttachments.children[0]
      let attachments = relatedData[current_oid].attachments;
      if(!(attachments.length === 0)){
        let attach_idx = attachments.indexOf(visit_attachment);

        if(attach_idx === 0) {
             visit_attachment.replaceWith(attachments[attachments.length - 1])
        } else {
             visit_attachment.replaceWith(attachments[attach_idx-1])
           };
      }
    }


     function addRankStars (ranking) {
      if (ranking) {
        visitHeader.appendChild(rankText);
        for (x of Array(ranking).keys()) {
          let span = document.createElement("span")
          span.className = "rankStar"
          span.innerHTML = "&#9733"
          visitHeader.appendChild(span)
        }
        if (ranking < 5){
          let noFill = 5 - ranking
          for (x of Array(noFill).keys()) {
            let span = document.createElement("span");
            span.className = "rankStarNoFill"
            span.innerHTML = "&#9733"
            visitHeader.appendChild(span)
          }
        }
      }
  }


     function createSidebar(screenPoint,oid) {
       relatedData = {};
       visited = true;
       console.log(oid)
       if (!(oid)) {oid = null}
       view.hitTest(screenPoint).then(function(response){

        if(response.results.length === 0 || response.results[0].graphic.layer.Id === 1) {

          console.log("No hit")

          if (highlight) {highlight.remove();}

          let searchRes = response.screenPoint.result;

          if (searchRes){
          let attributes = searchRes.feature.attributes;
          headerTitle.innerHTML = attributes.name;
          placeInfo.innerHTML = attributes.comment;
          headerSubTitle.style.display = "none";
          headerImg.style.display = "none";
          addRankStars(attributes.finn_rank);

          if (attributes.visited != 1) {
              visited = false;
            }

            return attributes.OBJECTID
          }

          if (oid) {
            console.log("hit here")
            return oid
          }

          headerTitle.innerHTML = "Finn Maps";
          headerSubTitle.style.display = "block";
          headerSubTitle.innerHTML = "Click any of the points on the map to view details on Finn's many adventures!";
          headerImg.style.display = "block";
          visitHeader.style.display = "none";
          searchWidget.clear();
          return
        } 
         let graphic = response.results[0].graphic
         // Highlights feature when clicked, removes highlight if
         // new feature is clicked.
         view.whenLayerView(graphic.layer).then(function(layerView){

          if (highlight) {
             searchWidget.clear();
             highlight.remove();
          }

          highlight = layerView.highlight(graphic);
         });

         headerTitle.innerHTML = graphic.attributes.name;
         placeInfo.innerHTML = graphic.attributes.comment;
         headerSubTitle.style.display = "none";
         headerImg.style.display = "none";
         addRankStars(graphic.attributes.finn_rank);

         if (graphic.attributes.visited != 1) {
           visited = false;
         }

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

               let visit_paragraph = document.createElement("p");
               let tick_info = document.createElement("span");
               visit_paragraph.id = oid
               visit_paragraph.innerHTML = `${note}`
               tick_info.id = oid
               tick_info.innerHTML = `<b>Ticks Found:</b> ${num_ticks_found}`
               relatedData[oid].visit_paragraph = visit_paragraph;
               relatedData[oid].tick_info = tick_info;
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
            setTimeout(function(){updateSidebar(relatedData)},1500);
         })
       }
        }).catch(function(error){
          console.log(error);
        });
       };
  
  // /**  All the stuff that should be done after an edit is made 
  //  * @param msg Alert message for user after edit.
  // */
  // function editComplete(msg,coord){
  //   //deletePlace = false;
  //   addPlace = false;
  //   viewDiv.style.cursor = "default";
  //   if (highlight) {
  //     highlight.remove();
  //   }
  //   let div = document.createElement("div");
  //   div.className = "eventMsg";
  //   div.classList.add("elementToFadeInAndOut");
  //   div.classList.add("esri-component");
  //   div.classList.add("esri-widget");
  //   div.innerHTML=`<p> ${msg} </p>`;
  //   let innerView = document.getElementsByClassName("esri-ui-inner-container")[0];
  //   innerView.append(div);
  //   setTimeout(function(){
  //     innerView.removeChild(div);
  //     finnPlaces.refresh();
  //     view.goTo({
  //       target:coord,
  //       zoom:view.zoom+2
  //     })
  //   }, 2000);
  // }
  

    /**  All the stuff that should be done after an edit is made 
   * @param msg Alert message for user after edit.
  */
 function editComplete(msg,coord){
  addPlace = false;
  deletePlace = false;
  placeTypeVal = "";
  viewDiv.style.cursor = "default";
  if (highlight) {
    highlight.remove();
  }
  setTimeout(function(){
    finnPlaces.refresh();
    createAlert(msg,"white","black","viewDiv")
    view.goTo({
      target:coord,
      zoom:view.zoom+1
    })
  }, 1000);
}

function editError(msg){
  addPlace = false;
  deletePlace = false;
  viewDiv.style.cursor = "default"
  createAlert(msg,"red","white","viewDiv",true,true,"white")
}


// Set up map and view---------------------------------------------------------
  var map = new Map({
    basemap:"osm"
  });
  
 
  var view = new MapView({
    map: map,
    container: "viewDiv",
    center: center,
    zoom:zoom
  });

  const root_url = "https://services2.arcgis.com/O48sbyo4drQXsscH/arcgis/rest/" +
                   "services/Finn_Maps_HFS_Public/FeatureServer";
  let finnPlaces = new FeatureLayer({
    url:`${root_url}/0`,
    Id:0
  });
  let visitData = new FeatureLayer({
    url:`${root_url}/1`
  });
  let finnLastLocation = new FeatureLayer({
    url:'https://services2.arcgis.com/O48sbyo4drQXsscH/arcgis/rest/services/finn_last_location/FeatureServer/0',
    Id:1
  });

  finnPlaces.outFields = ["*"]

  const legend = new Legend({
    view: view,
    layerInfos: [{
      layer: finnPlaces,
      title: " "
    },
    {layer:finnLastLocation,title:""}]
  });

  const homeWidget = new Home({
    view: view
  });

  const searchWidget = new Search({
    view: view,
    allPlaceholder: "Search...",
    sources:[
      {
        layer:finnPlaces,
        searchFields:['name'],
        exactMatch:false,
        name: "Finn Places",
        outFields: ["*"],
        placeholder: "Example: Camp Hero State Park",
        zoomScale:9,

      }
    ]
  });

  const legendExpand = new Expand({
    expandIconClass: "esri-icon-key",
    view: view,
    content: legend,
    group:"top-right",
    expandTooltip:"Open Map Key",
    collapseTooltip:"Close Map Key"
  });

  const helpExpand = new Expand({
    expandIconClass: "esri-icon-description",
    view:view,
    group:"top-right",
    content:helpWidget,
    expandTooltip:"Open Help",
    collapseTooltip:"Close Help"
  })

// Add stuff to the map and view
  view.ui.add(legendExpand, "top-right");
  view.ui.move("zoom","top-left");
  view.ui.add(homeWidget,"top-left");
  view.ui.add(searchWidget,"bottom-left");
  view.ui.add(helpExpand, "top-right");
  view.ui.add(editWidgetExpand, "top-right");

  map.add(finnPlaces);
  map.add(finnLastLocation);

// All the DOM events are defined below----------------------------------------

view.when(function(){
  // Used for when get parameters are suplied with URL, if a place name to search is supplied
  // This will initiate a search on the finn places feature layer
  if (getPlace !== "null") {
      searchWidget.activeSourceIndex = 1;
      searchWidget.search(getPlace).then(function(){
        searchWidget.activeSourceIndex = -1; // set back to all sources
    })
  }
});

// Below are all DOM events for the sidebar
 nextVisitButton.addEventListener("click", function(event){
   nextVisit(relatedData);
 });

 prevVisitButton.addEventListener("click", function(event){
  prevVisit(relatedData);
});

 nextAttachButton.addEventListener("click", function(event){
   nextAttach(relatedData);
  });

  prevAttachButton.addEventListener("click", function(event){
    prevAttach(relatedData);
   });
 

// Below are all DOM events for the sign up form
 numberField.addEventListener("input", function(){
    let filterValue = numberField.value.replace('+1 ', '').match(/\d*/g).join('');
    numberField.value = filterValue.replace(/(\d{0,3})\-?(\d{0,3})\-?(\d{0,4}).*/,'$1-$2-$3')
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
      success: function(){createAlert(`Thanks for signing up ${name}, Finn will be in touch!`,"white","black","viewDiv")},
      error: function(){createAlert("Your submission failed, please try again!","red","white","viewDiv",true,true,"white")}
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
    createAlert("Place ready to add, click anywhere on the map!","white","black","viewDiv")
    viewDiv.style.cursor = "crosshair";
    editWidget.style.display = "none";
    overlay.style.display= "none";
  })

  deleteBtn.addEventListener("click",function(){
    deletePlace = true;
    createAlert("Delete enabled, click place you want to delete","white","black","viewDiv")
    viewDiv.style.cursor = "crosshair";
    editWidget.style.display = "none";
    overlay.style.display= "none";
  })

  watchUtils.whenTrue(view, "navigating", function () {
    finnPlaces.refresh();
  });

  searchWidget.on("select-result",function(event){
    clearSidebar()
    createSidebar(event)
  })

  view.on("click",function(evt){
    let pt = view.toMap({ x: evt.x, y: evt.y })
    var coord = [pt.longitude,pt.latitude]

    if (deletePlace === false && addPlace === false){
      clearSidebar()
      createSidebar(evt);
      return
    }

    if (deletePlace === true) {
      view.hitTest(evt).then(function (response) {
        let result = response.results;
        if (result === 0){
          return 
        }
        let attributes = response.results[0].graphic.attributes;
        let oid = attributes.OBJECTID;
        let placeName = attributes.name;
        let deleteAttributes = [oid,placeName]
        return deleteAttributes
      }).then(function(deleteAttributes){
        let data = {'oid':deleteAttributes[0]}
        let msg = `${deleteAttributes[1]} was deleted! <img class = "smolFinnImg" src = "https://cvgeospatial.maps.arcgis.com/sharing/rest/content/items/6e2a077e2ed847d09606edd0094cba23/data">`
        let errMsg = `Delete place failed, check deleting criteria and try again`
        data = JSON.stringify(data);
        $.ajax({
          type:"POST",
          url: "/deleteplace",
          data:data,
          contentType:"application/json",
          success:function(){editComplete(msg,coord)},
          error:function(){editError(errMsg)}
        })
      }).catch(function(error){
        console.log(error);
      })
    }

    if (addPlace === true) {
      let placeName = document.getElementById("placeName").value
      let msg = `Added ${placeName} <img class = "smolFinnImg" src = "https://cvgeospatial.maps.arcgis.com/sharing/rest/content/items/6e2a077e2ed847d09606edd0094cba23/data">`;
      let errMsg = "Add place failed, must enter both a valid name and place type"
      let data = {'name':placeName,'type':placeTypeVal,'coord':coord}
      data = JSON.stringify(data);
      $.ajax({
        type:"POST",
        url: "/addplace",
        data:data,
        contentType:"application/json",
        dataType:"json",
        success: function(){editComplete(msg,coord)},
        error:function(){editError(errMsg)}
      })
    }
  });

  closeEditWidget.addEventListener("click",function(){
    editWidget.style.display = "none";
    overlay.style.display= "none";
    editForm.reset();
  });

  placeTypeInput.addEventListener("click",function(){
    placeTypeDropdown.style.display = "block"
  });


  for (let key in placeTypeConfig) {
    let span = document.createElement('span');
    let img = document.createElement('img');
    span.className = "placeTypeOption"
    img.src = `${imgDir}/${key.toLowerCase().replace(" ","_")}.png`
    img.style.verticalAlign = "middle"
    span.innerHTML =  key + " "
    placeTypeDropdown.appendChild(span);
    span.appendChild(img);
    span.addEventListener("click",function(){
      placeTypeVal = `${placeTypeConfig[key]}`;
      placeTypeDropdown.style.display="none";
      placeTypeInput.value = key;

    });
  };


});
