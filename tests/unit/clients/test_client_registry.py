from __future__ import annotations

from roak_sdk.clients.client_registry import ClientRegistry


class _DummyClient:
    def __init__(self, headers, base_url, registry, debug, request_timeout=None):
        self.headers = headers
        self.base_url = base_url
        self.registry = registry
        self.debug = debug
        self.request_timeout = request_timeout


def test_get_caches_client_instances() -> None:
    registry = ClientRegistry(headers={"authorization": "Bearer a"}, base_url="https://example.test")

    first = registry.get(_DummyClient)
    second = registry.get(_DummyClient)

    assert first is second
    assert first.request_timeout is not None


def test_get_passes_request_timeout_to_new_clients() -> None:
    registry = ClientRegistry(
        headers={"authorization": "Bearer a"},
        base_url="https://example.test",
        request_timeout=9,
    )

    client = registry.get(_DummyClient)

    assert client.request_timeout == 9


def test_update_headers_propagates_to_cached_clients() -> None:
    registry = ClientRegistry(headers={"authorization": "Bearer a"}, base_url="https://example.test")
    client = registry.get(_DummyClient)

    new_headers = {"authorization": "Bearer b"}
    registry.update_headers(new_headers)

    assert registry.headers == new_headers
    assert client.headers == new_headers


def test_refresh_tokens_with_callback_updates_headers_and_returns_new_headers() -> None:
    registry = ClientRegistry(
        headers={"authorization": "Bearer a"},
        base_url="https://example.test",
        refresh_callback=lambda: {"authorization": "Bearer refreshed"},
    )
    client = registry.get(_DummyClient)

    refreshed = registry.refresh_tokens()

    assert refreshed == {"authorization": "Bearer refreshed"}
    assert registry.headers == {"authorization": "Bearer refreshed"}
    assert client.headers == {"authorization": "Bearer refreshed"}


def test_refresh_tokens_without_callback_returns_none() -> None:
    registry = ClientRegistry(headers={"authorization": "Bearer a"}, base_url="https://example.test")

    refreshed = registry.refresh_tokens()

    assert refreshed is None
