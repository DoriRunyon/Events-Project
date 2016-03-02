import sys
import spotipy
import spotipy.util as util
import os


SPOTIPY_CLIENT_ID = os.environ['SPOTIFY_CONSUMER_KEY']
SPOTIPY_CLIENT_SECRET=os.environ['SPOTIFY_CONSUMER_SECRET']
SPOTIPY_REDIRECT_URI='http://localhost:5000/dashboard'



scope = 'user-library-read'

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print "Usage: %s username" % (sys.argv[0],)
    sys.exit()

token = util.prompt_for_user_token(username, scope=scope, client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI)

if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_saved_tracks()
    for item in results['items']:
        track = item['track']
        print track['name'] + ' - ' + track['artists'][0]['name']
else:
    print "Can't get token for", username


