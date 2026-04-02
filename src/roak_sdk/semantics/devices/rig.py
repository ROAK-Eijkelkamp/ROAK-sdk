from __future__ import annotations

from roak_sdk.semantics.device import Device
from roak_sdk.clients.rig_client import RigClient
from roak_sdk.clients.client_registry import ClientRegistry
from roak_sdk.semantics.assets.borehole import Borehole
from roak_sdk.config import DEFAULT_RIG_FEEDS
from roak_sdk.roak_error import AmbiguousAssetMatchError, AssetNotFoundError


class Rig(Device):
    """
    Represents a drilling rig in the ROAK system.

    Attributes:
        guid (str): The unique identifier for the rig.
        name (str): The name of the rig.
    """

    DEFAULT_FEEDS = DEFAULT_RIG_FEEDS

    def __init__(self, data: dict, registry: ClientRegistry) -> None:
        """
        Initialize Rig from API response data.

        Args:
            data (dict): Rig data from the API.
            registry (ClientRegistry): Registry for obtaining client instances.
        """
        super().__init__(data, registry)
        self._rig_client = registry.get(RigClient)

    def get_boreholes(self) -> list[Borehole]:
        """
        Retrieve all boreholes associated with this rig.

        Returns:
            list[Borehole]: A list of Borehole objects.
        """
        borehole_data = self._rig_client.get_boreholes(self.guid)
      
        return [Borehole(data['borehole'], self._registry) for data in borehole_data]
    
    def get_borehole_by_name(self, name: str, allow_first_match: bool = False) -> Borehole:
        """
        Retrieve a specific borehole by name.

        Args:
            name (str): The name of the borehole to retrieve.
            allow_first_match (bool): If True, return the first matching
                borehole when multiple are found.

        Returns:
            Borehole: The Borehole object with the specified name.

        Raises:
            ValueError: If no borehole with the given name is found.
        """
        boreholes = self.get_boreholes()
        matches = [borehole for borehole in boreholes if borehole.name == name]
        if len(matches) == 0:
            raise AssetNotFoundError("Borehole", "name", name, scope=f"rig '{self.name}'")
        if len(matches) > 1 and not allow_first_match:
            raise AmbiguousAssetMatchError("Borehole", "name", name, len(matches), scope=f"rig '{self.name}'")
        return matches[0]

    def get_borehole_by_guid(self, guid: str) -> Borehole:
        """
        Retrieve a specific borehole by its GUID.

        Args:
            guid (str): The GUID of the borehole to retrieve.

        Returns:
            Borehole: The Borehole object with the specified GUID.

        Raises:
            ValueError: If no borehole with the given GUID is found.
        """
        boreholes = self.get_boreholes()
        matches = [borehole for borehole in boreholes if borehole.guid == guid]
        if len(matches) == 0:
            raise AssetNotFoundError("Borehole", "GUID", guid, scope=f"rig '{self.name}'")
        return matches[0]