from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from roak_sdk.clients.roak_client import RoakClient
from roak_sdk.roak_error import AmbiguousAssetMatchError, AssetNotFoundError


def test_get_asset_by_name_and_type_raises_when_no_matches() -> None:
    client = RoakClient(headers={}, base_url="https://example.test")
    client._request = lambda url, params=None: []

    with pytest.raises(AssetNotFoundError, match="not found"):
        client.get_asset_by_name_and_type("Alpha", type_guid="ED_SITE")


def test_get_asset_by_name_and_type_raises_on_multiple_when_not_allowed() -> None:
    client = RoakClient(headers={}, base_url="https://example.test")
    payload = [
        {"guid": "1", "name": "Alpha", "typeGuid": "ED_SITE"},
        {"guid": "2", "name": "Alpha", "typeGuid": "ED_SITE"},
    ]
    client._request = lambda url, params=None: payload

    with pytest.raises(AmbiguousAssetMatchError, match="allow_first_match=True"):
        client.get_asset_by_name_and_type("Alpha", type_guid="ED_SITE")


def test_get_asset_by_name_and_type_returns_first_on_multiple_when_allowed() -> None:
    client = RoakClient(headers={}, base_url="https://example.test")
    payload = [
        {"guid": "1", "name": "Alpha", "typeGuid": "ED_SITE"},
        {"guid": "2", "name": "Alpha", "typeGuid": "ED_SITE"},
    ]
    client._request = lambda url, params=None: payload

    result = client.get_asset_by_name_and_type(
        "Alpha",
        type_guid="ED_SITE",
        allow_first_match=True,
    )

    assert result["guid"] == "1"


def test_get_asset_by_name_and_type_filters_exact_name_when_type_not_provided() -> None:
    client = RoakClient(headers={}, base_url="https://example.test")
    payload = [
        {"guid": "1", "name": "Alpha", "typeGuid": "TYPE_A"},
        {"guid": "2", "name": "Alpha-1", "typeGuid": "TYPE_A"},
    ]
    client._request = lambda url, params=None: payload

    result = client.get_asset_by_name_and_type("Alpha")

    assert result["guid"] == "1"


def test_get_assets_builds_expected_query_with_type_filter() -> None:
    client = RoakClient(headers={}, base_url="https://example.test")
    payload = [{"guid": "x-1", "name": "Alpha", "typeGuid": "TYPE_A"}]
    client._request = MagicMock(return_value=payload)

    result = client.get_assets(type_guid="TYPE_A")

    client._request.assert_called_once_with(
        "https://example.test/api/data/assets",
        params={"typeGuid": "TYPE_A"},
    )
    assert result == payload


def test_get_wells_builds_expected_assets_query() -> None:
    client = RoakClient(headers={}, base_url="https://example.test")
    payload = [{"guid": "w-1", "name": "Well 1", "typeGuid": "GWM_WELL"}]
    client._request = MagicMock(return_value=payload)

    result = client.get_wells()

    client._request.assert_called_once_with(
        "https://example.test/api/data/assets",
        params={"typeGuid": "GWM_WELL"},
    )
    assert result == payload


def test_get_boreholes_builds_expected_assets_query() -> None:
    client = RoakClient(headers={}, base_url="https://example.test")
    payload = [{"guid": "bh-1", "name": "Borehole 1", "typeGuid": "MWD_BOREHOLE"}]
    client._request = MagicMock(return_value=payload)

    result = client.get_boreholes()

    client._request.assert_called_once_with(
        "https://example.test/api/data/assets",
        params={"typeGuid": "MWD_BOREHOLE"},
    )
    assert result == payload
