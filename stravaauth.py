#!/usr/bin/env python3

"""Strava OAuth token loading + auto-refresh."""

import os
import time
import json
import requests

account_file = 'account.json'
token_file = 'strava_tokens.json'
base_path = os.path.dirname(os.path.realpath(__file__))


def get_account(path='{}/conf'.format(base_path)):
    with open(path + '/' + account_file) as f:
        return json.load(f)


def get_tokens(path='{}/conf'.format(base_path)):
    tf = path + '/' + token_file

    with open(tf) as f:
        strava_tokens = json.load(f)

    if strava_tokens['expires_at'] < time.time():
        account = get_account(path)
        res = requests.post(
            url='https://www.strava.com/oauth/token',
            data={
                'client_id': account['client_id'],
                'client_secret': account['client_secret'],
                'grant_type': 'refresh_token',
                'refresh_token': strava_tokens['refresh_token'],
            },
        )
        res.raise_for_status()
        strava_tokens = res.json()
        with open(tf, 'w') as f:
            json.dump(strava_tokens, f)

    return strava_tokens
