# I am a user that has a license with only API access.  I know my device_ids, but have no wells.
# I want for each modem to get all data of the previous day.

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

START = datetime(2026, 1, 29, tzinfo=timezone.utc)
END = datetime(2026, 1, 31, tzinfo=timezone.utc)

MODEM_GUID_300 = "43501505"
MODEM_GUID_400 = "51418045"
DIVER = "FY747"

# connect to roak
roak = roak_sdk.Roak(
    username=ROAK_USERNAME,
    password=ROAK_PASSWORD,
    base_url=ROAK_BASE_URL,
)   

# get all modems
#modems = roak.get_modems()
#assert len(modems) >= 63

# works for pro 400
modem_400 = roak.get_modem_by_guid(MODEM_GUID_400)
print([key for key in modem_400.get_attributes()])

data = modem_400.get_data_through_children(
    feeds=["diverPressure", "diverTemperature", "baroPressure", "baroTemperature"],
    start_datetime=START,
    end_datetime=END,
)
assert len(data) == 3 # 3 children with data in the period

children = modem_400.get_children()
diver = [x for x in children if x.name == DIVER][0]
data = diver.get_data(
    feeds=["diverPressure", "diverTemperature"],
    start_datetime=START,
    end_datetime=END,
)
assert len(data) == 2 # diver has data in the period fopr both feeds


# works for pro 300
modem_300 = roak.get_modem_by_guid(MODEM_GUID_300)
print(modem_300.get_attributes())
data = modem_300.get_data_through_children(
    feeds=["diverPressure", "diverTemperature", "baroPressure", "baroTemperature"],
    start_datetime=START,
    end_datetime=END,
)
assert len(data) == 2 # 2 children with data in the period