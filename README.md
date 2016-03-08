Do you love seeing live music and want to discover up-and-coming artists? Broadcast quickly searches for concerts based on whatever mood and city you’re in. Enter an artist and city (or let the geolocator automatically determine your city) and Broadcast will ask the Spotify API for related artists, then will asynchronously request each artist’s calendar from the Songkick API to determine if the group has any upcoming events. Multiple searches can subsequently be performed by clicking on artist images. A user can save events they find interesting to their profile and view event venues on an interactive map. Users can also create a playlist based on their saved events. 


![Broadcast Homepage](https://github.com/DoriRunyon/Events-Project/blob/master/static/images/Broadcast_homepage.png)

Broadcast is a web app created by Dori Runyon. 

## Table of Contents
* [Technologies Used](#technologiesused)
* [How to locally run Broadcast](#run)
* [How to use Broadcast](#use)
* [Version 2.0](#next)
* [About the Author](#author)

## <a name="technologiesused">Technologies Used

* Python
* Flask
* PostgreSQL
* SQLAlchemy
* Javascript/jQuery
* AJAX/JSON
* Jinja2
* Bootstrap
* Spotify API
* Songkick API
* Google Maps API

(dependencies are listed in requirements.txt)

## <a name="run">How to locally run Broadcast

Broadcast has not yet been deployed. See below for instructions on how to run the app locally on your machine.

### Run the Broadcast Flask App

  * Set up and activate a python virtualenv, and install all dependencies:
    * `pip install -r requirements.txt`
  * Make sure you have PostgreSQL running. Create a new database in psql named noodledb:
	* `psql`
  	* `CREATE DATABASE noodledb;`
  * Create the tables in your database:
    * `python -i model.py`
    * While in interactive mode, create tables: `db.create_all()`
  * Now, quit interactive mode. Start up the flask server:
    * `python server.py`
  * Go to localhost:5000 to see the web app


## <a name="use">Using Broadcast

### Enter an artist name and your city (or let geolocator determine your location), then click `Submit`
The search results (displayed below) show concerts found for the artist you searched for, and for the 20 related artists, based on Spotify's related artist relationships. When you click 'Submit' the app requests related artists from Spotify, then asynchronously requests calendars for each of those artists from Songkick. The desired city is then searched for within each calendar. Click 'Buy Tickets' to purchase tickets or click 'Save Show' to save the event to your profile. Any of the images below the event results can be clicked to easily run another search. 

![Broadcast Search Results](https://github.com/DoriRunyon/Events-Project/blob/master/static/images/Broadcast_search.png)

### My Saved Shows, Create a Playlist, and See Your Events on an Interactive Map
Your saved concerts will appear under 'My Saved Shows' along with a map showing all of the venues. The music note icons will display concert information when clicked, and if an venue has more than one upcoming concert, the concert occuring soonest will display. You can also click 'Create Playlist Based on Saved Shows' to create a playlist based on the performing artists for your saved concerts. This feature will request three tracks from Spotify for each artist and include them in all in a playlist.

![Broadcast Search Results](https://github.com/DoriRunyon/Events-Project/blob/master/static/images/Broadcast_map.png)

## <a name="next">Version 2.0

Next steps for the app include allowing users to save a playlist to their Spotify account and adding an alert feature (using the Twilio API) such that users will receive a text reminding them about their events.

## <a name="author">Author
Dori Runyon is a software engineer in Oakland, CA. 

Read more about Dori here: https://www.linkedin.com/in/dorirunyon. You can also email her with any questions or suggestions at dorileerunyon@gmail.com.