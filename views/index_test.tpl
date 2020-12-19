<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Finn Maps</title>
    <link rel="stylesheet"  type="text/css" href="https://js.arcgis.com/4.17/esri/themes/light/main.css"></link>
    <link rel="stylesheet"  type="text/css" href="/static/main.css?version=1.0"></link>
    <script type="text/javascript" src="https://js.arcgis.com/4.17/"></script>
    <script type="text/javascript" src="/static/main.js?version=1.0"></script>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
  </head>
  <body>
    <div id="flexContainer">
      <div id="sidebar">
        <div id="sidebarHeader" class="sidebarItem">
          <h2 id ="headerTitle" class="headerItem"> Finn Maps </h2>
          <p id="headerSubTitle" class="headerItem"> Click any of the points on the map to view details on Finn's many Adventures! </p>
        </div>
        <div id = "sidebarContent">
          <p id="placeInfo" class="sidebarItem"></p>
          <aside id="visitHeader" class="sidebarItem"></aside>
          <div id= "visitAttachments" class = "sidebarItem"></div>
          <a href="#" id="nextAttach" class = "sidebarButton sidebarItem"> <strong>Next</strong> &raquo;</a>
          <div id="visitInfo" class = "sidebarItem"></div>
          <a href="#" id="nextVisit" class = "sidebarButton sidebarItem"> <strong>See Next Visit</strong> &raquo;</a>
        </div>
        <div id="sidebarFooter" class = "sidebarItem">
          <p><strong> Want to stay up to date with Finn? <a id="openForm" href="#">Click Here</a></strong></p>
        </div>
      </div>
      <div id="viewDiv"></div>
      <div id="overlay"></div>
    </div>
    <form name = "submitForm" method="post" action="/">
      <div class ="formContainer" id ="signupWidget">
        <a href="#" class = "closeButton" id="closeForm">x</a>
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
        <p class="widgetFooter" id="signupWidgetFooter"> All The Best 🐶 </p>
      </div>
    </form>
    <form name = "editForm" method="post" action="/">
      <div class = "formContainer" id ="editWidget">
        <a href="#" class = "closeButton" id="closeEditWidget">x</a>
        <h3 id = "addPlaceHeader"> Suggest a Place for Finn to Visit! </h3>
        <label for="placename" class="formLabel">Place Name</label>
        <input type="text" placeholder = "Enter Name of The Place" name="placename" class="formField" id="placeName">
        <label for="placeTypeList" class="formLabel">Place Type</label>
        <input type="text" readonly placeholder = "Click to Select a Place Type" name="placetype" class="formField" id="placeTypeInput">
        <div class="finnMapBtn" id="editWidgetBtn">Add Place</div>
        <p class="widgetInfo" id="editWidgetInfo">
          Fill out the above fields, then hit "Add Place". After submission you can click anywhere
          on the map to add the location of the place you think Finn should visit. The map will automatically update,
          if you don't see your place right away don't worry, it can sometimes take a moment and you may need to
          zoom in and out to see the change.
        </p>
        <p class="widgetFooter" id="editWidgetFooter"> Thanks for The Suggestion! 🐶 </p>
      </div>
    </form>
    <div id="placeTypeDropdown" class="dropdownContent"></div>
  </body>
  </html>
