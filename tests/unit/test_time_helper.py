import unittest
from roak_sdk.time_helper import TimeHelper
import datetime as dt
from roak_sdk.clients.base_client import (
    MILLISECONDS_IN_ONE_SECOND,
    MILLISECONDS_IN_ONE_MINUTE,
    MILLISECONDS_IN_ONE_HOUR,
    MILLISECONDS_IN_ONE_DAY,
    MILLISECONDS_IN_ONE_WEEK,
)


class TestTimeHelper(unittest.TestCase):

    def test_parse_relative_time(self):
        cases = [
            ("30s", 30 * MILLISECONDS_IN_ONE_SECOND),
            ("15m", 15 * MILLISECONDS_IN_ONE_MINUTE),
            ("6h", 6 * MILLISECONDS_IN_ONE_HOUR),
            ("3d", 3 * MILLISECONDS_IN_ONE_DAY),
            ("2w", 2 * MILLISECONDS_IN_ONE_WEEK),
        ]
        for val, expected in cases:
            self.assertEqual(TimeHelper.parse_relative_time(val), expected)

    def test_parse_relative_time_invalid(self):
        with self.assertRaises(ValueError):
            TimeHelper.parse_relative_time("10x")

    def test_parse_time_string_datetime(self):
        dt_str = "2025-11-06 12:00:00"
        ref = 0
        ms = TimeHelper.parse_time_string(dt_str, ref)
        expected = int(
            dt.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").timestamp() * 1000
        )
        self.assertEqual(ms, expected)

    def test_parse_time_string_relative(self):
        ref = 100_000
        ms = TimeHelper.parse_time_string("6h", ref)
        self.assertEqual(ms, ref - 6 * MILLISECONDS_IN_ONE_HOUR)

    def test_normalize_start_end_datetime(self):
        now = dt.datetime.now()
        ms = int(now.timestamp() * 1000)
        self.assertEqual(TimeHelper.normalize_start_time(now, ms, None), ms)
        self.assertEqual(TimeHelper.normalize_end_time(now, ms), ms)

    def test_normalize_start_end_int(self):
        val = 123456
        self.assertEqual(TimeHelper.normalize_start_time(val, 0, None), val)
        self.assertEqual(TimeHelper.normalize_end_time(val, 0), val)

    def test_normalize_start_end_relative(self):
        end_ms = 2_000_000
        start_ms = TimeHelper.normalize_start_time(None, end_ms, "6h")
        self.assertEqual(start_ms, end_ms - 6 * MILLISECONDS_IN_ONE_HOUR)

    def test_normalize_start_end_invalid_type(self):
        with self.assertRaises(TypeError):
            TimeHelper.normalize_start_time([1, 2, 3], 0)  # type: ignore
        with self.assertRaises(TypeError):
            TimeHelper.normalize_end_time([1, 2, 3], 0)  # type: ignore

    def test_define_time_defaults(self):
        times = TimeHelper.define_time()
        self.assertIn("from", times)
        self.assertIn("to", times)
        self.assertGreater(times["to"], times["from"])

    def test_define_time_custom_start_end(self):
        start = dt.datetime.now() - dt.timedelta(hours=2)
        end = dt.datetime.now()
        times = TimeHelper.define_time(start=start, end=end)
        self.assertEqual(times["from"], int(start.timestamp() * 1000))
        self.assertEqual(times["to"], int(end.timestamp() * 1000))

    def test_define_time_relative_only(self):
        end_ms = int(dt.datetime.now().timestamp() * 1000)
        times = TimeHelper.define_time(time_period="3h", end=end_ms)
        self.assertEqual(times["from"], end_ms - 3 * MILLISECONDS_IN_ONE_HOUR)
        self.assertEqual(times["to"], end_ms)
