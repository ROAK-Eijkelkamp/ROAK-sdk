import unittest
import pytest
import requests
from roak_sdk.auth import Auth
from roak_sdk.clients.well_client import WellClient
from roak_sdk.semantics.assets.well import Well
import os


@pytest.fixture(scope="session")
def auth_headers():
    PASSWORD = os.getenv("ROAK_PASSWORD")
    USERNAME = "e.garbov@eijkelkamp.com"
    auth = Auth(user=USERNAME, password=PASSWORD)
    return auth.authenticate()


@pytest.fixture
def client(auth_headers):
    return WellClient(authorization=auth_headers)


@pytest.mark.integration
class TestClientWellDataIntegration:

    valid_well_guid = "548006ef-28bd-4b0e-9f17-8234e1db9f64"
    invalid_well_guid = "00000000-0000-0000-0000-000000000000"

    def test_get_well_data_success(self, client):
        """Well data should return pivoted feed dictionaries."""
        well_asset = Well(self.valid_well_guid, "Test Well", client)
        result = well_asset.get_data()  # resolves feeds automatically

        assert isinstance(result, list)
        assert len(result) >= 1

        first_record = result[0]

        # Pivoted format keys
        assert "timestamp" in first_record
        assert any(k != "timestamp" for k in first_record.keys())  # at least one feed

        for feed, value in first_record.items():
            if feed != "timestamp":
                assert isinstance(
                    value, (int, float, str, type(None))
                )  # feed value type

    def test_get_well_data_invalid_guid(self, client):
        """Invalid well GUID should raise HTTPError from API"""
        well_asset = Well(self.invalid_well_guid, "Test Well", client)
        with pytest.raises(requests.exceptions.HTTPError):
            well_asset.get_data()  # resolves feeds, then calls fetch_data

    def test_get_well_data_invalid_token(self):
        """Force invalid token → expect HTTPError"""
        bad_client = WellClient(authorization={"authorization": "Bearer INVALID"})
        well_asset = Well(self.valid_well_guid, "Test Well", bad_client)
        with pytest.raises(requests.exceptions.HTTPError):
            well_asset.get_data()
