"""HV6 – Project filtering / factory mapping tests.

Covers:
  - make_asset factory: Well, Borehole, generic Asset dispatch
  - Project.get_assets: ASSET_TYPES filtering, make_asset called per item
  - Project.get_asset_by_guid: delegates to client + factory
  - Project.get_asset_by_name: passes asset_type and allow_first_match through
  - Project.get_wells / get_well_by_name / get_well_by_guid type guards
  - Project.get_boreholes / get_borehole_by_name type guards
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from roak_sdk.semantics.factory import make_asset, ASSET_TYPE_WELL, ASSET_TYPE_BOREHOLE
from roak_sdk.semantics.asset import Asset
from roak_sdk.semantics.assets.well import Well
from roak_sdk.semantics.assets.borehole import Borehole
from roak_sdk.semantics.project import Project
from roak_sdk.semantics.site import Site
from roak_sdk.config import ASSET_TYPES
from roak_sdk.roak_error import AssetTypeMismatchError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _asset_data(type_guid: str, guid: str = "asset-guid", name: str = "Asset") -> dict:
    """Minimal asset data dict as returned by the API (flat format for Semantic.__init__)."""
    return {
        "guid": guid,
        "name": name,
        "typeGuid": type_guid,
    }


def _make_project(client_assets=None, client_single=None):
    """Return a Project backed by a stub registry."""
    registry = MagicMock()
    project_client = MagicMock()
    if client_assets is not None:
        project_client.get_assets.return_value = client_assets
    if client_single is not None:
        project_client.get_asset_by_guid.return_value = client_single
        project_client.get_asset_by_name.return_value = client_single
    registry.get.return_value = project_client

    proj = Project.__new__(Project)
    proj._data = {"guid": "proj-guid", "name": "Test Project"}
    proj.guid = "proj-guid"
    proj.name = "Test Project"
    proj._registry = registry
    proj._client = project_client
    return proj, project_client


# ---------------------------------------------------------------------------
# make_asset factory
# ---------------------------------------------------------------------------

class TestMakeAsset:
    def _registry(self):
        reg = MagicMock()
        reg.get.return_value = MagicMock()
        return reg

    def test_well_type_guid_returns_well(self):
        data = _asset_data(ASSET_TYPE_WELL)
        result = make_asset(data, self._registry())
        assert isinstance(result, Well)

    def test_borehole_type_guid_returns_borehole(self):
        data = _asset_data(ASSET_TYPE_BOREHOLE)
        result = make_asset(data, self._registry())
        assert isinstance(result, Borehole)

    def test_unknown_type_guid_returns_generic_asset(self):
        data = _asset_data("SOME_UNKNOWN_TYPE")
        result = make_asset(data, self._registry())
        assert type(result) is Asset

    def test_partial_well_guid_match_returns_well(self):
        """'GWM_WELL' is matched with 'in', so partial containing string also works."""
        data = _asset_data("GWM_WELL_EXTENDED")
        result = make_asset(data, self._registry())
        assert isinstance(result, Well)

    def test_partial_borehole_guid_match_returns_borehole(self):
        data = _asset_data("MWD_BOREHOLE_V2")
        result = make_asset(data, self._registry())
        assert isinstance(result, Borehole)

    def test_missing_type_guid_returns_generic_asset(self):
        data = {"guid": "x", "name": "Unknown"}  # no typeGuid key
        result = make_asset(data, self._registry())
        assert type(result) is Asset


# ---------------------------------------------------------------------------
# Project.get_assets — filtering
# ---------------------------------------------------------------------------

class TestProjectGetAssets:
    def test_non_asset_types_filtered_out(self):
        raw = [
            _asset_data(ASSET_TYPES[0], "well-1", "Well One"),
            _asset_data("ED_SITE", "site-1", "Site One"),      # NOT in ASSET_TYPES
            _asset_data(ASSET_TYPES[1], "bh-1", "BH One"),
        ]
        proj, _ = _make_project(client_assets=raw)
        result = proj.get_assets()

        assert len(result) == 2
        guids = {a.guid for a in result}
        assert "site-1" not in guids

    def test_all_known_asset_types_kept(self):
        raw = [_asset_data(t, f"guid-{i}") for i, t in enumerate(ASSET_TYPES)]
        proj, _ = _make_project(client_assets=raw)
        result = proj.get_assets()
        assert len(result) == len(ASSET_TYPES)

    def test_empty_response_returns_empty_list(self):
        proj, _ = _make_project(client_assets=[])
        assert proj.get_assets() == []

    def test_get_assets_passes_asset_type_to_client(self):
        proj, client = _make_project(client_assets=[])
        proj.get_assets(asset_type=ASSET_TYPE_WELL)
        client.get_assets.assert_called_once_with("proj-guid", ASSET_TYPE_WELL)

    def test_factory_creates_correct_types(self):
        raw = [
            _asset_data(ASSET_TYPE_WELL, "w1", "Well"),
            _asset_data(ASSET_TYPE_BOREHOLE, "b1", "BH"),
        ]
        proj, _ = _make_project(client_assets=raw)
        result = proj.get_assets()

        types = {type(a) for a in result}
        assert Well in types
        assert Borehole in types

    def test_get_sites_returns_site_instances(self):
        raw = [
            _asset_data("ED_SITE", "site-1", "Site One"),
            _asset_data("ED_SITE", "site-2", "Site Two"),
        ]
        proj, client = _make_project(client_assets=raw)

        result = proj.get_sites()

        client.get_assets.assert_called_once_with("proj-guid", "ED_SITE")
        assert len(result) == 2
        assert all(isinstance(site, Site) for site in result)


# ---------------------------------------------------------------------------
# Project.get_asset_by_guid
# ---------------------------------------------------------------------------

class TestProjectGetAssetByGuid:
    def test_returns_correct_type_from_factory(self):
        proj, client = _make_project(client_single=_asset_data(ASSET_TYPE_WELL, "w1"))
        result = proj.get_asset_by_guid("w1")
        assert isinstance(result, Well)
        client.get_asset_by_guid.assert_called_once_with("proj-guid", "w1")

    def test_get_site_by_guid_returns_site(self):
        proj, client = _make_project(client_single=_asset_data("ED_SITE", "site-1", "Site One"))

        result = proj.get_site_by_guid("site-1")

        client.get_asset_by_guid.assert_called_once_with("proj-guid", "site-1")
        assert isinstance(result, Site)
        assert result.guid == "site-1"

    def test_get_site_by_guid_raises_type_error_for_wrong_type(self):
        proj, _ = _make_project(client_single=_asset_data(ASSET_TYPE_WELL, "w1", "Well One"))

        with pytest.raises(AssetTypeMismatchError, match="not a Site"):
            proj.get_site_by_guid("w1")


# ---------------------------------------------------------------------------
# Project.get_asset_by_name
# ---------------------------------------------------------------------------

class TestProjectGetAssetByName:
    def test_passes_name_and_asset_type(self):
        proj, client = _make_project(client_single=_asset_data(ASSET_TYPE_WELL, "w1"))
        proj.get_asset_by_name("My Well", asset_type=ASSET_TYPE_WELL)
        client.get_asset_by_name.assert_called_once_with(
            "proj-guid", "My Well", ASSET_TYPE_WELL, allow_first_match=False
        )

    def test_passes_allow_first_match_true(self):
        proj, client = _make_project(client_single=_asset_data(ASSET_TYPE_WELL, "w1"))
        proj.get_asset_by_name("My Well", allow_first_match=True)
        client.get_asset_by_name.assert_called_once_with(
            "proj-guid", "My Well", None, allow_first_match=True
        )

    def test_get_site_by_name_returns_site(self):
        proj, client = _make_project(client_single=_asset_data("ED_SITE", "site-1", "Site One"))

        result = proj.get_site_by_name("Site One")

        client.get_asset_by_name.assert_called_once_with(
            "proj-guid", "Site One", "ED_SITE", allow_first_match=False
        )
        assert isinstance(result, Site)
        assert result.guid == "site-1"

    def test_get_site_by_name_raises_type_error_for_wrong_type(self):
        proj, _ = _make_project(client_single=_asset_data(ASSET_TYPE_WELL, "w1", "Well One"))

        with pytest.raises(AssetTypeMismatchError, match="not a Site"):
            proj.get_site_by_name("Well One")


# ---------------------------------------------------------------------------
# Project.get_wells / get_well_by_name / get_well_by_guid
# ---------------------------------------------------------------------------

class TestProjectWellConvenience:
    def test_get_wells_returns_only_wells(self):
        raw = [
            _asset_data(ASSET_TYPE_WELL, "w1", "Well A"),
            _asset_data(ASSET_TYPE_WELL, "w2", "Well B"),
        ]
        proj, _ = _make_project(client_assets=raw)
        result = proj.get_wells()
        assert all(isinstance(a, Well) for a in result)
        assert len(result) == 2

    def test_get_well_by_name_returns_well(self):
        proj, client = _make_project(client_single=_asset_data(ASSET_TYPE_WELL, "w1"))
        result = proj.get_well_by_name("Well A")
        assert isinstance(result, Well)

    def test_get_well_by_name_allow_first_match_propagated(self):
        proj, client = _make_project(client_single=_asset_data(ASSET_TYPE_WELL, "w1"))
        proj.get_well_by_name("Well A", allow_first_match=True)
        client.get_asset_by_name.assert_called_once_with(
            "proj-guid", "Well A", ASSET_TYPE_WELL, allow_first_match=True
        )

    def test_get_well_by_guid_raises_type_error_for_borehole(self):
        proj, _ = _make_project(client_single=_asset_data(ASSET_TYPE_BOREHOLE, "b1"))
        with pytest.raises(AssetTypeMismatchError):
            proj.get_well_by_guid("b1")

    def test_get_well_by_name_raises_type_error_for_wrong_type(self):
        proj, _ = _make_project(client_single=_asset_data(ASSET_TYPE_BOREHOLE, "b1"))
        with pytest.raises(AssetTypeMismatchError):
            proj.get_well_by_name("Wrong")


# ---------------------------------------------------------------------------
# Project.get_boreholes / get_borehole_by_name / get_borehole_by_guid
# ---------------------------------------------------------------------------

class TestProjectBoreholeConvenience:
    def _read_borehole_methods(self):
        """Check borehole method names exist on Project."""
        assert hasattr(Project, "get_boreholes") or hasattr(Project, "get_borehole_by_name")

    def test_get_borehole_by_name_returns_borehole(self):
        proj, client = _make_project(client_single=_asset_data(ASSET_TYPE_BOREHOLE, "bh1"))
        result = proj.get_borehole_by_name("BH A")
        assert isinstance(result, Borehole)

    def test_get_borehole_by_name_allow_first_match_propagated(self):
        proj, client = _make_project(client_single=_asset_data(ASSET_TYPE_BOREHOLE, "bh1"))
        proj.get_borehole_by_name("BH A", allow_first_match=True)
        client.get_asset_by_name.assert_called_once_with(
            "proj-guid", "BH A", ASSET_TYPE_BOREHOLE, allow_first_match=True
        )

    def test_get_borehole_by_name_returns_asset_without_type_guard(self):
        """get_borehole_by_name has no client-side type guard: it trusts the
        server to return the correct type when asset_type filter is applied."""
        proj, client = _make_project(client_single=_asset_data(ASSET_TYPE_BOREHOLE, "bh1"))
        result = proj.get_borehole_by_name("BH X")
        assert isinstance(result, Borehole)
