from __future__ import annotations

from .base_client import BaseClient
from roak_sdk.roak_error import AmbiguousAssetMatchError, AssetNotFoundError


class ProjectClient(BaseClient):
    """
    Client for project-related API operations.
    
    Handles fetching assets within a project context.
    """

    def get_assets(
        self, project_guid: str, asset_type: str | None = None
    ) -> list[dict]:
        """
        Fetch all assets for a project, optionally filtered by type.

        Args:
            project_guid (str): GUID of the project.
            asset_type (str | None): Optional asset type to filter by 
                                      (e.g., "well", "borehole", "rig").

        Returns:
            list[dict]: List of asset data dictionaries.
        """
        url = f"{self.base_url}/api/data/assets"
        params = {"scopeGuid": project_guid}
        if asset_type:
            params["typeGuid"] = asset_type
        return self._request(url, params=params if params else None)

    def get_asset_by_guid(self, project_guid: str, guid: str) -> dict:
        """
        Fetch a single asset by its GUID.

        Args:
            guid (str): GUID of the asset.

        Returns:
            dict: Asset data dictionary.
        """
        url = f"{self.base_url}/api/data/assets"
        params = {"scopeGuid": project_guid}
        all_assets = self._request(url, params=params)
        filtered_assets = [x for x in all_assets if x["guid"] == guid]
        if filtered_assets:
            return filtered_assets[0]
        raise AssetNotFoundError("Asset", "GUID", guid, scope=f"project '{project_guid}'")

    def get_asset_by_name(
        self,
        project_guid: str,
        name: str,
        asset_type: str | None = None,
        allow_first_match: bool = False,
    ) -> dict:
        """
        Fetch a single asset by name within a project.

        Args:
            project_guid (str): GUID of the project.
            name (str): Name of the asset.
            asset_type (str | None): Optional asset type to filter by.
            allow_first_match (bool): If True, return the first match when
                multiple assets match the name.

        Returns:
            dict: Asset data dictionary.

        Raises:
            ValueError: If no asset with the given name is found.
        """
        url = f"{self.base_url}/api/ed/projects/{project_guid}/assets"
        params = {"name": name}
        if asset_type:
            params["type"] = asset_type
        
        result = self._request(url, params=params)
        
        # API may return list or single item
        if isinstance(result, list):
            if len(result) == 0:
                raise AssetNotFoundError("Asset", "name", name, scope=f"project '{project_guid}'")
            if len(result) > 1 and not allow_first_match:
                raise AmbiguousAssetMatchError("Asset", "name", name, len(result), scope=f"project '{project_guid}'")
            return result[0]
        return result