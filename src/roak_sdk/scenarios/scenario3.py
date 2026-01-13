# THIS DOESNT WORK API CANNOT FIND ASSET_TYPE: 'rig' or "GWM_RIG"


import roak_sdk
import os
from datetime import datetime, timedelta

TODAY = datetime.today()
YESTERDAY = TODAY - timedelta(days=1)

# connect
password = os.getenv("ROAK_PASSWORD")
username = "e.garbov@eijkelkamp.com"
roak = roak_sdk.roak(user=username, password=password)  # tenant hier?

# gets a specific project
project = roak.get_project(name="Demo boreholes")

all_rigs = project.get_assets("rig")

# get data per rig
for rig in all_rigs:  # feeds optinal ,leeg = alles
    data = rig.get_data(start=YESTERDAY, end=TODAY, feeds=["Bit Force", "Depth"])
    print(f"Stored data from rig: {rig.name} , {data}")
