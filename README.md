# Strava Utils

Command-line utilities for interacting with Strava.

## Scripts

  * `sweep.py` — main tool. Fetches every activity via the Strava API, finds ones that still have default names ("Morning Run", "Evening Run", etc.), reverse-geocodes each start location, and renames them to `M/D/YYYY City, State (Township) - X.XX miles`. Handles Strava's rate limits automatically (waits to the next 15-minute UTC window on 429).
  * `give_kudos.py` — Playwright-based script that logs in to strava.com and gives kudos to activities on your Following feed. Independent of the API; uses username/password from `conf/account.json`.
  * `stravaauth.py` — library. Loads OAuth tokens from `conf/strava_tokens.json` and refreshes them automatically when expired.

## Requirements

  * Python 3.10+ and the packages: `requests`, `geopy`, `certifi`. For `give_kudos.py`: `playwright` (plus `playwright install firefox`).
  * A **Strava subscription**. As of 2024, Strava restricts third-party API access (activity reads/writes) to subscribers. Without a subscription the API returns `403 Forbidden: {"resource":"Application","field":"Status","code":"Inactive"}`.

## Authorization Setup (OAuth Walkthrough)

You need two files in `conf/`, both derived from `.example` templates:

  * `conf/account.json` — your Strava app credentials
  * `conf/strava_tokens.json` — your OAuth access + refresh tokens

Once `strava_tokens.json` exists, `stravaauth.get_tokens()` refreshes the access token automatically, so the steps below are one-time setup.

### Step 1 — Create a Strava API application

  1. Sign in to Strava and go to https://www.strava.com/settings/api.
  2. Create an application. For "Authorization Callback Domain" enter `localhost` (anything works — we never run a real callback server, we just read the `code` out of the redirect URL).
  3. Copy the **Client ID** and **Client Secret**.

### Step 2 — Create `conf/account.json`

```bash
cp conf/account.json.example conf/account.json
```

Edit it:

```json
{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "username": "",
    "password": ""
}
```

`username`/`password` are only used by `give_kudos.py`; leave them blank if you only care about `sweep.py`.

### Step 3 — Get an authorization code

Visit this URL in a browser, replacing `[CLIENT-ID]` with your Client ID:

```
https://www.strava.com/oauth/authorize?client_id=[CLIENT-ID]&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=read,activity:read_all,activity:write,profile:read_all,read_all
```

  * Keep all scope boxes checked — `activity:write` is required for `sweep.py` to rename activities.
  * After you click "Authorize", the browser redirects to a `localhost` URL that fails to load. That's expected. Copy the `code=` parameter out of the URL bar. It expires quickly, so do Step 4 right away.

### Step 4 — Exchange the code for tokens

```bash
curl -X POST https://www.strava.com/oauth/token \
  -F client_id=YOUR_CLIENT_ID \
  -F client_secret=YOUR_CLIENT_SECRET \
  -F code=CODE_FROM_STEP_3 \
  -F grant_type=authorization_code \
  > conf/strava_tokens.json
```

Verify:

```bash
cat conf/strava_tokens.json | python3 -m json.tool
```

You should see `access_token`, `refresh_token`, and `expires_at`. If you see `errors` instead, the code expired — redo Step 3.

### Step 5 — Smoke test

```bash
python3 -c "from stravaauth import get_tokens; import requests; t=get_tokens(); r=requests.get('https://www.strava.com/api/v3/athlete', headers={'Authorization':'Bearer '+t['access_token']}); print(r.status_code, r.json().get('firstname'))"
```

`200 <your name>` means you're good. If you see `403 Forbidden: Application Status Inactive`, check your Strava subscription.

## Usage

```bash
python3 sweep.py
```

Pages through all activities, then renames every default-titled Run. Runs without GPS coordinates (treadmill, etc.) are skipped. Progress prints per activity. On a Strava 429, the script sleeps until the next 15-minute UTC boundary and continues.

## Notes

  * The refresh token in `conf/strava_tokens.json` is what keeps everything working long-term. Keep that file out of version control (already covered by `.gitignore`; the file is effectively a password).
  * Strava rate limits: 100 requests / 15-min rolling window, 1000 / day. `sweep.py` paces at ~10s per rename to stay comfortably under the window ceiling.
  * For a full historical archive of your activities (including original GPX/FIT files), request the bulk data export from Strava: Settings → My Account → Download or Delete Your Account → Get Started → Request your archive. It arrives within a day.
  * An alternative OAuth walkthrough is [here](https://medium.com/@annthurium/getting-started-with-the-strava-api-a-tutorial-f3909496cd2d).
