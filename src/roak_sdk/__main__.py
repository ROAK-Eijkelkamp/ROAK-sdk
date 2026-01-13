"""
This module exists for test/demo reasons
Parts/All of it may be removed later
"""

from roak_sdk.auth import Auth
from roak_sdk.roak_error import AuthenticationError
from roak_sdk.clients.well_client import WellClient
from roak_sdk.semantics.assets.well import Well
from roak_sdk.clients.rig_client import RigClient
from roak_sdk.semantics.assets.rig import Rig
from roak_sdk.semantics.assets.borehole import Borehole
from roak_sdk.clients.asset_client import AssetClient
from roak_sdk.clients.project_client import ProjectClient
from roak_sdk.clients.generic_asset_client import GenericAssetClient
from roak_sdk.semantics.assets.generic_asset import GenericAsset
import os
from datetime import datetime, timedelta

import pandas as pd
from pprint import pprint

# --- Constants ---
TYPE_GUIDS = ["GWM_WELL", "MWD_BOREHOLE", "MWD_RIGS", "ED_GENERIC_ASSET"]

type_guid = "ED_GENERIC_ASSET"

WELL_GUID = "548006ef-28bd-4b0e-9f17-8234e1db9f64"
RIG_GUID = "5c63cd4b-a2fd-42ab-a5a8-efeb38eeb4af"
BOREHOLE_GUID = "2422c5aa-5bbd-490a-b278-48eb22966951"


# gets well feeds
def run_well_feeds(client):
    feeds = client.get_feeds(WELL_GUID)
    print("well feeds:")
    pprint(feeds)


# --- Example: Well Data (all feeds default unless specified wich ALSO time is default 24h if left empty) ---
def run_well_example(client):
    well = Well(WELL_GUID, "TestWell1", client)
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=1)
    data = well.get_data(feeds=["wellLength"], start=start_dt, end=end_dt)
    pprint(data)


# ---Example: Show rig Feeds
def run_rig_feeds(client):
    data = client.get_feeds(RIG_GUID)  # get_borehole_params
    print("Rig feeds:")
    pprint(data)


def run_rig_example(client):
    rig = Rig(RIG_GUID, "Rignaam", client)
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=1)
    data = rig.get_data(feeds=["Depth", "Bit Force"], start=start_dt, end=end_dt)
    pprint(data)


# --- Example: Depth Data) ---
def run_depth_example(client):
    borehole = Borehole(RIG_GUID, "Borehole2", client)
    data = borehole.get_data(feeds="ALL")
    print(data)


# --- Example: Fetch all assets ---
def run_all_assets_example(client):
    all_assets = client.get_all_assets_per_type(TYPE_GUIDS)
    print("All Assets:")
    df_assets = pd.DataFrame(all_assets)
    print(df_assets)


# --- Example: Fetch assets for one fixed type ---
def run_fixed_asset_example(client):
    borehole_assets = client.get_assets_base(type_guid)
    print("Assets:")
    df_borehole = pd.DataFrame(borehole_assets)
    print(df_borehole)


# --- Example: Fetch all types of assets ---
def run_asset_types_example(client):
    asset_types = client.get_asset_types()
    print("Asset Types:")
    pprint(asset_types)


# --- Example: get project via name leave empty for all owned projects
def run_get_project(client):
    data = client.get_project("Gerard Test")
    print(data)


GENERIC_GUID = "5b7d3c59-893e-4c22-95b0-f9a4597ee34e"


def run_test(client):
    asset = GenericAsset(GENERIC_GUID, "Test Generic Asset", client)
    data = asset.get_data(feeds="ALL")
    # data = client.get_feeds(GENERIC_GUID)
    # print("GENERIC_ASSET feeds:")
    print(data)


if __name__ == "__main__":
    # --- Authenticate ---
    PASSWORD = os.getenv("ROAK_PASSWORD")
    USERNAME = "e.garbov@eijkelkamp.com"
    auth = Auth(USERNAME, PASSWORD, base_url=None)
    try:
        headers = auth.authenticate()
    except AuthenticationError as e:
        print("Authentication failed:", e)
        exit(1)

    # --- Clients ---
    well_client = WellClient(headers)
    rig_client = RigClient(headers)
    asset_client = AssetClient(headers)
    project_client = ProjectClient(headers)
    generic_asset_client = GenericAssetClient(headers)

    # --- Choose which example to run happens when code runs ---
    choice = (
        input(
            "Which example to run? (well/wellfeeds/rigfeeds/rig/depth/all assets/fixed asset/asset types/project): "
        )
        .strip()
        .lower()
    )

    if choice == "well":
        run_well_example(well_client)
    elif choice == "wellfeeds":
        run_well_feeds(well_client)
    #   scenario_one(well_client, asset_client, TYPE_GUIDS[0])
    elif choice == "rigfeeds":
        run_rig_feeds(rig_client)
    elif choice == "rig":
        run_rig_example(rig_client)
    #   elif choice == "test2":
    #   scenario_two(asset_client, rig_client)
    elif choice == "depth":
        run_depth_example(rig_client)
    elif choice == "all assets":
        run_all_assets_example(asset_client)
    elif choice == "fixed asset":
        run_fixed_asset_example(asset_client)
    elif choice == "asset types":
        run_asset_types_example(asset_client)
    elif choice == "project":
        run_get_project(project_client)
    elif choice == "test":
        run_test(generic_asset_client)
    else:
        print("Invalid choice.")
