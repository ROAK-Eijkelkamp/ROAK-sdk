import pytest
import requests
from roak_sdk.auth import Auth
from roak_sdk.clients.rig_client import RigClient
import os


@pytest.fixture(scope="session")
def auth_headers():
    PASSWORD = os.getenv("ROAK_PASSWORD")
    USERNAME = "e.garbov@eijkelkamp.com"
    auth = Auth(user=USERNAME, password=PASSWORD)
    return auth.authenticate()


@pytest.fixture
def client(auth_headers):
    return RigClient(authorization=auth_headers)


@pytest.mark.integration
class TestClientRigDataIntegration:

    valid_borehole_guid = "f8fefd7e-ef7c-4cb8-9bb4-4a0d426f8832"
    invalid_borehole_guid = "00000000-0000-0000-0000-000000000000"

    def test_get_rig_data_all_feeds(self, client):
        """Should return all feeds if no feeds specified"""
        result = client.get_rig_data(self.valid_borehole_guid)
        assert isinstance(result, list)
        assert len(result) >= 1
        # Check one feed has expected keys
        assert "feedName" in result[0]
        assert "readings" in result[0]

    def test_get_rig_data_specific_feeds(self, client):
        """Should return only requested feeds"""
        feeds = ["Inclination x", "Inclination y"]
        result = client.get_rig_data(self.valid_borehole_guid, feeds=feeds)

        assert isinstance(result, list)
        assert len(result) >= 1

        data_feeds = [d["feedName"] for d in result]
        for feed in feeds:
            assert feed in data_feeds

    def test_get_rig_data_invalid_guid(self, client):
        """Invalid borehole GUID should raise HTTPError"""
        with pytest.raises(requests.exceptions.HTTPError):
            client.get_rig_data(self.invalid_borehole_guid)

    def test_get_rig_data_invalid_token(self):
        """Force invalid token → expect HTTPError"""
        bad_client = RigClient(authorization={"authorization": "Bearer INVALID"})
        with pytest.raises(requests.exceptions.HTTPError):
            bad_client.get_rig_data(self.valid_borehole_guid)
