from .base_client import BaseClient
from roak_sdk.config import CUSTOMER_TYPE, MODEM_TYPES, RIG_TYPES
from roak_sdk.roak_error import AmbiguousAssetMatchError, AssetNotFoundError


class RoakClient(BaseClient):

    # --- Asset Type methods ---
    def get_asset_types(self) -> list[dict]:
        """
        Fetch all asset types from the ROAK API.

        Returns:
            list[dict]: List of asset type dictionaries.
        """
        url = f"{self.base_url}/api/data/assetsTypes"
        asset_types = self._request(url)
        return asset_types  # return list of all asset types
    
    def get_asset_by_guid(self, guid: str) -> dict:
        """
        Fetch an asset by its GUID.

        Args:
            guid (str): GUID of the asset.

        Returns:
            dict: Asset data dictionary.
        """
        url = f"{self.base_url}/api/ed/genericAssets/{guid}"
        asset = self._request(url)
        return asset  # return single asset matching the GUID

    def get_assets(self, type_guid: str | None = None) -> list[dict]:
        """Fetch account-wide assets, optionally filtered by type GUID."""
        url = f"{self.base_url}/api/data/assets"
        params = None if type_guid is None else {"typeGuid": type_guid}
        return self._request(url, params=params)

    def get_wells(self) -> list[dict]:
        """Fetch all wells from the ROAK API."""
        return self.get_assets(type_guid="GWM_WELL")

    def get_boreholes(self) -> list[dict]:
        """Fetch all boreholes from the ROAK API."""
        return self.get_assets(type_guid="MWD_BOREHOLE")

    # --- Customer methods ---

    def get_customers(self) -> list[dict]:
        """
        Fetch all customers from the ROAK API.

        Returns:
            list[dict]: List of customer data dictionaries.
        """
        customers = self.get_assets(type_guid=CUSTOMER_TYPE)
        return customers

    # --- Project methods ---

    def get_projects(self) -> list[dict]:
        """
        Fetch all projects from the ROAK API.

        Returns:
            list[dict]: List of project data dictionaries.
        """
        url = f"{self.base_url}/api/ed/projects"
        projects = self._request(url)
        return projects  # return list of all projects
    
    def get_asset_by_name_and_type(
        self,
        name: str,
        type_guid: str | None = None,
        allow_first_match: bool = False,
    ) -> dict:
        """
        Fetch an asset by its name and type GUID.

        Args:
            name (str): Name of the asset.
            type_guid (str): Type GUID of the asset.
            allow_first_match (bool): If True, return the first match when
                multiple assets match the name.

        Returns:
            dict: Asset data dictionary.
        """
        url = f"{self.base_url}/api/data/assets"
        params = {"query": name}
        if type_guid is not None:
            params["typeGuid"] = type_guid

        assets = self._request(url, params=params)
        if type_guid:
            filtered_assets = [asset for asset in assets if asset.get("name") == name and asset.get("typeGuid") == type_guid]
        else:
            filtered_assets = [asset for asset in assets if asset.get("name") == name]

        if len(filtered_assets) == 0:
            raise AssetNotFoundError("Asset", "name", name, scope=f"type '{type_guid}'")

        if len(filtered_assets) > 1 and not allow_first_match:
            raise AmbiguousAssetMatchError("Asset", "name", name, len(filtered_assets), scope=f"type '{type_guid}'")
        
        return filtered_assets[0]  # return single asset matching the name and type
    
    def get_project_by_guid(self, guid: str) -> dict:
        """
        Fetch a project by its GUID.

        Args:
            guid (str): GUID of the project.
        Returns:
            dict: Project data dictionary.
        """
        url = f"{self.base_url}/api/ed/projects/{guid}"
        project = self._request(url)
        return project  # return single project matching the GUID

    # --- Site methods ---
    
    def get_sites(self) -> list[dict]:
        """
        Fetch all sites from the ROAK API.

        Returns:
            list[dict]: List of site data dictionaries.
        """
        sites = self.get_assets(type_guid="ED_SITE")
        return sites  # return list of all sites
    
    def get_modems(self) -> list[dict]:
        """
        Docstring for get_modems
        
        :param self: Description
        :return: Description
        :rtype: list[dict]

        TODO: now first get a root in order to get all assets -> should be a prettier way to do this.
        """
        url = f"{self.base_url}/api/data/assets"
        root = self._request(url)[0]["guid"]

        params = {"scopeGuid": root}
        assets = self._request(url, params=params)
        
        modems = [x for x in assets if x["typeGuid"] in MODEM_TYPES]
        return modems  # return list of all modems
    
    def get_rigs(self) -> list[dict]:
        """
        Fetch all rigs from the ROAK API.

        Returns:
            list[dict]: List of rig data dictionaries.
        """
        url = f"{self.base_url}/api/data/assets"
        root = self._request(url)[0]["guid"]

        params = {"scopeGuid": root}
        assets = self._request(url, params=params)
        rigs = [x for x in assets if x["typeGuid"] in RIG_TYPES]
        return rigs  # return list of all rigs