import unittest
from unittest.mock import patch, Mock
import datetime as dt
import requests

from roak_sdk.clients.base_client import (
    BaseClient,
    MILLISECONDS_IN_ONE_SECOND,
    MILLISECONDS_IN_ONE_MINUTE,
    MILLISECONDS_IN_ONE_HOUR,
    MILLISECONDS_IN_ONE_DAY,
    MILLISECONDS_IN_ONE_WEEK,
)
from roak_sdk.roak_error import InvalidJSONError


class TestBaseClient(unittest.TestCase):
    """Unit tests for BaseClient."""

    def setUp(self):
        """Set up a BaseClient instance with fake authorization headers."""
        self.client = BaseClient(authorization={"Authorization": "Bearer fake"})

    # -----------------------
    # _request() tests
    # -----------------------
    @patch("roak_sdk.clients.base_client.requests.get")
    def test_request_success(self, mock_get):
        """Test _request returns parsed JSON for successful GET request."""
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"ok": True}
        mock_get.return_value = mock_resp

        url = "http://fake.url"
        result = self.client._request(url)
        self.assertEqual(result, {"ok": True})
        mock_get.assert_called_once_with(url, headers=self.client.headers, params=None)

    @patch("roak_sdk.clients.base_client.requests.get")
    def test_request_invalid_json(self, mock_get):
        """Test _request raises InvalidJSONError when JSON parsing fails."""
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.side_effect = ValueError("bad json")
        mock_get.return_value = mock_resp

        with self.assertRaises(InvalidJSONError):
            self.client._request("http://fake.url")

    @patch("roak_sdk.clients.base_client.requests.get")
    def test_request_http_error(self, mock_get):
        """Test _request raises HTTPError when the GET request fails."""
        mock_resp = Mock()
        mock_resp.raise_for_status.side_effect = requests.HTTPError("fail")
        mock_get.return_value = mock_resp

        with self.assertRaises(requests.HTTPError):
            self.client._request("http://fake.url")


if __name__ == "__main__":
    unittest.main()
