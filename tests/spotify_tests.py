from unittest import TestCase

from model import Artist, connect_to_db, db
from server import app, spotify, get_artist_spotify_uri


class FakeSpotifyClient(object):
    def __init__(self, seed_data):
        self._seed_data = seed_data
        self.search_was_called = False

    def search(self, query, limit=None, offset=None, type=None):
        self.search_was_called = True

        if query in self._seed_data:
            results = [
                {
                    'uri': self._seed_data[query],
                }
            ]
        else:
            results = []

        return {
            'artists': {
                'items': results
            }
        }





class SpotifyTestCase(TestCase):
    def setUp(self):
        self.spotify = FakeSpotifyClient({
            'Prince': 'princeyprince'
        })

        app.config['TESTING'] = True
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()
        app.config['SQLALCHEMY_ECHO'] = False

    def tearDown(self):
        db.session.close()
        db.drop_all()

    def test_when_artist_exists_in_db_fetches_from_db(self):
        artist = Artist()
        artist.artist_spotify_id = "abc123"
        artist.artist_name = "David Bowie"

        db.session.add(artist)
        db.session.commit()

        uri = get_artist_spotify_uri(self.spotify, "David Bowie")
        self.assertEqual("abc123", uri)
        self.assertFalse(self.spotify.search_was_called)

    def test_when_artist_not_in_db_and_not_in_spotify_returns_nothing(self):
       
        uri = get_artist_spotify_uri(self.spotify, "David Bowie")
        self.assertIsNone(uri)
        self.assertTrue(self.spotify.search_was_called)

    def test_when_artist_not_in_db_but_in_spotify_returns_uri_from_spotify(self):

        uri = get_artist_spotify_uri(self.spotify, "Prince")
        self.assertTrue(self.spotify.search_was_called)
        self.assertEqual("princeyprince", uri)

        prince = Artist.query.first()
        self.assertEqual("Prince", prince.artist_name)


    def test_search_integration_with_spotify_returns_uri(self):
        uri = get_artist_spotify_uri(spotify, "Prince")
        self.assertIsNotNone(uri)

