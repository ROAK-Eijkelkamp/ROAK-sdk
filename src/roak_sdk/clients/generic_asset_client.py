from roak_sdk.clients.base_client import BaseClient
from roak_sdk.semantics.assets.generic_asset import GenericAsset


class GenericAssetClient(BaseClient):
    """Client for generic asset API fetching"""

    ASSET_TYPE = {"generic": "GENERIC_ASSET"}
    STANDARD_FEEDS = None  # dynamic fallback via Asset

    def get_generic_data(self, guid, feeds=None, start=None, end=None):
        asset = GenericAsset(guid, "GenericAsset", self)
        return asset.get_data(feeds=feeds, start=start, end=end)
