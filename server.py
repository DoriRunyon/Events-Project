import spotipy

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Artist, Event, UserEvent, Playlist
from test import get_artist_spotify_uri, get_related_artists, check_for_events
from werkzeug.contrib.cache import SimpleCache

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


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
