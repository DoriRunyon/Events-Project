import spotipy, requests, os

from jinja2 import StrictUndefined
from pprint import pprint

from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Artist, Event, UserEvent
from werkzeug.contrib.cache import SimpleCache


api_key = os.environ['SONGKICK_API_KEY']


spotify = spotipy.Spotify()
cache = SimpleCache()

spotify = spotipy.Spotify()

app = Flask(__name__)
cache = SimpleCache()

app.secret_key = "ABC"

app.jinja_env.undefined = StrictUndefined



@app.route('/')
def login():
    """Login page."""

    return render_template("login.html")

@app.route('/logged-in', methods=["POST"])
def logged_in():
    """Users with an account can login."""

    email = request.form.get("email")
    password = request.form.get("password")


    user = User.query.filter(User.email == email).first()

    if user.password == password:
        user_id = user.user_id
        session['user'] = user_id
        print user_id
        flash(("Hello %s, you are now logged in.") % email)
        return redirect('/dashboard')

    else:
        return "Incorrect password. <a href='/dashboard'>Try again.</a>"

@app.route('/log-out')
def logout():

    del session['user']
    flash("Goodbye, you are now logged out.")
    return redirect('/dashboard')

@app.route('/create-account')
def create_account():
    """Page for creating account."""

    return render_template("create-account.html")


@app.route('/process-new-account-form', methods=["POST"])
def create_new_user():
    """Creates new account, redirects to login page."""

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter(User.email == email).first()
    print user

    if user == None:
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()

    return redirect("/")


@app.route('/dashboard')
def dashboard():
    """Dashboard for user, can search shows and see saved shows and playlists."""

    events = ""
    artist = ""

    return render_template("dashboard.html",
                            events=events,
                            artist=artist)

    #this will check if login info is correct, if not will redirect back to login page


@app.route('/search-for-shows.json')
def search_for_shows():
    """Search Spotify's related artists and find artists with upcoming shows based on Songkick data."""

    searched_artist = request.args.get("artist")
    city = request.args.get("city")

    related_artist_dict = check_for_events(searched_artist, city)

    searched_artist_name_img = [searched_artist.replace(" ", "-"), related_artist_dict[searched_artist]['img']]
    related_artist_names_imgs = []
    events = []

    for artist, info in related_artist_dict.iteritems():
        if artist == searched_artist:
            if related_artist_dict[artist]['event'] is not None:
                events.append([artist, related_artist_dict[artist]['event']])
        else:
            related_artist_names_imgs.append([artist.replace(" ", "-"), related_artist_dict[artist]['img']])
            if related_artist_dict[artist]['event'] is not None:
                events.append([artist, related_artist_dict[artist]['event']])

    results = {"events": events, "searched_artist_name_img": searched_artist_name_img, "related_artist_names_imgs": related_artist_names_imgs}

    return jsonify(results)


# @app.route('/saved-shows.json')
# def save_show():
#     """Save show for user, add it to their My Saved Shows."""




def get_artist_spotify_uri(artist):
    """Search for artist in database, if not there, get spotify URI and save artist to db."""

    artist_db = Artist.query.filter(Artist.artist_name == artist).first()
    if artist_db is not None:
        artist_uri = artist_db.artist_spotify_id
    else:
        artist_search = spotify.search(artist, limit=1, offset=0, type='artist')
        print artist_search
        artist_uri = artist_search['artists']['items'][0]['uri'].lstrip("spotify:artist:")
        artist = Artist(artist_name=artist, artist_spotify_id=artist_uri)
        db.session.add(artist)
        db.session.commit()

    return artist_uri


def get_artist_img(artist):
    """Get an artist's image from Spotify."""

    results = spotify.search(q='artist:' + artist, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        artist_lu = items[0]
        artist_img = artist_lu['images'][0]['url']
    else:
        artist_img = 'https://pbs.twimg.com/profile_images/1324123785/macaroni_noodle_icom_-_web_taken_400x400.jpg'

    return artist_img


def get_artist_songkick_id(artist):
    """Get artist songkick id."""


    payload = {'query': artist, 'apikey': api_key}
    artist_request = 'http://api.songkick.com/api/3.0/search/artists.json'
    artist_id = requests.get(artist_request, params=payload)
    jdict_artist = artist_id.json()

    if 'artist' in jdict_artist['resultsPage']['results']:
        artist_songkick_id = jdict_artist['resultsPage']['results']['artist'][0]['id']
    else:
        artist_songkick_id = None

    return artist_songkick_id

def save_artist_to_db(artist):
    """Look up artist in db, if not there get artist info and save it to db."""

    artist_spotify_id = get_artist_spotify_uri(artist)
    artist_img = get_artist_img(artist)
    artist_songkick_id = get_artist_songkick_id(artist)

    artist_db = Artist.query.filter(Artist.artist_name == artist).first()

    if artist_db is None:
        artist = Artist(artist_name=artist,
                        artist_spotify_id=artist_spotify_id,
                        artist_songkick_id=artist_songkick_id,
                        artist_img=artist_img)
        db.session.add(artist)
        db.session.commit()



def get_related_artists(artist):
    """Get related artists for user entered artist and organize all the info in a dictionary."""

    related_artist_dict = {}

    save_artist_to_db(artist)
    artist_db = Artist.query.filter(Artist.artist_name == artist).first()
    artist_spotify_id = artist_db.artist_spotify_id
    artist_img = artist_db.artist_img

    #put all related artist info into dict, value is list -->
    #[identifier for relationship sequence, spotify URI, songkick URI or None for no event found]
    related_artist_dict[artist] = {'spotify_uri': artist_spotify_id,
                                    'event': None,
                                    'img': artist_img}

    #get related artists for user entered artist
    related_artists = spotify.artist_related_artists(related_artist_dict[artist]['spotify_uri'])
    related_artists = related_artists['artists']

    for artist in related_artists:
        artist_name = artist['name']
        artist_uri = artist['uri'].lstrip("spotify:artist:")
        if artist['images'] == []:
            artist_img = 'https://pbs.twimg.com/profile_images/1324123785/macaroni_noodle_icom_-_web_taken_400x400.jpg'
        else:
            artist_img = artist['images'][0]['url']
        related_artist_dict[artist_name] = {'spotify_uri': artist_spotify_id, 'event': None, 'img': artist_img}

    return related_artist_dict



def save_event_to_db(event_dict):
    """Checks if event is in db, if not saves event to db."""

    event_songkick_id = str(event_dict['event_id'])
    event_name = event_dict['event_name_date']
    city = event_dict['city']
    lat = event_dict['lat']
    lng = event_dict['lng']
    performing_artist = event_dict['performing_artist']
    event_songkick_link = event_dict['songkick_link']
    event_datetime = event_dict['event_datetime']

    event_db = Event.query.filter(Event.event_songkick_id == event_songkick_id).first()
    artist_db = Artist.query.filter(Artist.artist_name == performing_artist).first()

    if artist_db is None:
        save_artist_to_db(performing_artist)
        artist_db = Artist.query.filter(Artist.artist_name == performing_artist).first()
        
    artist_id = artist_db.artist_id

    if event_db is None:
        event = Event(event_songkick_id=event_songkick_id,
                    artist_id=artist_id,
                    event_name=event_name,
                    city=city,
                    lat=lat,
                    lng=lng,
                    event_songkick_link=event_songkick_link,
                    datetime=event_datetime)
        db.session.add(event)
        db.session.commit()



def check_for_events(artist, user_city):
    """Checks for events for a given dictionary of artists and adds Songkick URI to the dictionary if event is found."""

    related_artist_dict = get_related_artists(artist)

    for artist, info in related_artist_dict.iteritems():

        payload = {'query': artist, 'apikey': api_key}
        artist_request = 'http://api.songkick.com/api/3.0/search/artists.json'

        artist_id = cache.get(artist)
        print artist_id, "HEY@@"
        if artist_id is None:
            artist_id = requests.get(artist_request, params=payload)
            cache.set(artist, artist_id, timeout=24 * 60 * 60)
        
        jdict_artist = artist_id.json()

        if 'artist' in jdict_artist['resultsPage']['results']:
            artist_songkick_id = jdict_artist['resultsPage']['results']['artist'][0]['id']

            event_request = "http://api.songkick.com/api/3.0/artists/%s/calendar.json?apikey=%s" % (artist_songkick_id, api_key)
            artist_calendar = cache.get(artist_songkick_id)
            if artist_calendar is None:
                artist_calendar = requests.get(event_request)
                cache.set(artist_songkick_id, artist_calendar, timeout=24 * 60 * 60)

            jdict_events = artist_calendar.json()

            if jdict_events['resultsPage']['totalEntries'] != 0:
                list_of_events = jdict_events['resultsPage']['results']['event']
            else:
                continue

            for event in list_of_events:
                city = event['location']['city']
                if user_city in city:
                    event_id = event['id']
                    event_name_date = event['displayName']
                    city = event['location']['city']
                    lat = event['location']['lat']
                    lng = event['location']['lng']
                    performing_artist = event['performance'][0]['displayName']
                    event_datetime = event['start']['datetime']
                    songkick_link = event['performance'][0]['artist']['uri']
                    events_info = {'event_id': event_id,
                                   'performing_artist': performing_artist,
                                   'event_name_date': event_name_date,
                                   'city': city,
                                   'lat': lat,
                                   'lng': lng,
                                   'songkick_link': songkick_link,
                                   'event_datetime': event_datetime}
                    save_event_to_db(events_info)
                    related_artist_dict[artist]['event'] = {'id': event_id,
                                                            'event_name': event_name_date,
                                                            'city': city,
                                                            'lat': lat,
                                                            'lng': lng,
                                                            'songkick_link': songkick_link}

    return related_artist_dict




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
