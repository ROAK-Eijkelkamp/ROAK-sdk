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
ROAK_BASE_URL = "https://dev.roak.com" 

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
site = roak.get_site_by_name(SITE_NAME)

wells = site.get_wells()
print([well.name for well in wells])
assert len(wells) >= 5

print(wells[0].get_attributes())
print(wells[0].refresh_attributes())
print(wells[0].get_last_values())