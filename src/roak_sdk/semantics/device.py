from __future__ import annotations

from roak_sdk.semantics.asset import Asset
from roak_sdk.clients.device_client import DeviceClient
from roak_sdk.clients.client_registry import ClientRegistry


class Device(Asset):
    """
    Base class for all ROAK devices.

    Provides common device functionality and dynamic attribute access.
    Inherits data and feed operations from Asset.
    Subclasses can override class attributes to customize behavior.
    """

    def __init__(self, data: dict, registry: ClientRegistry) -> None:
        """
        Initialize Device from API response data.

        Args:
            data (dict): Device data from the API.
            registry (ClientRegistry): Registry for obtaining client instances.
        """
        super().__init__(data, registry)
        self._device_client = registry.get(DeviceClient)

    def get_children(self) -> list[Device]:
        """
        Fetch child devices of this device.

        Returns:
            list[Device]: List of child Device instances.
        """
        raw_children = self._device_client.get_children(self.guid)
        return [Device(child, self._registry) for child in raw_children]