from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from roak_sdk.semantics.project import Project
from roak_sdk.semantics.site import Site


def _make_site() -> Site:
    registry = MagicMock()
    registry.get.return_value = MagicMock()
    data = {
        "guid": "site-guid-1",
        "name": "Site Alpha",
        "typeGuid": "ED_SITE",
    }
    return Site(data, registry)


def test_site_is_project_subclass() -> None:
    assert issubclass(Site, Project)


def test_get_sites_raises_not_implemented_error() -> None:
    site = _make_site()

    with pytest.raises(NotImplementedError, match="Sites cannot contain child sites"):
        site.get_sites()


def test_get_sites_raises_without_client_calls() -> None:
    site = _make_site()
    site._client = MagicMock()

    with pytest.raises(NotImplementedError):
        site.get_sites()

    assert site._client.mock_calls == []


def test_inherited_project_methods_still_work_get_assets() -> None:
    site = _make_site()
    site._client = MagicMock()
    site._client.get_assets.return_value = []

    result = site.get_assets()

    assert result == []
    site._client.get_assets.assert_called_once_with("site-guid-1", None)


def test_inherited_well_lookup_behavior_available_on_site() -> None:
    site = _make_site()
    site._client = MagicMock()
    site._client.get_asset_by_name.return_value = {
        "guid": "well-1",
        "name": "Well One",
        "typeGuid": "GWM_WELL",
    }

    well = site.get_well_by_name("Well One", allow_first_match=True)

    assert well.guid == "well-1"
    site._client.get_asset_by_name.assert_called_once_with(
        "site-guid-1",
        "Well One",
        "GWM_WELL",
        allow_first_match=True,
    )
