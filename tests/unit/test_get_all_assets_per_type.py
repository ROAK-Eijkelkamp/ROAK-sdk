import unittest
from unittest.mock import patch
from roak_sdk.clients.asset_client import AssetClient


class TestClientAssets(unittest.TestCase):

    @patch.object(AssetClient, "_request")
    def test_multiple_types_combined(self, mock_request):
        mock_request.side_effect = [
            [{"guid": "a1", "name": "Rigs"}],
            [{"guid": "a2", "name": "Modems"}],
        ]
        client = AssetClient(authorization={"Authorization": "Bearer fake-token"})
        type_guids = ["MWD_RIGS", "GWM_MODEMS"]

        result = client.get_all_assets_per_type(type_guids)
        self.assertEqual(len(result), 2)
        self.assertTrue(any(a["guid"] == "a1" for a in result))
        self.assertTrue(any(a["guid"] == "a2" for a in result))

    @patch.object(AssetClient, "_request")
    def test_duplicate_removal(self, mock_request):
        mock_request.side_effect = [
            [{"guid": "dup", "name": "Rigs"}],
            [{"guid": "dup", "name": "Rigs"}],
        ]
        client = AssetClient(authorization={"Authorization": "Bearer fake-token"})
        result = client.get_all_assets_per_type(["MWD_RIGS", "MWD_RIGS"])
        self.assertEqual(len(result), 1)

    @patch.object(AssetClient, "_request")
    def test_empty_type_results(self, mock_request):
        mock_request.side_effect = [[], [{"guid": "a2", "name": "Modems"}]]
        client = AssetClient(authorization={"Authorization": "Bearer fake-token"})
        result = client.get_all_assets_per_type(["MWD_RIGS", "GWM_MODEMS"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["guid"], "a2")

    @patch.object(AssetClient, "_request")
    def test_all_empty_types(self, mock_request):
        mock_request.side_effect = [[], []]
        client = AssetClient(authorization={"Authorization": "Bearer fake-token"})
        result = client.get_all_assets_per_type(["MWD_RIGS", "GWM_MODEMS"])
        self.assertEqual(result, [])

    @patch.object(AssetClient, "_request")
    def test_single_type(self, mock_request):
        mock_request.return_value = [{"guid": "x1", "name": "Rigs"}]
        client = AssetClient(authorization={"Authorization": "Bearer fake-token"})
        result = client.get_all_assets_per_type(["MWD_RIGS"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["guid"], "x1")

    @patch.object(AssetClient, "_request")
    def test_handles_http_error(self, mock_request):
        mock_request.side_effect = Exception("Server Error")
        client = AssetClient(authorization={"Authorization": "Bearer fake-token"})
        type_guids = ["MWD_RIGS", "GWM_WELL"]

        with self.assertRaises(Exception) as context:
            client.get_all_assets_per_type(type_guids)
        self.assertIn("Server Error", str(context.exception))


if __name__ == "__main__":
    unittest.main()
