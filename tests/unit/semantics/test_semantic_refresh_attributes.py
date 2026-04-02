from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from roak_sdk.clients.semantic_client import SemanticClient
from roak_sdk.semantics.semantic import Semantic
from tests.conftest import StubRegistry


def _make_semantic(payload):
    semantic_client = MagicMock(spec=SemanticClient)
    semantic_client.get_attributes.return_value = payload
    registry = StubRegistry({SemanticClient: semantic_client})
    semantic = Semantic({"guid": "sem-1", "name": "Semantic A"}, registry)
    return semantic, semantic_client


def test_refresh_attributes_calls_semantic_client_with_guid() -> None:
    semantic, semantic_client = _make_semantic([])

    semantic.refresh_attributes()

    semantic_client.get_attributes.assert_called_once_with("sem-1")


def test_refresh_attributes_maps_content_name_value_into_data() -> None:
    semantic, _ = _make_semantic(
        [
            {"name": "Diameter", "value": "150"},
            {"name": "Start date", "value": None},
        ]
    )

    result = semantic.refresh_attributes()

    assert result["Diameter"] == "150"
    assert "Start date" in result
    assert result["Start date"] is None


def test_refresh_attributes_noop_for_empty_attribute_list() -> None:
    semantic, _ = _make_semantic([])

    result = semantic.refresh_attributes()

    assert result["guid"] == "sem-1"
    assert result["name"] == "Semantic A"


def test_refresh_attributes_updates_guid_and_name_when_present() -> None:
    semantic, _ = _make_semantic(
        [
            {"name": "guid", "value": "sem-2"},
            {"name": "name", "value": "Semantic B"},
        ]
    )

    semantic.refresh_attributes()

    assert semantic.guid == "sem-2"
    assert semantic.name == "Semantic B"
