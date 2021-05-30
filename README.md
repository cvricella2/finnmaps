# Finn Maps - My First Full Stack Web Application

[Finn Maps](https://finnmaps.org) is a full stack web application that shows places my dog Finn has been. Simple on the surface but somewhat complex and hacky underneath, I'm proud of this project and happy to share it with the world. 

## Who is Finn?

Finn (full name Phineas Johnson Vricella), also known as Master Finn, Finn Master Flex, Finny Wiggles, Finn Boi, Finny Beans, Dobby and like a 100 other nicknames, is my 9 year old lab mix. I adopted him as a puppy from the [North Shore Animal League](https://www.animalleague.org/) in Long Island, NYS. He's an easy going dog who's favorite thing to do is go around sniffing new places. 

![Pic of Finn](https://github.com/cvricella2/finnmaps/blob/main/images/finn%20couch.jpg)

## What's Finn Maps Made of? 

Finn Maps Stack is:

- Linux (Red hat) running on an [AWS free tier](https://aws.amazon.com/free/?all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all) EC2 Instance
- Apache (also known as HTTPD on red hat)
- Sqlite3 + ArcGIS Online for data storage and hosting
- Python + bottle for the application back end
- Mostly vanilla JS/CSS/HTML on the front end but I do utilize the [ArcGIS API for JavaScript](https://developers.arcgis.com/javascript/latest/) pretty heavily and Jquery to handle HTTP requests. 

In addition to these main components I utilize ArcGIS Collector (Field Maps would work also) to actively update the places Finn has visited and Pythonista to run a python 2 script that updates Finn's last known location on the map via my IPhone (so his last known location is really my phones location when the script was run). To get access to the ArcGIS platform I have an [ArcGIS for personal use license](https://www.esri.com/en-us/arcgis/products/arcgis-for-personal-use/buy) this is a $100 a year. [Pythonista](http://omz-software.com/pythonista/) is a one time purchase of $10 and is pretty cool, I think it's well worth that; note this link actually says python 3, but the version I have runs Python 2.   

Below is a very hacky Architecture diagram of Finn Maps

![Arch Diagram](https://github.com/cvricella2/finnmaps/blob/main/images/Finn%20Maps%20Architecture.png)

Here is an ERD, as you can see the database is divided into two with all the mapping data stored on ArcGIS Online and user data stored in SQLITE.

![ERD Diagram](https://github.com/cvricella2/finnmaps/blob/main/images/Finn%20Maps%20ERD.png)

## What Features Does Finn Maps Have?

On first glance, Finn Maps just looks like a simple map viewer, but it does have a couple features that make it a full stack application. The first thing to talk about is feature editing and how I implemented it. 

### Feature Editing

The ArcGIS  API for JavaScript coupled with ArcGIS Online will actually provides editing capabilities out of the box, but they do not work in a way that I was looking for and I also ran into issues with ESRI's mobile applications where they would not recogonize me as a named user and made all my editing anonymous, this in turned messed up the two editing work flows I wanted to implement:

- An admin workflow where an administrator can add, update and edit any data point
- An anonymous work flow where the anon user could only add or delete a data point that they themselves owned. This led me to creating my own customish data editing functions using the [ArcGIS REST API](https://developers.arcgis.com/rest/) and SQLITE.

The admin workflow is very simple, the admin does not do edits through the application but utilizing either an ESRI mobile app (Collector or Field Maps) or through ArcGIS Online. The anon workflow is where the work begins, below I'll explain it in more detail:

#### Anonymous Editing Workflow

The anon workflow is based around two tables I created in the SQLITE database, one stores what I call "Edit Sessions" and it only has one field a "Key" field that is a primary unique key, and an "Added Places" table that has that same key field as a foreign key and another field called "oid" which is the Object ID of a feature that was added during an edit session; this allows for anon editing to take place. Finn Maps knows if you've visited before by getting a cookie I created called "sessionid" if this cookie is in the database I know you're a returning user, if not then a new session id/key is made for you. This has obivious drawbacks, for starters if you're in a private browser the cookie will be gone once you leave or refresh the page in most cases, also if you delete  your cache the cookie will also be lost; That's okay though because the whole purpose is really just to make sure that (1) You can't delete places you did not add and (2) let you delete a place you just added incase you made a typo and I don't think anyone is going to be lying awake at night worried they misspelled something on Finn Maps 3 months ago and wanting to go and change it (and they could always email me if they really wanted to). 

That's the basics of it, but how does a user actually add or delete a place? This is done with a form, a very ugly form but a form that works nonetheless. I have two routes set up on the back end one for adding places and one for deleting places, within the form you fill out the fields and click "Add Place" this will then change the state of the application and it will wait for you click somewhere on the map to add the place, once you do, the add place route will be triggered and I have some python code that will go and make that edit on ArcGIS Online. Delete place works the same way, but you don't need to fill out the form fields, just click "Delete Place".

### Subscribe for Updates From Finnmaps

I know everyone who uses this application is probably dying to know when I update it or when Finn visits a new place so to appease the masses I created a form and underlying database table to allow for a "User" of Finn Maps to be created. I say "User" loosely because really Finn Maps is all anonymous, I don't store your information anywhere with cookies, there are no user accounts, as you read above all your editing is anonymous; as a matter of fact you don't even need to give me your name all I need is an email or a phone number, both work. With that being said I did call this table the "User" table for some reason so the distinction needs to be made. Just like with editing theres a form and associated route on the server, you fill out the form, click submit an HTTP payload is posted to the server and some python code updates the database. Wait though, there is more, I have a webhook set up! ArcGIS Online allows you set up web hooks very easily and bottle let's me set up a simple listener on the server. When the webhook is triggered the listener route is hit and some code parses the payload, if it's the first time finn has visited a place a notification will be sent to all the "Users" letting them know Finn's been to a new place and they need to see it ASAP, also providing a nifty URL with some parameters set that will bring you to that exact place on the map.

## Conclusion and References

That's it folks, I'm done with Finn Maps, I learned a ton making this application and belive it or not I could have not done it alone. Special thanks to my good friends [Nick Muse](https://nickmuse.com/) and [Lawerence Vricella](https://www.anxietycult.com/). Nick was my server senpai during this project, I had never set up my own web server before or had much experience with Linux and he was a huge help in getting that all set up. Larry did all the art work for Finn Maps, check out his site and instagram @anxiety.cult. Also thanks to all the developer communities out there that put together awesome documentation and answer forum questions. 

### References Not Found Via the Hyperlinks Above

- https://pwp.stevecassidy.net/ (This was my bible for Python Web Programming)
- https://bottlepy.org/docs/0.12/
- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/SSL-on-amazon-linux-ami.html#ssl-certificate-alami
- https://www.serverlab.ca/tutorials/linux/administration-linux/troubleshooting-selinux-centos-red-hat/ (Ever had issues with SELinux? Definitely look at this)
- https://www.tecmint.com/disable-selinux-in-centos-rhel-fedora/ (Temp disable SELinux)
- https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/deploying_different_types_of_servers/setting-apache-http-server_deploying-different-types-of-servers
- https://www.rootusers.com/how-to-configure-an-apache-virtual-host/
