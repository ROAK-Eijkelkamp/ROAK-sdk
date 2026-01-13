import roak_sdk
import os
from datetime import datetime, timedelta

roak = roak_sdk.roak(user="e.garbov@eijkelkamp.com", password="Hummer2002!!")

project = roak.get_project(name="Demo boreholes")

TODAY = datetime.today()
YESTERDAY = TODAY - timedelta(days=1)

all_rigs = project.get_assets("borehole")

for borehole in all_rigs:
    data = borehole.get_data(start=YESTERDAY, end=TODAY, feeds=["Depth"])
    depth = next((feed for feed in data if feed["name"] == "Depth"), None)
