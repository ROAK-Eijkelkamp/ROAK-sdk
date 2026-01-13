import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from roak_sdk.semantics.assets.generic_asset import GenericAsset
from roak_sdk.clients.generic_asset_client import GenericAssetClient
from roak_sdk.auth import DEFAULT_URL


class TestGenericAsset(unittest.TestCase):

    def test_get_data_calls_client(self):
        """Ensure get_data delegates to client.fetch_data with correct args and returns the response."""
        mock_client = MagicMock()
        mock_client.fetch_data.return_value = [{"feedName": "ALL", "readings": []}]

        asset = GenericAsset("guid123", "MyAsset", mock_client)
        result = asset.get_data(feeds="ALL")

        self.assertEqual(mock_client.fetch_data.call_count, 1)

        args, kwargs = mock_client.fetch_data.call_args
        self.assertEqual(args[0], "guid123")
        self.assertIn("start", kwargs)
        self.assertIn("end", kwargs)
        # Don't assert type if None is allowed
        self.assertEqual(result, [{"feedName": "ALL", "readings": []}])

    def test_get_feeds_calls_client(self):
        """Ensure get_feeds delegates to client.get_feeds and returns the correct feed list."""
        mock_client = MagicMock()
        mock_client.get_feeds.return_value = ["feedA"]

        asset = GenericAsset("guid123", "AName", mock_client)
        result = asset.get_feeds()

        mock_client.get_feeds.assert_called_once_with("guid123")
        self.assertEqual(result, ["feedA"])

    def test_resolve_feeds_all(self):
        """Ensure passing 'ALL' triggers get_feeds()."""
        mock_client = MagicMock()
        mock_client.get_feeds.return_value = ["A", "B"]

        asset = GenericAsset("guid123", "AName", mock_client)
        result = asset._resolve_feeds("ALL")

        self.assertEqual(result, ["A", "B"])

    def test_resolve_feeds_none_raises(self):
        """Ensure GenericAsset raises when no feeds are provided."""
        asset = GenericAsset("guid123", "AName", MagicMock())

        with self.assertRaises(ValueError):
            asset._resolve_feeds(None)

    def test_resolve_feeds_custom_list(self):
        """Ensure custom feed list is returned unchanged."""
        asset = GenericAsset("guid123", "AName", MagicMock())
        result = asset._resolve_feeds(["ABC", "DEF"])

        self.assertEqual(result, ["ABC", "DEF"])
