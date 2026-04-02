from __future__ import annotations

from .base_client import BaseClient

class DeviceClient(BaseClient):
    """
    Docstring for DeviceClient
    """
    def get_children(self, guid: str) -> list[dict]:
        url = f"{self.base_url}/api/tcn/devices/{guid}/details"
        children = self._request(url)
        return children['children']  # return list of child assets
    
   