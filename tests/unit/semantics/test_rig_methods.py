"""
Unit tests for Rig class methods.
"""
from unittest.mock import MagicMock

import pytest

from roak_sdk.semantics.devices.rig import Rig
from roak_sdk.semantics.assets.borehole import Borehole
from roak_sdk.clients.rig_client import RigClient
from roak_sdk.roak_error import AssetNotFoundError
from tests.conftest import StubRegistry


class TestRigBoreholeRetrieval:
    """Tests for Rig borehole retrieval methods."""

    def test_get_borehole_by_guid_returns_matching_borehole(self):
        """Test that get_borehole_by_guid returns the correct borehole."""
        registry = StubRegistry()
        rig_data = {"guid": "rig-1", "name": "Rig A", "typeGuid": "MWD_CRS_S"}
        rig = Rig(rig_data, registry)
        
        # Mock the rig client to return boreholes
        rig._rig_client = MagicMock(spec=RigClient)
        rig._rig_client.get_boreholes.return_value = [
            {"borehole": {"guid": "bh-1", "name": "Borehole 1", "typeGuid": "MWD_BOREHOLE"}},
            {"borehole": {"guid": "bh-2", "name": "Borehole 2", "typeGuid": "MWD_BOREHOLE"}},
            {"borehole": {"guid": "bh-3", "name": "Borehole 3", "typeGuid": "MWD_BOREHOLE"}},
        ]
        
        # Get borehole by GUID
        borehole = rig.get_borehole_by_guid("bh-2")
        
        assert isinstance(borehole, Borehole)
        assert borehole.guid == "bh-2"
        assert borehole.name == "Borehole 2"

    def test_get_borehole_by_guid_raises_when_not_found(self):
        """Test that get_borehole_by_guid raises ValueError when GUID not found."""
        registry = StubRegistry()
        rig_data = {"guid": "rig-1", "name": "Rig A", "typeGuid": "MWD_CRS_S"}
        rig = Rig(rig_data, registry)
        
        # Mock the rig client to return boreholes
        rig._rig_client = MagicMock(spec=RigClient)
        rig._rig_client.get_boreholes.return_value = [
            {"borehole": {"guid": "bh-1", "name": "Borehole 1", "typeGuid": "MWD_BOREHOLE"}},
        ]
        
        # Attempt to get non-existent borehole
        with pytest.raises(AssetNotFoundError, match="Borehole with GUID 'bh-999' not found in rig 'Rig A'"):
            rig.get_borehole_by_guid("bh-999")

    def test_get_borehole_by_guid_with_empty_boreholes(self):
        """Test get_borehole_by_guid when rig has no boreholes."""
        registry = StubRegistry()
        rig_data = {"guid": "rig-1", "name": "Rig A", "typeGuid": "MWD_CRS_S"}
        rig = Rig(rig_data, registry)
        
        # Mock the rig client to return empty list
        rig._rig_client = MagicMock(spec=RigClient)
        rig._rig_client.get_boreholes.return_value = []
        
        # Attempt to get borehole from empty rig
        with pytest.raises(AssetNotFoundError, match="Borehole with GUID 'bh-1' not found in rig 'Rig A'"):
            rig.get_borehole_by_guid("bh-1")
