import unittest
from unittest.mock import patch
from roak_sdk.clients.asset_client import AssetClient


class TestClientAssetsBase(unittest.TestCase):

    @patch.object(AssetClient, "_request")
    def test_correct_url_and_params(self, mock_request):
        mock_request.return_value = []
        client = AssetClient(authorization={"Authorization": "Bearer fake-token"})

        result = client.get_assets_base(
            type_guid="MWD_RIGS", scope_guid="ROOT_1", query="test"
        )

        mock_request.assert_called_once()
        self.assertEqual(result, [])

    @patch.object(AssetClient, "_request")
    def test_empty_response(self, mock_request):
        mock_request.return_value = []
        client = AssetClient(authorization={"Authorization": "Bearer fake-token"})

        result = client.get_assets_base()
        self.assertEqual(result, [])

    @patch.object(AssetClient, "_request")
    def test_single_asset_dict(self, mock_request):
        mock_request.return_value = {"guid": "123", "name": "Rigs"}
        client = AssetClient(authorization={"Authorization": "Bearer fake-token"})

        result = client.get_assets_base()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["guid"], "123")

    @patch.object(AssetClient, "_request")
    def test_dict_values_conversion(self, mock_request):
        mock_request.return_value = {
            "modem": {"guid": "m1", "name": "Modem 1"},
            "rig": {"guid": "r1", "name": "Rig 1"},
        }
        client = AssetClient(authorization={"Authorization": "Bearer fake-token"})

        result = client.get_assets_base()
        self.assertEqual(len(result), 2)
        self.assertTrue(any(a["guid"] == "m1" for a in result))
        self.assertTrue(any(a["guid"] == "r1" for a in result))

    @patch.object(AssetClient, "_request")
    def test_non_json_response_raises(self, mock_request):
        mock_request.side_effect = Exception("Invalid JSON")
        client = AssetClient(authorization={"Authorization": "Bearer fake-token"})

        with self.assertRaises(Exception):
            client.get_assets_base()

    @patch.object(AssetClient, "_request")
    def test_http_error_response(self, mock_request):
        mock_request.side_effect = Exception("Server Error")
        client = AssetClient(authorization={"Authorization": "Bearer fake-token"})

        with self.assertRaises(Exception) as context:
            client.get_assets_base(type_guid="MWD_RIGS")

        self.assertIn("Server Error", str(context.exception))


if __name__ == "__main__":
    unittest.main()
