# same as get_well_data_scenario.py but then through a site

# import necessary modules and classes
from roak_sdk.roak import Roak
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# settings
ROAK_USERNAME = os.getenv("ROAK_USERNAME")
ROAK_PASSWORD = os.getenv("ROAK_PASSWORD")

# set the location of the roak instance to connect to, especially if you are using a tenant on another base url than the main roak.com domain
ROAK_BASE_URL = os.getenv("ROAK_BASE_URL", "https://royaleijkelkamp.roak.com") 

START_DATE = datetime.strptime("2024-06-01", "%Y-%m-%d")
END_DATE = datetime.strptime("2024-06-02", "%Y-%m-%d")

SITE_NAME = "Home"

# connect to roak
roak = Roak(
    username=ROAK_USERNAME,
    password=ROAK_PASSWORD,
    base_url=ROAK_BASE_URL,
)   

# get a specific site
# Setting allow_first_match means that the program does not crash if you have two sites of the same name. 
# This is just for demo purposes, in production code you should make sure site names are unique 
# or use a different method to get the site you want to work with (e.g. by guid)
site = roak.get_site_by_name(SITE_NAME, allow_first_match=True)

# get all the wells of that site and check that there are at least 2
wells = site.get_wells()
assert len(wells) >= 2

# The initial call to get_attributes only gets a limited set of attributes.
# If we refresh the attributes, we get the full set
small_set_of_attributes = wells[0].get_attributes()
assert len(small_set_of_attributes) == 6

larger_set_of_attributes = wells[0].refresh_attributes()
assert len(larger_set_of_attributes) == 42

# from that moment onwards, we get this full set on a get_attributes() call
assert len(wells[0].get_attributes()) == 42

# Get last data on the well
last_data = wells[0].get_last_values() 
assert len(last_data) >= 46

print(f"Successfully retrieved data and attributes for well '{wells[0].name}' in site '{site.name}'.")