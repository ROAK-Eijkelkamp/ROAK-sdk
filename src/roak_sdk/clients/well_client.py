from roak_sdk.clients.base_client import BaseClient
from roak_sdk.semantics.assets.well import Well


class WellClient(BaseClient):
    ASSET_TYPE = {"well": "GWM_WELL"}

    def fetch_assets(self, project_guid: str, asset_type: str = "well"):
        """
        Fetch wells for a project.
        asset_type parameter is required for compatibility with Project.get_assets
        """
        return self.get_assets_for_project(project_guid, "well")

    def get_well_data(self, well_guid, feeds=None, start=None, end=None):
        well_asset = Well(well_guid, "Unknown Well", self)
        return well_asset.get_data(feeds=feeds, start=start, end=end)
