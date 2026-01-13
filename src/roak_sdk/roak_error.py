class RoakError(Exception):
    pass


class AuthenticationError(RoakError):
    def __init__(self, status_code, message):
        super().__init__(
            f"Authentication failed! Status: {status_code} | " + f"Message: {message}"
        )
        self.status_code = status_code  # raw values for access
        self.message = message


class MissingPasswordError(RoakError):
    def __init__(self, message="Missing USER_PASSWORD environment variable"):
        super().__init__(message)


class MissingTokenError(RoakError):
    def __init__(self, message="Authentication response missing access token"):
        super().__init__(message)


class InvalidJSONError(RoakError):
    def __init__(self, message="API Returned 200 but response is not valid JSON"):
        super().__init__(message)


class MissingRefreshTokenError(RoakError):
    def __init__(self, message="No refresh token available — please re-authenticate"):
        super().__init__(message)
