import unittest
from unittest.mock import patch, Mock
from roak_sdk.auth import Auth
from roak_sdk.roak_error import (
    AuthenticationError,
    MissingPasswordError,
    MissingTokenError,
    InvalidJSONError,
    MissingRefreshTokenError,
)


class TestAuth(unittest.TestCase):
    """Tests for Auth authentication and token management."""

    @patch("roak_sdk.auth.requests.post")
    def test_authenticate_success_200(self, mock_post):
        """Checks successful authentication returns headers with token."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"accessToken": "test_token"}
        mock_post.return_value = mock_response

        auth = Auth(user="fake_user", password="fake_password")
        headers = auth.authenticate()

        self.assertIn("authorization", headers)
        self.assertEqual(headers["authorization"], "Bearer test_token")
        self.assertEqual(headers["content-type"], "application/json")

    @patch("roak_sdk.auth.requests.post")
    def test_authenticate_failure_401(self, mock_post):
        """Checks authentication failure raises AuthenticationError."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        auth = Auth(user="fake_user", password="fake_password")
        with self.assertRaises(AuthenticationError):
            auth.authenticate()

    @patch("roak_sdk.auth.requests.post")
    def test_username_provided_explicitly(self, mock_post):
        """Checks Auth works when username is provided explicitly."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"accessToken": "test_token"}
        mock_post.return_value = mock_response

        # Provide user and password explicitly
        auth = Auth(user="explicit_user", password="fake_password")
        headers = auth.authenticate()

        self.assertEqual(headers["authorization"], "Bearer test_token")
        self.assertEqual(headers["content-type"], "application/json")

    def test_missing_password(self):
        """Checks missing password raises MissingPasswordError."""
        with self.assertRaises(MissingPasswordError):
            Auth(user="fake_user", password=None)

    @patch("roak_sdk.auth.requests.post")
    def test_missing_access_token(self, mock_post):
        """Checks missing access token raises MissingTokenError."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # missing token
        mock_post.return_value = mock_response

        auth = Auth(user="fake_user", password="fake_password")
        with self.assertRaises(MissingTokenError):
            auth.authenticate()

    @patch("roak_sdk.auth.requests.post")
    def test_invalid_json_response(self, mock_post):
        """Checks invalid JSON response raises InvalidJSONError."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError()
        mock_post.return_value = mock_response

        auth = Auth(user="fake_user", password="fake_password")
        with self.assertRaises(InvalidJSONError):
            auth.authenticate()

    @patch("roak_sdk.auth.requests.post")
    def test_force_refresh(self, mock_post):
        """Checks force_refresh re-authenticates even if headers exist."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"accessToken": "new_token"}
        mock_post.return_value = mock_response

        auth = Auth(user="fake_user", password="fake_password")
        # simulate existing headers
        auth.headers = {
            "authorization": "Bearer old_token",
            "content-type": "application/json",
        }

        headers = auth.authenticate(force_refresh=True)
        self.assertEqual(headers["authorization"], "Bearer new_token")

    @patch("roak_sdk.auth.requests.post")
    def test_refresh_access_token_success(self, mock_post):
        """Checks refresh_access_token updates headers correctly."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"accessToken": "refreshed_token"}
        mock_post.return_value = mock_response

        auth = Auth(user="fake_user", password="fake_password")
        auth.refresh_token = "existing_refresh"
        headers = auth.refresh_access_token()
        self.assertEqual(headers["authorization"], "Bearer refreshed_token")

    def test_refresh_access_token_missing_token(self):
        """Checks refresh_access_token raises error if no refresh token."""
        auth = Auth(user="fake_user", password="fake_password")
        with self.assertRaises(MissingRefreshTokenError):
            auth.refresh_access_token()


if __name__ == "__main__":
    unittest.main()
