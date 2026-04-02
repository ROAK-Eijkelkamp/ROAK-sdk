from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

import requests
from typing import TYPE_CHECKING
from roak_sdk.config import (
    DEFAULT_HTTP_RETRY_ATTEMPTS,
    DEFAULT_HTTP_RETRY_BACKOFF_FACTOR,
    DEFAULT_HTTP_RETRY_STATUS_CODES,
    DEFAULT_REQUEST_TIMEOUT,
    normalize_request_timeout,
)
from roak_sdk.roak_error import InvalidJSONError

if TYPE_CHECKING:
    from roak_sdk.clients.client_registry import ClientRegistry


logger = logging.getLogger("roak_sdk")


def datetime_to_millis(dt: datetime) -> int:
    """
    Convert a datetime object to milliseconds since Unix epoch.

    Args:
        dt (datetime): The datetime to convert.

    Returns:
        int: Milliseconds since January 1, 1970 (Unix epoch).
    """
    return int(dt.timestamp() * 1000)


def millis_to_datetime(millis: int) -> datetime:
    """
    Convert milliseconds since Unix epoch to a datetime object.

    Args:
        millis (int): Milliseconds since January 1, 1970 (Unix epoch).

    Returns:
        datetime: A timezone-aware datetime object in UTC.
    """
    return datetime.fromtimestamp(millis / 1000, tz=timezone.utc)


class BaseClient:
    """
    Base client providing shared functionality for ROAK API clients.

    Handles generic HTTP requests, time parsing, and normalization.
    All specialized clients (e.g., WellClient, RigClient) inherit from this class.
    Automatically retries requests once on 401 (token expired) after refreshing tokens.
    """

    def __init__(
        self,
        headers: dict[str, str],
        base_url: str,
        registry: "ClientRegistry | None" = None,
        debug: bool = False,
        request_timeout: int | float | None = DEFAULT_REQUEST_TIMEOUT,
    ) -> None:
        """
        Initialize the BaseClient with authentication headers.

        Args:
            headers (dict[str, str]): Dictionary containing authorization headers.
            base_url (str): Base URL for the ROAK API.
            registry (ClientRegistry | None): Optional registry for token refresh.
            debug (bool): Enable debug logging for requests.
        """
        self.headers = headers
        self.base_url = base_url
        self._registry = registry
        self._debug = debug
        self._timeout = normalize_request_timeout(request_timeout)
        self._max_attempts = DEFAULT_HTTP_RETRY_ATTEMPTS
        self._backoff_factor = DEFAULT_HTTP_RETRY_BACKOFF_FACTOR
        self._retry_status_codes = set(DEFAULT_HTTP_RETRY_STATUS_CODES)
        self._session = requests.Session()

    def set_request_timeout(self, request_timeout: int | float | None) -> float | None:
        """Update the timeout used for future requests on this client."""
        self._timeout = normalize_request_timeout(request_timeout)
        return self._timeout

    def _sleep_before_retry(self, attempt: int) -> None:
        delay = self._backoff_factor * (2 ** (attempt - 1))
        time.sleep(delay)

    def _is_retryable_exception(self, error: Exception) -> bool:
        return isinstance(error, (requests.ConnectionError, requests.Timeout, requests.HTTPError))

    def _is_retryable_status(self, status_code: int) -> bool:
        return status_code in self._retry_status_codes

    def _request(self, url: str, params: dict | None = None) -> dict | list:
        """
        Perform a generic GET request to the ROAK API.
        
        Automatically retries once if the request fails with 401 (Unauthorized),
        after attempting to refresh the access token.

        Args:
            url (str): Full URL for the request.
            params (dict, optional): Dictionary of query parameters.

        Returns:
            dict | list: Parsed JSON response from the API.

        Raises:
            requests.HTTPError: If the response status code indicates an error.
            InvalidJSONError: If the response cannot be parsed as JSON.
        """
        last_error: Exception | None = None

        for attempt in range(1, self._max_attempts + 1):
            try:
                response = self._session.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=self._timeout,
                )
            except requests.RequestException as error:
                last_error = error
                if attempt < self._max_attempts and self._is_retryable_exception(error):
                    self._sleep_before_retry(attempt)
                    continue
                raise

            if self._debug:
                logger.debug(
                    "GET %s params=%s -> %s %s (%d bytes)",
                    url,
                    params,
                    response.status_code,
                    response.reason,
                    len(response.content),
                )

            if response.status_code == 401 and self._registry:
                new_headers = self._registry.refresh_tokens()
                if new_headers:
                    continue

            if self._is_retryable_status(response.status_code) and attempt < self._max_attempts:
                self._sleep_before_retry(attempt)
                continue

            response.raise_for_status()

            try:
                return response.json()
            except Exception:
                raise InvalidJSONError()

        if last_error:
            raise last_error
        raise requests.RequestException("Request failed after retries")
