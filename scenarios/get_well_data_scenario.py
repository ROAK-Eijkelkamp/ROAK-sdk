# I am an IT expert at company with wells (gemeente / provincie / waterschap)
# My goal is to every day get all data of the previous day and synchronize is to my own database / warehouse.

import roak_sdk
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# settings
ROAK_USERNAME = os.getenv("ROAK_USERNAME")
ROAK_PASSWORD = os.getenv("ROAK_PASSWORD")
ROAK_BASE_URL = "https://dev.roak.com" 

START_DATE = datetime.strptime("2026-03-01", "%Y-%m-%d").replace(tzinfo=timezone.utc)
END_DATE = datetime.strptime("2026-03-02", "%Y-%m-%d").replace(tzinfo=timezone.utc)

PROJECT_NAME = "Gerard Test"
WELL_GUID = "548006ef-28bd-4b0e-9f17-8234e1db9f64"

# connect to roak
roak = roak_sdk.Roak(
    username=ROAK_USERNAME,
    password=ROAK_PASSWORD,
    base_url=ROAK_BASE_URL,
)   

# get all (asset) types
asset_types = roak.get_asset_types()
print([at['guid'] for at in asset_types])
assert len(asset_types) >= 60

# get all projects and verify that there is at least 154
projects = roak.get_projects()
assert len(projects) >= 154

# get a specific project
project = roak.get_project_by_name(PROJECT_NAME)
print(project._data)

# verify that the number of assets in this project is at least 29
assets = project.get_assets()
assert len(assets) > 28

# get well data for a specific well in that project
well = project.get_well_by_guid(WELL_GUID)

# get data for that well
well_data = well.get_data(
    start_datetime=START_DATE,
    end_datetime=END_DATE,
)

# check if well data has 144 records
assert len(well_data[0]["readings"]) == 144

# well_data = well.get_data(
#     start_datetime=START_DATE,      
#     end_datetime=END_DATE
# )

# get all feeds for a well and check that there are 46 feeds
feeds = well.get_feeds()
assert len(feeds) == 46
