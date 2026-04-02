from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from roak_sdk.clients.asset_client import AssetClient
from roak_sdk.clients.semantic_client import SemanticClient
from roak_sdk.roak_error import AssetValidationError
from roak_sdk.semantics.asset import Asset
from tests.conftest import StubRegistry


def _make_asset() -> tuple[Asset, MagicMock]:
    asset_client = MagicMock(spec=AssetClient)
    asset_client.get_data.return_value = [{"ok": True}]
    semantic_client = MagicMock(spec=SemanticClient)

    registry = StubRegistry(
        {
            AssetClient: asset_client,
            SemanticClient: semantic_client,
        }
    )
    asset = Asset({"guid": "asset-1", "name": "Asset A"}, registry)
    return asset, asset_client


def test_asset_get_data_accepts_timezone_aware_datetimes() -> None:
    asset, asset_client = _make_asset()
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end = datetime(2024, 1, 2, tzinfo=timezone.utc)

    result = asset.get_data(start_datetime=start, end_datetime=end)

    assert result == [{"ok": True}]
    asset_client.get_data.assert_called_once_with(
        "asset-1",
        int(start.timestamp() * 1000),
        int(end.timestamp() * 1000),
        [],
    )


def test_asset_get_data_accepts_epoch_millis() -> None:
    asset, asset_client = _make_asset()

    asset.get_data(start_datetime=1000, end_datetime=2000)

    asset_client.get_data.assert_called_once_with("asset-1", 1000, 2000, [])


@pytest.mark.parametrize(
    ("start_value", "end_value", "expected_error", "expected_message"),
    [
        (datetime(2024, 1, 1), 2000, AssetValidationError, "timezone-aware"),
        (1000, datetime(2024, 1, 1), AssetValidationError, "timezone-aware"),
        (True, 2000, AssetValidationError, "not bool"),
        (1000, False, AssetValidationError, "not bool"),
        (3000, 2000, AssetValidationError, "less than or equal"),
    ],
)
def test_asset_get_data_validates_time_inputs(
    start_value,
    end_value,
    expected_error,
    expected_message,
) -> None:
    asset, _ = _make_asset()

    with pytest.raises(expected_error, match=expected_message):
        asset.get_data(start_datetime=start_value, end_datetime=end_value)


def test_asset_get_data_defaults_missing_start_datetime_to_asset_window() -> None:
    asset, asset_client = _make_asset()
    fixed_now = 1_700_000_000_000
    asset._utc_now_millis = lambda: fixed_now

    asset.get_data(end_datetime=2000)

    expected_start = 2000 - int(30 * 24 * 60 * 60 * 1000)
    asset_client.get_data.assert_called_once_with("asset-1", expected_start, 2000, [])


def test_asset_get_data_defaults_missing_end_datetime_to_now() -> None:
    asset, asset_client = _make_asset()
    fixed_now = 1_700_000_000_000
    asset._utc_now_millis = lambda: fixed_now

    asset.get_data(start_datetime=1000)

    asset_client.get_data.assert_called_once_with("asset-1", 1000, fixed_now, [])


def test_asset_get_data_defaults_both_datetimes_to_asset_window() -> None:
    asset, asset_client = _make_asset()
    fixed_now = 1_700_000_000_000
    asset._utc_now_millis = lambda: fixed_now

    asset.get_data()

    expected_start = fixed_now - int(30 * 24 * 60 * 60 * 1000)
    asset_client.get_data.assert_called_once_with("asset-1", expected_start, fixed_now, [])
