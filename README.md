Do you love seeing live music and want to discover up-and-coming artists? Broadcast quickly searches for concerts based on whatever mood and city you’re in. Enter an artist and city (or let the geolocator automatically determine your city) and Broadcast will ask the Spotify API for related artists, then will asynchronously request each artist’s calendar from the Songkick API to determine if the group has any upcoming events. Multiple searches can subsequently be performed by clicking on artist images. A user can save events they find interesting to their profile and view event venues on an interactive map. Users can also create a playlist based on their saved events.

![Broadcast Homepage](https://github.com/DoriRunyon/Events-Project/blob/master/static/images/Broadcast_homepage.png)

Broadcast is a web app created by Dori Runyon. 

## Table of Contents
* [Technologies Used](#technologiesused)
* [How to locally run Broadcast](#run)
* [How to use Broadcast](#use)

## Technologies Used

* Python
* Flask
* PostgresSQL
* SQLAlchemy
* Javascript/jQuery
* AJAX/JSON
* Jinja2
* Bootstrap
* Spotify API
* Songkick API
* Google Maps API

(dependencies are listed in requirements.txt)

## How to locally run Broadcast

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
  * Go to localhost:9000 to see the web app


## Broadcast

### Enter an artist name and your city (or let geolocator determine your location), then click `Submit`
Explain what they are looking at here.

Put a pic here of search results

### Press the `X` button
Explain stuff here.

Put a pic here.

### Press the `X` button
Explain stuff here.

Put a pic here.

## Author
Dori Runyon is a software engineer in Oakland, CA. Read more about the Dori here: https://www.linkedin.com/in/dorirunyon
