
import Keys
import requests, urllib3, xmltodict, tweepy
from geopy.geocoders import Nominatim
from datetime import datetime, date, timedelta

consumer_key = Keys.consumer_key
consumer_secret = Keys.consumer_secret
access_token = Keys.access_token
access_token_secret = Keys.access_token_secret

auth = tweepy.OAuthHandler(Keys.consumer_key, Keys.consumer_secret)
auth.set_access_token(Keys.access_token, Keys.access_token_secret)
api = tweepy.API(auth)

http = urllib3.PoolManager()

geolocator = Nominatim(user_agent = 'ISS_Tracker')

tomorrow = date.today() + timedelta(days=1)
get_weekday = tomorrow.weekday()
weekday_dict = {
    0: 'Mon', 1: 'Tues', 2: 'Wed', 3: 'Thurs', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
weekday = weekday_dict[get_weekday]

# reports only on longest sighting, when sky is clear
# city and state variables do not account for values with more than 1 word
# in some cases, an underscore may fix this
# check spot the station website for specific location to amend url properly
def find_best_sighting(city, state):

    # initialize local variables
    longest_time = 0
    appears = 0
    disappears = 0
    best = 0
    best_time = 0
    dict_in_list = 0
    current_item = 0

    # get RSS and parse to list of sightings tomorrow
    location = geolocator.geocode(city + ', ' + state)
    lat = round(location.latitude, 2)
    lon = round(location.longitude, 2)
    url_iss = 'https://spotthestation.nasa.gov/sightings/xml_files/United_States_' + state.capitalize() + '_' + city.capitalize() + '.xml'
    url_weather = 'https://api.openweathermap.org/data/2.5/forecast?lat=' + str(lat) + '&lon=' + str(lon) + '&appid=' + Keys.weatherappid
    file_iss = http.request('GET', url_iss)
    list_dicts = xmltodict.parse(file_iss.data)['rss']['channel']['item']
    times_tomorrow = list(filter(lambda list_dicts: list_dicts['title'].find(str(tomorrow)) != -1, list_dicts))
    sightings = len(times_tomorrow)

    # searches for longest duration of sightings in times_tomorrow list
    while dict_in_list != sightings:

        duration_search = times_tomorrow[dict_in_list]['description'].find('Duration:')
        new_duration_time = times_tomorrow[dict_in_list]['description'][duration_search + 10]
        time_find = times_tomorrow[dict_in_list]['description'].find('Time:')

        if new_duration_time == 'l':
            dict_in_list += 1
        elif int(new_duration_time) > int(longest_time):
            longest_time = new_duration_time
            best = times_tomorrow[dict_in_list]['description'][time_find + 6:time_find + 10]
            best_time = datetime.strptime(best, '%H:%M')
            find_appears = times_tomorrow[dict_in_list]['description'].find('Approach:')
            appears = times_tomorrow[dict_in_list]['description'][find_appears + 10:find_appears + 23]
            find_disappears = times_tomorrow[dict_in_list]['description'].find('Departure:')
            disappears = times_tomorrow[dict_in_list]['description'][find_disappears + 11:find_disappears + 24]
            if disappears[12] != 'N' or 'S' or 'W' or 'E':
                disappears = disappears[0:11]
            if appears[12] != 'N' or 'S' or 'W' or 'E':
                appears = appears[0:11]
            dict_in_list += 1
        else:
            break

    # reformat datetime for sighting to unix time
    date_datetime_str = str(tomorrow) + ' ' + str(best)
    date_time = datetime.strptime(str(date_datetime_str), '%Y-%m-%d %H:%M')
    unix_time = int(datetime.timestamp(date_time))

    parse_weather = requests.get(url_weather)
    weather_json = parse_weather.json()
    weather_len = len(weather_json['list'])

    # send tweet function
    def clear_sky():
        api.update_status('The #ISS will be visible from #' + city.capitalize() + ' tomorrow, ' + weekday + ' ' + tomorrow.strftime('%B %d') + ' at ' + date.strftime(best_time, '%H:%M %p') + ', for ' + longest_time + ' min.\n\n' + 'Appears: ' + appears + '\nDisappears: ' + disappears)
        #print('The #ISS will be visible from #' + city.capitalize() + ' tomorrow, ' + weekday + ' ' + tomorrow.strftime('%B %d') + ' at ' + date.strftime(best_time, '%H:%M %p') + ', for ' + str(longest_time) + ' min.\n\n' + 'Appears: ' + appears + '\nDisappears: ' + disappears)


    # loop sends twitter update if sky is clear for longest sighting
    while current_item != weather_len:
        if int(weather_json['list'][current_item]['dt']) > unix_time:
            current_item += 1
        elif weather_json['list'][current_item-1]['weather'][0]['description'].find('clear sky') != -1:
            clear_sky()
            break
        else:
            #print(city.capitalize() + ' weather: ' + weather_json['list'][current_item-1]['weather'][0]['description'])
            #print(str(unix_time) + ' , ' + str(weather_json['list'][current_item]['dt']))
            break

find_best_sighting('medford', 'oregon')
find_best_sighting('eugene', 'oregon')
find_best_sighting('portland', 'oregon')
find_best_sighting('bend','oregon')
find_best_sighting('newport', 'oregon')