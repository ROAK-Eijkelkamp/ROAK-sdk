from roak_sdk.semantics.semantic import Semantic
from roak_sdk.clients.well_client import WellClient
from roak_sdk.clients.rig_client import RigClient
from roak_sdk.clients.generic_asset_client import GenericAssetClient
from roak_sdk.semantics.assets.rig import Rig
from roak_sdk.semantics.assets.well import Well
from roak_sdk.semantics.assets.borehole import Borehole
from roak_sdk.semantics.assets.generic_asset import GenericAsset
import difflib


class Project(Semantic):
    """
    Represents a project in ROAK.
    A Project has its own client and contains multiple Sites.
    Automatically loads feed variables on initialization.
    """

    CLIENTSDICT = {
        "well": (WellClient, Well),
        "rig": (RigClient, Rig),
        "borehole": (RigClient, Borehole),
        "generic_asset": (GenericAssetClient, GenericAsset),
    }  # add more assets gernic , boreholes

    def __init__(self, data: dict, client=None):
        """
        Initialize Project from API dict and auto-load feeds.
        """
        self._feeds_loaded = False

        super().__init__(guid=data["guid"], name=data["name"], client=client)
        self.client = client

        if not self.client or not getattr(self.client, "headers", None):
            raise ValueError(
                "Project must have a client with valid authorization headers"
            )

        # Basic project info
        self.id = data.get("id")
        self.owner_id = data.get("ownerId")
        self.name = data.get("name")
        self.guid = data.get("guid")
        self.path = data.get("path")
        self.guid_path = data.get("guidPath")
        self.type_guid = data.get("typeGuid")
        self.parent_guid = data.get("parentGuid")
        self.country = data.get("country")
        self.start_date = data.get("startDate")
        self.child_types = data.get("childTypes", [])

        self._sites: list = []  # Will hold list of Site instances

        # --- Automatically load feeds ---
        self.load_feeds()
        self._feeds_loaded = True

    def get_assets(self, asset_type: str):
        """
        Fetch all assets of a given type for this project.
        Ensures Boreholes have a rig client attached for depth data.
        """
        if asset_type not in self.CLIENTSDICT:
            closest = difflib.get_close_matches(
                asset_type, self.CLIENTSDICT.keys(), n=1
            )
            suggestion = f" Did you mean '{closest[0]}'?" if closest else ""
            raise ValueError(
                f"Unknown asset type: {asset_type!r}.{suggestion} "
                "Please check your spelling or ensure the asset type is supported."
            )

        client_cls, asset_class = self.CLIENTSDICT[asset_type]

        if self.client is None:
            raise RuntimeError("Project.get_assets: self.client is None!")

        authorization = self.client.headers
        client = client_cls(authorization=authorization)

        # Attach rig client if this is a borehole
        if asset_type == "borehole":
            client._rig_client = getattr(self.client, "_rig_client", None)

        raw_assets = client.fetch_assets(self.guid, asset_type)

        # Pass the client with _rig_client attached
        return [
            asset_class(asset["guid"], asset["name"], client=client, project=self)
            for asset in raw_assets
        ]

    def __repr__(self):
        """
        Return the official string representation of the Project.

        Shows the project's name and guid for easier debugging and inspection.
        """
        return f"<Project name={self.name!r} guid={self.guid!r}>"

    def add_site(self, site):
        """ "This function is WIP"""
        self._sites.append(site)

    def get_sites(self):
        """ "This function is WIP"""
        return self._sites
