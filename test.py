import requests, spotipy
from pprint import pprint
import os

api_key = os.environ['SONGKICK_API_KEY']


spotify = spotipy.Spotify()

# def get_id_for_metro_area(location):

#     payload = {'query': location, 'apikey': api_key}

#     location_request = 'http://api.songkick.com/api/3.0/search/locations.json'
#     locations = requests.get(location_request, params=payload)
#     jdict_location = locations.json()
#     metro_id = jdict_location["resultsPage"]["results"]["location"][0]["metroArea"]["id"]

#     return metro_id


# def get_events_given_metro_id(metro_id):

#     metro_area_event_look_up = "http://api.songkick.com/api/3.0/metro_areas/%s/calendar.json?apikey=%s" % (metro_id, api_key)
#     events = requests.get(metro_area_event_look_up)
#     jdict_events = events.json()
#     dict_of_events = jdict_events['resultsPage']['results']['event']

#     final_event_dict = {}

#     for event in dict_of_events:
#         city = event["location"]["city"]
#         if event["performance"] == []:
#             artist = "Festival"
#         else:
#             artist = event["performance"][0]["artist"]["displayName"]
#         venue = event["venue"]["displayName"]
#         date = event["start"]["date"]
#         uri = event["uri"]
#         final_event_dict[uri] = [artist, city, venue, date]

#     return final_event_dict

# SF_ID = get_id_for_metro_area("San Francisco")
# SF_events = get_events_given_metro_id(SF_ID)

# for key, value in SF_events.iteritems():
#     print key, value


# ****************************************



def get_artist_spotify_uri(artist):

    artist = spotify.search(artist, limit=1, offset=0, type='artist')
    artist_uri = artist['artists']['items'][0]['uri'].lstrip("spotify:artist:")

    return artist_uri

def get_related_artists(artist):
    """Get related artists for user entered artist and organize all the info in a dictionary."""

    related_artist_dict = {}

    artist_uri = get_artist_spotify_uri(artist)

    #put all related artist info into dict, value is list -->
    #[identifier for relationship sequence, spotify URI, songkick URI or None for no event found]
    related_artist_dict[artist] = {'relationship_id': "A", 'spotify_uri': artist_uri, 'event': None}

    #get related artists for user entered artist
    related_artists = spotify.artist_related_artists(related_artist_dict[artist]['spotify_uri'])
    related_artists = related_artists['artists']

    count = 1

    #count is for assigning each related artist an identifier (for showing relationship sequence later)
    #this function goes through each related artist and organizes their info in a dictionary
    for artist in related_artists:
        count = str(count)
        artist_name = artist['name']
        artist_uri = artist['uri'].lstrip("spotify:artist:")
        relationship_id = "B" + count

        related_artist_dict[artist_name] = {'relationship_id': relationship_id, 'spotify_uri': artist_uri, 'event': None}
    
        count = int(count)
        count += 1


    return related_artist_dict



def check_for_events(artist, user_city):
    """Checks for events for a given dictionary of artists and adds Songkick URI to the dictionary if event is found."""

    related_artist_dict = get_related_artists(artist)
    second_level_search = []
    event_ids= []

    for artists, info in related_artist_dict.iteritems():


        payload = {'query': artists, 'apikey': api_key}
        artist_request = 'http://api.songkick.com/api/3.0/search/artists.json'
        artist = requests.get(artist_request, params=payload)
        jdict_artist = artist.json()


        if 'artist' in jdict_artist['resultsPage']['results']:
            artist_songkick_id = jdict_artist['resultsPage']['results']['artist'][0]['id']

            event_request = "http://api.songkick.com/api/3.0/artists/%s/calendar.json?apikey=%s" % (artist_songkick_id, api_key)
            events = requests.get(event_request)
            jdict_events = events.json()

            if jdict_events['resultsPage']['totalEntries'] != 0:
                list_of_events = jdict_events['resultsPage']['results']['event']
            else:
                continue

            for event in list_of_events:
                city = event['location']['city']
                if user_city in city:
                    event_id = event['id']
                    event_ids.append(event_id)
                    print artists, event_id


    return second_level_search

check_for_events("Bryan Ferry", "San Francisco")

def second_search(artist, user_city):

    second_level_search = check_for_events(artist, user_city)

    for artist in second_level_search:
        artist_dict = get_related_artists(artist)
        events = check_for_events(artist, user_city)

    return "DONE!"

# second_search("David Bowie", "San Francisco")

artist = "Blood Orange"
user_city = "London"

payload = {'query': artist, 'apikey': api_key}
artist_request = 'http://api.songkick.com/api/3.0/search/artists.json'
artist = requests.get(artist_request, params=payload)
jdict_artist = artist.json()

artist_songkick_id = jdict_artist['resultsPage']['results']['artist'][0]['id']

# event_request = "http://api.songkick.com/api/3.0/artists/%s/calendar.json?apikey=%s" % (artist_songkick_id, api_key)
event_url = "http://api.songkick.com/api/3.0/artists/%s/calendar.json" % artist_songkick_id
events = requests.get(event_url, params={'apikey': api_key, 'per_page': 2, 'page': 2})

jdict_events = events.json()
# pprint(jdict_events)
# print len(jdict_events['resultsPage']['results']['event'])

# print jdict_events
# list_of_events = jdict_events['resultsPage']['results']['event']

# for event in list_of_events:
#     city = event['location']['city']
#     print city
#     print user_city
#     if user_city in city:
#         events_found.append(event['id'])

















