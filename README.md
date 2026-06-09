# Strava Utils

Command Line Utilities for interacting with Strava.

## Scripts

  * Main Script
    * `maintain.py` - calls functions in the `fix` library to (1) re-title activities; (2) correct elevation to use Strava elevation (not device) if elevation is off.

  * Other Scripts

    These can also be called standalone.
    * `get_activities.py` - gets activities from Strava as JSON object(s). By default, retrieves only the most five recent activities.
    * `fix.py` - functions to correct Strava data.

  * Libraries
    * `stravaauth.py` - manages auth tokens, etc.

## Authorization Setup (OAuth Walkthrough)

The scripts read two files in `conf/` that you need to create from the `.example` templates:

  * `conf/account.json` — your Strava app credentials
  * `conf/strava_tokens.json` — your OAuth access + refresh tokens

Once `strava_tokens.json` exists, `stravaauth.get_tokens()` will refresh the access token automatically when it expires, so the steps below only need to be done once.

### Step 1 — Create a Strava API application

  1. Sign in to Strava and go to https://www.strava.com/settings/api.
  2. Create an application. For "Authorization Callback Domain" enter `localhost` (anything works here — we never run a real callback server, we just read the `code` out of the redirect URL).
  3. Copy the **Client ID** and **Client Secret** that Strava shows you.

### Step 2 — Create `conf/account.json`

Copy the example and fill in your client ID and secret:

```bash
cp conf/account.json.example conf/account.json
```

Edit `conf/account.json` so it looks like:

```json
{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "username": "",
    "password": ""
}
```

`username`/`password` are only used by the (currently disabled) Selenium-based `give_kudos.py` flow; leave them blank for normal use.

### Step 3 — Get an authorization code

In a browser, visit the URL below, **replacing `[CLIENT-ID]` with your Client ID from Step 1**:

```
https://www.strava.com/oauth/authorize?client_id=[CLIENT-ID]&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=read,activity:read_all,activity:write,profile:read_all,read_all
```

  * Strava will ask you to authorize the app. Make sure the scope boxes (especially `activity:write`) stay checked — `maintenance.py` needs write access to rename activities.
  * After you click "Authorize", the browser will redirect to a `localhost` URL that will fail to load. **That's fine.** Look at the URL bar — it will look like:

    ```
    http://localhost/exchange_token?state=&code=abc123def456...&scope=read,activity:read_all,activity:write,...
    ```

  * Copy the value of the `code=` parameter. You'll use it in the next step. It is single-use and expires quickly, so do Step 4 right away.

### Step 4 — Exchange the code for tokens

Run this `curl` command, substituting your client ID, client secret, and the code from Step 3:

```bash
curl -X POST https://www.strava.com/oauth/token \
  -F client_id=YOUR_CLIENT_ID \
  -F client_secret=YOUR_CLIENT_SECRET \
  -F code=CODE_FROM_STEP_3 \
  -F grant_type=authorization_code \
  > conf/strava_tokens.json
```

Verify `conf/strava_tokens.json` now contains `access_token`, `refresh_token`, and `expires_at`:

```bash
cat conf/strava_tokens.json | python3 -m json.tool
```

If you see an `errors` field instead, the code probably expired — re-run Step 3 to get a fresh one and try again.

### Step 5 — Smoke test

From the repo root:

```bash
python3 get_activities.py
```

This should hit the Strava API, write `data/activities0.json`, and print page numbers. If it succeeds, `python3 maintenance.py` is ready to run.

### Notes

  * After the initial setup, the refresh token in `conf/strava_tokens.json` is what keeps everything working long-term. Keep that file out of version control (it's effectively a password).
  * An alternative walkthrough is [here](https://medium.com/@annthurium/getting-started-with-the-strava-api-a-tutorial-f3909496cd2d).
