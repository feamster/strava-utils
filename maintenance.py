#!/usr/bin/env python3

from stravaauth import get_tokens, get_account, site_login
from get_activities import get_activities
from fix import name_fix, elevation_fix

from selenium import webdriver

if __name__ == '__main__':

    ###############################
    # Get Auth Tokens from File
    # Refresh if needed

    tokens = get_tokens()

    ###############################
    # Get Activities from JSON file
    activities = get_activities(tokens)

    ###############################
    # Activity Name Fix

    name_fix(activities,tokens)

    ###############################
    # Fix the Elevations - Chicago is Flat, so we look for a pretty low threshold

    driver = webdriver.Firefox()
    elevation_fix(driver,activities)
