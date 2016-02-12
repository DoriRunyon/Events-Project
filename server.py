import spotipy

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Artist, Event, UserEvent, Playlist

spotify = spotipy.Spotify()

app = Flask(__name__)

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

    related_artists = ""
    count = ""

    return render_template("dashboard.html",
                            related_artists=related_artists,
                            count=count)

    #this will check if login info is correct, if not will redirect back to login page


@app.route('/search-for-shows')
def search_for_shows():
    """Search Spotify's related artists and find artists with upcoming shows based on Songkick data."""

    artist1 = request.args.get("artist1")
    artist2 = request.args.get("artist2")
    artist3 = request.args.get("artist3")
    artist4 = request.args.get("artist4")
    artist5 = request.args.get("artist5")

    user_input = [artist1, artist2, artist3, artist4, artist5]
    artist_list = {}

    #iterate over user inputs, search for artist in Spotify library, get artist URI
    #put artist name and uri as key value pairs in artist list dictionary
    for artist in user_input:
        if artist != "":
            artist_obj = spotify.search(artist, limit=1, offset=0, type='artist')
            artist_uri = artist_obj['artists']['items'][0]['uri'].lstrip("spotify:artist:")
            artist_list[artist] = artist_uri

    #get related artists for all the artists in the 'artist list', put them in a dictionary
    #called "related artists" where the key is the artist and the values are a list of lists
    #i.e. {'Perfume Genius': [["Sharon Van Etten", "URI"], ["Blood Orange", "URI"]]}

    related_artists = {}

    for key, value in artist_list.iteritems():
        list_of_relations = []
        related_artists[key] = list_of_relations
        dict_of_related_artists = spotify.artist_related_artists(value)
        list_of_related_artists = dict_of_related_artists['artists']
        for artist in list_of_related_artists:
            related_artist_name = artist['name']
            related_artist_uri = artist['uri'].lstrip("spotify:artist:")
            related_artist_nameuri = [related_artist_name, related_artist_uri]
            list_of_relations.append(related_artist_nameuri)
            # related_artists[key] = (related_artist_name, related_artist_uri)


    all_artists = []

    #put just the related artists names in a list called "all artists". Then create a set of
    #those items called "no duplicates" so there are no duplicate artists. This list will be checked
    #against Songkick data.

    for artist, related_artists_list in related_artists.iteritems():
        for related_artist in related_artists_list:
            all_artists.append(related_artist[0])

    number_of_related_all = len(all_artists)
    no_duplicates = set(all_artists)
    count = len(no_duplicates)
    related_artists = list(no_duplicates)

    return render_template("dashboard.html",
                            related_artists=related_artists,
                            count=count)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
