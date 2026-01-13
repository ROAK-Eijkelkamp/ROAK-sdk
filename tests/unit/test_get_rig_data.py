import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
from roak_sdk.clients.rig_client import RigClient
from roak_sdk.semantics.assets.rig import Rig
from roak_sdk.semantics.assets.borehole import Borehole
from roak_sdk.auth import DEFAULT_URL


RIG_GUID = "test-rig-guid"
BOREHOLE_GUID = "test-borehole-guid"


class TestRigData(unittest.TestCase):
    """Tests for rig and borehole data retrieval."""

    @patch.object(RigClient, "_request")
    def test_get_rig_data_with_explicit_feeds_and_time(self, mock_request):
        """Tests Rig.get_data with custom feeds and a specific time range."""
        mock_request.return_value = [{"feedName": "Depth", "readings": []}]
        client = RigClient(authorization={"Authorization": "Bearer fake-token"})
        rig = Rig(RIG_GUID, "TestRig", client)

        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=3)
        feeds = ["Depth", "Bit Force"]

        result = rig.get_data(feeds=feeds, start=start_dt, end=end_dt)

        # _request is now called TWICE:
        # 1) during feed resolution? NO, because feeds are provided → only ONCE
        mock_request.assert_called_once()

        called_url = mock_request.call_args.args[0]
        called_params = mock_request.call_args.kwargs["params"]

        # URL must match
        self.assertEqual(called_url, f"{DEFAULT_URL}/api/data/assets/{RIG_GUID}/data")

        # NEW ASSERTION: dict-based feedNames parameter
        self.assertIn("feedNames", called_params)
        self.assertEqual(called_params["feedNames"], "Depth,Bit Force")

        # Should include time bounds
        self.assertIn("from", called_params)
        self.assertIn("to", called_params)

        # Response must be passed through
        self.assertEqual(result, [{"feedName": "Depth", "readings": []}])

    @patch.object(RigClient, "_request")
    def test_get_rig_data_default_feeds(self, mock_request):
        """Tests Rig.get_data when no feeds are specified (uses STANDARD_FEEDS)."""
        mock_request.return_value = [{"feedName": "Depth", "readings": []}]
        client = RigClient(authorization={"Authorization": "Bearer fake-token"})
        rig = Rig(RIG_GUID, "DefaultFeedRig", client)

        result = rig.get_data()

        # validate _request was called exactly once
        mock_request.assert_called_once()

        called_params = mock_request.call_args.kwargs["params"]

        # NEW: Assert "feedNames" exists in the params dict
        self.assertIn("feedNames", called_params)

        # NEW: STANDARD_FEEDS should be comma-joined
        self.assertIsInstance(called_params["feedNames"], str)
        self.assertGreater(len(called_params["feedNames"]), 0)

        # Verify final returned result
        self.assertEqual(result, [{"feedName": "Depth", "readings": []}])

    @patch.object(RigClient, "_request")
    def test_get_rig_data_empty_response(self, mock_request):
        """Tests Rig.get_data when the API returns an empty list."""
        mock_request.return_value = []
        client = RigClient(authorization={"Authorization": "Bearer fake-token"})
        rig = Rig(RIG_GUID, "EmptyRig", client)

        result = rig.get_data()
        self.assertEqual(result, [])

    @patch.object(RigClient, "_request")
    def test_get_rig_data_invalid_feed_error(self, mock_request):
        """Tests Rig.get_data when the API returns an error."""
        mock_request.return_value = {"error": "Invalid feed name"}
        client = RigClient(authorization={"Authorization": "Bearer fake-token"})
        rig = Rig(RIG_GUID, "ErrorRig", client)

        result = rig.get_data(feeds=["InvalidFeed"])
        self.assertEqual(result, {"error": "Invalid feed name"})


if __name__ == "__main__":
    unittest.main()
