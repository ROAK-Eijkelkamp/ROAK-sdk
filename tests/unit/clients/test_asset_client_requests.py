from __future__ import annotations

from unittest.mock import MagicMock

from roak_sdk.clients.asset_client import AssetClient


def test_asset_client_get_data_sends_millisecond_params() -> None:
    client = AssetClient(headers={}, base_url="https://example.test")
    client._request = MagicMock(return_value=[{"ok": True}])

    result = client.get_data("asset-1", 1700000000000, 1700000100000, ["feedA", "feedB"])

    assert result == [{"ok": True}]
    client._request.assert_called_once_with(
        "https://example.test/api/data/assets/asset-1/data",
        params={
            "from": 1700000000000,
            "to": 1700000100000,
            "feedNames": ["feedA", "feedB"],
        },
    )
