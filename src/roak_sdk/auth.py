from __future__ import annotations

import requests
from datetime import datetime, timedelta, timezone
from roak_sdk.roak_error import (
    AuthenticationError,
    MissingUsernameError,
    MissingPasswordError,
    MissingTokenError,
    MissingAccessListError,
    TenantNotFoundError,
    InvalidJSONError,
    MissingRefreshTokenError,
    TokenExpiredError,
)
from roak_sdk.config import (
    DEFAULT_BASE_URL,
    AUTH_EMAIL_ENDPOINT,
    AUTH_REFRESH_ENDPOINT,
    DEFAULT_REQUEST_TIMEOUT,
    normalize_request_timeout,
)


class Auth:
    """
    Handles authentication and token management for the ROAK API.

    Provides methods to log in, obtain access tokens, and refresh tokens.
    """

    def __init__(
        self,
        username: str,
        password: str,
        base_url: str | None = None,
        tenant: str | None = None,
        request_timeout: int | float | None = DEFAULT_REQUEST_TIMEOUT,
    ) -> None:
        """
        Initialize the Auth object with user credentials.

        Args:
            user (str): Username/email for authentication.
            password (str): Password for authentication.
            base_url (str | None): Optional custom base URL for the API.
            tenant (str | None): Optional tenant identifier for multi-tenant scenarios.

        Raises:
            MissingUsernameError: If no username is provided.
            MissingPasswordError: If no password is provided.
        """
        self.username = username
        self.password = password
        self.base_url = base_url or DEFAULT_BASE_URL
        self.tenant = tenant
        self.request_timeout = normalize_request_timeout(request_timeout)

        if not self.username:
            raise MissingUsernameError()
        if not self.password:
            raise MissingPasswordError()

        self.login_url = f"{self.base_url}{AUTH_EMAIL_ENDPOINT}"
        self.refresh_url = f"{self.base_url}{AUTH_REFRESH_ENDPOINT}"

        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.token_expires_at: datetime | None = None
        self.headers: dict[str, str] | None = None

    def authenticate(self, force_refresh: bool = False) -> dict[str, str]:
        """
        Log in to the ROAK API and retrieve an access token.

        Args:
            force_refresh (bool, optional): If True, forces re-authentication even if
                                            headers already exist. Defaults to False.

        Returns:
            dict[str, str]: Headers containing the 'authorization' key with Bearer token.

        Raises:
            AuthenticationError: If the HTTP request fails or server returns non-200.
            InvalidJSONError: If the response cannot be parsed as JSON.
            MissingTokenError: If the response does not contain an access token.
        """
        if not force_refresh and self.headers:
            return self.headers

        body = {"username": self.username, "password": self.password}

        headers = {
            "accept": "application/vnd.fullSignInResponse+json",
            "accept-encoding": "gzip, deflate, br",
            "connection": "keep-alive",
            "content-type": "application/json",
        }

        try:
            response = requests.post(
                self.login_url, json=body, headers=headers, timeout=self.request_timeout
            )
        except requests.RequestException as e:
            raise AuthenticationError("Request failed", str(e))

        if response.status_code != 200:
            raise AuthenticationError(response.status_code, response.text)

        try:
            data = response.json()
        except ValueError:
            raise InvalidJSONError()

        self.access_token = self._select_access_token(data)
        self.refresh_token = data.get("refreshToken")
        self._set_token_expiry(data)

        headers["authorization"] = f"Bearer {self.access_token}"
        headers['accept'] = "application/json"  # Update accept header for future requests
        self.headers = headers
        return headers

    def refresh_access_token(self) -> dict[str, str]:
        """
        Refresh the access token using the current refresh token.

        Returns:
            dict[str, str]: Headers containing the 'authorization' key with Bearer token.

        Raises:
            MissingRefreshTokenError: If no refresh token is available.
            AuthenticationError: If the refresh HTTP request fails or server returns non-200.
            InvalidJSONError: If the response cannot be parsed as JSON.
            MissingTokenError: If the refreshed response does not contain an access token.
        """
        if not self.refresh_token:
            raise MissingRefreshTokenError(
                "No refresh token available — please re-authenticate"
            )

        try:
            response = requests.post(
                self.refresh_url,
                json={"refreshToken": self.refresh_token},
                headers={
                    "accept": "application/vnd.fullSignInResponse+json",
                    "content-type": "application/json",
                },
                timeout=self.request_timeout,
            )
        except requests.RequestException as e:
            raise AuthenticationError("Refresh request failed", str(e))

        if response.status_code != 200:
            raise AuthenticationError(response.status_code, response.text)

        try:
            data = response.json()
        except ValueError:
            raise InvalidJSONError()

        self.access_token = self._select_access_token(data)
        self.refresh_token = data.get("refreshToken", self.refresh_token)
        self._set_token_expiry(data)

        # Update stored headers with new token (preserve full headers)
        if self.headers:
            self.headers["authorization"] = f"Bearer {self.access_token}"
        else:
            self.headers = {
                "accept": "application/json",
                "accept-encoding": "gzip, deflate, br",
                "connection": "keep-alive",
                "content-type": "application/json",
                "authorization": f"Bearer {self.access_token}",
            }

        return self.headers

    def _select_access_token(self, data: dict) -> str:
        """
        Select the access token from the authentication response.

        Behavior:
        - If `accessList` is present:
          - with tenant: select matching tenant context
          - without tenant: use first item
        - If `accessList` is absent, fall back to top-level `accessToken`.
        """
        access_list = data.get("accessList")
        if access_list is None:
            token = data.get("accessToken")
            if not token:
                raise MissingTokenError()
            return token

        if not isinstance(access_list, list) or len(access_list) == 0:
            raise MissingAccessListError()

        selected_access = None
        if self.tenant:
            tenant_lookup = str(self.tenant).strip().lower()
            for access in access_list:
                context_name = str(access.get("contextName", "")).strip().lower()
                context_id = str(access.get("contextId", "")).strip().lower()
                if tenant_lookup in (context_name, context_id):
                    selected_access = access
                    break
            if selected_access is None:
                raise TenantNotFoundError(self.tenant)
        else:
            selected_access = access_list[0]

        token = selected_access.get("accessToken")
        if not token:
            raise MissingTokenError()
        return token

    def is_token_expired(self) -> bool:
        """
        Check if the access token has expired.

        Returns:
            bool: True if the token has expired or expiry is unknown, False otherwise.
        """
        if self.token_expires_at is None:
            return True
        return datetime.now(timezone.utc) >= self.token_expires_at

    def _set_token_expiry(self, data: dict) -> None:
        """
        Set the token expiry time from the authentication response.

        Args:
            data (dict): The authentication response data.
        """
        # Try common field names for expiry
        expires_in = data.get("expiresIn") or data.get("expires_in")
        if expires_in:
            # expiresIn is typically in seconds
            self.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))
        elif data.get("expiresAt") or data.get("expires_at"):
            # If absolute timestamp is provided
            expires_at = data.get("expiresAt") or data.get("expires_at")
            if isinstance(expires_at, (int, float)):
                self.token_expires_at = datetime.fromtimestamp(expires_at, tz=timezone.utc)
        else:
            # Default to 1 hour if not provided
            self.token_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
