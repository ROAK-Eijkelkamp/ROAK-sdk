import unittest
from unittest.mock import patch
from roak_sdk.clients.rig_client import RigClient
from roak_sdk.semantics.assets.borehole import Borehole
from roak_sdk.auth import DEFAULT_URL
from unittest.mock import MagicMock

BOREHOLE_GUID = "test-borehole-guid"


class TestBoreholeDepthData(unittest.TestCase):
    """Tests Borehole depth data and RigClient.get_depth_data_raw."""

    @patch.object(RigClient, "_request")
    def test_get_depth_data_raw_returns_json(self, mock_request):
        """Checks that get_depth_data_raw returns the raw JSON data."""
        fake_response = [
            {
                "name": "DepthFeed1",
                "unitName": "Meter",
                "unitSymbol": "m",
                "values": [
                    {"time": 1000, "depth": 0.0, "value": "OK"},
                    {"time": 2000, "depth": 0.01, "value": "OK"},
                ],
            }
        ]
        mock_request.return_value = fake_response
        client = RigClient(authorization={"Authorization": "fake-token"})

        result = client.get_depth_data_raw(BOREHOLE_GUID)

        mock_request.assert_called_once_with(
            f"{DEFAULT_URL}/api/mwd/boreholes/{BOREHOLE_GUID}/depthData"
        )
        self.assertEqual(result, fake_response)

    @patch.object(RigClient, "_request")
    def test_get_depth_data_raw_empty_values(self, mock_request):
        """Checks that feeds with empty 'values' list are handled."""
        fake_response = [
            {"name": "EmptyFeed", "unitName": "Meter", "unitSymbol": "m", "values": []}
        ]
        mock_request.return_value = fake_response
        client = RigClient(authorization={"Authorization": "fake-token"})

        result = client.get_depth_data_raw(BOREHOLE_GUID)
        self.assertEqual(result, fake_response)

    @patch.object(RigClient, "_request")
    def test_get_depth_data_raw_empty_response(self, mock_request):
        """Checks that an empty API response is handled."""
        mock_request.return_value = []
        client = RigClient(authorization={"Authorization": "fake-token"})

        result = client.get_depth_data_raw(BOREHOLE_GUID)
        self.assertEqual(result, [])

    @patch.object(RigClient, "_request")
    def test_get_depth_data_raw_error_response(self, mock_request):
        """Checks that API error responses are returned as-is."""
        fake_response = {"error": "Unauthorized"}
        mock_request.return_value = fake_response
        client = RigClient(authorization={"Authorization": "fake-token"})

        result = client.get_depth_data_raw(BOREHOLE_GUID)
        self.assertEqual(result, fake_response)

    def test_borehole_get_depth_data_calls_client(self):
        fake_response = [
            {
                "name": "RealDepth",
                "values": [{"time": 456, "value": 1.23, "depth": 1.23}],
            }
        ]

        client = RigClient(authorization={"Authorization": "fake-token"})
        borehole = Borehole(BOREHOLE_GUID, "TestBorehole", client)

        client.get_depth_data_raw = MagicMock(return_value=fake_response)

        result = borehole.get_depth_data()

        client.get_depth_data_raw.assert_called_once_with(BOREHOLE_GUID)

        expected = borehole._pivot_depth_data(fake_response)
        assert result == expected


if __name__ == "__main__":
    unittest.main()
