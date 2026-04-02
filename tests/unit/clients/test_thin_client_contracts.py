from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from roak_sdk.clients.borehole_client import BoreholeClient
from roak_sdk.clients.device_client import DeviceClient
from roak_sdk.clients.rig_client import RigClient
from roak_sdk.clients.semantic_client import SemanticClient


def test_device_client_get_children_builds_details_url_and_returns_children_list() -> None:
    client = DeviceClient(headers={}, base_url="https://example.test")
    client._request = MagicMock(return_value={"children": [{"guid": "c1"}]})

    result = client.get_children("dev-1")

    client._request.assert_called_once_with("https://example.test/api/tcn/devices/dev-1/details")
    assert result == [{"guid": "c1"}]


def test_device_client_get_children_raises_key_error_when_children_key_missing() -> None:
    client = DeviceClient(headers={}, base_url="https://example.test")
    client._request = MagicMock(return_value={"items": []})

    with pytest.raises(KeyError):
        client.get_children("dev-1")


def test_device_client_get_children_returns_empty_list_when_present() -> None:
    client = DeviceClient(headers={}, base_url="https://example.test")
    client._request = MagicMock(return_value={"children": []})

    result = client.get_children("dev-2")

    assert result == []


def test_rig_client_get_boreholes_builds_expected_url() -> None:
    client = RigClient(headers={}, base_url="https://example.test")
    payload = [{"guid": "bh-1"}, {"guid": "bh-2"}]
    client._request = MagicMock(return_value=payload)

    result = client.get_boreholes("rig-1")

    client._request.assert_called_once_with("https://example.test/api/mwd/rigs/rig-1/boreHoles")
    assert result == payload


def test_rig_client_get_boreholes_returns_empty_list_passthrough() -> None:
    client = RigClient(headers={}, base_url="https://example.test")
    client._request = MagicMock(return_value=[])

    assert client.get_boreholes("rig-2") == []


def test_borehole_client_get_depth_data_builds_expected_url() -> None:
    client = BoreholeClient(headers={}, base_url="https://example.test")
    payload = [{"name": "RPM", "values": []}]
    client._request = MagicMock(return_value=payload)

    result = client.get_depth_data("bh-1")

    client._request.assert_called_once_with("https://example.test/api/mwd/boreholes/bh-1/depthData")
    assert result == payload


def test_borehole_client_get_depth_data_returns_empty_list_passthrough() -> None:
    client = BoreholeClient(headers={}, base_url="https://example.test")
    client._request = MagicMock(return_value=[])

    assert client.get_depth_data("bh-2") == []


def test_semantic_client_get_attributes_builds_expected_url_for_dict_payload() -> None:
    client = SemanticClient(headers={}, base_url="https://example.test")
    payload = {"content": [{"name": "x", "value": 1}]}
    client._request = MagicMock(return_value=payload)

    result = client.get_attributes("sem-1")

    client._request.assert_called_once_with("https://example.test/api/semantics/sem-1/attributes")
    assert result == payload


def test_semantic_client_get_attributes_builds_expected_url_for_list_payload() -> None:
    client = SemanticClient(headers={}, base_url="https://example.test")
    payload = [{"name": "x", "value": 1}]
    client._request = MagicMock(return_value=payload)

    result = client.get_attributes("sem-2")

    client._request.assert_called_once_with("https://example.test/api/semantics/sem-2/attributes")
    assert result == payload


def test_semantic_client_get_feeds_builds_expected_url() -> None:
    client = SemanticClient(headers={}, base_url="https://example.test")
    payload = {"content": []}
    client._request = MagicMock(return_value=payload)

    result = client.get_feeds("sem-3")

    client._request.assert_called_once_with("https://example.test/api/semantics/sem-3/feeds")
    assert result == payload
