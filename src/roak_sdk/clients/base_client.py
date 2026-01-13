import requests
from roak_sdk.roak_error import InvalidJSONError
import datetime as dt
from roak_sdk.auth import DEFAULT_URL
from roak_sdk.time_helper import TimeHelper

__all__ = ["BaseClient"]

MILLISECONDS_IN_ONE_SECOND = 1000
MILLISECONDS_IN_ONE_MINUTE = 60 * MILLISECONDS_IN_ONE_SECOND
MILLISECONDS_IN_ONE_HOUR = 60 * MILLISECONDS_IN_ONE_MINUTE
MILLISECONDS_IN_ONE_DAY = 24 * MILLISECONDS_IN_ONE_HOUR
MILLISECONDS_IN_ONE_WEEK = 7 * MILLISECONDS_IN_ONE_DAY


class BaseClient:
    """
    Base client providing shared functionality for ROAK API clients.

    Handles generic HTTP requests, time parsing, and normalization.
    All specialized clients (e.g., WellClient, RigClient) inherit from this class.
    """

    # children override
    ASSET_TYPE = None
    STANDARD_FEEDS = None
    _rig_client = None

    def __init__(self, authorization, base_url: str | None = None):
        """
        Initialize the BaseClient with authentication headers.

        Args:
            authorization (dict): Dictionary containing authorization headers (e.g., {'Authorization': 'Bearer <token>'})
        """
        self.headers = authorization
        self.base_url = base_url or DEFAULT_URL

    # Generic HTTP request
    def _request(self, url, params=None):
        """
        Perform a generic GET request to the ROAK API.

        Args:
            url (str): Full URL for the request.
            params (dict, optional): Dictionary of query parameters.

        Returns:
            dict: Parsed JSON response from the API.

        Raises:
            requests.HTTPError: If the response status code indicates an error.
            InvalidJSONError: If the response cannot be parsed as JSON.
        """

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        try:
            return response.json()
        except Exception:
            raise InvalidJSONError(f"Could not parse JSON from {url}")

    def fetch_data(
        self,
        guid: str,
        feeds: list[str] | str | None = None,
        start: str | int | dt.datetime | None = None,
        end: str | int | dt.datetime | None = None,
        time_period: str | None = None,
    ):
        """
        Universal method to fetch data for any asset type.
        'feeds' should be pre-resolved by the Asset.
        """
        if feeds is None:
            raise ValueError(
                "fetch_data requires a list of feeds. Assets should resolve feeds first."
            )

        url = f"{self.base_url}/api/data/assets/{guid}/data"
        time_params = self.define_time(start=start, end=end, time_period=time_period)

        params = {
            "feedNames": ",".join(feeds),
            "from": str(time_params["from"]),
            "to": str(time_params["to"]),
        }

        return self._request(url, params=params)

    def get_depth_data_raw(self, borehole_guid: str):
        if self._rig_client is None:
            raise NotImplementedError(
                "Depth data is only supported when a RigClient is attached."
            )
        return self._rig_client.get_depth_data_raw(borehole_guid)

    def get_feeds(self, guid):
        """Default: return static STANDARD_FEEDS if defined."""
        if self.STANDARD_FEEDS:
            return self.STANDARD_FEEDS

        # If no STANDARD_FEEDS → fall back to dynamic default:
        url = f"{DEFAULT_URL}/api/data/assets/{guid}/feedNames"
        raw_feeds = self._request(url)
        return [f["name"] for f in raw_feeds if "name" in f]

    def get_assets_for_project(self, project_guid: str, asset_type: str):
        if not isinstance(self.ASSET_TYPE, dict):
            raise NotImplementedError(
                f"{self.__class__.__name__} must define ASSET_TYPE as a dict in the correct client class"
            )

        if asset_type not in self.ASSET_TYPE:
            raise ValueError(f"Unknown asset type: {asset_type}")

        type_guid = self.ASSET_TYPE[asset_type]

        url = f"{self.base_url}/api/data/assets"
        params = {"typeGuid": type_guid, "scopeGuid": project_guid}

        try:
            assets = self._request(url, params=params)
            if not assets:
                print(
                    f"\n No assets of type '{asset_type}' found for project '{project_guid}'!\n"
                )
                return []
            return assets
        except Exception as e:
            print(
                f"\n Could not fetch assets of type '{asset_type}' for project '{project_guid}': {e}\n"
            )
            return []

    def fetch_assets(self, project_guid: str, asset_type: str):
        if self.ASSET_TYPE is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define ASSET_TYPE as a dict in the correct client class"
            )

        return self.get_assets_for_project(project_guid, asset_type)

    def define_time(self, start=None, end=None, time_period=None):
        return TimeHelper.define_time(start, end, time_period)

    def fetch_feeds(self, guid: str) -> dict:
        """
        Default fetch_feeds method for clients that don't support feeds.
        Returns empty dict to prevent crashes.
        """
        return {}
