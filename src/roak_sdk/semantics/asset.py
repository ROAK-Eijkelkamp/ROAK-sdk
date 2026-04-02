from __future__ import annotations

from datetime import datetime, timezone, timedelta
from difflib import get_close_matches

from roak_sdk.semantics.semantic import Semantic
from roak_sdk.clients.asset_client import AssetClient
from roak_sdk.clients.client_registry import ClientRegistry
from roak_sdk.roak_error import AssetValidationError, FeedNotFoundError


class Asset(Semantic):
    """
    Base class for all ROAK assets (Wells, Boreholes, Rigs, etc.).
    
    Provides common asset functionality and dynamic attribute access.
    Subclasses can override class attributes to customize behavior.
    """

    # --- Subclass configuration (override in subclasses) ---
    DEFAULT_FEEDS: list[str] = []  # Feed names to include by default
    DEFAULT_TIMEFRAME_DAYS: int = 30  # Default data fetch window

    def __init__(self, data: dict, registry: ClientRegistry) -> None:
        """
        Initialize Asset from API response data.

        Args:
            data (dict): Asset data from the API.
            registry (ClientRegistry): Registry for obtaining client instances.
        """
        super().__init__(data, registry)
        self._client = registry.get(AssetClient)

    def get_data(
        self,
        start_datetime: datetime | int | None = None,
        end_datetime: datetime | int | None = None,
        feeds: list[str] | None = None,
    ) -> list[dict]:
        """
        First check if requested feeds exist.
        Fetch data for this asset within a date range.

        Args:
            start_datetime (datetime | int | None): Start of the date range as
                timezone-aware datetime or milliseconds since epoch.
            end_datetime (datetime | int | None): End of the date range as
                timezone-aware datetime or milliseconds since epoch.

        Returns:
            list[dict]: List of data records.

        Raises:
            AssetValidationError: If provided datetimes are naive or invalid.
        """
        start_millis, end_millis = self._resolve_time_range(start_datetime, end_datetime)

        if start_millis > end_millis:
            raise AssetValidationError(
                "date range",
                "start_datetime must be less than or equal to end_datetime.",
            )

        if feeds is None:
            feeds = self.DEFAULT_FEEDS
        else:
            feeds = self._resolve_feed_names(feeds)

        return self._client.get_data(self.guid, start_millis, end_millis, feeds)

    @staticmethod
    def _to_epoch_millis(value: datetime | int | None, field_name: str) -> int | None:
        """Normalize a datetime/int input to milliseconds since epoch."""
        if value is None:
            return None

        if isinstance(value, bool):
            raise AssetValidationError(field_name, "must be int milliseconds or datetime, not bool.")

        if isinstance(value, int):
            return value

        if isinstance(value, datetime):
            if value.tzinfo is None or value.utcoffset() is None:
                raise AssetValidationError(field_name, "must be timezone-aware.")
            return int(value.timestamp() * 1000)

        raise AssetValidationError(
            field_name,
            f"must be milliseconds since epoch (int) or datetime, not {type(value).__name__}.",
        )

    @staticmethod
    def _utc_now_millis() -> int:
        return int(datetime.now(timezone.utc).timestamp() * 1000)

    def _resolve_time_range(
        self,
        start_datetime: datetime | int | None,
        end_datetime: datetime | int | None,
    ) -> tuple[int, int]:
        end_millis = self._to_epoch_millis(end_datetime, "end_datetime")
        if end_millis is None:
            end_millis = self._utc_now_millis()

        start_millis = self._to_epoch_millis(start_datetime, "start_datetime")
        if start_millis is None:
            start_millis = end_millis - int(timedelta(days=self.DEFAULT_TIMEFRAME_DAYS).total_seconds() * 1000)

        return start_millis, end_millis

    def get_feeds(self) -> list[dict]:
        """
        Fetch available data feeds for this asset.

        Returns:
            list[dict]: List of feed definitions.
        """
        return self._client.get_feeds(self.guid)

    def _resolve_feed_names(self, requested_feeds: list[str]) -> list[str]:
        """Resolve feed names using strict exact matching only."""
        available_feeds = self.get_feeds()
        feed_names = [feed["name"] for feed in available_feeds]
        feed_name_set = set(feed_names)

        missing = [requested for requested in requested_feeds if requested not in feed_name_set]

        if missing:
            suggestion_text = self._build_feed_suggestion_text(missing, feed_names)
            raise FeedNotFoundError(self.name, missing, suggestion_text)

        return requested_feeds

    @staticmethod
    def _build_feed_suggestion_text(missing: list[str], available_feed_names: list[str]) -> str:
        """Provide user-friendly guidance when no acceptable match exists."""
        normalized_lookup = {name.casefold(): name for name in available_feed_names}
        suggestions: list[str] = []
        for feed in missing:
            close = get_close_matches(feed.casefold(), normalized_lookup.keys(), n=1, cutoff=0.75)
            if close:
                suggestions.append(f" '{feed}' -> '{normalized_lookup[close[0]]}'")
        if suggestions:
            return " Did you mean" + ",".join(suggestions) + "?"
        return ""
