from __future__ import annotations

from .base_client import BaseClient


class AssetClient(BaseClient):
    """
    Client for asset-specific API operations.
    
    Handles operations on individual assets like fetching data, feeds, etc.
    Works for all asset types (wells, boreholes, rigs).
    """

    def get_data(
        self,
        asset_guid: str,
        start_millis: int,
        end_millis: int,
        feeds: list[str],
    ) -> list[dict]:
        """
        Fetch data for an asset within a date range.

        Args:
            asset_guid (str): GUID of the asset.
            start_millis (int): Start of the date range (epoch milliseconds).
            end_millis (int): End of the date range (epoch milliseconds).

        Returns:
            list[dict]: List of data records.
        """
        url = f"{self.base_url}/api/data/assets/{asset_guid}/data"
        params = {
            "from": start_millis,
            "to": end_millis,
            "feedNames": feeds,
        }
        return self._request(url, params=params)

    def get_feeds(self, asset_guid: str) -> list[dict]:
        """
        Fetch available data feeds for an asset.

        Args:
            asset_guid (str): GUID of the asset.

        Returns:
            list[dict]: List of feed definitions.
        """
        url = f"{self.base_url}/api/data/assets/{asset_guid}/feedNames"
        return self._request(url)
