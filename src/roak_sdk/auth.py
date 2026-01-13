import requests
import json
from dotenv import load_dotenv
from roak_sdk.roak_error import (
    AuthenticationError,
    MissingPasswordError,
    MissingTokenError,
    InvalidJSONError,
    MissingRefreshTokenError,
)

# --- Constants ---
DEFAULT_URL = (
    "https://dev.roak.com"  # parameter zo dat zelf ingevult met als Default Productie
)
LOGIN_URL = f"{DEFAULT_URL}/api/ed/authentication/email"
REFRESH_URL = f"{DEFAULT_URL}/api/ed/authentication/renewal"
MILLISECONDS_IN_ONE_DAY = 86400000

load_dotenv()


class Auth:
    """
    Handles authentication and token management for the ROAK API.

    Provides methods to log in, obtain access tokens, and refresh tokens.
    Credentials can be provided explicitly or read from environment variables:
    ROAK_USERNAME and ROAK_PASSWORD.
    """

    def __init__(self, user, password, base_url=None):
        """
        Initialize the Auth object with user credentials.

        Args:
            user (str | None): Username/email for authentication. Falls back to
                               ROAK_USERNAME environment variable if None.
            password (str | None): Password for authentication. Falls back to
                                   ROAK_PASSWORD environment variable if None.

        Raises:
            MissingPasswordError: If no password is provided and environment variable is missing.
        """
        self.user = user
        self.password = password
        self.base_url = base_url or DEFAULT_URL
        if not self.password:
            raise MissingPasswordError()

        self.login_url = f"{self.base_url}/api/ed/authentication/email"
        self.refresh_url = f"{self.base_url}/api/ed/authentication/renewal"

        self.access_token = None
        self.refresh_token = None
        self.headers = None

    def authenticate(self, force_refresh=False):
        """
        Log in to the ROAK API and retrieve an access token.

        Args:
            force_refresh (bool, optional): If True, forces re-authentication even if
                                            headers already exist. Defaults to False.

        Returns:
            dict: Headers containing the 'authorization' key with Bearer token.

        Raises:
            AuthenticationError: If the HTTP request fails or server returns non-200.
            InvalidJSONError: If the response cannot be parsed as JSON.
            MissingTokenError: If the response does not contain an access token.
        """
        if not force_refresh and self.headers:
            return self.headers

        body = {"username": self.user, "password": self.password}

        headers = {
            "accept": "text/plain, application/vnd.user.v1+json",
            "accept-encoding": "gzip, deflate, br",
            "connection": "keep-alive",
            "content-type": "application/json",
        }

        try:
            response = requests.post(
                self.login_url, data=json.dumps(body), headers=headers
            )
        except requests.RequestException as e:
            raise AuthenticationError("Request failed", str(e))

        if response.status_code != 200:
            raise AuthenticationError(response.status_code, response.text)

        try:
            data = response.json()
        except ValueError:
            raise InvalidJSONError()

        if "accessToken" not in data:
            raise MissingTokenError()

        self.access_token = data["accessToken"]
        self.refresh_token = data.get("refreshToken")

        headers["authorization"] = f"Bearer {self.access_token}"
        self.headers = headers
        return headers

    def refresh_access_token(self):
        """
        Refresh the access token using the current refresh token.

        Returns:
            dict: Headers containing the updated 'authorization' key with Bearer token.

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

        headers = {
            "accept": "application/vnd.fullSignInResponse+json",
            "content-type": "application/json",
        }

        try:
            response = requests.post(
                self.refresh_url,
                json={"refreshToken": self.refresh_token},
                headers=headers,
            )
        except requests.RequestException as e:
            raise AuthenticationError("Refresh request failed", str(e))

        if response.status_code != 200:
            raise AuthenticationError(response.status_code, response.text)

        try:
            data = response.json()
        except ValueError:
            raise InvalidJSONError()

        if "accessToken" not in data:
            raise MissingTokenError()

        self.access_token = data["accessToken"]
        self.refresh_token = data.get("refreshToken", self.refresh_token)
        self.headers = {"authorization": f"Bearer {self.access_token}"}

        return self.headers
