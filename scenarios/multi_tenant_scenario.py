import os

import roak_sdk
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# settings
MULTI_TENANT_USERNAME = os.getenv("ROAK_USERNAME")

print(f"Using multi-tenant username: {MULTI_TENANT_USERNAME}")
MULTI_TENANT_PASSWORD = os.getenv("ROAK_PASSWORD")
print(f"Using multi-tenant password: {'*'*(len(MULTI_TENANT_PASSWORD)) if MULTI_TENANT_PASSWORD else None}")
ROAK_MAIN_URL = "https://dev.roak.com"#"https://royaleijkelkamp.roak.com"

if not MULTI_TENANT_USERNAME or not MULTI_TENANT_PASSWORD:
	raise ValueError(
		"MULTI_TENANT_USERNAME and MULTI_TENANT_PASSWORD must be set in your environment or .env file."
	)

# first: try to log in with the multi-tenant user
roak = roak_sdk.Roak(
	username=MULTI_TENANT_USERNAME,
	password=MULTI_TENANT_PASSWORD,
	base_url=ROAK_MAIN_URL,
	debug=True,  # enable debug logging to see request details
)

# simple authentication/access check
asset_types = roak.get_asset_types()
assert len(asset_types) >= 1

# multi-tenant users should generally see multiple customers
customers = roak.get_customers()
assert len(customers) >= 2

print(f"Authenticated as multi-tenant user. Customers found: {len(customers)}")
print("Sample customers:", [customer.name for customer in customers[:5]])

# verify we can drill down into customer-scoped data
first_customer = customers[0]
wells = first_customer.get_wells()
print(f"Customer '{first_customer.name}' has {len(wells)} wells.")

# second, try to log in not caring about which tenant
roak_no_tenant = roak_sdk.Roak(
	username=MULTI_TENANT_USERNAME,
	password=MULTI_TENANT_PASSWORD,
	base_url=ROAK_MAIN_URL,
	debug=True,
)
asset_types_no_tenant = roak_no_tenant.get_asset_types()
assert len(asset_types_no_tenant) >= 1