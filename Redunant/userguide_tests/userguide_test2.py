import roak_sdk
from datetime import datetime, timedelta
import os

username = "e.garbov@eijkelkamp.com"
password = os.getenv("ROAK_PASSWORD")

roak = roak_sdk.roak(user=username, password=password)

project = roak.get_project(name="Gerard Test")

TODAY = datetime.today()
YESTERDAY = TODAY - timedelta(days=1)

all_wells = project.get_assets("well")


for well in all_wells:
    data = well.get_data(
        start=YESTERDAY,
        end=TODAY,
        feeds=["waterLevelReference", "diverPressure"],
    )

    print(f"{well.name}, {data}")
