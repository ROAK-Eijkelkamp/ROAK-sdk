from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from roak_sdk.clients.asset_client import AssetClient
from roak_sdk.clients.device_client import DeviceClient
from roak_sdk.clients.semantic_client import SemanticClient
from roak_sdk.roak_error import AssetValidationError
from roak_sdk.semantics.devices.modem import Modem
from tests.conftest import StubRegistry


class _ChildDevice:
    def __init__(self, name: str, feeds: list[str] | None = None) -> None:
        self.name = name
        self.last_call = None
        self._feeds = feeds or ["diverPressure", "other"]

    def get_feeds(self) -> list[dict]:
        return [{"name": feed_name} for feed_name in self._feeds]

    def get_data(self, start_datetime, end_datetime, feeds):
        self.last_call = {
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "feeds": feeds,
        }
        return [{"value": 1}]


def _make_modem() -> Modem:
    registry = StubRegistry(
        {
            SemanticClient: MagicMock(spec=SemanticClient),
            AssetClient: MagicMock(spec=AssetClient),
            DeviceClient: MagicMock(spec=DeviceClient),
        }
    )
    return Modem({"guid": "modem-1", "name": "Modem A"}, registry)


def test_modem_get_data_through_children_accepts_datetimes_and_forwards_millis() -> None:
    modem = _make_modem()
    child = _ChildDevice("child-1")
    modem.get_children = MagicMock(return_value=[child])

    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end = datetime(2024, 1, 2, tzinfo=timezone.utc)

    result = modem.get_data_through_children(start_datetime=start, end_datetime=end)

    assert result == {"child-1": [{"value": 1}]}
    assert child.last_call == {
        "start_datetime": int(start.timestamp() * 1000),
        "end_datetime": int(end.timestamp() * 1000),
        "feeds": ["diverPressure"],
    }


def test_modem_get_data_through_children_skips_children_without_relevant_feeds() -> None:
    modem = _make_modem()
    matching_child = _ChildDevice("child-match", feeds=["diverPressure"])
    non_matching_child = _ChildDevice("child-skip", feeds=["foo", "bar"])
    modem.get_children = MagicMock(return_value=[matching_child, non_matching_child])

    result = modem.get_data_through_children(start_datetime=1000, end_datetime=2000)

    assert "child-match" in result
    assert "child-skip" not in result
    assert matching_child.last_call == {
        "start_datetime": 1000,
        "end_datetime": 2000,
        "feeds": ["diverPressure"],
    }
    assert non_matching_child.last_call is None


def test_modem_get_data_through_children_uses_requested_feeds_filter() -> None:
    modem = _make_modem()
    child = _ChildDevice("child-1", feeds=["diverPressure", "baroPressure", "other"])
    modem.get_children = MagicMock(return_value=[child])

    result = modem.get_data_through_children(
        feeds=["baroPressure"],
        start_datetime=1000,
        end_datetime=2000,
    )

    assert result == {"child-1": [{"value": 1}]}
    assert child.last_call == {
        "start_datetime": 1000,
        "end_datetime": 2000,
        "feeds": ["baroPressure"],
    }


@pytest.mark.parametrize(
    ("start_value", "end_value", "expected_error", "expected_message"),
    [
        (datetime(2024, 1, 1), 2000, AssetValidationError, "timezone-aware"),
        (1000, datetime(2024, 1, 1), AssetValidationError, "timezone-aware"),
    ],
)
def test_modem_get_data_through_children_validates_time_inputs(
    start_value,
    end_value,
    expected_error,
    expected_message,
) -> None:
    modem = _make_modem()

    with pytest.raises(expected_error, match=expected_message):
        modem.get_data_through_children(start_datetime=start_value, end_datetime=end_value)


def test_modem_get_data_through_children_defaults_missing_start_datetime() -> None:
    modem = _make_modem()
    child = _ChildDevice("child-1")
    modem.get_children = MagicMock(return_value=[child])
    fixed_now = 1_700_000_000_000
    modem._utc_now_millis = lambda: fixed_now

    modem.get_data_through_children(end_datetime=2000)

    expected_start = 2000 - int(30 * 24 * 60 * 60 * 1000)
    assert child.last_call == {
        "start_datetime": expected_start,
        "end_datetime": 2000,
        "feeds": ["diverPressure"],
    }


def test_modem_get_data_through_children_defaults_missing_end_datetime() -> None:
    modem = _make_modem()
    child = _ChildDevice("child-1")
    modem.get_children = MagicMock(return_value=[child])
    fixed_now = 1_700_000_000_000
    modem._utc_now_millis = lambda: fixed_now

    modem.get_data_through_children(start_datetime=1000)

    assert child.last_call == {
        "start_datetime": 1000,
        "end_datetime": fixed_now,
        "feeds": ["diverPressure"],
    }


def test_modem_get_data_through_children_defaults_both_datetimes() -> None:
    modem = _make_modem()
    child = _ChildDevice("child-1")
    modem.get_children = MagicMock(return_value=[child])
    fixed_now = 1_700_000_000_000
    modem._utc_now_millis = lambda: fixed_now

    modem.get_data_through_children()

    expected_start = fixed_now - int(30 * 24 * 60 * 60 * 1000)
    assert child.last_call == {
        "start_datetime": expected_start,
        "end_datetime": fixed_now,
        "feeds": ["diverPressure"],
    }
