from __future__ import annotations

from datetime import datetime

from roak_sdk.semantics.device import Device


class Modem(Device):
    """
    Represents a Modem device in the ROAK system.
    Inherits from the base Device class.
    """

    DEFAULT_FEEDS = ["diverPressure", "diverTemperature", "baroPressure", "baroTemperature"]

    def get_data_through_children(
        self,
        feeds: list[str] | None = None,
        start_datetime: datetime | int | None = None,
        end_datetime: datetime | int | None = None,
    ) -> dict:
        """
        Fetch data for this device by aggregating data from child devices.

        Args:
            feeds (list[str] | None): Optional list of feed names to filter by.
            start_datetime (datetime | int | None): Start datetime as timezone-aware
                datetime or milliseconds since epoch.
            end_datetime (datetime | int | None): End datetime as timezone-aware
                datetime or milliseconds since epoch.

        Returns:
            dict: Mapping of child device name to its data.
        """
        if not feeds:
            feeds = self.DEFAULT_FEEDS

        start_millis, end_millis = self._resolve_time_range(start_datetime, end_datetime)

        children = self.get_children()
        data = {}
        for child in children:
            child_feeds = child.get_feeds()
            relevant_feeds = [feed['name'] for feed in child_feeds if feed['name'] in feeds]
            if relevant_feeds:
                child_data = child.get_data(
                    start_datetime=start_millis,
                    end_datetime=end_millis,
                    feeds=relevant_feeds,
                )
                data[child.name] = child_data
        return data