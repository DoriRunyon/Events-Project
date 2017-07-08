from unittest import TestCase
#test case is the smallest unit of testing - checks for a specific response to a particular set of inputs


from model import Artist, connect_to_db, db
from server import app, spotify, get_artist_spotify_uri


class FakeSpotifyClient(object): #setting up mock API
    def __init__(self, seed_data):
        self._seed_data = seed_data
        self.search_was_called = False #default of search was called is False

    def search(self, query, limit=None, offset=None, type=None):
        #above are the parameters for a spotify search
        self.search_was_called = True #set search called True

        if query in self._seed_data:  #if query in seed data ..?
            results = [
                {
                    'uri': self._seed_data[query], #uri is equal to ..? (not sure what this is doing)
                }
            ]
        else:
            results = [] #else results equal an empty list

        return {
            'artists': {
                'items': results #return results
            }
        }

#above is saying - when search is run, API call is set to True,
#if query is in the seed data, the uri is set to ??, otherwise
#the results are an empty list. The return gives the function 
#the format needed (the data in the format Spotify gives it in)


#testing of get spotify URI funciton - 5 parts
class SpotifyTestCase(TestCase):
    def setUp(self):
        self.spotify = FakeSpotifyClient({
            #we are creating an instance of FakeSpotifyClient, and giving it seed data 
            'Prince': 'princeyprince'
        })

        #create test db and tables
        app.config['TESTING'] = True
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()
        app.config['SQLALCHEMY_ECHO'] = False

        #tear down db after tests are run
    def tearDown(self):
        db.session.close()
        db.drop_all()

    def test_when_artist_exists_in_db_fetches_from_db(self):

        #create fake artist and spotify id, add and commit artist to db
        artist = Artist()
        artist.artist_spotify_id = "abc123"
        artist.artist_name = "David Bowie"

        db.session.add(artist)
        db.session.commit()

        #(can't remember why we're passing in spotify??)
        #pass 'David Bowie' into the function we're testing
        uri = get_artist_spotify_uri(self.spotify, "David Bowie")
        self.assertEqual("abc123", uri) #check that the db uri is equal to what the function call returned 
        self.assertFalse(self.spotify.search_was_called) #check that the API was not called

    def test_when_artist_not_in_db_and_not_in_spotify_returns_nothing(self):
       
        uri = get_artist_spotify_uri(self.spotify, "David Bowie") #pass in paramters
        self.assertIsNone(uri) #check that what function returns is none
        self.assertTrue(self.spotify.search_was_called) #check that API was called

    def test_when_artist_not_in_db_but_in_spotify_returns_uri_from_spotify(self):

        uri = get_artist_spotify_uri(self.spotify, "Prince") #pass in parameters
        self.assertTrue(self.spotify.search_was_called) #check that API was called
        self.assertEqual("princeyprince", uri) #check that what function returned is what mock API returns

        prince = Artist.query.first() #create this artist in the db
        self.assertEqual("Prince", prince.artist_name) #check that what we put in db matches what's in db


    def test_search_integration_with_spotify_returns_uri(self):
        uri = get_artist_spotify_uri(spotify, "Prince") #pass in parameters
        self.assertIsNotNone(uri) #check that the real function with API call works (I think that's what this tests)



# def get_artist_spotify_uri(spotify, artist):
#     """Search for artist in database, if not there, get spotify URI and save artist to db."""

#     artist_db = Artist.query.filter(Artist.artist_name == artist).first()
#     if artist_db is not None:
#         artist_uri = artist_db.artist_spotify_id
#     else:
#         artist_search = spotify.search(artist, limit=1, offset=0, type='artist')
#         if artist_search['artists']['items'] == []:
#             print artist_search['artists']['items']
#             return None

#         else:
#             artist_uri = artist_search['artists']['items'][0]['uri'].lstrip("spotify:artist:")
#             artist = Artist(artist_name=artist, artist_spotify_id=artist_uri)
#             db.session.add(artist)
#             db.session.commit()

#     return artist_uri
