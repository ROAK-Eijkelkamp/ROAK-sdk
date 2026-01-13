import unittest
from unittest.mock import patch
from roak_sdk.clients.well_client import WellClient
from roak_sdk.semantics.assets.well import Well
from roak_sdk.auth import DEFAULT_URL
from datetime import datetime, timedelta


class TestWellClient(unittest.TestCase):
    """Unit tests for WellClient (API communication)."""

    @patch.object(WellClient, "_request")
    def test_fetch_data_with_feeds_and_time(self, mock_request):
        """Test fetch_data calls _request with correct URL and parameters."""
        client = WellClient(authorization={"Authorization": "Bearer token"})
        mock_request.return_value = [{"name": "feed1", "values": []}]

        feeds = ["feed1"]
        start = int(datetime.now().timestamp() * 1000)
        end = start + 1000
        client.fetch_data("well123", feeds=feeds, start=start, end=end)

        self.assertTrue(mock_request.called)
        args, kwargs = mock_request.call_args

        # URL contains the well GUID
        self.assertIn("well123", args[0])

        # NEW: check that "feedNames" key exists and its value contains "feed1"
        self.assertIn("feedNames", kwargs["params"])
        self.assertIn("feed1", kwargs["params"]["feedNames"])

        # Optional: check start/end params
        self.assertIn("from", kwargs["params"])
        self.assertIn("to", kwargs["params"])

    @patch.object(WellClient, "get_feeds")
    @patch.object(WellClient, "fetch_data")
    def test_well_get_data(self, mock_fetch, mock_get_feeds):
        """Test Well.get_data returns expected pivoted data using 'ALL' feeds."""

        # get_feeds will be called because feeds="ALL"
        mock_get_feeds.return_value = ["waterLevelReference"]

        # fetch_data returns raw data shaped for _pivot_data
        mock_fetch.return_value = [
            {
                "feedName": "waterLevelReference",
                "readings": [{"timestamp": 456, "data": 1.23}],
            }
        ]

        client = WellClient(authorization={"Authorization": "fake-token"})
        well = Well("guid123", "TestWell", client)

        data = well.get_data(feeds="ALL")  # <-- feeds="ALL" triggers get_feeds()

        mock_get_feeds.assert_called_once()  # Now it will be called
        mock_fetch.assert_called_once()

        expected = [{"timestamp": 456, "waterLevelReference": 1.23}]
        assert data == expected

    @patch.object(WellClient, "_request")
    def test_get_feeds_filters_missing_name(self, mock_request):
        """Ensure get_feeds only returns feed names that exist in response."""
        client = WellClient(authorization={"Authorization": "Bearer token"})
        mock_request.return_value = [{"name": "a"}, {"other": "b"}]
        feeds = client.get_feeds("well123")
        self.assertEqual(feeds, ["a"])

    @patch.object(WellClient, "_request")
    def test_get_wells_for_project_returns_list(self, mock_request):
        """Ensure get_wells_for_project returns all wells with correct params."""
        client = WellClient(authorization={"Authorization": "Bearer token"})
        mock_request.return_value = [{"guid": "w1"}, {"guid": "w2"}]
        wells = client.get_assets_for_project("proj123", "well")
        mock_request.assert_called_once_with(
            f"{DEFAULT_URL}/api/data/assets",
            params={"typeGuid": "GWM_WELL", "scopeGuid": "proj123"},
        )
        self.assertEqual(len(wells), 2)
