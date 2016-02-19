# import requests, spotipy
# from pprint import pprint
# import os
# from werkzeug.contrib.cache import SimpleCache
# from model import connect_to_db, db, User, Artist, Event, UserEvent

# api_key = os.environ['SONGKICK_API_KEY']


# spotify = spotipy.Spotify()
# cache = SimpleCache()



# def get_artist_spotify_uri(artist):
#     """Search for artist in database, if not there, get spotify URI and save artist to db."""

#     artist = Artist.query.filter(Artist.artist_name == artist).one()
#     if artist is not None:
#         artist_uri = artist.artist_songkick_id
#     else:
#         artist = spotify.search(artist, limit=1, offset=0, type='artist')
#         artist_uri = artist['artists']['items'][0]['uri'].lstrip("spotify:artist:")
#         artist = Artist(artist_name=artist, artist_spotify_id=artist_uri)
#         db.session.add(artist)
#         db.session.commit()

#     return artist_uri


# def get_artist_img(artist):
#     """Get an artist's image from Spotify when given artist name."""

#     results = spotify.search(q='artist:' + artist, type='artist')
#     items = results['artists']['items']
#     if len(items) > 0:
#         artist_lu = items[0]
#         artist_img = artist_lu['images'][0]['url']
#     else:
#         artist_img = None

#     return artist_img

# # def get_artist_info(artist_uri):
# #     """Get artist info based on spotify uri."""

# def get_related_artists(artist):
#     """Get related artists for user entered artist and organize all the info in a dictionary."""

#     related_artist_dict = {}

#     artist_uri = get_artist_spotify_uri(artist)
#     artist_img = get_artist_img(artist)

#     #put all related artist info into dict, value is list -->
#     #[identifier for relationship sequence, spotify URI, songkick URI or None for no event found]
#     related_artist_dict[artist] = {'spotify_uri': artist_uri,
#                                     'event': None,
#                                     'img': artist_img}

#     #get related artists for user entered artist
#     related_artists = spotify.artist_related_artists(related_artist_dict[artist]['spotify_uri'])
#     related_artists = related_artists['artists']

#     for artist in related_artists:
#         artist_name = artist['name']
#         artist_uri = artist['uri'].lstrip("spotify:artist:")
#         if artist['images'] == []:
#             artist_img = 'https://pbs.twimg.com/profile_images/1324123785/macaroni_noodle_icom_-_web_taken_400x400.jpg'
#         else:
#             artist_img = artist['images'][0]['url']
#         related_artist_dict[artist_name] = {'spotify_uri': artist_uri, 'event': None, 'img': artist_img}

#     return related_artist_dict


# def check_for_events(artist, user_city):
#     """Checks for events for a given dictionary of artists and adds Songkick URI to the dictionary if event is found."""

#     related_artist_dict = get_related_artists(artist)

#     for artist, info in related_artist_dict.iteritems():


#         payload = {'query': artist, 'apikey': api_key}
#         artist_request = 'http://api.songkick.com/api/3.0/search/artists.json'

#         artist_id = cache.get(artist)
#         print artist_id, "HEY@@"
#         if artist_id is None:
#             artist_id = requests.get(artist_request, params=payload)
#             cache.set(artist, artist_id, timeout=24 * 60 * 60)
        
#         jdict_artist = artist_id.json()

#         if 'artist' in jdict_artist['resultsPage']['results']:
#             artist_songkick_id = jdict_artist['resultsPage']['results']['artist'][0]['id']

#             event_request = "http://api.songkick.com/api/3.0/artists/%s/calendar.json?apikey=%s" % (artist_songkick_id, api_key)
#             artist_calendar = cache.get(artist_songkick_id)
#             print artist_calendar, "BOOOOP"
#             if artist_calendar is None:
#                 artist_calendar = requests.get(event_request)
#                 cache.set(artist_songkick_id, artist_calendar, timeout=24 * 60 * 60)

#             jdict_events = artist_calendar.json()

#             if jdict_events['resultsPage']['totalEntries'] != 0:
#                 list_of_events = jdict_events['resultsPage']['results']['event']
#             else:
#                 continue

#             for event in list_of_events:
#                 city = event['location']['city']
#                 if user_city in city:
#                     event_id = event['id']
#                     event_name_date = event['displayName']
#                     city = event['location']['city']
#                     lat = event['location']['lat']
#                     lng = event['location']['lng']
#                     songkick_link = event['performance'][0]['artist']['uri']
#                     related_artist_dict[artist]['event'] = {'id': event_id,
#                                                             'event_name': event_name_date,
#                                                             'city': city,
#                                                             'lat': lat,
#                                                             'lng': lng,
#                                                             'songkick_link': songkick_link}

#     return related_artist_dict


# check_for_events("Radiohead", "San Francisco")

# second_search("David Bowie", "San Francisco")

# artist = "Blood Orange"
# user_city = "London"

# payload = {'query': artist, 'apikey': api_key}
# artist_request = 'http://api.songkick.com/api/3.0/search/artists.json'
# artist = requests.get(artist_request, params=payload)
# jdict_artist = artist.json()

# artist_songkick_id = jdict_artist['resultsPage']['results']['artist'][0]['id']

# # event_request = "http://api.songkick.com/api/3.0/artists/%s/calendar.json?apikey=%s" % (artist_songkick_id, api_key)
# event_url = "http://api.songkick.com/api/3.0/artists/%s/calendar.json" % artist_songkick_id
# events = requests.get(event_url, params={'apikey': api_key, 'per_page': 2, 'page': 2})

# jdict_events = events.json()
# pprint(jdict_events)
# print len(jdict_events['resultsPage']['results']['event'])

# print jdict_events
# list_of_events = jdict_events['resultsPage']['results']['event']

# for event in list_of_events:
#     city = event['location']['city']
#     print city
#     print user_city
#     if user_city in city:
# #         events_found.append(event['id'])

# city = "London"
# payload = {'query': city, 'apikey': api_key}
# metro_id_request = 'http://api.songkick.com/api/3.0/search/locations.json'
# metro_id = requests.get(metro_id_request, params=payload)
# jdict_metroid = metro_id.json()

# lat = jdict_metroid['resultsPage']['results']['location'][0]['city']['lat']
# lng = jdict_metroid['resultsPage']['results']['location'][0]['city']['lng']


# artist = "Blood Orange"

# geo = "geo:%s,%s" % (lat, lng)


# event_search_by_location = 'http://api.songkick.com/api/3.0/search/locations.json'
# payload = {'apikey': api_key, 'location': geo}

# events = requests.get(event_search_by_location, params=payload)
# jdict_events = events.json()
# pprint(jdict_events)

# if jdict_events[]


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


# def second_level_related(artist):
#     """Get related artists for 20 directly related artists (twenty for each artist)."""

#     related_artist_dict = get_related_artists(artist)
#     print len(related_artist_dict)

#     related_artists_lists = []

#     for artist, value in related_artist_dict.iteritems():
#         related_artists = spotify.artist_related_artists(related_artist_dict[artist]['spotify_uri'])
#         related_artists = related_artists['artists']
#         related_artists_lists.append(related_artists)

#     for artist_list in related_artists_lists:
#         for artist in artist_list:
#             if artist['name'] in related_artist_dict.keys():
#                 continue
#             else:
#                 artist_name = artist['name']
#                 artist_uri = artist['uri'].lstrip("spotify:artist:")
#                 related_artist_dict[artist_name] = {'relationship_id': None, 'spotify_uri': artist_uri, 'event': None}

#     return related_artist_dict


# 

# print len(second_search("Blood Orange"))

# def get_related_artists(artist):
#     """Get related artists for user entered artist and organize all the info in a dictionary."""

#     count = 1

#     #count is for assigning each related artist an identifier (for showing relationship sequence later)
#     #this function goes through each related artist and organizes their info in a dictionary
#     for artist in related_artists:
#         count = str(count)
#         artist_name = artist['name']
#         artist_uri = artist['uri'].lstrip("spotify:artist:")
#         relationship_id = "B" + count

#         related_artist_dict[artist_name] = {'relationship_id': relationship_id, 'spotify_uri': artist_uri, 'event': None}
#         count = int(count)
#         count += 1


#     return related_artist_dict



