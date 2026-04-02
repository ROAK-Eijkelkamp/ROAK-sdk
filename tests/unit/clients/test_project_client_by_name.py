from __future__ import annotations

import pytest

from roak_sdk.clients.project_client import ProjectClient
from roak_sdk.roak_error import AmbiguousAssetMatchError, AssetNotFoundError


def test_project_client_get_asset_by_name_raises_when_no_matches() -> None:
    client = ProjectClient(headers={}, base_url="https://example.test")
    client._request = lambda url, params=None: []

    with pytest.raises(AssetNotFoundError, match="not found"):
        client.get_asset_by_name("project-1", "Alpha")


def test_project_client_get_asset_by_name_raises_on_multiple_when_not_allowed() -> None:
    client = ProjectClient(headers={}, base_url="https://example.test")
    payload = [{"guid": "1"}, {"guid": "2"}]
    client._request = lambda url, params=None: payload

    with pytest.raises(AmbiguousAssetMatchError, match="allow_first_match=True"):
        client.get_asset_by_name("project-1", "Alpha")


def test_project_client_get_asset_by_name_returns_first_when_allowed() -> None:
    client = ProjectClient(headers={}, base_url="https://example.test")
    payload = [{"guid": "1"}, {"guid": "2"}]
    client._request = lambda url, params=None: payload

    result = client.get_asset_by_name("project-1", "Alpha", allow_first_match=True)

    assert result["guid"] == "1"


def test_project_client_get_asset_by_name_returns_dict_payload_directly() -> None:
    client = ProjectClient(headers={}, base_url="https://example.test")
    payload = {"guid": "single", "name": "Alpha"}
    client._request = lambda url, params=None: payload

    result = client.get_asset_by_name("project-1", "Alpha")

    assert result["guid"] == "single"
