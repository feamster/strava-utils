#!/usr/bin/env python3

from stravaauth import get_tokens

import os
import sys
import requests
import json
import time

###########################

base_path = os.path.dirname(os.path.realpath(__file__))

def get_activities(strava_tokens, per_page=5, start=1, end=2, actfile='{}/data/activities0.json'.format(base_path)):

    # pages: 200 results per page, so by default we fetch 20 pages.
    # there is a small bug, outputting "][" in between each JSON dump
    # should append array and then dump at the end.

    data = []

    # Writing the latest into an JSON file
    f = open(actfile, 'w')

    for page in range (start,end):
        print(page)

        # Get activities
        url = "https://www.strava.com/api/v3/activities?access_token="
        pstr = '&page={}&per_page={}'.format(page,per_page)

        res = requests.get(url + strava_tokens['access_token'] + pstr)
        data = res.json()

        # Write activities json to my activities json file
        json.dump(data,f)
    f.close()

    # return the last page of activities as an array of JSON dicts
    return data

###########################

if __name__ == '__main__':

    tokens = get_tokens()
    get_activities(tokens)
