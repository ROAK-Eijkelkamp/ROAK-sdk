from roak_sdk.clients.base_client import BaseClient
from roak_sdk.auth import DEFAULT_URL
from roak_sdk.clients.base_client import MILLISECONDS_IN_ONE_DAY
import datetime
from typing import Optional
from roak_sdk.semantics.assets.borehole import Borehole
from roak_sdk.semantics.assets.rig import Rig


class RigClient(BaseClient):
    """
    Client for interacting with rig-related data from the ROAK API.

    Provides methods to retrieve rig data, depth data, and associated boreholes.
    Inherits from BaseClient for shared functionality such as time normalization
    and HTTP request handling.
    """

    ASSET_TYPE = {
        "rig": "MWD_RIGS",
        "borehole": "MWD_BOREHOLE",
    }

    def get_rig_data(
        self,
        borehole_guid: str,
        feeds: list[str] | str | None = None,
        start=None,
        end=None,
        time_period=None,
    ):
        rig_asset = Rig(borehole_guid, "Unknown Rig", self)
        return rig_asset.get_data(feeds=feeds, start=start, end=end)

    def get_depth_data_raw(self, borehole_guid: str):
        """
        Fetch raw depth data for a specific borehole.

        Args:
            borehole_guid (str): GUID of the borehole to fetch depth data for.

        Returns:
            dict | list: JSON response containing depth data.
        """
        url = f"{DEFAULT_URL}/api/mwd/boreholes/{borehole_guid}/depthData"
        return self._request(url)

    def get_rig(self, guid: str):
        """
        Instantiate and return a Rig asset object linked to this client.

        Args:
            guid (str): GUID of the rig.

        Returns:
            Rig: A Rig asset instance associated with this client.
        """

        return Rig(guid, "Unknown Rig", self)

    def get_boreholes_for_rig(self, rig_guid: str):
        """
        Retrieve all boreholes associated with a given rig.

        Args:
            rig_guid (str): GUID of the rig.

        Returns:
            list[Borehole]: List of Borehole asset objects belonging to the rig.
        """

        TYPE_GUID = "MWD_BOREHOLE"
        response = self._request(
            f"{DEFAULT_URL}/api/mwd/rigs/{rig_guid}/boreHoles",
            params={"typeGuid": TYPE_GUID},
        )
        # Each item has a "borehole" key that has the actual data
        borehole_assets = [item["borehole"] for item in response if "borehole" in item]

        return [
            Borehole(
                guid=b["guid"],
                name=b.get("name", "Unnamed Borehole"),
                client=self,
            )
            for b in borehole_assets
        ]

    def get_feeds(self, guid):
        """Return feeds for boreholes using the correct MWD API."""

        url = f"{DEFAULT_URL}/api/data/assets/{guid}/feedNames"
        raw = self._request(url)
        return [f["name"] for f in raw if "name" in f]
