# I am an IT expert at company with wells (gemeente / provincie / waterschap)
# My goal is to every day get all data of the previous day and synchronize is to my own database / warehouse.


import roak_sdk
import os
from datetime import datetime, timedelta

TODAY = datetime.today()
YESTERDAY = TODAY - timedelta(days=1)

# connect
password = os.getenv("ROAK_PASSWORD")
username = "e.garbov@eijkelkamp.com"
roak = roak_sdk.roak(
    user=username, password=password, base_url="https://dev.roak.com"
)  # tenant hier?

# gets a specific project
project = roak.get_project(name="Gerard Test")

all_wells = project.get_assets("well")

# get data per well
for well in all_wells:  # feeds optinal ,leeg = alles
    data = well.get_data(
        start=YESTERDAY, end=TODAY, feeds=["waterLevelReference", "diverPressure"]
    )
    print(f"Stored data from well: {well.name} , {data}")
