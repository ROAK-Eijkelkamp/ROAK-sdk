import os

import roak_sdk
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# settings
ROAK_USERNAME = os.getenv("ROAK_USERNAME")
ROAK_PASSWORD = os.getenv("ROAK_PASSWORD")
ROAK_BASE_URL = os.getenv("ROAK_BASE_URL", "https://dev.roak.com")
CUSTOMER_NAME = os.getenv("ROAK_CUSTOMER_NAME", "Royal Eijkelkamp")

if not ROAK_USERNAME or not ROAK_PASSWORD:
    raise ValueError("ROAK_USERNAME and ROAK_PASSWORD must be set in your environment or .env file.")

# connect to roak
roak = roak_sdk.Roak(
    username=ROAK_USERNAME,
    password=ROAK_PASSWORD,
    base_url=ROAK_BASE_URL,
)

# fetch one customer and count wells
customer = roak.get_customer_by_name(CUSTOMER_NAME)
wells = customer.get_wells()
well_count = len(wells)

print(f"Customer '{customer.name}' has {well_count} wells.")

wells_with_data = 0
for well in wells:
    data = well.get_data(feeds=["diverPressure",]) # empty feed list means "use defaults"
    #import pdb; pdb.set_trace()
    if data[0]["readings"]:
        wells_with_data += 1
print(f"Customer '{customer.name}' has {wells_with_data} wells with data.")

