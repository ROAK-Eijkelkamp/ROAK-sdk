from __future__ import annotations

from unittest.mock import MagicMock

from roak_sdk.clients.semantic_client import SemanticClient
from roak_sdk.semantics.semantic import Semantic
from tests.conftest import StubRegistry


def _make_semantic_with_feeds(payload):
    semantic_client = MagicMock(spec=SemanticClient)
    semantic_client.get_feeds.return_value = payload
    registry = StubRegistry({SemanticClient: semantic_client})
    semantic = Semantic({"guid": "sem-1", "name": "Semantic A"}, registry)
    return semantic, semantic_client


def test_get_last_values_calls_semantic_client_with_guid() -> None:
    semantic, semantic_client = _make_semantic_with_feeds([])

    semantic.get_last_values()

    semantic_client.get_feeds.assert_called_once_with("sem-1")


def test_get_last_values_maps_requested_fields_from_last_received_reading() -> None:
    semantic, _ = _make_semantic_with_feeds(
        [
            {
                "name": "Air Temperature",
                "unit": {"name": "CELSIUS"},
                "lastReceivedReading": {
                    "data": "23.9",
                    "recordingTime": 1773747134303,
                },
                "lastSentReading": None,
            }
        ]
    )

    result = semantic.get_last_values()

    assert result == [
        {
            "feedname": "Air Temperature",
            "last_value": "23.9",
            "unit": "CELSIUS",
            "record_time": 1773747134303,
        }
    ]


def test_get_last_values_falls_back_to_last_sent_when_last_received_missing() -> None:
    semantic, _ = _make_semantic_with_feeds(
        [
            {
                "name": "BoreHole",
                "unit": {"name": "TEXT"},
                "lastReceivedReading": None,
                "lastSentReading": {
                    "data": "f4693cd2-0c30-43f6-97ea-efeb621322f5",
                    "recordingTime": 1731073681599,
                },
            }
        ]
    )

    result = semantic.get_last_values()

    assert result[0]["last_value"] == "f4693cd2-0c30-43f6-97ea-efeb621322f5"
    assert result[0]["record_time"] == 1731073681599


def test_get_last_values_handles_missing_readings_and_unit() -> None:
    semantic, _ = _make_semantic_with_feeds(
        [
            {
                "name": "CPU load",
                "unit": None,
                "lastReceivedReading": None,
                "lastSentReading": None,
            }
        ]
    )

    result = semantic.get_last_values()

    assert result == [
        {
            "feedname": "CPU load",
            "last_value": None,
            "unit": None,
            "record_time": None,
        }
    ]


def test_get_last_values_returns_empty_for_non_dict_or_missing_content() -> None:
    semantic_a, _ = _make_semantic_with_feeds({})
    semantic_b, _ = _make_semantic_with_feeds([])

    assert semantic_a.get_last_values() == []
    assert semantic_b.get_last_values() == []
