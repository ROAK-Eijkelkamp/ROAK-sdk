from __future__ import annotations

from typing import Type, TypeVar, Callable

from roak_sdk.config import DEFAULT_REQUEST_TIMEOUT, normalize_request_timeout

T = TypeVar("T")

class ClientRegistry:
    """
    Registry that holds credentials and lazily creates/caches client instances.
    
    This allows each semantic class to request only the client it needs,
    while ensuring clients are created once and share the same credentials.
    """

    def __init__(
        self,
        headers: dict[str, str],
        base_url: str,
        refresh_callback: Callable[[], dict[str, str]] | None = None,
        debug: bool = False,
        request_timeout: int | float | None = DEFAULT_REQUEST_TIMEOUT,
    ) -> None:
        """
        Initialize the registry with authentication credentials.

        Args:
            headers (dict[str, str]): Authorization headers for API requests.
            base_url (str): Base URL for the ROAK API.
            refresh_callback: Optional function to call to refresh tokens.
                              Should return new headers dict.
            debug (bool): Enable debug logging for requests.
        """
        self.headers = headers
        self.base_url = base_url
        self._refresh_callback = refresh_callback
        self._debug = debug
        self.request_timeout = normalize_request_timeout(request_timeout)
        self._clients: dict[type, object] = {}

    def get(self, client_class: Type[T]) -> T:
        """
        Get or create a client instance of the specified class.

        Clients are cached - subsequent calls return the same instance.

        Args:
            client_class: The client class to instantiate.

        Returns:
            An instance of the requested client class.
        """
        if client_class not in self._clients:
            self._clients[client_class] = client_class(
                self.headers,
                self.base_url,
                self,
                self._debug,
                self.request_timeout,
            )
        return self._clients[client_class]

    def update_headers(self, new_headers: dict[str, str]) -> None:
        """
        Update headers for all cached clients (e.g., after token refresh).

        Args:
            new_headers (dict[str, str]): The new authorization headers.
        """
        self.headers = new_headers
        for client in self._clients.values():
            client.headers = new_headers

    def update_request_timeout(self, request_timeout: int | float | None) -> float | None:
        """Update the timeout for all cached clients and future client creation."""
        self.request_timeout = normalize_request_timeout(request_timeout)
        for client in self._clients.values():
            if hasattr(client, "set_request_timeout"):
                client.set_request_timeout(self.request_timeout)
            else:
                client._timeout = self.request_timeout
        return self.request_timeout

    def refresh_tokens(self) -> dict[str, str] | None:
        """
        Attempt to refresh tokens using the callback.

        Returns:
            New headers dict if refresh succeeded, None if no callback available.
        """
        if self._refresh_callback:
            new_headers = self._refresh_callback()
            self.update_headers(new_headers)
            return new_headers
        return None
