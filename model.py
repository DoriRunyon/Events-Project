"""Models and database functions for Broadcast."""

from flask_sqlalchemy import SQLAlchemy



# Here's where we create the idea of our database. We're getting this through
# the Flask-SQLAlchemy library. On db, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Part 1: Compose ORM

class User(db.Model):
    """A user can save multiple events."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Event user_id=%s email =%s>" % (self.user_id,
                                                 self.email)


class UserEvent(db.Model):
    """Association table for events user has saved."""

    __tablename__ = "user_events"

    user_event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)


class Event(db.Model):
    """An event can be attended by many users."""

    __tablename__ = "events"

    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_songkick_id = db.Column(db.String(100), nullable=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.artist_id'), nullable=True)
    event_name = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    event_songkick_link = db.Column(db.String(100), nullable=True)
    datetime = db.Column(db.DateTime, nullable=True)

    artist = db.relationship('Artist', backref=db.backref("artists"))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Event event_id=%s artist_id =%s venue_name=%s datetime =%s>" % (self.event_id,
                                                                                 self.artist_id,
                                                                                 self.event_name,
                                                                                 self.datetime)


class Artist(db.Model):
    """Table for artist info."""

    __tablename__ = "artists"

    artist_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist_songkick_id = db.Column(db.String(100), nullable=True)
    artist_spotify_id = db.Column(db.String(100), nullable=True)
    artist_name = db.Column(db.String(50), nullable=True)
    artist_img = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Event artist_id=%s artist_name =%s>" % (self.artist_id,
                                                         self.artist_name)

def example_data():
    """Create some sample data."""

    # In case this is run more than once, empty out existing data
    User.query.delete()

    # Add sample employees and departments
    admin = User(email='admin', password='default')

    db.session.add_all([admin])
    db.session.commit()


def connect_to_db(app, db_uri="postgresql:///noodledb"):
    """Connect the database to our Flask app."""

    # Configure to use our postgres database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    # app.config['SQLALCHEMY_ECHO'] = True
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
