from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from roak_sdk.clients.borehole_client import BoreholeClient
from roak_sdk.clients.base_client import millis_to_datetime
from roak_sdk.semantics.asset import Asset
from roak_sdk.config import DEFAULT_BOREHOLE_FEEDS
from roak_sdk.clients.client_registry import ClientRegistry
    

class Borehole(Asset):
    """Represents a Borehole asset."""

    DEFAULT_FEEDS = DEFAULT_BOREHOLE_FEEDS
    DEFAULT_TIMEFRAME_DAYS = 1  # Boreholes often need very recent data

    def __init__(self, data: dict, registry: ClientRegistry) -> None:
        """Initialize Borehole from API response data."""
        super().__init__(data, registry)
        self._borehole_client = registry.get(BoreholeClient)  # Assuming RigClient has borehole-specific methods

    def get_depth_data(self) -> list[dict]:
        """Fetch depth data for this borehole.
        
        Returns:
            list[dict]: A list of records, each containing:
                - timestamp: The time of the measurement (millis since epoch)
                - datetime: Python datetime object (UTC) derived from timestamp
                - depth: The depth of the measurement
                - <feedname>: The value for each feed at that timestamp/depth
        """
        raw_depth_data = self._borehole_client.get_depth_data(self.guid)
        feed_names = {feed.get("name") for feed in raw_depth_data if feed.get("name")}
        result = self._pivot_depth_data(raw_depth_data)
        return self._forward_fill_values(result, feed_names)

    def _pivot_depth_data(self, raw_data: list[dict]) -> list[dict]:
        """Transform feed-centric depth data to timestamp/depth-centric format.
        
        Args:
            raw_data: List of dicts with name, unitName, unitSymbol, and values
                     (where values is a list of {time, depth, value})
        
        Returns:
            List of dicts with timestamp, datetime, depth, and each feed as <feedname>: <value>
        """
        # Group values by (timestamp, depth)
        grouped = defaultdict(dict)
        
        for feed in raw_data:
            feed_name = feed.get("name")
            for entry in feed.get("values", []):
                key = (entry.get("time"), entry.get("depth"))
                grouped[key][feed_name] = entry.get("value")
        
        # Build the result list
        result = []
        for (timestamp, depth), feed_values in grouped.items():
            record = {
                "timestamp": timestamp,
                "datetime": millis_to_datetime(timestamp) if timestamp is not None else None,
                "depth": depth,
            }
            record.update(feed_values)
            result.append(record)
        
        # Sort by timestamp, then by depth
        result.sort(key=lambda x: (x.get("timestamp") or 0, x.get("depth") or 0))
        
        return result

    def _forward_fill_values(self, records: list[dict], feed_names: set[str]) -> list[dict]:
        """Forward-fill empty values from previous records.
        
        Args:
            records: List of record dicts to fill.
            feed_names: Set of feed names to check and fill.
        
        Returns:
            New list of dicts with empty values forward-filled.
        """
        result = []
        last_values = {}
        for record in records:
            filled_record = record.copy()
            for feed_name in feed_names:
                value = filled_record.get(feed_name)
                if value is None or value == "":
                    # Use previous value if available
                    if feed_name in last_values:
                        filled_record[feed_name] = last_values[feed_name]
                else:
                    # Update last known value
                    last_values[feed_name] = value
            result.append(filled_record)
        return result