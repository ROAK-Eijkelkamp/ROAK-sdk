# I am a data scientist at a drilling company.
# I am interested in getting data from two sets of boreholes to compare the drilling efficiency.

import roak_sdk
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# settings
ROAK_USERNAME = os.getenv("ROAK_USERNAME")
ROAK_PASSWORD = os.getenv("ROAK_PASSWORD")

START_DATETIME = datetime(2023, 7, 21, tzinfo=timezone.utc)
END_DATETIME = datetime(2023, 7, 22, tzinfo=timezone.utc)

RIG_NAME = "42823101test"
BOREHOLE_NAME = "21_7_field_1"

# connect
password = os.getenv("ROAK_PASSWORD")
username = os.getenv("ROAK_USERNAME")

# connect to roak
roak = roak_sdk.Roak(
    username=ROAK_USERNAME,
    password=ROAK_PASSWORD,
    debug=True,  # enable debug logging to see request details
)   

# do not timeout, as some of the data requests in this scenario can be large and take a while to complete
roak.set_request_timeout(-1)

# get the rig. Setting allow_first_match means that the program does not crash if you have two rigs of the same name
rig = roak.get_rig_by_name(RIG_NAME)

boreholes = rig.get_boreholes()
assert len(boreholes) >= 30

# collects one rig's data
borehole = rig.get_borehole_by_name(BOREHOLE_NAME)
feeds = borehole.get_feeds()
assert len(feeds) >= 3

# you can get specific data by setting the feeds
feeds = ["Rotation Pressure", "Torque"]
data = borehole.get_data(feeds=feeds, start_datetime=START_DATETIME, end_datetime=END_DATETIME)
assert len(data) == 2 # two feeds in the period

data = rig.get_data(start_datetime=START_DATETIME, end_datetime=END_DATETIME)
assert len(data) == 9 # 2 feeds in the period

depth_data = borehole.get_depth_data()
df = pd.DataFrame(depth_data)
print(df.head())

# Example result
"""
            timestamp Inclination x Inclination y Pulldown Pressure Pullup Pressure Rotation Pressure Sonic Pressure Running Status  ... Rotation Speed Sonic Frequency  Torque Total operating hours Total sonic hours Drilling fluid used Oil used Penetration Speed
556     1731077070974           NaN           NaN             109.0         107.625            41.275          141.0            NaN  ...            NaN             NaN     NaN                   NaN               NaN                 NaN      NaN               NaN
559     1731077071153           NaN           NaN           108.825          119.75             41.15        138.525            NaN  ...            NaN             NaN     NaN                   NaN               NaN                 NaN      NaN               NaN
563     1731077071328           NaN           NaN               NaN          116.35            41.925            NaN            NaN  ...            NaN             NaN     NaN                   NaN               NaN                 NaN      NaN               NaN
566     1731077071484           NaN           NaN            113.35           122.1               NaN          155.3            NaN  ...            NaN             NaN     NaN                   NaN               NaN                 NaN      NaN               NaN
568     1731077071603           NaN           NaN             110.6         120.475              41.5         155.95            NaN  ...            NaN             NaN     NaN                   NaN               NaN                 NaN      NaN               NaN
...               ...           ...           ...               ...             ...               ...            ...            ...  ...            ...             ...     ...                   ...               ...                 ...      ...               ...
175765  1732203143163           1.0           0.3             3.575             0.0             0.275          0.975        started  ...        0.00000         0.00000    4.32              610.2500          15.55151                 NaN      NaN               NaN
178732  1736513465587           0.9           0.4             3.575             0.0               0.3            1.0        started  ...        0.00000         0.00000    4.71              610.2500          15.55151                 NaN      NaN               NaN
183272  1736514036853           1.0           0.3             3.525             0.0             0.275            1.0        started  ...        0.00000         0.00000    4.32                   NaN          15.55151                 NaN      NaN               NaN
186857  1738331718311           0.9           0.4               0.0             0.0               0.0            0.0        started  ...        0.00000         0.00000    0.00               -0.1000          15.55151                 NaN      NaN               NaN
186858  1738331719324
"""
