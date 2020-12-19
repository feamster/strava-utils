#!/usr/bin/env python3

#########
# stravaauth.py


import time
import json
import requests

from selenium import webdriver

account_file = 'account.json'
token_file = 'strava_tokens.json'

def get_account(path='conf'):
    af = path + '/' + account_file
    with open(af) as account:
        account = json.load(account)
    return account 


def get_tokens(path='conf'):

    tf = path + '/' + token_file

    #load token files
    with open(tf) as tokenFile:
        strava_tokens = json.load(tokenFile)

    # get client_id and client_secret
    account = get_account(path)

    # If current token has expired make post request for new one
    if strava_tokens['expires_at'] < time.time():
        res = requests.post(
            url = 'https://www.strava.com/oauth/token',
            data = {
                'client_id': account['client_id'],
                'client_secret': account['client_secret'],
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

    return strava_tokens


def site_login(driver):
    account = get_account()

    driver.get("https://strava.com/login")
    driver.find_element_by_id('email').send_keys(account['username'])
    driver.find_element_by_id('password').send_keys(account['password'])
    driver.find_element_by_id('login-button').click()


#######################
# Step 1: url for when you need new code
# https://www.strava.com/oauth/authorize?scope=read,activity:read_all,activity:write,profile:read_all,read_all&client_id=58450&response_type=code&redirect_uri=http://localhost:8888/strava-call-back.php&approval_prompt=force

# Step 2: get access token
# curl -X POST https://www.strava.com/oauth/token -F client_id=[client_id] -F client_secret=[client_secret] -F code=[CODE from URL] -F grant_type=authorization_code

# client_id is specific to Strava username 
# newTokenUrl = "https://www.strava.com/oauth/authorize?scope=read,activity:read_all,profile:read_all,read_all&client_id=&response_type=code&redirect_uri=http://localhost:8888/strava-call-back.php&approval_prompt=force"


