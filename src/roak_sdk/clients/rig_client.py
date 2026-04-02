from __future__ import annotations

from .base_client import BaseClient


class RigClient(BaseClient):
    """
    Client for rig-specific API operations.
    """
    def get_boreholes(self, rig_guid: str) -> list[dict]:
        """
        Retrieve all boreholes associated with a specific rig.

        Args:
            rig_guid (str): The unique identifier of the rig.

        Returns:
            list[dict]: A list of borehole data dictionaries.
        """
        url = f"{self.base_url}/api/mwd/rigs/{rig_guid}/boreHoles"
        return self._request(url)
