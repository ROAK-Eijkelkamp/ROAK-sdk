# I am a data scientist at a dirlling company.
# I am interested in getting data from two sets of boreholes to compare the drilling efficiency.
# hij wil data hebben op een manier die hij zelf kan anyaliseren (op rawe data)

import roak_sdk
import os
from datetime import datetime, timedelta
import pandas as pd

TODAY = datetime.today()
LAST_MONTH = TODAY - timedelta(days=30)

# connect
password = os.getenv("ROAK_password")
username = "e.garbov@eijkelkamp.com"
roak_client = roak_sdk.roak(user=username, password=password)

# get all boreholes of the last month that belong to two specific rigs (MWD Test)
rig1_guid = "SOLSA_MWD"
rig2_guid = "5c63cd4b-a2fd-42ab-a5a8-efeb38eeb4af"

# collects one rig's data
rig1 = roak_client.get_rig(guid=rig1_guid)

# get all boreholes inside of the rig and put it in list/array
boreholes_rig1 = rig1.get_boreholes()

borehole_data = boreholes_rig1[0].get_data(end=TODAY, feeds="ALL")
bh = pd.DataFrame(borehole_data)

print(bh[bh["Depth"].notnull()])

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
