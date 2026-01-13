import unittest
from unittest.mock import patch
from roak_sdk.roak import Roak
from roak_sdk.auth import Auth
from roak_sdk.clients.rig_client import RigClient
from roak_sdk.clients.project_client import ProjectClient
from roak_sdk.clients.asset_client import AssetClient
from roak_sdk.semantics.assets.borehole import Borehole
from roak_sdk.semantics.project import Project


class TestRoak(unittest.TestCase):
    """Unit tests for the Roak SDK main class."""

    @patch.object(Auth, "authenticate", return_value={"authorization": "Bearer fake"})
    @patch("roak_sdk.roak.Auth")
    @patch("roak_sdk.roak.WellClient")
    @patch("roak_sdk.roak.RigClient")
    @patch("roak_sdk.roak.ProjectClient")
    @patch("roak_sdk.roak.AssetClient")
    def test_init_happy_path(
        self,
        mock_asset,
        mock_project,
        mock_rig,
        mock_well,
        mock_auth,
        mock_authenticate,
    ):
        """Test that initialization sets headers and clients correctly."""
        auth_instance = mock_auth.return_value
        auth_instance.authenticate.return_value = {"authorization": "Bearer token"}

        sdk = Roak(user="test", password="pass")
        self.assertEqual(sdk.headers["authorization"], "Bearer token")
        mock_well.assert_called_with(
            sdk.headers, base_url=mock_auth.return_value.base_url
        )
        mock_rig.assert_called_with(
            sdk.headers, base_url=mock_auth.return_value.base_url
        )
        mock_project.assert_called_with(
            sdk.headers, base_url=mock_auth.return_value.base_url
        )
        mock_asset.assert_called_with(
            sdk.headers, base_url=mock_auth.return_value.base_url
        )

    @patch.object(Auth, "authenticate", return_value={"authorization": "Bearer fake"})
    @patch.object(
        Auth, "refresh_access_token", return_value={"authorization": "Bearer newtoken"}
    )
    @patch("roak_sdk.roak.WellClient")
    @patch("roak_sdk.roak.RigClient")
    @patch("roak_sdk.roak.ProjectClient")
    def test_refresh_tokens_updates_all_clients(
        self, mock_project, mock_rig, mock_well, mock_refresh, mock_authenticate
    ):
        """Test that refresh_tokens updates headers in all clients."""
        sdk = Roak(user="u", password="p")
        sdk.headers = {"authorization": "Bearer old"}
        sdk.well_client = mock_well.return_value
        sdk.rig_client = mock_rig.return_value
        sdk.project_client = mock_project.return_value

        sdk.refresh_tokens()

        self.assertEqual(sdk.headers["authorization"], "Bearer newtoken")
        self.assertEqual(sdk.well_client.headers["authorization"], "Bearer newtoken")
        self.assertEqual(sdk.project_client.headers["authorization"], "Bearer newtoken")
        self.assertEqual(sdk.rig_client.headers["authorization"], "Bearer newtoken")

    @patch.object(Auth, "authenticate", return_value={"authorization": "Bearer fake"})
    @patch.object(ProjectClient, "get_project_data")
    def test_get_project_guid_raises(self, mock_get_project_data, mock_authenticate):
        """Test get_project_guid raises ValueError if project not found."""
        mock_get_project_data.return_value = []
        sdk = Roak(user="u", password="p")
        with self.assertRaises(ValueError):
            sdk.get_project_guid("nonexistent")

    @patch.object(Auth, "authenticate", return_value={"authorization": "Bearer fake"})
    @patch("roak_sdk.roak.WellClient")
    def test_get_well_returns_object(self, mock_well, mock_authenticate):
        """Test get_well returns a Well object."""
        sdk = Roak(user="u", password="p")
        well = sdk.get_well("guid123")
        self.assertEqual(well._guid, "guid123")

    @patch.object(Auth, "authenticate", return_value={"authorization": "Bearer fake"})
    @patch.object(RigClient, "get_rig")
    def test_get_rig_returns_object(self, mock_get_rig, mock_authenticate):
        """Test get_rig returns object from RigClient."""
        sdk = Roak(user="u", password="p")
        mock_get_rig.return_value = "RIG_OBJECT"
        rig = sdk.get_rig("rig123")
        self.assertEqual(rig, "RIG_OBJECT")

    @patch.object(Auth, "authenticate", return_value={"authorization": "Bearer fake"})
    @patch.object(RigClient, "__init__", lambda self, headers, base_url=None: None)
    @patch.object(AssetClient, "get_assets_base")
    @patch.object(AssetClient, "deduplicate_assets")
    def test_get_boreholes_returns_list(
        self, mock_dedupe, mock_get_assets, mock_authenticate
    ):
        """Test get_boreholes returns list of Borehole objects."""
        mock_get_assets.return_value = [{"guid": "b1", "name": "B1"}]
        mock_dedupe.return_value = [{"guid": "b1", "name": "B1"}]
        sdk = Roak(user="u", password="p")
        boreholes = sdk.get_boreholes()
        self.assertIsInstance(boreholes, list)
        self.assertIsInstance(boreholes[0], Borehole)
