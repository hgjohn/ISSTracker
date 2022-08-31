
import os, time, json, urllib3, tweepy
from geopy.geocoders import Nominatim

# authentication of consumer keys and access tokens, tweepy setup
consumer_key = os.environ['consumer_key']
consumer_secret = os.environ['consumer_secret']
access_token = os.environ['access_token']
access_token_secret = os.environ['access_token_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

url_location = 'http://api.open-notify.org/iss-now.json'

on = True

def Track_ISS():
    while on:
        # API requests, data formatting, pull lat and lon from dict
        http = urllib3.PoolManager()
        position_data = http.request('GET', url_location)
        position_dict = json.loads(position_data.data.decode('UTF-8'))
        lon = position_dict['iss_position']['longitude']
        lat = position_dict['iss_position']['latitude']

        # geolocation of (latitude, longitude) coordinates
        geolocator = Nominatim(user_agent='geoapiExercises')
        location = geolocator.reverse(lat+','+lon, language='en')

        # continues if location is over ocean, tweets if Oregon or Washington,
        # waits to avoid double tweeting then loops
        if location is None:
            time.sleep(10)
        else:
            address = location.raw['address']
            state = address.get('state', '')
            if state == 'Oregon' or state == 'Washington':
                api.update_status(status='The ISS is currently flying over ' + state + '!')
                time.sleep(3600)
            else:
                time.sleep(10)

Track_ISS()