#!/usr/bin/env python3

from geopy.geocoders import Nominatim

app = Nominatim(user_agent="strava-fix")
(lat, lon) = [41.79334, -87.591213]
coordinates = f"{lat}, {lon}"
location = app.reverse(coordinates, language='en').raw
print(location)
