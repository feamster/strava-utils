#!/usr/bin/env python3
"""One-shot: fetch all activities, rename defaults, respect Strava rate limits.

Strava non-app rate limit: 100 requests / 15-min rolling window, 1000 / day.
We pace at ~10s per rename (~90/15min) and retry once on 429 by sleeping to
the next quarter-hour boundary.
"""

import json, re, time, ssl, certifi, requests
from datetime import datetime, timezone
from geopy.geocoders import Nominatim
from stravaauth import get_tokens

DEFAULT_RE = re.compile(r'.*?(Morning|Lunch|Afternoon|Evening|Night) Run.*')
STRAVA_API = 'https://www.strava.com/api/v3'


def fetch_all(tokens, per_page=200):
    activities, page = [], 1
    while True:
        r = requests.get(
            f'{STRAVA_API}/athlete/activities',
            headers={'Authorization': 'Bearer ' + tokens['access_token']},
            params={'page': page, 'per_page': per_page},
        )
        if r.status_code == 429:
            sleep_until_next_window()
            continue
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        activities.extend(batch)
        print(f'  page {page}: +{len(batch)} (total {len(activities)})')
        page += 1
        time.sleep(1)
    return activities


def sleep_until_next_window():
    now = datetime.now(timezone.utc)
    minute = (now.minute // 15 + 1) * 15
    if minute == 60:
        target = now.replace(minute=0, second=5, microsecond=0)
        target = target.replace(hour=(now.hour + 1) % 24)
    else:
        target = now.replace(minute=minute, second=5, microsecond=0)
    wait = (target - now).total_seconds()
    print(f'  Rate limit hit. Sleeping {int(wait)}s until {target.isoformat()}...')
    time.sleep(wait)


def build_name(activity, geocoder):
    dt = datetime.strptime(activity['start_date'], '%Y-%m-%dT%H:%M:%SZ')
    distance = activity['distance'] / 1609.344
    if not activity.get('start_latlng'):
        return None
    try:
        lat, lon = activity['start_latlng']
    except ValueError:
        return None
    if lat == 0 and lon == 0:
        return None
    time.sleep(1)  # Nominatim rate limit
    try:
        addr = geocoder.reverse(f'{lat}, {lon}', language='en').raw['address']
    except Exception as e:
        print(f'  Geocode failed ({type(e).__name__}), using Chicago fallback')
        return f'{dt.month}/{dt.day}/{dt.year} Chicago, Illinois - {distance:4.2f} miles'
    city = addr.get('city') or addr.get('town') or addr.get('village') or addr.get('hamlet')
    state = addr.get('state')
    muni = addr.get('municipality')
    if city and state and muni:
        return f'{dt.month}/{dt.day}/{dt.year} {city}, {state} ({muni}) - {distance:4.2f} miles'
    if city and state:
        return f'{dt.month}/{dt.day}/{dt.year} {city}, {state} - {distance:4.2f} miles'
    return f'{dt.month}/{dt.day}/{dt.year} Unknown Location - {distance:4.2f} miles'


def rename(activity, new_name, tokens):
    headers = {'Authorization': 'Bearer ' + tokens['access_token'],
               'Content-Type': 'application/json'}
    url = f'{STRAVA_API}/activities/{activity["id"]}'
    return requests.put(url, data=json.dumps({'name': new_name}), headers=headers)


if __name__ == '__main__':
    tokens = get_tokens()
    print('Fetching all activities...')
    activities = fetch_all(tokens)
    print(f'Total activities: {len(activities)}')

    defaults = [a for a in activities if DEFAULT_RE.match(a.get('name') or '')]
    print(f'\nDefault-named Run activities: {len(defaults)}')
    if not defaults:
        raise SystemExit('Nothing to rename.')

    dates = sorted(a['start_date'] for a in defaults)
    print(f'  oldest: {dates[0]}   newest: {dates[-1]}')

    ctx = ssl.create_default_context(cafile=certifi.where())
    geocoder = Nominatim(user_agent='strava-fix', ssl_context=ctx)

    updated = skipped = failed = 0
    for i, activity in enumerate(defaults, 1):
        print(f'\n[{i}/{len(defaults)}] {activity["name"]}, {activity["start_date"]}')
        new_name = build_name(activity, geocoder)
        if not new_name:
            print('  Skipping - no location')
            skipped += 1
            continue
        print(f'  -> {new_name}')

        for attempt in range(2):
            resp = rename(activity, new_name, tokens)
            if resp.status_code == 200:
                print('  ✓ updated')
                updated += 1
                break
            if resp.status_code == 429:
                sleep_until_next_window()
                continue
            print(f'  ✗ {resp.status_code}: {resp.content[:200]}')
            failed += 1
            break
        time.sleep(9)  # ~100 req / 15min ceiling

    print(f'\nDone. updated={updated} skipped={skipped} failed={failed}')
