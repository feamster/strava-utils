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

## Authorization Setup

1. Create a Strava App [from your account](https://strava.com/settings/api/). You will need the client ID and client secret later.

2. Enter the URL below (modified with your Strava client ID) to get an authorization token with the appropriate scope. The Strava API explains calls and scopes. We ask for read and write here because the scripts do write to activities (updating activity names, for example).

  * Need client ID from Strava

  `https://www.strava.com/oauth/authorize?scope=read,activity:read_all,activity:write,profile:read_all,read_all&client_id=[CLIENT-ID]&response_type=code&redirect_uri=http://localhost:8888/strava-call-back.php&approval_prompt=force`

3. Get an access token
`curl -X POST https://www.strava.com/oauth/token -F client_id=[client_id] -F client_secret=[client_secret] -F code=[CODE from URL] -F grant_type=authorization_code > conf/strava_tokens.json`

Once you have the initial tokens, the scripts will use the refresh token to fetch new tokens once these expire. An alternative walkthrough is [here](https://medium.com/@annthurium/getting-started-with-the-strava-api-a-tutorial-f3909496cd2d).


