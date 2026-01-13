from roak_sdk.semantics.asset import Asset
from typing import override
from datetime import datetime
import bisect


class Borehole(Asset):
    """
    Represents a borehole within a rig in ROAK.
    """

    STANDARD_FEEDS = [
        "Depth",
        "Rotation Speed",
        "Rotation Pressure",
        "Bit Force",
        "Pullup Pressure",
    ]

    def __init__(self, guid, name, client, project=None):
        self._guid = guid
        self._name = name
        self._client = client
        self._project = project

    @override
    def get_start_time(self):
        """Borehole default start time is epoch (1970-01-01)."""
        return 0

    # -----------------------------
    # Depth API
    # -----------------------------
    def get_depth_data(self):
        """
        Fetch raw depth data from the depth endpoint, then pivot it into
        timestamp-centric records with all STANDARD_FEEDS.
        """
        raw = self._client.get_depth_data_raw(self._guid)
        return self._pivot_depth_data(raw)

    def _pivot_depth_data(self, feeds_data):
        """
        Convert ROAK depthData response into timestamp-based records.

        Each feed value contains: time, depth, value.
        Returns timestamp-centric records with depth included.
        """

        if not feeds_data:
            return []

        def get_ts(v):
            return v.get("time") or v.get("timestamp")

        timestamps = sorted(
            {
                get_ts(v)
                for f in feeds_data
                for v in f.get("values", [])
                if get_ts(v) is not None
            }
        )

        feed_lookup = {
            f.get("name"): {
                get_ts(v): (v.get("value"), v.get("depth"))
                for v in f.get("values", [])
                if get_ts(v) is not None
            }
            for f in feeds_data
        }

        results = []
        for ts in timestamps:
            record = {"timestamp": ts}
            depth_for_ts = None

            for fname, by_ts in feed_lookup.items():
                value_depth = by_ts.get(ts)
                if value_depth:
                    value, depth = value_depth
                    record[fname] = value
                    if depth is not None:
                        depth_for_ts = depth
                else:
                    record[fname] = None

            record["depth"] = depth_for_ts
            results.append(record)

        return results
