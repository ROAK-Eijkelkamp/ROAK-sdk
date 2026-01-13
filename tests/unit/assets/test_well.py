import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from roak_sdk.semantics.assets.well import Well
from roak_sdk.clients.well_client import WellClient


WELL_GUID = "test-guid"


class TestWellAsset(unittest.TestCase):
    """Unit tests for the Well asset wrapper."""

    def setUp(self):
        """Set up a mock client and Well object."""
        self.mock_client = Mock(spec=WellClient)
        self.well = Well(WELL_GUID, "TestWell", self.mock_client)

    @patch.object(WellClient, "fetch_data")
    def test_get_data_returns_expected(self, mock_fetch):
        """Test get_data calls fetch_data with correct parameters and returns results."""

        # Mocked data in the exact format expected by _pivot_data
        mock_fetch.return_value = [
            {
                "feedName": "waterLevelReference",
                "values": [{"timestamp": 456, "value": 1.23}],
            }
        ]

        client = WellClient(authorization={"Authorization": "Bearer fake-token"})
        well = Well("guid123", "TestWell", client)

        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=1)

        data = well.get_data(start=start_dt, end=end_dt)
        client.fetch_data.assert_called_once()  # type: ignore

        # Expected pivoted output
        expected = well._pivot_data(mock_fetch.return_value)
        assert data == expected

    @patch.object(WellClient, "fetch_data")
    def test_get_data_with_no_params_uses_defaults(self, mock_fetch):
        """Test get_data works with default time and feeds when no parameters are provided."""

        # Correct feedName key for _pivot_data
        mock_fetch.return_value = [{"feedName": "diverPressure", "values": []}]

        # Replace self.well's client fetch_data with the mock
        self.well._client.fetch_data = mock_fetch

        data = self.well.get_data()

        # Assert the mock was called
        mock_fetch.assert_called_once()

        # Assert the returned data matches pivot output
        expected = self.well._pivot_data(mock_fetch.return_value)
        assert data == expected

    def test_standard_feeds_property_exists(self):
        """Ensure the Well asset has a STANDARD_FEEDS list."""
        self.assertTrue(hasattr(self.well, "STANDARD_FEEDS"))
        self.assertIn("waterLevelReference", self.well.STANDARD_FEEDS)
