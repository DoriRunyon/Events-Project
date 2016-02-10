"""Models and database functions for Bunkee."""

from flask_sqlalchemy import SQLAlchemy


# Here's where we create the idea of our database. We're getting this through
# the Flask-SQLAlchemy library. On db, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Part 1: Compose ORM

class User(db.Model):
    """A user can have multiple playlists and multiple events."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    user_spotify_id = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Event user_id=%s email =%s>" % (self.user_id,
                                                 self.email)


class UserEvent(db.Model):
    """Association table for events user has saved."""

    __tablename__ = "user-events"

    user_event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.user_id'), nullable=False)

    user = db.relationship('User', backref=db.backref("users"))
    event = db.relationship('Event', backref=db.backref("events"))


class Event(db.Model):
    """An event can be attended by many users."""

    __tablename__ = "events"

    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    songkick_id = db.Column(db.String(100), nullable=True)
    artist = db.Column(db.String(50), nullable=False)
    venue_name = db.Column(db.String(50), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    street_address = db.Column(db.String(50), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    zipcode = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Event event_id=%s artist =%s venue_name=%s datetime =%s>" % (self.event_id,
                                                                            self.artist,
                                                                            self.venue_name,
                                                                            self.datetime)

class Playlist(db.Model):
    """A playlist can only belong to one user."""

    __tablename__ = "playlists"

    playlist_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playlist_spotify_id = db.Column(db.String(100), nullable=True)
    playlist_name = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref=db.backref("users"))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Event playlist_id=%s playlist_name =%s created_on =%s>" % (self.playlist_id,
                                                                                self.playlist_name,
                                                                                self.created_on)


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///bunkee'
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."
