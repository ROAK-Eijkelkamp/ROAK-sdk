import roak_sdk

# Replace with your credentials
username = "e.garbov@eijkelkamp.com"
password = "Hummer2002!!"

# Connect to ROAK
roak = roak_sdk.roak(user=username, password=password)

# =========================
# Example: Borehole
# =========================
# borehole_guid = "2422c5aa-5bbd-490a-b278-48eb22966951"

# borehole = roak.get_borehole(borehole_guid)

# # Get all feeds
# borehole_feeds = borehole.get_feeds()

# print("Borehole feeds:")
# for feed in borehole_feeds:
#     print(feed)

# =========================
# Example: Rig
# =========================
rig_guid = "5c63cd4b-a2fd-42ab-a5a8-efeb38eeb4af"

rig = roak.get_rig(rig_guid)

# Get all feeds
rig_feeds = rig.get_feeds()


print(rig_feeds)
