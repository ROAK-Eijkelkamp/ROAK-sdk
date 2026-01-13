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

all_rigs = project.get_assets("borehole")


print(all_rigs)
