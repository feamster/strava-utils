#!/usr/bin/env python3

import time
import sys
import json
from selenium import webdriver

import re
from datetime import datetime
from geopy.geocoders import Nominatim
import requests

from stravaauth import get_tokens, get_account, site_login


#from selenium.webdriver.firefox.options import Options as FirefoxOptions
#options = FirefoxOptions()
#options.add_argument("--headless")

def get_activities_from_file(af):
    with open(af) as tokenFile:
        activities = json.load(tokenFile)
    return activities

def correct_elevation(driver,act_id):
    activity_url = 'https://www.strava.com/activities/{}'.format(act_id)
    driver.get(activity_url)
    driver.find_element_by_xpath('//*[@id="elevation-adjusted-help"]').click()
    driver.find_element_by_xpath('/html/body/div[6]/div[1]/a').click()
    time.sleep(4)

def elevation_check(activity,thresh=0.01):
    elevation = activity['total_elevation_gain']
    distance = activity['distance']
    if distance == 0:
        return -1
    ratio = float(elevation) / float(distance) 
    if ratio > thresh:
        print(activity['id'], activity['name'], elevation, distance, ratio)
        return activity['id']
    else:
        return -1

def elevation_fix(driver,activities,thresh=0.01):
    site_login(driver)

    for activity in activities:
        try:
            atype = activity['workout_type']
            result = elevation_check(activity,thresh) 

            if result > 0 and (atype is None or atype == 0):
                correct_elevation(driver,activity['id'])
                continue
        except:
            continue

def name_fix(activities,tokens):
    app = Nominatim(user_agent="strava-fix")

    for activity in activities:
        name = activity['name']

        # convert distance from meters to miles
        distance = activity['distance']/1609.344

        if re.match(r'.*?(Morning|Lunch|Afternoon|Evening|Night) Run.*', name):  #name == 'Morning Run':

            if activity['start_latlng'] is None:
                continue

            dt = datetime.strptime(activity['start_date'], '%Y-%m-%dT%H:%M:%SZ')

            print(name, dt)

            try:
                (lat, lon) = activity['start_latlng']
            except ValueError as e:
                (lat, lon) = (0,0)

            coordinates = f"{lat}, {lon}"
            location = app.reverse(coordinates, language='en').raw
            try:
                location = app.reverse(coordinates, language='en').raw
                #print(location)

                try: 
                    aname = '{}/{}/{} {}, {} ({}) - {:4.2f} miles'.format( dt.month, dt.day, dt.year, 
                            location['address']['city'], location['address']['state'], 
                            location['address']['municipality'], distance)
                except KeyError as e:
                    try:
                        aname = '{}/{}/{} {}, {} - {:4.2f} miles'.format( dt.month, dt.day, dt.year, 
                                location['address']['city'], location['address']['state'], distance)
                    except KeyError as e:
                        aname = '{}/{}/{} Unknown - {:4.2f} miles'.format( dt.month, dt.day, dt.year, distance)

            except:
                aname = '{}/{}/{} {}, {} - {:4.2f} miles'.format( dt.month, dt.day, dt.year, 
                        'Chicago', 'Illinois', distance)

            print(aname)
            activity['name'] = aname

            print("Updating {}".format(activity['id']))
            #print(activity)
            access_token = tokens['access_token']
            headers = {'Authorization': 'Bearer ' + access_token, "Content-Type": "application/json"}
            url = 'https://www.strava.com/api/v3/activities/{}'.format(activity['id'])
            activity_json = json.dumps(activity)
            response = requests.put(url, data=activity_json, headers=headers)
            print(response.content)
            time.sleep(1)


if __name__ == '__main__':

    ###############################
    # Get Auth Tokens from File
    # Refresh if needed

    tokens = get_tokens()

    ###############################
    # Get Activities from JSON file
    activities = get_activities_from_file('data/activities0.json')

    ###############################
    # Activity Name Fix

    name_fix(activities,tokens)

    ###############################
    # Fix the Elevations - Chicago is Flat, so we look for a pretty low threshold

    driver = webdriver.Firefox()
    elevation_fix(driver,activities)
