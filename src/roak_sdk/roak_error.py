"""
Custom exceptions for the ROAK SDK.
"""


def asset_not_found_message(entity: str, field: str, value: str, scope: str | None = None) -> str:
    scope_text = f" in {scope}" if scope else ""
    return f"{entity} with {field} '{value}' not found{scope_text}"


def ambiguous_asset_message(
    entity: str,
    field: str,
    value: str,
    count: int,
    scope: str | None = None,
) -> str:
    scope_text = f" in {scope}" if scope else ""
    return (
        f"Found {count} {entity.lower()}s with {field} '{value}'{scope_text}. "
        "Set allow_first_match=True to accept the first result."
    )


def asset_type_mismatch_message(
    entity: str,
    field: str,
    value: str,
    actual_type: str,
) -> str:
    return f"Asset with {field} '{value}' is not a {entity}; got type '{actual_type}'."


def asset_validation_message(field_name: str, detail: str) -> str:
    return f"{field_name}: {detail}"


def feed_not_found_message(asset_name: str, missing: list[str], suggestions: str = "") -> str:
    return f"Feed(s) {missing} not found for asset '{asset_name}'.{suggestions}"


class RoakError(Exception):
    """Base exception for all ROAK SDK errors."""

    pass


class AuthenticationError(RoakError):
    """Raised when authentication fails."""

    def __init__(self, status_code, message=None):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Authentication failed ({status_code}): {message}")


class MissingUsernameError(RoakError):
    """Raised when no username is provided."""

    def __init__(self):
        super().__init__("Username is required for authentication")


class MissingPasswordError(RoakError):
    """Raised when no password is provided."""

    def __init__(self):
        super().__init__("Password is required for authentication")


class MissingTokenError(RoakError):
    """Raised when access token is missing from authentication response."""

    def __init__(self):
        super().__init__("Access token not found in authentication response")


class MissingAccessListError(RoakError):
    """Raised when accessList is empty or invalid for multi-tenant auth responses."""

    def __init__(self):
        super().__init__("No access contexts found in accessList")


class TenantNotFoundError(RoakError):
    """Raised when the requested tenant is not present in accessList."""

    def __init__(self, tenant):
        super().__init__(f"Tenant '{tenant}' not found in accessList")


class MissingRefreshTokenError(RoakError):
    """Raised when refresh token is missing but required."""

    def __init__(self, message=None):
        super().__init__(message or "Refresh token is required but not available")


class InvalidJSONError(RoakError):
    """Raised when response cannot be parsed as JSON."""

    def __init__(self):
        super().__init__("Failed to parse response as JSON")


class TokenExpiredError(RoakError):
    """Raised when the access token has expired."""

    def __init__(self):
        super().__init__("Access token has expired - please refresh or re-authenticate")


class AssetNotFoundError(RoakError):
    """Raised when a lookup cannot find a matching asset."""

    def __init__(self, entity: str, field: str, value: str, scope: str | None = None):
        super().__init__(asset_not_found_message(entity, field, value, scope))


class AmbiguousAssetMatchError(RoakError):
    """Raised when a lookup returns multiple matches and first-match fallback is disabled."""

    def __init__(
        self,
        entity: str,
        field: str,
        value: str,
        count: int,
        scope: str | None = None,
    ):
        super().__init__(ambiguous_asset_message(entity, field, value, count, scope))


class AssetTypeMismatchError(RoakError):
    """Raised when a lookup returns an asset of the wrong semantic type."""

    def __init__(self, entity: str, field: str, value: str, actual_type: str):
        super().__init__(asset_type_mismatch_message(entity, field, value, actual_type))


class AssetValidationError(RoakError):
    """Raised when an asset date/time input is invalid."""

    def __init__(self, field_name: str, detail: str):
        super().__init__(asset_validation_message(field_name, detail))


class FeedNotFoundError(RoakError):
    """Raised when requested feed names are not available on an asset."""

    def __init__(self, asset_name: str, missing: list[str], suggestions: str = ""):
        super().__init__(feed_not_found_message(asset_name, missing, suggestions))
