import logging

from .auth import Auth
from .clients.roak_client import RoakClient
from .clients.client_registry import ClientRegistry
from .semantics.project import Project
from .semantics.site import Site
from .semantics.customer import Customer
from .semantics.factory import make_asset
from .semantics.assets.well import Well
from .semantics.assets.borehole import Borehole
from .semantics.devices.modem import Modem
from .semantics.devices.rig import Rig
from .config import DEFAULT_BASE_URL, MODEM_TYPES, RIG_TYPES, CUSTOMER_TYPE
from .config import DEFAULT_REQUEST_TIMEOUT, normalize_request_timeout
from .roak_error import AssetTypeMismatchError


logger = logging.getLogger("roak_sdk")


class Roak:
    """
    Main entry point for the ROAK SDK.
    It is a facade pattern. 

    Handles authentication and provides methods for a user to get lists of his assets

    Users must provide explicit credentials (user + password). Provides convenience methods
    to fetch Projects, Wells, Rigs, and Boreholes as objects.
    """

    def __init__(
        self,
        username,
        password,
        base_url=None,
        tenant=None,
        debug=False,
        request_timeout: int | float | None = DEFAULT_REQUEST_TIMEOUT,
    ):
        """
        Initialize the Roak SDK with authentication and set up clients.

        Args:
            username (str): Username or email for authentication.
            password (str): Password for authentication.
            base_url (str | None): Optional custom base URL for the API.
            tenant (str | None): Optional tenant identifier for multi-tenant scenarios.
            debug (bool): Enable debug logging for API requests. Default is False.
            request_timeout (int | float | None): Timeout in seconds for HTTP requests.
                Use None or a negative value to disable request timeouts.

        Raises:
            AuthenticationError, MissingPasswordError, or related Auth exceptions.
        """
        # --- Configure logging if debug is enabled ---
        if debug:
            logging.basicConfig(
                level=logging.WARNING,
                format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            )
            logger.setLevel(logging.DEBUG)
            # Suppress noisy third-party loggers
            logging.getLogger("urllib3").setLevel(logging.WARNING)
            logging.getLogger("requests").setLevel(logging.WARNING)
        
        # --- Auth & headers ---
        base_url = base_url or DEFAULT_BASE_URL
        self.request_timeout = normalize_request_timeout(request_timeout)
        self.auth = Auth(
            username=username,
            password=password,
            base_url=base_url,
            tenant=tenant,
            request_timeout=self.request_timeout,
        )
        self.headers = self.auth.authenticate()

        # --- Initialize client registry with refresh callback ---
        self._registry = ClientRegistry(
            self.headers,
            base_url=self.auth.base_url,
            refresh_callback=self._refresh_tokens,
            debug=debug,
            request_timeout=self.request_timeout,
        )
        self._roak_client = self._registry.get(RoakClient)

    # --- Token / auth methods ---

    def _refresh_tokens(self) -> dict[str, str]:
        """
        Internal callback for token refresh. Called by registry on 401 errors.

        Returns:
            dict[str, str]: New headers with refreshed token.
        """
        new_headers = self.auth.refresh_access_token()
        self.headers = new_headers
        return new_headers

    def refresh_tokens(self) -> dict[str, str] | None:
        """
        Manually refresh the authentication tokens and update headers in all clients.

        Returns:
            dict[str, str] | None: New headers if refresh succeeded.
        """
        return self._registry.refresh_tokens()

    def set_request_timeout(self, request_timeout: int | float | None) -> float | None:
        """Update the timeout used for auth and future client requests.

        Use None or a negative value to disable request timeouts.
        """
        self.request_timeout = normalize_request_timeout(request_timeout)
        self.auth.request_timeout = self.request_timeout
        self._registry.update_request_timeout(self.request_timeout)
        return self.request_timeout

    # --- type methods ---

    def get_asset_types(self) -> list[dict]:
        """
        Fetch all asset types from the ROAK API.

        Returns:
            list[dict]: List of asset type dictionaries.
        """
        data = self._roak_client.get_asset_types()
        return data

    # --- Customer methods ---

    def get_customers(self) -> list["Customer"]:
        """
        Fetch all customers from the ROAK API.

        Returns:
            list[Customer]: List of Customer objects.
        """
        data = self._roak_client.get_customers()
        return [Customer(d, self._registry) for d in data]

    def get_customer_by_name(self, name: str, allow_first_match: bool = False) -> "Customer":
        """
        Fetch a customer by its name.

        Args:
            name (str): Name of the customer.
            allow_first_match (bool): If True, return the first match when
                multiple customers share the same name.

        Returns:
            Customer: Customer object matching the given name.
        """
        data = self._roak_client.get_asset_by_name_and_type(
            name=name,
            type_guid=CUSTOMER_TYPE,
            allow_first_match=allow_first_match,
        )
        return Customer(data, self._registry)

    def get_customer_by_guid(self, guid: str) -> "Customer":
        """
        Fetch a customer by its GUID.

        Args:
            guid (str): GUID of the customer.

        Returns:
            Customer: Customer object matching the given GUID.
        """
        data = self._roak_client.get_asset_by_guid(guid=guid)
        return Customer(data, self._registry)

    def get_asset_by_guid(self, guid: str):
        """Fetch an asset by its GUID and materialize the best semantic type."""
        data = self._roak_client.get_asset_by_guid(guid=guid)
        return make_asset(data, self._registry)

    def get_asset_by_name(
        self,
        name: str,
        asset_type: str | None = None,
        allow_first_match: bool = False,
    ):
        """Fetch an asset by name and materialize the best semantic type."""
        data = self._roak_client.get_asset_by_name_and_type(
            name=name,
            type_guid=asset_type,
            allow_first_match=allow_first_match,
        )
        return make_asset(data, self._registry)

    def _get_assets(self, asset_type: str, constructor):
        """Fetch account-wide assets for a type and materialize them with the given constructor."""
        data = self._roak_client.get_assets(type_guid=asset_type)
        return [constructor(item, self._registry) for item in data]

    def get_wells(self) -> list["Well"]:
        """Fetch all wells from the ROAK API."""
        return self._get_assets("GWM_WELL", Well)

    def get_boreholes(self) -> list["Borehole"]:
        """Fetch all boreholes from the ROAK API."""
        return self._get_assets("MWD_BOREHOLE", Borehole)

    # --- Project methods ---

    def get_project_by_name(self, name: str, allow_first_match: bool = False) -> "Project":
        """
        Fetch a project by its name.

        Args:
            name (str): Name of the project.
            allow_first_match (bool): If True, return the first match when
                multiple projects share the same name.

        Returns:
            Project: Project object matching the given name.
        """
        data = self._roak_client.get_asset_by_name_and_type(
            name=name,
            type_guid="ED_PROJECT",
            allow_first_match=allow_first_match,
        )
        return Project(data, self._registry)

    def get_project_by_guid(self, guid: str) -> "Project":
        """
        Fetch a project by its GUID.

        Args:
            guid (str): GUID of the project.

        Returns:
            Project: Project object matching the given GUID.
        """
        data = self._roak_client.get_project_by_guid(guid=guid)
        return Project(data, self._registry)
        
    def get_projects(self) -> list["Project"]:
        """
        Fetch all projects from ProjectClient.
        Returns a list of Project objects.
        """
        data = self._roak_client.get_projects()

        projects = [Project(proj_data, self._registry) for proj_data in data]
        return projects

    # --- Site methods ---

    def get_sites(self) -> list["Site"]:
        """
        Fetch all sites from the ROAK API.

        Returns:
            list["Site"]: List of Site objects.
        """
        return self._get_assets("ED_SITE", Site)
    
    def get_site_by_name(self, name: str, allow_first_match: bool = False) -> "Site":
        """
        Fetch a site by its name.

        Args:
            name (str): Name of the site.
            allow_first_match (bool): If True, return the first match when
                multiple sites share the same name.

        Returns:
            Site: Site object matching the given name.
        """
        data = self._roak_client.get_asset_by_name_and_type(
            name=name,
            type_guid="ED_SITE",
            allow_first_match=allow_first_match,
        )
        return Site(data, self._registry)

    def get_site_by_guid(self, guid: str) -> "Site":
        """
        Fetch a site by its GUID.

        Args:
            guid (str): GUID of the site.

        Returns:
            Site: Site object matching the given GUID.
        """
        data = self._roak_client.get_asset_by_guid(guid=guid)
        return Site(data, self._registry)

    def get_borehole_by_guid(self, guid: str) -> "Borehole":
        """Fetch a borehole by its GUID."""
        data = self._roak_client.get_asset_by_guid(guid=guid)
        if data["typeGuid"] != "MWD_BOREHOLE":
            raise AssetTypeMismatchError("Borehole", "GUID", guid, data["typeGuid"])
        return Borehole(data, self._registry)

    def get_well_by_guid(self, guid: str) -> "Well":
        """Fetch a well by its GUID."""
        data = self._roak_client.get_asset_by_guid(guid=guid)
        if data["typeGuid"] != "GWM_WELL":
            raise AssetTypeMismatchError("Well", "GUID", guid, data["typeGuid"])
        return Well(data, self._registry)

    def get_well_by_name(self, name: str, allow_first_match: bool = False) -> "Well":
        """Fetch a well by its name."""
        data = self._roak_client.get_asset_by_name_and_type(
            name=name,
            type_guid="GWM_WELL",
            allow_first_match=allow_first_match,
        )
        if data["typeGuid"] != "GWM_WELL":
            raise AssetTypeMismatchError("Well", "name", name, data["typeGuid"])
        return Well(data, self._registry)

    def get_borehole_by_name(self, name: str, allow_first_match: bool = False) -> "Borehole":
        """Fetch a borehole by its name."""
        data = self._roak_client.get_asset_by_name_and_type(
            name=name,
            type_guid="MWD_BOREHOLE",
            allow_first_match=allow_first_match,
        )
        if data["typeGuid"] != "MWD_BOREHOLE":
            raise AssetTypeMismatchError("Borehole", "name", name, data["typeGuid"])
        return Borehole(data, self._registry)

    # --- Drilling methods ---

    def get_rigs(self) -> list[Rig]:
        """
        Fetch all rigs from the ROAK API.

        Returns:
            list[Rig]: List of Rig objects.
        """
        data = self._roak_client.get_rigs()
        rigs = [Rig(rig_data, self._registry) for rig_data in data]
        return rigs

    def get_rig_by_name(self, name: str, allow_first_match: bool = False) -> Rig:
        """
        Fetch a rig by its name.

        Args:
            name (str): Name of the rig.
            allow_first_match (bool): If True, return the first match when
                multiple assets share the same rig name.

        Returns:
            Rig: Rig object matching the given name.
        """
        data = self._roak_client.get_asset_by_name_and_type(
            name=name,
            allow_first_match=allow_first_match,
        )
        # check if result is actually a rig
        if data["typeGuid"] not in RIG_TYPES:
            raise AssetTypeMismatchError("Rig", "name", name, data["typeGuid"])
        return Rig(data, self._registry)

    def get_rig_by_guid(self, guid: str) -> Rig:
        """
        Fetch a rig by its GUID.

        Args:
            guid (str): GUID of the rig.

        Returns:
            Rig: Rig object matching the given GUID.
        """
        data = self._roak_client.get_asset_by_guid(guid=guid)
        # check if result is actually a rig
        if data["typeGuid"] not in RIG_TYPES:
            raise AssetTypeMismatchError("Rig", "GUID", guid, data["typeGuid"])
        return Rig(data, self._registry)

    # --- Modem methods ---

    def get_modems(self) -> list["Modem"]:
        """
        Fetch all modems from the ROAK API.

        Returns:
            list["Modem"]: List of Modem objects.
        """

        data = self._roak_client.get_modems()
        modems = [Modem(modem_data, self._registry) for modem_data in data]
        return modems

    def get_modem_by_guid(self, guid: str) -> "Modem":
        """
        Fetch a modem by its GUID.

        Args:
            guid (str): GUID of the modem.

        Returns:
            Modem: Modem object matching the given GUID.
        """
        data = self._roak_client.get_asset_by_guid(guid=guid)

        #check that asset is a modem
        if data["typeGuid"] not in MODEM_TYPES:
            raise AssetTypeMismatchError("Modem", "GUID", guid, data["typeGuid"])
        return Modem(data, self._registry)

    def get_modem_by_name(self, name: str, allow_first_match: bool = False) -> "Modem":
        """
        Fetch a modem by its name (serial number).

        For modems, the name/serial number is the same as the GUID,
        so this method delegates to get_modem_by_guid().

        Args:
            name (str): Name/serial number of the modem.
            allow_first_match (bool): Ignored for modems (kept for API consistency).

        Returns:
            Modem: Modem object matching the given name.
        """
        return self.get_modem_by_guid(guid=name)
