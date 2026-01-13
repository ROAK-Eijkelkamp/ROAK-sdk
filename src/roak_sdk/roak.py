from roak_sdk.auth import Auth
from roak_sdk.clients.well_client import WellClient
from roak_sdk.clients.rig_client import RigClient
from roak_sdk.clients.project_client import ProjectClient
from roak_sdk.clients.asset_client import AssetClient
from roak_sdk.semantics.assets.borehole import Borehole
from roak_sdk.semantics.project import Project
from roak_sdk.semantics.assets.well import Well
from roak_sdk.clients.base_client import BaseClient
from roak_sdk.semantics.assets.generic_asset import GenericAsset


class Roak:
    """
    Main entry point for the ROAK SDK.

    Handles authentication and provides access to different clients:
    WellClient, RigClient, ProjectClient, and AssetClient.

    Users must provide explicit credentials (user + password) or have them
    available in environment variables (.env). Provides convenience methods
    to fetch Projects, Wells, Rigs, and Boreholes as objects.
    """

    def __init__(self, user, password, base_url=None):
        """
        Initialize the Roak SDK with authentication and set up clients.

        Args:
            user (str): Username or email for authentication.
            password (str): Password for authentication.

        Raises:
            AuthenticationError, MissingPasswordError, or related Auth exceptions.
        """
        # --- Auth & headers ---
        self.auth = Auth(user=user, password=password, base_url=base_url)
        self.headers = self.auth.authenticate()

        # --- Initialize clients ---
        self.well_client = WellClient(self.headers, base_url=self.auth.base_url)
        self.rig_client = RigClient(self.headers, base_url=self.auth.base_url)
        self.project_client = ProjectClient(self.headers, base_url=self.auth.base_url)
        self.asset_client = AssetClient(self.headers, base_url=self.auth.base_url)

    def refresh_tokens(self):
        """
        Refresh the authentication tokens and update headers in all clients.

        Note:
            This method has not been fully tested yet.
        """
        new_headers = self.auth.refresh_access_token()
        self.headers = new_headers
        self.well_client.headers = new_headers
        self.project_client.headers = new_headers
        self.rig_client.headers = new_headers

    def get_project(self, name: str) -> "Project":
        """
        Fetch project(s) from ProjectClient.
        Returns a single Project if name is provided, otherwise a list[Project].
        """
        data = self.project_client.get_project_data(name=name)

        client_instance = BaseClient(authorization=self.headers)

        if name is not None:
            # Always return single Project
            return Project(data, client=client_instance)
        else:
            # Return list of Projects
            return [Project(d, client=client_instance) for d in data]

    def get_project_guid(self, name):
        """
        Get the GUID of a project by name.

        Args:
            name (str): Name of the project.

        Returns:
            str: Project GUID.

        Raises:
            ValueError: If project with the given name does not exist.
        """
        data = self.project_client.get_project_data(name=name)
        if isinstance(data, dict):
            return data["guid"]
        elif isinstance(data, list) and len(data) > 0:
            return data[0]["guid"]
        else:
            raise ValueError(f"Project '{name}' not found")

    def get_well(self, guid):
        """
        Create a Well object for the given GUID.

        Args:
            guid (str): Well GUID.

        Returns:
            Well: Well object associated with the given GUID.
        """

        return Well(guid, "Unknown Well", self.well_client)

    def get_assets(self, asset_type: str, project_guid: str):
        client = {
            "well": self.well_client,
            "rig": self.rig_client,
            "borehole": self.asset_client,
            "generic": self.asset_client,
        }[asset_type]

        raw = client.get_assets_for_project(project_guid, asset_type)

        # convert dict → object
        constructor = {
            "well": self.get_well,
            "rig": self.get_rig,
            "borehole": self.get_borehole,
            "generic": self.get_generic_asset,
        }[asset_type]

        return [constructor(a["guid"]) for a in raw]

    def get_borehole(self, guid: str) -> Borehole:
        """
        Return a Borehole object for the given GUID.

        Args:
            guid (str): Borehole GUID.

        Returns:
            Borehole: Borehole object tied to the AssetClient.
        """
        return Borehole(guid, "Unknown Borehole", client=self.asset_client)

    def get_generic_asset(self, guid: str):
        """
        Return a generic asset object for the given GUID.

        Args:
            guid (str): Generic asset GUID.

        Returns:
            GenericAsset: Generic asset object tied to the AssetClient.
        """
        return GenericAsset(guid, "Unknown Asset", client=self.asset_client)

    def get_rig(self, guid):
        """
        Return a Rig object via the RigClient.

        Args:
            guid (str): GUID of the rig.

        Returns:
            Rig: Rig object associated with the given GUID.
        """
        return self.rig_client.get_rig(guid)

    def get_boreholes(self):
        """
        Fetch all boreholes owned by the user and return as Borehole objects.

        Returns:
            list[Borehole]: List of Borehole objects, deduplicated by GUID.
        """
        TYPE_GUID = "MWD_BOREHOLE"

        raw_assets = self.asset_client.get_assets_base(type_guid=TYPE_GUID)

        raw_assets = self.asset_client.deduplicate_assets(raw_assets)

        # Instantiate Borehole objects
        boreholes = [
            Borehole(guid=a["guid"], name=a["name"], client=self.rig_client)
            for a in raw_assets
        ]

        return boreholes
