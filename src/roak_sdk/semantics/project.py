from __future__ import annotations

from typing import TYPE_CHECKING

from roak_sdk.semantics.semantic import Semantic
from roak_sdk.clients.project_client import ProjectClient
from roak_sdk.clients.client_registry import ClientRegistry
from roak_sdk.semantics.factory import make_asset, ASSET_TYPE_WELL, ASSET_TYPE_BOREHOLE
from roak_sdk.semantics.asset import Asset
from roak_sdk.semantics.assets.well import Well
from roak_sdk.semantics.assets.borehole import Borehole
from roak_sdk.config import ASSET_TYPES, ASSET_TYPE_LIST
from roak_sdk.roak_error import AssetTypeMismatchError

if TYPE_CHECKING:
    from roak_sdk.semantics.site import Site

class Project(Semantic):
    """
    Represents a ROAK Project.
    
    Attributes are dynamically accessed from the API response data.
    Use snake_case names (e.g., `owner_id`, `start_date`) to access camelCase API fields.
    
    Provides methods to fetch assets (wells, boreholes, rigs) within the project.
    """

    def __init__(self, data: dict, registry: ClientRegistry) -> None:
        """
        Initialize Project from API response data.

        Args:
            data (dict): Project data from the API.
            registry (ClientRegistry): Registry for obtaining client instances.
        """
        super().__init__(data, registry)
        self._client = registry.get(ProjectClient)

    # =========================================================================
    # Generic asset methods
    # =========================================================================

    def get_assets(self, asset_type: str | None = None) -> list["Asset"]:
        """
        Fetch all assets in this project, optionally filtered by type.

        Args:
            asset_type (str | None): Optional asset type filter 
                                      (e.g., "well", "borehole", "rig").

        Returns:
            list[Asset]: List of Asset objects.
        """
        data = self._client.get_assets(self.guid, asset_type)

        # filter out non-assets
        data = [x for x in data if x["typeGuid"] in ASSET_TYPES]
        return [make_asset(d, self._registry) for d in data]

    def get_asset_by_guid(self, guid: str) -> "Asset": 
        """
        Fetch a single asset by its GUID.

        Args:
            guid (str): GUID of the asset.

        Returns:
            Asset: The asset object.
        """
        data = self._client.get_asset_by_guid(self.guid, guid)
        return make_asset(data, self._registry)

    def get_asset_by_name(
        self,
        name: str,
        asset_type: str | None = None,
        allow_first_match: bool = False,
    ) -> "Asset":
        """
        Fetch a single asset by name.

        Args:
            name (str): Name of the asset.
            asset_type (str | None): Optional asset type filter.
            allow_first_match (bool): If True, return the first match when
                multiple assets share the same name.

        Returns:
            Asset: The asset object.
        """
        data = self._client.get_asset_by_name(
            self.guid,
            name,
            asset_type,
            allow_first_match=allow_first_match,
        )
        return make_asset(data, self._registry)

    def get_sites(self) -> list["Site"]:
        """Fetch all child sites in this project scope."""
        from roak_sdk.semantics.site import Site

        data = self._client.get_assets(self.guid, "ED_SITE")
        return [Site(site_data, self._registry) for site_data in data]

    def get_site_by_guid(self, guid: str) -> "Site":
        """Fetch a site by its GUID within this project scope."""
        from roak_sdk.semantics.site import Site

        data = self._client.get_asset_by_guid(self.guid, guid)
        if data["typeGuid"] != "ED_SITE":
            raise AssetTypeMismatchError("Site", "GUID", guid, data["typeGuid"])
        return Site(data, self._registry)

    def get_site_by_name(self, name: str, allow_first_match: bool = False) -> "Site":
        """Fetch a site by its name within this project scope."""
        from roak_sdk.semantics.site import Site

        data = self._client.get_asset_by_name(
            self.guid,
            name,
            "ED_SITE",
            allow_first_match=allow_first_match,
        )
        if data["typeGuid"] != "ED_SITE":
            raise AssetTypeMismatchError("Site", "name", name, data["typeGuid"])
        return Site(data, self._registry)

    # =========================================================================
    # Well convenience methods
    # =========================================================================

    def get_wells(self) -> list["Well"]:
        """Fetch all wells in this project."""
        return self.get_assets(asset_type=ASSET_TYPE_WELL)

    def get_well_by_guid(self, guid: str) -> "Well":
        """Fetch a well by its GUID."""
        asset = self.get_asset_by_guid(guid)
        if not asset.typeGuid == ASSET_TYPE_WELL:
            raise AssetTypeMismatchError("Well", "GUID", guid, asset.typeGuid)
        return asset

    def get_well_by_name(self, name: str, allow_first_match: bool = False) -> "Well":
        """Fetch a well by its name."""
        asset = self.get_asset_by_name(
            name,
            asset_type=ASSET_TYPE_WELL,
            allow_first_match=allow_first_match,
        )
        if not asset.typeGuid == ASSET_TYPE_WELL:
            raise AssetTypeMismatchError("Well", "name", name, asset.typeGuid)
        return asset
    
    # =========================================================================
    # Borehole convenience methods
    # =========================================================================

    def get_boreholes(self) -> list["Borehole"]:
        """Fetch all boreholes in this project."""
        return self.get_assets(asset_type=ASSET_TYPE_BOREHOLE)

    def get_borehole_by_guid(self, guid: str) -> "Borehole":
        """Fetch a borehole by its GUID."""
        asset = self.get_asset_by_guid(guid)
        from roak_sdk.semantics.asset import Borehole
        if not isinstance(asset, Borehole):
            actual_type = getattr(asset, "typeGuid", type(asset).__name__)
            raise AssetTypeMismatchError("Borehole", "GUID", guid, actual_type)
        return asset

    def get_borehole_by_name(self, name: str, allow_first_match: bool = False) -> "Borehole":
        """Fetch a borehole by its name."""
        return self.get_asset_by_name(
            name,
            asset_type=ASSET_TYPE_BOREHOLE,
            allow_first_match=allow_first_match,
        )

