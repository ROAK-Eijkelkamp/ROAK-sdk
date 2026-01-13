from datetime import datetime, timedelta
from roak_sdk.semantics.semantic import Semantic


class Asset(Semantic):
    """
    Base class for all asset types (e.g., Well, Borehole, Generic_Asset).
    Provides shared methods for fetching data and feeds.
    """

    DEFAULT_HOURS = 24

    def __init__(self, guid, name, client, project=None):
        self._guid = guid
        self._name = name
        self._client = client
        self._project = project

    def get_start_time(self):
        """Return a default start time (24 hours ago) unless overridden."""
        return datetime.now() - timedelta(hours=self.DEFAULT_HOURS)

    def get_end_time(self):
        """Return the current datetime as the default end time."""
        return datetime.now()

    def _resolve_feeds(self, feeds=None):
        """
        Resolves which feeds to use:
        - feeds=None  → use STANDARD_FEEDS
        - feeds="ALL" → call client's get_feeds() to get all feeds from the API
        - feeds=list  → use provided list E.g ["wellLength" , "baroTemperature"]
        """

        if feeds is None:
            if hasattr(self, "STANDARD_FEEDS"):
                return getattr(self, "STANDARD_FEEDS")
            raise ValueError("No feeds provided and no STANDARD_FEEDS defined.")

        if feeds == "ALL":
            return self._client.get_feeds(self._guid)

        if isinstance(feeds, list):
            # Validate feeds
            available = set(self.get_feeds())
            invalid = [f for f in feeds if f not in available]

            if invalid:
                raise ValueError(
                    f"One or more of the provided feeds are invalid for asset {self._name}: {invalid}\n"
                    f"Available feeds are: {sorted(available)}"
                )
            return feeds

        raise TypeError("feeds must be None, 'ALL', or a list of strings.")

    def get_feeds(self):
        """
        Return a list of available feeds for this asset.
        Delegates to the client automatically.

        Usage:
            feeds = well.get_feeds()
        """
        return self._client.get_feeds(self._guid)

    def _pivot_data(self, raw_data):
        """
        Convert feed-based format into timestamp-based records.

        From:
            [{"feedName": X, "readings": [{"timestamp": .., "data": ..}, ...]}, ...]

        Into:
            [
                {"timestamp": 12345, "feed1": "value", "feed2": "value"},
                ...
            ]
        """
        timeline = {}

        for feed_block in raw_data:
            feed = feed_block["feedName"]
            for reading in feed_block.get("readings", []):
                ts = reading["timestamp"]
                val = reading["data"]

                if ts not in timeline:
                    timeline[ts] = {"timestamp": ts}

                timeline[ts][feed] = val

        # return sorted by timestamp
        return [timeline[t] for t in sorted(timeline.keys())]

    def get_data(self, feeds=None, start=None, end=None):
        """
        Fetches and pivots time series data for the asset.

        Args:
            feeds (list[str] | str | None): Feed(s) to fetch. Defaults to asset's feeds.
            start (int | float | datetime | None): Start time. Defaults to asset's start.
            end (int | float | datetime | None): End time. Defaults to current time.

        Returns:
            list[dict]: Pivoted data with timestamps and feed values.
        """
        feeds_to_use = self._resolve_feeds(feeds)

        from_ms = start if start is not None else self.get_start_time()
        to_ms = end if end is not None else int(self.get_end_time().timestamp() * 1000)

        raw_data = self._client.fetch_data(
            self._guid, feeds=feeds_to_use, start=from_ms, end=to_ms
        )

        return self._pivot_data(raw_data)
