from __future__ import annotations

from datetime import datetime, timezone

import pytest
import requests

from roak_sdk.clients.base_client import BaseClient, datetime_to_millis, millis_to_datetime
from roak_sdk.roak_error import InvalidJSONError


class _Response:
    def __init__(self, status_code: int, payload=None, raise_http: bool = False) -> None:
        self.status_code = status_code
        self.reason = "OK" if status_code < 400 else "Unauthorized"
        self.content = b"{}"
        self._payload = payload
        self._raise_http = raise_http

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload

    def raise_for_status(self):
        if self._raise_http:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class _Registry:
    def __init__(self, on_refresh=None):
        self.calls = 0
        self.on_refresh = on_refresh

    def refresh_tokens(self):
        self.calls += 1
        if self.on_refresh:
            return self.on_refresh()
        return None


def test_base_client_request_success_returns_json(monkeypatch: pytest.MonkeyPatch) -> None:
    client = BaseClient(headers={"authorization": "Bearer a"}, base_url="https://example.test")

    def _fake_get(url, headers, params, timeout):
        return _Response(200, payload={"ok": True})

    monkeypatch.setattr(client._session, "get", _fake_get)

    result = client._request("https://example.test/path", params={"x": 1})

    assert result == {"ok": True}


def test_base_client_request_passes_default_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    client = BaseClient(headers={"authorization": "Bearer a"}, base_url="https://example.test")

    observed_timeout = {}

    def _fake_get(url, headers, params, timeout):
        observed_timeout["value"] = timeout
        return _Response(200, payload={"ok": True})

    monkeypatch.setattr(client._session, "get", _fake_get)

    result = client._request("https://example.test/path")

    assert result == {"ok": True}
    assert observed_timeout["value"] == client._timeout


def test_base_client_request_can_disable_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    client = BaseClient(
        headers={"authorization": "Bearer a"},
        base_url="https://example.test",
        request_timeout=-1,
    )

    observed_timeout = {}

    def _fake_get(url, headers, params, timeout):
        observed_timeout["value"] = timeout
        return _Response(200, payload={"ok": True})

    monkeypatch.setattr(client._session, "get", _fake_get)

    result = client._request("https://example.test/path")

    assert result == {"ok": True}
    assert observed_timeout["value"] is None


def test_base_client_request_retries_once_after_401_when_refresh_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = BaseClient(headers={"authorization": "Bearer old"}, base_url="https://example.test")

    def _refresh():
        client.headers = {"authorization": "Bearer new"}
        return client.headers

    registry = _Registry(on_refresh=_refresh)
    client._registry = registry

    calls = {"count": 0}

    def _fake_get(url, headers, params, timeout):
        calls["count"] += 1
        if calls["count"] == 1:
            return _Response(401, payload={"error": "expired"})
        return _Response(200, payload={"ok": True})

    monkeypatch.setattr(client._session, "get", _fake_get)

    result = client._request("https://example.test/path")

    assert result == {"ok": True}
    assert calls["count"] == 2
    assert registry.calls == 1


def test_base_client_request_retries_transient_status_with_backoff(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = BaseClient(headers={"authorization": "Bearer a"}, base_url="https://example.test")

    calls = {"count": 0}
    sleeps: list[float] = []

    def _fake_sleep(delay: float) -> None:
        sleeps.append(delay)

    def _fake_get(url, headers, params, timeout):
        calls["count"] += 1
        if calls["count"] < 3:
            return _Response(503, payload={"error": "temporary"}, raise_http=True)
        return _Response(200, payload={"ok": True})

    monkeypatch.setattr("roak_sdk.clients.base_client.time.sleep", _fake_sleep)
    monkeypatch.setattr(client._session, "get", _fake_get)

    result = client._request("https://example.test/path")

    assert result == {"ok": True}
    assert calls["count"] == 3
    assert sleeps == [client._backoff_factor, client._backoff_factor * 2]


def test_base_client_request_401_without_registry_raises_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = BaseClient(headers={"authorization": "Bearer old"}, base_url="https://example.test")

    monkeypatch.setattr(
        client._session,
        "get",
        lambda url, headers, params, timeout: _Response(
            401, payload={"error": "expired"}, raise_http=True
        ),
    )

    with pytest.raises(requests.HTTPError):
        client._request("https://example.test/path")


def test_base_client_request_401_with_refresh_failure_raises_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = BaseClient(headers={"authorization": "Bearer old"}, base_url="https://example.test")
    client._registry = _Registry(on_refresh=lambda: None)

    monkeypatch.setattr(
        client._session,
        "get",
        lambda url, headers, params, timeout: _Response(
            401, payload={"error": "expired"}, raise_http=True
        ),
    )

    with pytest.raises(requests.HTTPError):
        client._request("https://example.test/path")


def test_base_client_request_invalid_json_raises_invalid_json_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = BaseClient(headers={"authorization": "Bearer a"}, base_url="https://example.test")

    monkeypatch.setattr(
        client._session,
        "get",
        lambda url, headers, params, timeout: _Response(200, payload=ValueError("bad json")),
    )

    with pytest.raises(InvalidJSONError):
        client._request("https://example.test/path")


def test_datetime_to_millis_and_millis_to_datetime_round_trip() -> None:
    original = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    millis = datetime_to_millis(original)
    restored = millis_to_datetime(millis)

    assert millis == int(original.timestamp() * 1000)
    assert restored == original
