import unittest
from unittest.mock import patch
from roak_sdk.clients.generic_asset_client import GenericAssetClient
from roak_sdk.semantics.assets.generic_asset import GenericAsset
import pytest


class TestGenericAssetClient(unittest.TestCase):

    @patch.object(GenericAssetClient, "_request")
    def test_fetch_data_with_feeds_and_time(self, mock_request):
        """Ensure fetch_data constructs URL and params correctly when feeds/start/end are provided."""
        client = GenericAssetClient(authorization={"Authorization": "Bearer token"})

        # Only one _request call happens because feeds are provided
        mock_request.return_value = [{"feedName": "Temperature", "readings": []}]

        asset = GenericAsset("generic123", "Test Asset", client)

        feeds = ["Temperature"]
        start = 1000
        end = 2000

        result = asset.get_data(feeds=feeds, start=start, end=end)

        assert result == [{"feedName": "Temperature", "readings": []}]
        assert mock_request.call_count == 1

        # Check that feedNames and time params are in the request
        call_kwargs = mock_request.call_args[1]  # kwargs of the single _request call
        params = call_kwargs["params"]
        assert params["feedNames"] == ",".join(feeds)
        assert params["from"] == str(start)
        assert params["to"] == str(end)

    @patch.object(GenericAssetClient, "_request")
    def test_generic_asset_get_data_raises_for_none_feeds(self, mock_request):
        client = GenericAssetClient(authorization={"Authorization": "Bearer token"})
        asset = GenericAsset("generic123", "Generic", client)

        with self.assertRaises(ValueError) as ctx:
            asset.get_data(feeds=None)

        assert "requires you to provide specific feeds" in str(ctx.exception)

    @patch.object(GenericAssetClient, "_request")
    def test_fetch_data_empty_feed_list(self, mock_request):
        """Ensure empty list results in no 'feedNames' parameter."""
        client = GenericAssetClient(authorization={"Authorization": "Bearer token"})
        mock_request.return_value = []

        client.fetch_data("generic123", feeds=[])

        params = mock_request.call_args.kwargs["params"]
        self.assertEqual(params.get("feedNames"), "")

    @patch.object(GenericAssetClient, "_request")
    def test_fetch_data_invalid_feeds_type(self, mock_request):
        """Ensure invalid feed types (non-string, non-list) raise TypeError."""
        client = GenericAssetClient(authorization={"Authorization": "Bearer token"})

        with self.assertRaises(TypeError):
            client.fetch_data("generic123", feeds=123)  # type: ignore

    @patch.object(GenericAssetClient, "_request")
    def test_fetch_data_api_error_propagates(self, mock_request):
        """Ensure that request errors bubble up to the caller."""
        client = GenericAssetClient(authorization={"Authorization": "Bearer token"})
        mock_request.side_effect = RuntimeError("API failure")

        asset = GenericAsset("generic123", "Test Asset", client)

        # Provide feeds explicitly to satisfy fetch_data
        with pytest.raises(RuntimeError) as exc:
            asset.get_data(feeds=["Temperature"])

        assert str(exc.value) == "API failure"
