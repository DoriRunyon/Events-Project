import spotipy, requests, os, json, grequests, urllib
from jinja2 import StrictUndefined
from pprint import pprint
from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Artist, Event, UserEvent
from werkzeug.contrib.cache import SimpleCache
from datetime import datetime
from base64 import b64encode

api_key = os.environ['SONGKICK_API_KEY']
spotify_client_ID = os.environ['SPOTIFY_CONSUMER_KEY']
spotify_client_secret = os.environ['SPOTIFY_CONSUMER_SECRET']
google_maps_api_key = os.environ['GOOGLE_MAPS_API_KEY']
cache = SimpleCache()

app = Flask(__name__)

app.secret_key = "ABC"
app.jinja_env.undefined = StrictUndefined

grant_type = 'client_credentials'

#Request based on Client Credentials Flow from https://developer.spotify.com/web-api/authorization-guide/
#Request body parameter: grant_type Value: Required. Set it to client_credentials
body_params = {'grant_type' : grant_type}
url='https://accounts.spotify.com/api/token'
response = requests.post(url, data=body_params, auth=(spotify_client_ID, spotify_client_secret))
response_data = json.loads(response.text)
access_token = response_data["access_token"]

authorization_header = {"Authorization":"Bearer {}".format(access_token)}


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

    if user == None:
        flash("Incorrect email or password, please try again.")
        return redirect('/dashboard')

    elif user.password == password:
        user_id = user.user_id
        session['user'] = user_id
        flash(("Hello %s, you are now logged in.") % email)
        return redirect(('/dashboard/%d') % (user_id))

    else:
        flash("Incorrect email or password, please try again.")
        return redirect('/dashboard')

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

    if user == None:
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()

    return redirect("/")

@app.route("/save-show.json")
def save_show():
    """Look up show using songkick link, save show for user."""

    event_songkick_id = request.args.get("event_songkick_id")
    event = Event.query.filter(Event.event_songkick_id == event_songkick_id).first()

    event_id = event.event_id
    event_name = event.event_name
    user_id = session.get("user")

    event = UserEvent.query.filter((UserEvent.user_id == user_id) & (UserEvent.event_id == event_id)).first()

    if event is not None:
        event_name = "You already saved this one silly!"
    else:
        saved_show = UserEvent(event_id=event_id, user_id=user_id)
        db.session.add(saved_show)
        db.session.commit()

    return jsonify({'event_name': event_name})


@app.route('/dashboard/<int:user_id>')
def user_dashboard(user_id):
    """Dashboard for user, can search shows and see saved shows and playlists."""

    events = ""
    artist = ""

    today = datetime.utcnow()

    user_saved_events = UserEvent.query.filter(UserEvent.user_id == user_id).all()
    events_list = []
    event_locations_unsorted = []
    performing_artists = []

    for event in user_saved_events:
        event_id = event.event_id
        event_info = Event.query.filter(Event.event_id == event_id).first()
        event_date = event_info.datetime
        if event_date > today:
            event_name = event_info.event_name
            event_date = event_info.datetime
            artist = Artist.query.filter(Artist.artist_id == event_info.artist_id).first()
            performing_artists.append(artist.artist_name)
            events_list.append([event_date, event_name])
            event_lng = event_info.lng
            event_lat = event_info.lat
            event_latlng = [(event_lat, event_lng), event_date, event_name]
            event_locations_unsorted.append(event_latlng)

    events_list = sorted(events_list)
    event_locations = sort_events_by_location_date(event_locations_unsorted)
    print performing_artists

    return render_template("user_dashboard.html",
                            events=events,
                            artist=artist,
                            events_list=events_list,
                            user_id=user_id,
                            data=json.dumps(event_locations),
                            performing_artists=json.dumps(performing_artists))

@app.route('/dashboard')
def dashboard():
    """Dashboard when logged in, can search for shows."""

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

    print searched_artist
    print city

    related_artist_dict = check_for_events(searched_artist, city)

    if related_artist_dict is None:
        error_message = "Error."
        return jsonify({"wrong_input": error_message})

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

    results = {"events": events, "searched_artist_name_img": searched_artist_name_img, "related_artist_names_imgs": related_artist_names_imgs, "wrong_input": None}

    return jsonify(results)


@app.route("/make-playlist.json")
def make_playlist():
    """Create a playlist based on the user's saved events."""

    playlist_name = request.args.get('playlistName')
    print playlist_name
    artists = request.args.get('performingArtistsList')
    artists = artists.split("+")
    artists = artists[1:]

    tracks = create_playlist_for_artists(artists)
    list_of_tracks = []

    for artist in tracks:
        for track in artist:
            track = track[1]
            list_of_tracks.append(track)

    no_duplicate_tracks = set(list_of_tracks)
    list_of_tracks = list(no_duplicate_tracks)

    results = {"tracks": list_of_tracks, "playlistName": playlist_name}

    return jsonify(results)

def get_artist_spotify_uri(artist):
    """Search for artist URI in database, if not there, get spotify URI and save artist to db."""

    artist_db = Artist.query.filter(Artist.artist_name == artist).first()
    if artist_db is not None:
        artist_uri = artist_db.artist_spotify_id
    else:
        artist_request = "https://api.spotify.com/v1/search?q=" + artist + "&type=artist"
        artist_id = requests.get(artist_request, headers=authorization_header)
        artist_dict = artist_id.json()
        if artist_dict['artists']['items'] == []:
            return None
        else:
            artist_uri = artist_dict['artists']['items'][0]['uri'].lstrip("spotify:artist:")
            artist = Artist(artist_name=artist, artist_spotify_id=artist_uri)
            db.session.add(artist)
            db.session.commit()

    return artist_uri


def get_artist_img(artist):
    """Get an artist's image from Spotify."""

    artist_request = "https://api.spotify.com/v1/search?q=" + artist + "&type=artist"
    artist_id = requests.get(artist_request, headers=authorization_header)
    artist_dict = artist_id.json()

    artists = artist_dict['artists']['items']
    if len(artists) > 0:
        first_artist = artists[0]
        artist_img = first_artist['images'][0]['url']
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

    if artist_spotify_id is None:
        return None

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

    if artist_db is None:
        return None

    artist_spotify_id = artist_db.artist_spotify_id
    artist_img = artist_db.artist_img

    #put all related artist info into dict, value is list -->
    #[identifier for relationship sequence, spotify URI, songkick URI or None for no event found]
    related_artist_dict[artist] = {'spotify_uri': artist_spotify_id,
                                    'event': None,
                                    'img': artist_img}

    #get related artists for user entered artist
    related_artist_endpoint = "https://api.spotify.com/v1/artists/" + artist_spotify_id + "/related-artists"
    related_artist_request = requests.get(related_artist_endpoint, headers=authorization_header)
    related_artist_dict = related_artist_request.json()

    related_artists = related_artist_dict['artists']

    for artist in related_artists:
        artist_name = artist['name']
        artist_uri = artist['uri'].lstrip("spotify:artist:")
        if artist['images'] == []:
            artist_img = 'https://pbs.twimg.com/profile_images/1324123785/macaroni_noodle_icom_-_web_taken_400x400.jpg'
        else:
            artist_img = artist['images'][0]['url']
        related_artist_dict[artist_name] = {'spotify_uri': artist_uri, 'event': None, 'img': artist_img}

    return related_artist_dict

def get_spotify_id_and_img_for_one_artist(artist):
    """Gets Spotify id and img for artist."""

    save_artist_to_db(artist)
    artist_db = Artist.query.filter(Artist.artist_name == artist).first()

    if artist_db is None:
        return None

    artist_spotify_id = artist_db.artist_spotify_id
    artist_img = artist_db.artist_img

    artist_info = [artist_spotify_id, artist_img]

    return artist_info

def request_spotify_related_artists(artist):
    """Requests related artists from Spotify given artist name."""

    artist_spotify_id = get_artist_spotify_uri(artist)

    related_artist_endpoint = "https://api.spotify.com/v1/artists/" + artist_spotify_id + "/related-artists"
    related_artist_request = requests.get(related_artist_endpoint, headers=authorization_header)
    related_artist_dict = related_artist_request.json()

    related_artists = related_artist_dict['artists']

    return related_artists

def make_new_related_artist_dict(artist):
    """Requests related artist from Spotify, puts all artist info into a dictionary."""

    related_artist_dict = {}
    artist_info = get_spotify_id_and_img_for_one_artist(artist)
    related_artist_info = request_spotify_related_artists(artist)

    related_artist_dict[artist] = {'spotify_uri': artist_info[0],
                                    'event': None,
                                    'img': artist_info[1]}

    for artist in related_artist_info:
        artist_name = artist['name']
        artist_spotify_id = artist['uri'].lstrip("spotify:artist:")
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



def make_artist_list(related_artist_dict):
    """Makes a list of artist names from the related artist dictionary.

    >>> [make_artist_list({'artist': {'spotify_uri': '123', 'event': 'x', 'img': 'x'}, 'artist2': {'spotify_uri': '123', 'event': 'x', 'img': 'x'}})]
    [['artist2', 'artist']]
    """

    related_artist_list = []

    if related_artist_dict is None:
        return None

    for artist, info in related_artist_dict.iteritems():
        related_artist_list.append(artist)

    return related_artist_list

def get_songkick_ids(related_artist_list):
    """Given list of artist names, gets Songkick ids."""

    songkick_id_requests = []
    for artist in related_artist_list:
        artist = artist.encode('ascii', 'ignore')
        payload = {'query': artist, 'apikey': api_key}
        payload_url = urllib.urlencode(payload)
        artist_request = 'http://api.songkick.com/api/3.0/search/artists.json?%s' % (payload_url)

        # artist_id = requests.get(artist_request, params=payload)
        songkick_id_requests.append(artist_request)

    #create set of unsent requests
    rs = (grequests.get(u) for u in songkick_id_requests)

    #send requests all at once
    songkick_id_responses = grequests.map(rs)
    print songkick_id_responses

    #make a dictionary out of each response object, put songkick ID in list
    artist_songkick_ids = []
    for artist_id in songkick_id_responses:
        jdict_artist = artist_id.json()

        if 'artist' in jdict_artist['resultsPage']['results']:
            artist_songkick_id = jdict_artist['resultsPage']['results']['artist'][0]['id']
            artist_songkick_ids.append(artist_songkick_id)

    return artist_songkick_ids

def get_artist_calendars(artist_songkick_ids):
    """Given artist songkick ids, requests artist calendars from Songkick."""

    calendar_requests = []

    for artist_id in artist_songkick_ids:
        event_request = "http://api.songkick.com/api/3.0/artists/%s/calendar.json?apikey=%s" % (artist_id, api_key)
        # artist_calendar = requests.get(event_request)
        calendar_requests.append(event_request)

    #create a set of unsent requests
    rs = (grequests.get(u) for u in calendar_requests)

    #send all requests at once
    calendar_responses = grequests.map(rs)

    all_events = []
    for calendar in calendar_responses:
        jdict_events = calendar.json()

        if jdict_events['resultsPage']['totalEntries'] != 0:
            list_of_events = jdict_events['resultsPage']['results']['event']
            all_events.append(list_of_events)
        else:
            continue

    return all_events

def search_events_for_city(all_events, user_city):
    """Searches artist calendars for city, returns events where city matches."""

    saved_events = []

    #code for look for city in calendar
    for calendar in all_events:
        for event in calendar:
            city = event['location']['city']
            if user_city in city:
                event_id = event['id']
                event_name_date = event['displayName']
                city = event['location']['city']
                lat = event['location']['lat']
                lng = event['location']['lng']
                performing_artist = event['performance'][0]['displayName']
                event_datetime = event['start']['datetime']
                if event_datetime is None:
                    event_datetime = event['start']['date']
                songkick_link = event['performance'][0]['artist']['uri']
                events_info = create_events_info_dict(event_id, event_name_date, city, lat, lng, performing_artist, event_datetime, songkick_link)
                save_event_to_db(events_info)
                saved_event = [performing_artist, {'id': event_id,
                                                    'event_name': event_name_date,
                                                    'city': city,
                                                    'lat': lat,
                                                    'lng': lng,
                                                    'songkick_link': songkick_link}]
                saved_events.append(saved_event)

    return saved_events

def check_for_events(artist, user_city):
    """Makes requests to Spotify for related artists, requests to Songkick for event calendars and returns events for city if found."""

    related_artist_dict = make_new_related_artist_dict(artist)
    related_artist_list = make_artist_list(related_artist_dict)
    artist_songkick_ids = get_songkick_ids(related_artist_list)
    all_events = get_artist_calendars(artist_songkick_ids)
    saved_events = search_events_for_city(all_events, user_city)

    for artist in saved_events:
        if artist[0] in related_artist_dict.keys():
            related_artist_dict[artist[0]]['event'] = artist[1]

    return related_artist_dict



def create_events_info_dict(event_id, event_name_date, city, lat, lng, performing_artist, event_datetime, songkick_link):
    """Creates a dictionary of event information."""


    events_info = {'event_id': event_id,
                   'performing_artist': performing_artist,
                   'event_name_date': event_name_date,
                   'city': city,
                   'lat': lat,
                   'lng': lng,
                   'songkick_link': songkick_link,
                   'event_datetime': event_datetime}

    return events_info


def get_tracks_for_artist(artist):
    """Gets artists top tracks. Tracks come from most popular list according to Spotify."""

    artist_spotify_id = get_artist_spotify_uri(artist)
    top_tracks_endpoint = "https://api.spotify.com/v1/artists/" + artist_spotify_id + "/top-tracks?country=US"
    top_tracks_request = requests.get(top_tracks_endpoint, headers=authorization_header)
    tracks_dict = top_tracks_request.json()

    tracks_list = []

    for track in tracks_dict['tracks']:
        track_id = track['album']['id']
        track_name = track['album']['name']
        track = (track_id, track_name)
        tracks_list.append(track)

    tracks_list = set(tracks_list)
    tracks_list = list(tracks_list)

    return tracks_list

def create_playlist_for_artists(artist_list):
    """Creates a playlist for a given list of artists"""

    playlist = []

    for artist in artist_list:
        tracks = get_tracks_for_artist(spotify, artist)
        playlist.append(tracks[0:3])

    return playlist


def sort_events_by_location_date(event_locations):
    """Sorts an event list by location and if there are duplicates, keeps only the event with the closest date.
    >>> [sort_events_by_location_date([[(1, 2), "2016-04-23 20:00:00", "event name"], [(5, 2), "2016-04-23 20:00:00", "event name"], [(1, 6), "2016-04-23 20:00:00", "event name"], [(1, 2), "2016-04-26 20:00:00", "event name"]])]
    [[[1, 2, 'event name'], [1, 6, 'event name'], [5, 2, 'event name']]]
    """

    event_locations_dict = {}
    event_locations_new = []

    for event in event_locations:
        event_datetime = event[1]
        if event[0] in event_locations_dict:
            stuff = event_locations_dict[event[0]][0]
            if event_datetime < event_locations_dict[event[0]][0]:
                event_locations_dict[event[0]] = [event_datetime, event[2]]
        else:
            event_locations_dict[event[0]] = [event_datetime, event[2]]

    for key, value in event_locations_dict.iteritems():
        lat = key[0]
        lng = key[1]
        event_name = value[1]
        event = [lat, lng, event_name]
        event_locations_new.append(event)

    return event_locations_new




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    # app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()

    import doctest
    doctest.testmod()