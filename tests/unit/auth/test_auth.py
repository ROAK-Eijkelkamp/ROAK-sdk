from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
import requests

from roak_sdk.auth import Auth
from roak_sdk.roak_error import (
    AuthenticationError,
    InvalidJSONError,
    MissingAccessListError,
    MissingPasswordError,
    MissingRefreshTokenError,
    MissingTokenError,
    MissingUsernameError,
    TenantNotFoundError,
)


class _Response:
    def __init__(self, status_code: int, payload=None, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


def test_auth_constructor_requires_username() -> None:
    with pytest.raises(MissingUsernameError):
        Auth("", "pass")


def test_auth_constructor_requires_password() -> None:
    with pytest.raises(MissingPasswordError):
        Auth("user", "")


def test_authenticate_success_sets_tokens_headers_and_expiry(monkeypatch: pytest.MonkeyPatch) -> None:
    auth = Auth("user", "pass", base_url="https://example.test")

    def _fake_post(url, json, headers, timeout):
        return _Response(
            200,
            payload={
                "accessToken": "token-1",
                "refreshToken": "refresh-1",
                "expiresIn": 300,
            },
        )

    monkeypatch.setattr(requests, "post", _fake_post)

    headers = auth.authenticate()

    assert headers["authorization"] == "Bearer token-1"
    assert headers["accept"] == "application/json"
    assert auth.access_token == "token-1"
    assert auth.refresh_token == "refresh-1"
    assert auth.token_expires_at is not None


def test_authenticate_uses_custom_request_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    observed_timeout = {}
    auth = Auth("user", "pass", base_url="https://example.test", request_timeout=7.5)

    def _fake_post(url, json, headers, timeout):
        observed_timeout["value"] = timeout
        return _Response(200, payload={"accessToken": "token-1"})

    monkeypatch.setattr(requests, "post", _fake_post)

    auth.authenticate()

    assert observed_timeout["value"] == 7.5


def test_authenticate_can_disable_request_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    observed_timeout = {}
    auth = Auth("user", "pass", base_url="https://example.test", request_timeout=-1)

    def _fake_post(url, json, headers, timeout):
        observed_timeout["value"] = timeout
        return _Response(200, payload={"accessToken": "token-1"})

    monkeypatch.setattr(requests, "post", _fake_post)

    auth.authenticate()

    assert observed_timeout["value"] is None


def test_authenticate_reuses_cached_headers_unless_forced(monkeypatch: pytest.MonkeyPatch) -> None:
    auth = Auth("user", "pass", base_url="https://example.test")
    calls = {"count": 0}

    def _fake_post(url, json, headers, timeout):
        calls["count"] += 1
        return _Response(
            200,
            payload={
                "accessToken": f"token-{calls['count']}",
                "refreshToken": "refresh-1",
            },
        )

    monkeypatch.setattr(requests, "post", _fake_post)

    first = auth.authenticate()
    second = auth.authenticate()
    third = auth.authenticate(force_refresh=True)

    assert calls["count"] == 2
    assert first is second
    assert third["authorization"] == "Bearer token-2"


def test_authenticate_request_exception_maps_to_authentication_error(monkeypatch: pytest.MonkeyPatch) -> None:
    auth = Auth("user", "pass", base_url="https://example.test")

    def _fake_post(url, json, headers, timeout):
        raise requests.RequestException("network down")

    monkeypatch.setattr(requests, "post", _fake_post)

    with pytest.raises(AuthenticationError, match="Request failed"):
        auth.authenticate()


def test_authenticate_non_200_raises_authentication_error(monkeypatch: pytest.MonkeyPatch) -> None:
    auth = Auth("user", "pass", base_url="https://example.test")

    monkeypatch.setattr(
        requests,
        "post",
        lambda url, json, headers, timeout: _Response(401, payload={}, text="Unauthorized"),
    )

    with pytest.raises(AuthenticationError, match="401"):
        auth.authenticate()


def test_authenticate_invalid_json_raises_invalid_json_error(monkeypatch: pytest.MonkeyPatch) -> None:
    auth = Auth("user", "pass", base_url="https://example.test")

    monkeypatch.setattr(
        requests,
        "post",
        lambda url, json, headers, timeout: _Response(200, payload=ValueError("bad json")),
    )

    with pytest.raises(InvalidJSONError):
        auth.authenticate()


def test_select_access_token_uses_top_level_access_token_when_access_list_missing() -> None:
    auth = Auth("user", "pass")

    token = auth._select_access_token({"accessToken": "top-token"})

    assert token == "top-token"


def test_select_access_token_raises_when_access_list_empty() -> None:
    auth = Auth("user", "pass")

    with pytest.raises(MissingAccessListError):
        auth._select_access_token({"accessList": []})


def test_select_access_token_uses_tenant_match_by_context_name() -> None:
    auth = Auth("user", "pass", tenant="tenant-a")

    token = auth._select_access_token(
        {
            "accessList": [
                {"contextName": "Tenant-A", "accessToken": "tenant-token"},
                {"contextName": "Tenant-B", "accessToken": "other-token"},
            ]
        }
    )

    assert token == "tenant-token"


def test_select_access_token_uses_tenant_match_by_context_id() -> None:
    auth = Auth("user", "pass", tenant="42")

    token = auth._select_access_token(
        {
            "accessList": [
                {"contextId": 42, "accessToken": "tenant-token"},
            ]
        }
    )

    assert token == "tenant-token"


def test_select_access_token_raises_when_tenant_not_found() -> None:
    auth = Auth("user", "pass", tenant="missing")

    with pytest.raises(TenantNotFoundError):
        auth._select_access_token(
            {
                "accessList": [
                    {"contextName": "tenant-a", "accessToken": "a"},
                ]
            }
        )


def test_select_access_token_raises_when_selected_token_missing() -> None:
    auth = Auth("user", "pass")

    with pytest.raises(MissingTokenError):
        auth._select_access_token({"accessList": [{"contextName": "tenant-a"}]})


def test_refresh_access_token_requires_refresh_token() -> None:
    auth = Auth("user", "pass")

    with pytest.raises(MissingRefreshTokenError):
        auth.refresh_access_token()


def test_refresh_access_token_success_updates_headers_and_refresh_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    auth = Auth("user", "pass", base_url="https://example.test")
    auth.refresh_token = "refresh-1"
    auth.headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer old-token",
    }

    monkeypatch.setattr(
        requests,
        "post",
        lambda url, json, headers, timeout: _Response(
            200,
            payload={
                "accessToken": "token-2",
                "refreshToken": "refresh-2",
                "expiresIn": 300,
            },
        ),
    )

    headers = auth.refresh_access_token()

    assert headers["authorization"] == "Bearer token-2"
    assert auth.refresh_token == "refresh-2"
    assert auth.token_expires_at is not None


def test_refresh_access_token_uses_custom_request_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    observed_timeout = {}
    auth = Auth("user", "pass", base_url="https://example.test", request_timeout=9)
    auth.refresh_token = "refresh-1"

    def _fake_post(url, json, headers, timeout):
        observed_timeout["value"] = timeout
        return _Response(200, payload={"accessToken": "token-2"})

    monkeypatch.setattr(requests, "post", _fake_post)

    auth.refresh_access_token()

    assert observed_timeout["value"] == 9


def test_refresh_access_token_request_exception_maps_to_authentication_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    auth = Auth("user", "pass", base_url="https://example.test")
    auth.refresh_token = "refresh-1"

    def _fake_post(url, json, headers, timeout):
        raise requests.RequestException("timeout")

    monkeypatch.setattr(requests, "post", _fake_post)

    with pytest.raises(AuthenticationError, match="Refresh request failed"):
        auth.refresh_access_token()


def test_refresh_access_token_non_200_raises_authentication_error(monkeypatch: pytest.MonkeyPatch) -> None:
    auth = Auth("user", "pass", base_url="https://example.test")
    auth.refresh_token = "refresh-1"

    monkeypatch.setattr(
        requests,
        "post",
        lambda url, json, headers, timeout: _Response(401, payload={}, text="Unauthorized"),
    )

    with pytest.raises(AuthenticationError, match="401"):
        auth.refresh_access_token()


def test_refresh_access_token_invalid_json_raises_invalid_json_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    auth = Auth("user", "pass", base_url="https://example.test")
    auth.refresh_token = "refresh-1"

    monkeypatch.setattr(
        requests,
        "post",
        lambda url, json, headers, timeout: _Response(200, payload=ValueError("bad json")),
    )

    with pytest.raises(InvalidJSONError):
        auth.refresh_access_token()


def test_is_token_expired_true_when_expiry_unknown() -> None:
    auth = Auth("user", "pass")

    assert auth.is_token_expired() is True


def test_is_token_expired_false_when_expiry_in_future() -> None:
    auth = Auth("user", "pass")
    auth.token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=1)

    assert auth.is_token_expired() is False


def test_is_token_expired_true_when_expiry_in_past() -> None:
    auth = Auth("user", "pass")
    auth.token_expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)

    assert auth.is_token_expired() is True
