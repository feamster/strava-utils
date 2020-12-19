#!/usr/bin/env python3

import requests
import json
import time

# Step 1: url for when you need new code
# https://www.strava.com/oauth/authorize?scope=read,activity:read_all,activity:write,profile:read_all,read_all&client_id=58450&response_type=code&redirect_uri=http://localhost:8888/strava-call-back.php&approval_prompt=force

# Step 2: get access token
# curl -X POST https://www.strava.com/oauth/token -F client_id=[client_id] -F client_secret=[client_secret] -F code=[CODE from URL] -F grant_type=authorization_code

# client_id is specific to Strava username 
newTokenUrl = "https://www.strava.com/oauth/authorize?scope=read,activity:read_all,profile:read_all,read_all&client_id=&response_type=code&redirect_uri=http://localhost:8888/strava-call-back.php&approval_prompt=force"

###########################

def get_activities(start=1, end=2):

    # pages: 200 results per page, so by default we fetch 20 pages.
    # there is a small bug, outputting "][" in between each JSON dump

    f = open('data/activities0.json', 'w')
    for p in range (start,end):
        print(p)
        #Get activities
        url = "https://www.strava.com/api/v3/activities?access_token="
        pstr = '&page={}&per_page=200'.format(p)

        res = requests.get(url + strava_tokens['access_token'] + pstr)
        data = res.json()

        #Write activities json to my activities json file
        #with open('data/activities4.json', 'w') as activitiesFile:
        #    json.dump(data, activitiesFile)
        json.dump(data,f)
    f.close()

###########################

if __name__ == '__main__':

    #Makes request for latest activity data with new token if expired
    #load token files
    with open('conf/strava_tokens.json') as tokenFile:
        strava_tokens = json.load(tokenFile)
    with open('conf/account.json') as myInfo:
        myInfo = json.load(myInfo)


    #If current token has expired make post request for new one
    if strava_tokens['expires_at'] < time.time():
        res = requests.post(
            url = 'https://www.strava.com/oauth/token',
            data = {
                'client_id': myInfo['client_id'],
                'client_secret': myInfo['client_secret'],
                'grant_type': 'refresh_token',
                'refresh_token': strava_tokens['refresh_token'],
                'access_token': strava_tokens['access_token']
                }
        )

        newtokens = res.json()

        #update token file
        with open('conf/strava_tokens.json', 'w') as newStravaTokens:
            json.dump(newtokens, newStravaTokens)
            strava_tokens = newtokens


    get_activities()
