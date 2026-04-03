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

START_DATE = datetime.strptime("2023-03-15", "%Y-%m-%d").replace(tzinfo=timezone.utc)
END_DATE = datetime.strptime("2023-03-17", "%Y-%m-%d").replace(tzinfo=timezone.utc)

PROJECT_NAME = "GWM Beta Test"
WELL_GUID = "075fcf56-fbe5-4a75-8fbe-70276aed9593"

# connect to roak
roak = roak_sdk.Roak(
    username=ROAK_USERNAME,
    password=ROAK_PASSWORD,
)   

# get all (asset) types
asset_types = roak.get_asset_types()
assert len(asset_types) >= 50

# get all projects and verify that there is at least 17
projects = roak.get_projects()
assert len(projects) >= 17

# get a specific project
project = roak.get_project_by_name(PROJECT_NAME)

# verify that the number of assets in this project is at least 4
assets = project.get_assets()
assert len(assets) >= 4

# get well data for a specific well in that project
well = project.get_well_by_guid(WELL_GUID)

# get data for that well
well_data = well.get_data(
    start_datetime=START_DATE,
    end_datetime=END_DATE,
)

# check if well data has 192 records
assert len(well_data[0]["readings"]) == 192

# get all feeds for a well and check that there are 46 feeds
feeds = well.get_feeds()
assert len(feeds) == 46

print(f"Successfully retrieved data for well '{well.name}' in project '{project.name}'.")