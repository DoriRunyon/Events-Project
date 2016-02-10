import requests
from pprint import pprint
import os

api_key = os.environ['SONGKICK_API_KEY']

def get_id_for_metro_area(location):

    payload = {'query': location, 'apikey': api_key}

    location_request = 'http://api.songkick.com/api/3.0/search/locations.json'
    locations = requests.get(location_request, params=payload)
    jdict_location = locations.json()
    metro_id = jdict_location["resultsPage"]["results"]["location"][0]["metroArea"]["id"]

    return metro_id


def get_events_given_metro_id(metro_id):

    metro_area_event_look_up = "http://api.songkick.com/api/3.0/metro_areas/%s/calendar.json?apikey=%s" % (metro_id, api_key)
    events = requests.get(metro_area_event_look_up)
    jdict_events = events.json()
    dict_of_events = jdict_events['resultsPage']['results']['event']

    final_event_dict = {}

    for event in dict_of_events:
        city = event["location"]["city"]
        if event["performance"] == []:
            artist = "Festival"
        else:
            artist = event["performance"][0]["artist"]["displayName"]
        venue = event["venue"]["displayName"]
        date = event["start"]["date"]
        uri = event["uri"]
        final_event_dict[uri] = [artist, city, venue, date]

    return final_event_dict

SF_ID = get_id_for_metro_area("Portland")
SF_events = get_events_given_metro_id(SF_ID)

for key, value in SF_events.iteritems():
    print key, value
