import re
import datetime as dt
from typing import Dict

MILLISECONDS_IN_ONE_SECOND = 1000
MILLISECONDS_IN_ONE_MINUTE = 60 * MILLISECONDS_IN_ONE_SECOND
MILLISECONDS_IN_ONE_HOUR = 60 * MILLISECONDS_IN_ONE_MINUTE
MILLISECONDS_IN_ONE_DAY = 24 * MILLISECONDS_IN_ONE_HOUR
MILLISECONDS_IN_ONE_WEEK = 7 * MILLISECONDS_IN_ONE_DAY


class TimeHelper:
    """
    Utility class for handling timestamps and relative times.

    Provides methods to get the current time in milliseconds, parse relative
    time strings (like '6h' or '3d'), convert absolute or relative time strings
    to milliseconds, and normalize start/end times for consistent time ranges.
    """

    @staticmethod
    def now_in_ms() -> int:
        return int(dt.datetime.now().timestamp() * 1000)

    @staticmethod
    def parse_relative_time(value: str) -> int:
        m = re.match(r"(\d+)([smhdw])$", value)
        if not m:
            raise ValueError(
                "Relative time must be like '6h', '3d', '2w', '15m', '30s'"
            )
        number, unit = m.groups()
        number = int(number)
        return {
            "s": number * MILLISECONDS_IN_ONE_SECOND,
            "m": number * MILLISECONDS_IN_ONE_MINUTE,
            "h": number * MILLISECONDS_IN_ONE_HOUR,
            "d": number * MILLISECONDS_IN_ONE_DAY,
            "w": number * MILLISECONDS_IN_ONE_WEEK,
        }[unit]

    @staticmethod
    def parse_time_string(time_str: str, reference_ms: int) -> int:
        try:
            dt_obj = dt.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            return int(dt_obj.timestamp() * 1000)
        except ValueError:
            return reference_ms - TimeHelper.parse_relative_time(time_str)

    @classmethod
    def normalize_start_time(
        cls, start, end_ms, time_period=None, default_ms=None
    ) -> int:
        if start is None and default_ms is not None:
            return default_ms
        if start is None:
            if time_period:
                return end_ms - cls.parse_relative_time(time_period)
            return end_ms - MILLISECONDS_IN_ONE_DAY
        if isinstance(start, dt.datetime):
            return int(start.timestamp() * 1000)
        if isinstance(start, int):
            return start
        if isinstance(start, str):
            return cls.parse_time_string(start, end_ms)
        raise TypeError(f"Unsupported start time type: {type(start)}")

    @classmethod
    def normalize_end_time(cls, end, now_ms) -> int:
        if end is None:
            return now_ms
        if isinstance(end, dt.datetime):
            return int(end.timestamp() * 1000)
        if isinstance(end, int):
            return end
        if isinstance(end, str):
            return cls.parse_time_string(end, now_ms)
        raise TypeError(f"Unsupported end time type: {type(end)}")

    @classmethod
    def define_time(cls, start=None, end=None, time_period=None) -> Dict[str, int]:
        now_ms = cls.now_in_ms()
        end_ms = cls.normalize_end_time(end, now_ms)
        start_ms = cls.normalize_start_time(start, end_ms, time_period)
        return {"from": start_ms, "to": end_ms}
