from .base_client import BaseClient

class BoreholeClient(BaseClient):
    """
    Client for borehole-specific API operations.
    """
    def get_depth_data(self, borehole_guid: str) -> list[dict]:
        """
        Retrieve depth data for a specific borehole.

        Args:
            borehole_guid (str): The unique identifier of the borehole. 
        Returns:
            list[dict]: A list of depth data records.
        """
        url = f"{self.base_url}/api/mwd/boreholes/{borehole_guid}/depthData"
        return self._request(url)