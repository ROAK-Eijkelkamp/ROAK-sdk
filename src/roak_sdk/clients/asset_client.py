from roak_sdk.clients.base_client import BaseClient
from roak_sdk.auth import DEFAULT_URL


class AssetClient(BaseClient):
    """
    Client for interacting with asset-related endpoints in the ROAK API.

    Inherits from BaseClient and provides functionality to fetch, transform,
    and deduplicate assets and asset types.
    """

    def fetch_assets_base(self, type_guid=None, scope_guid=None, query=None):
        """
        Fetch raw asset data from the ROAK API.

        Args:
            type_guid (str, optional): GUID of the asset type to filter by.
            scope_guid (str, optional): GUID of the scope to filter by.
            query (str, optional): Search query for asset names or metadata.

        Returns:
            dict | list: Raw JSON response from the API (assets or metadata).
        """
        url = f"{DEFAULT_URL}/api/data/assets"
        params = {}
        if type_guid:
            params["typeGuid"] = type_guid
        if scope_guid:
            params["scopeGuid"] = scope_guid
        if query:
            params["query"] = query
        return self._request(url, params=params)

    def transform_assets(self, data):
        """
        Normalize asset data into a list format.

        Ensures that the response from the API (which may be a dict or list)
        is converted into a list of asset dictionaries for consistent handling.

        Args:
            data (dict | list): Raw asset data from the API.

        Returns:
            list[dict]: Normalized list of asset dictionaries.
        """
        if isinstance(data, dict):
            if "guid" in data and "name" in data:
                data = [data]
            else:
                data = list(data.values())
        return data

    def get_assets_base(self, type_guid=None, scope_guid=None, query=None):
        """
        Retrieve and normalize asset data in one step.

        Combines `fetch_assets_base` and `transform_assets`
        to return consistently structured data.

        Args:
            type_guid (str, optional): GUID of the asset type to filter by.
            scope_guid (str, optional): GUID of the scope to filter by.
            query (str, optional): Search query for asset names or metadata.

        Returns:
            list[dict]: List of asset dictionaries.
        """
        return self.transform_assets(
            self.fetch_assets_base(type_guid, scope_guid, query)
        )

    def deduplicate_assets(self, assets):
        """
        Remove duplicate assets from a list based on their GUID.
        Parameters:
               assets (list[dict]): List of asset dictionaries. Each must contain a "guid" key.
        Returns:
            list[dict]: List of unique assets (duplicates removed), preserving the last occurrence.
        """
        return list({a["guid"]: a for a in assets}.values())

    def get_all_assets_per_type(self, type_guids):
        """
        Fetch and combine assets across multiple type GUIDs.

        Args:
            type_guids (list[str]): List of asset type GUIDs to fetch.

        Returns:
            list[dict]: Deduplicated list of assets across all provided types.
        """
        all_assets = []
        for tg in type_guids:
            all_assets.extend(self.get_assets_base(type_guid=tg))
        return self.deduplicate_assets(all_assets)

    def get_asset_types(self):
        """
        Retrieve all available asset types from the ROAK API.

        Returns:
            dict | list: JSON response containing asset type definitions.
        """
        url = f"{DEFAULT_URL}/api/data/assetsTypes"
        return self._request(url)
