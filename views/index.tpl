<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Finn Maps</title>
    <link rel="stylesheet"  type="text/css" href="https://js.arcgis.com/4.19/esri/themes/light/main.css"></link>
    <link rel="stylesheet"  type="text/css" href="/static/main.css?version=1.1"></link>
    <link rel="icon" href = "https://cvgeospatial.maps.arcgis.com/sharing/rest/content/items/6e2a077e2ed847d09606edd0094cba23/data">
    <script type="text/javascript" src="https://js.arcgis.com/4.19/"></script>
    <script type="text/javascript">

      let root_url = '{{root_url}}'
      let center = {{center}}
      let zoom = {{zoom}}
      let getPlace = `${decodeURIComponent("{{place_name}}")}`

      if ({{default}}) {
        let windowWidth = window.innerWidth
        if (windowWidth <= 2400) {
            zoom = 9;
        }

        if (windowWidth <= 400) {
            zoom = 7
            center = [-73.091659,40.802234]
        }  
      } 
     </script>
     <script type="text/javascript" src="/static/main.js?version=1.2"></script>
     <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
  </head>
  <body>
    <div id="flexContainer">
      <div id="sidebar">
        <div id="sidebarHeader" class="sidebarItem">
          <h2 id ="headerTitle" class="headerItem"> Finn Maps </h2>
          <img id = headerImg src ="https://cvgeospatial.maps.arcgis.com/sharing/rest/content/items/ed64d835a83942d98765dd2c02f1e40a/data" class="headerItem queryImg">
          <p id="headerSubTitle" class="headerItem"> Click any of the points on the map to view details on Finn's many adventures! </p>
        </div>
        <div id = "sidebarContent" class="sidebarItem">
          <p id="placeInfo" class="contentItem"></p>
          <aside id="visitHeader" class="contentItem"></aside>
          <div id="visitInfo" class = "contentItem"></div>
          <aside id="visitControl" class = "contentControl contentItem">
            <a href="#" id="prevVisit" class = "sidebarButton sidebarBtnLeft">&laquo; Previous Visit</a>
            <a href="#" id="nextVisit" class = "sidebarButton sidebarBtnRight">Next Visit &raquo;</a>
          </aside>
          <div id= "visitAttachments" class = "contentItem"></div>
          <aside id="imgControl" class = "contentControl contentItem">
            <a href="#" id="prevAttach" class = "sidebarButton sidebarBtnLeft">&laquo; Previous</a>
            <a href="#" id="nextAttach" class = "sidebarButton sidebarBtnRight">Next &raquo;</a>
          </aside>
        </div>
        <div id="sidebarFooter" class = "sidebarItem">
          <p>Want to stay up to date with Finn? <a id="openForm" href="#">Click here</a></p>
        </div>
      </div>
      <div id="viewDiv"></div>
      <div id="overlay"></div>
    </div>
    <form name = "submitForm" method="post" action="/">
      <div class ="formContainer" id ="signupWidget">
        <a href="#" class = "closeButton" id="closeForm">&times</a>
        <h3> Recieve Updates Regarding Finn Maps? </h3>
        <label for="name" class="formLabel">Name</label>
        <input type="text" placeholder = "Enter Full Name" name="name" class="formField" id="name">

        <label for="email" class="formLabel">Email</label>
        <input type="text" placeholder = "Enter Email Address" name="email" class="formField" id="email">

        <label for="phone_number" class="formLabel">Phone Number</label>
        <input type="text" placeholder = "Enter Phone Number" name="phone_number" class="formField" id="phone_number">

        <div class="finnMapBtn" id="submitFormBtn">Submit</div>
        <p class="widgetInfo" id= "signupWidgetInfo">
          Your information will be stored on a secure server and never shared with anyone.
          if you opt for notifications you will recieve text messages and/or emails when Finn is going to
          visit somewhere and when any major changes happen to Finn Maps. Your name is not required unless you would like
          to recieve a personalized notification (e.g. Hi Karen!). If this ever changes you will be notified and given the option to opt out.
        </p>
        <p class="widgetFooter" id="signupWidgetFooter"> All The Best  <img class = "smolFinnImg" src = "https://cvgeospatial.maps.arcgis.com/sharing/rest/content/items/6e2a077e2ed847d09606edd0094cba23/data"></p>
      </div>
    </form>
    <form name = "editForm" method="post" action="/">
      <div class = "formContainer" id ="editWidget">
        <a href="#" class = "closeButton" id="closeEditWidget">&times</a>
        <h3 id = "addPlaceHeader"> Suggest a Place for Finn to Visit! </h3>
        <label for="placename" class="formLabel">Place Name</label>
        <input type="text" placeholder = "Enter Name of The Place" name="placename" class="formField" id="placeName">
        <label for="placeTypeList" class="formLabel">Place Type</label>
        <input type="text" readonly="readonly" placeholder = "Click to Select a Place Type" name="placetype" class="formField" id="placeTypeInput">
        <div class = "dropdown">
          <div id="placeTypeDropdown" class="dropdownContent"></div>
        </div>
        <div class="finnMapBtn" id="editWidgetBtn">Add Place</div>
        <div class="finnMapBtn" id="deleteBtn">Delete Place</div>
        <p class="widgetInfo" id="editWidgetInfo">
          Fill out the above fields, then hit "<b>Add Place</b>". After submission you can click anywhere
          on the map to add the location of the place you think Finn should visit. The map will automatically update,
          if you don't see your place right away don't worry, it can sometimes take a moment and you may need to
          zoom in and out to see the change. If you need to delete a place, click "<b>Delete Place</b>" to delete it; you can only
          delete places you've added in your current session.
        </p>
        <p class="widgetFooter" id="editWidgetFooter"> Thanks for The Suggestion! <img class = "smolFinnImg" src = "https://cvgeospatial.maps.arcgis.com/sharing/rest/content/items/6e2a077e2ed847d09606edd0094cba23/data"> </p>
      </div>
    </form>
     % if not have_session:
    <div class="splashContainer" id="welcomeSplash">
      <h2>Welcome to Finn Maps</h2>
      <div class="splashBody">
        <p>Finn's a dog on a mission...to sniff as many things as possible
        <br>
        <br>
        Enjoy viewing his adventures and feel free to suggest new places for him to visit! 
        If at anytime you need help, click the help button in the top right corner
        <br>
        <br>
        Thanks for visiting!
        </p>
      </div>
      <div class="finnMapBtn" id="splashBtn">Got It!</div>
    </div>
    <script type="text/javascript">
      overlay.style.display="block";
      const splashBtn = document.getElementById("splashBtn");
      const welcomeSplash = document.getElementById("welcomeSplash");
      splashBtn.addEventListener("click",function(){
          overlay.style.display="none";
          welcomeSplash.style.display="none";
      });
     </script>
     % end
  </body>
  </html>
