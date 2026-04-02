"""HV5 – Borehole transformation logic tests.

Covers:
  - _pivot_depth_data: grouping, sort order, datetime conversion
  - _forward_fill_values: None and empty-string propagation
  - get_depth_data: end-to-end through both helpers
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from roak_sdk.semantics.assets.borehole import Borehole


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_borehole(depth_data=None):
    """Return a Borehole wired to a stub registry whose BoreholeClient returns depth_data."""
    registry = MagicMock()
    borehole_client = MagicMock()
    borehole_client.get_depth_data.return_value = depth_data or []
    registry.get.return_value = borehole_client

    data = {
        "attributes": [
            {"name": "guid", "value": "bh-guid-1"},
            {"name": "name", "value": "Borehole Alpha"},
            {"name": "typeGuid", "value": "bh-type-guid"},
        ]
    }
    bh = Borehole.__new__(Borehole)
    bh._data = {a["name"]: a["value"] for a in data["attributes"]}
    bh.guid = "bh-guid-1"
    bh.name = "Borehole Alpha"
    bh._client = MagicMock()
    bh._borehole_client = borehole_client
    return bh


# ---------------------------------------------------------------------------
# _pivot_depth_data
# ---------------------------------------------------------------------------

class TestPivotDepthData:
    def test_empty_raw_data_returns_empty_list(self):
        bh = _make_borehole()
        assert bh._pivot_depth_data([]) == []

    def test_single_feed_single_point(self):
        raw = [{"name": "RPM", "values": [{"time": 1000, "depth": 10.0, "value": 42.0}]}]
        bh = _make_borehole()
        result = bh._pivot_depth_data(raw)

        assert len(result) == 1
        rec = result[0]
        assert rec["timestamp"] == 1000
        assert rec["depth"] == 10.0
        assert rec["RPM"] == 42.0

    def test_datetime_field_is_utc_datetime(self):
        raw = [{"name": "WOB", "values": [{"time": 0, "depth": 0.0, "value": 1.0}]}]
        bh = _make_borehole()
        result = bh._pivot_depth_data(raw)

        dt = result[0]["datetime"]
        assert isinstance(dt, datetime)
        assert dt.tzinfo is not None  # timezone-aware

    def test_datetime_epoch_zero_is_unix_origin(self):
        raw = [{"name": "WOB", "values": [{"time": 0, "depth": 0.0, "value": 1.0}]}]
        bh = _make_borehole()
        result = bh._pivot_depth_data(raw)

        expected = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        assert result[0]["datetime"] == expected

    def test_null_timestamp_gives_none_datetime(self):
        raw = [{"name": "RPM", "values": [{"time": None, "depth": 5.0, "value": 9.0}]}]
        bh = _make_borehole()
        result = bh._pivot_depth_data(raw)

        assert result[0]["datetime"] is None

    def test_two_feeds_same_key_merged_into_one_record(self):
        raw = [
            {"name": "RPM", "values": [{"time": 2000, "depth": 20.0, "value": 10.0}]},
            {"name": "WOB", "values": [{"time": 2000, "depth": 20.0, "value": 50.0}]},
        ]
        bh = _make_borehole()
        result = bh._pivot_depth_data(raw)

        assert len(result) == 1
        assert result[0]["RPM"] == 10.0
        assert result[0]["WOB"] == 50.0

    def test_sorted_by_timestamp_then_depth(self):
        raw = [
            {"name": "RPM", "values": [
                {"time": 3000, "depth": 30.0, "value": 1},
                {"time": 1000, "depth": 10.0, "value": 2},
                {"time": 2000, "depth": 25.0, "value": 3},
                {"time": 2000, "depth": 10.0, "value": 4},
            ]},
        ]
        bh = _make_borehole()
        result = bh._pivot_depth_data(raw)

        timestamps = [r["timestamp"] for r in result]
        assert timestamps == [1000, 2000, 2000, 3000]

        # Within same timestamp, sorted by depth
        same_ts = [r for r in result if r["timestamp"] == 2000]
        depths = [r["depth"] for r in same_ts]
        assert depths == [10.0, 25.0]

    def test_feed_without_name_is_stored_under_none_key(self):
        """Feeds missing 'name' still get stored; this documents current behaviour."""
        raw = [{"values": [{"time": 100, "depth": 1.0, "value": "x"}]}]
        bh = _make_borehole()
        result = bh._pivot_depth_data(raw)

        assert len(result) == 1
        assert result[0][None] == "x"

    def test_missing_time_or_depth_in_entry_uses_none_key(self):
        raw = [{"name": "RPM", "values": [{"value": 99}]}]  # no time/depth
        bh = _make_borehole()
        result = bh._pivot_depth_data(raw)

        assert len(result) == 1
        assert result[0]["RPM"] == 99
        assert result[0]["timestamp"] is None
        assert result[0]["depth"] is None


# ---------------------------------------------------------------------------
# _forward_fill_values
# ---------------------------------------------------------------------------

class TestForwardFillValues:
    def test_empty_records_returns_empty(self):
        bh = _make_borehole()
        assert bh._forward_fill_values([], {"RPM"}) == []

    def test_none_value_filled_from_previous(self):
        records = [
            {"timestamp": 1, "RPM": 10.0},
            {"timestamp": 2, "RPM": None},
        ]
        bh = _make_borehole()
        result = bh._forward_fill_values(records, {"RPM"})

        assert result[1]["RPM"] == 10.0

    def test_empty_string_filled_from_previous(self):
        records = [
            {"timestamp": 1, "RPM": 10.0},
            {"timestamp": 2, "RPM": ""},
        ]
        bh = _make_borehole()
        result = bh._forward_fill_values(records, {"RPM"})

        assert result[1]["RPM"] == 10.0

    def test_first_record_none_stays_none_no_previous(self):
        records = [{"timestamp": 1, "RPM": None}]
        bh = _make_borehole()
        result = bh._forward_fill_values(records, {"RPM"})

        assert result[0]["RPM"] is None

    def test_non_none_value_not_overwritten(self):
        records = [
            {"timestamp": 1, "RPM": 30.0},
            {"timestamp": 2, "RPM": 50.0},
        ]
        bh = _make_borehole()
        result = bh._forward_fill_values(records, {"RPM"})

        assert result[1]["RPM"] == 50.0

    def test_multiple_feeds_filled_independently(self):
        records = [
            {"timestamp": 1, "RPM": 10.0, "WOB": 100.0},
            {"timestamp": 2, "RPM": None,  "WOB": None},
            {"timestamp": 3, "RPM": 20.0,  "WOB": None},
        ]
        bh = _make_borehole()
        result = bh._forward_fill_values(records, {"RPM", "WOB"})

        assert result[1]["RPM"] == 10.0
        assert result[1]["WOB"] == 100.0
        assert result[2]["RPM"] == 20.0
        assert result[2]["WOB"] == 100.0  # still from record[0]

    def test_original_records_not_mutated(self):
        records = [
            {"timestamp": 1, "RPM": 5.0},
            {"timestamp": 2, "RPM": None},
        ]
        original_second = records[1].copy()
        bh = _make_borehole()
        bh._forward_fill_values(records, {"RPM"})

        assert records[1] == original_second  # input not modified

    def test_feed_not_present_in_record_not_added(self):
        """If a record never had a key for a feed, it should not be injected."""
        records = [
            {"timestamp": 1, "RPM": 5.0},
            {"timestamp": 2},   # no RPM key at all
        ]
        bh = _make_borehole()
        result = bh._forward_fill_values(records, {"RPM"})

        # get() returns None → filled from last_values
        assert result[1]["RPM"] == 5.0


# ---------------------------------------------------------------------------
# get_depth_data – integration through both helpers
# ---------------------------------------------------------------------------

class TestGetDepthData:
    def test_empty_response_returns_empty_list(self):
        bh = _make_borehole(depth_data=[])
        assert bh.get_depth_data() == []

    def test_single_feed_single_point_end_to_end(self):
        depth_data = [
            {"name": "RPM", "values": [{"time": 5000, "depth": 15.0, "value": 120.0}]}
        ]
        bh = _make_borehole(depth_data=depth_data)
        result = bh.get_depth_data()

        assert len(result) == 1
        assert result[0]["timestamp"] == 5000
        assert result[0]["depth"] == 15.0
        assert result[0]["RPM"] == 120.0

    def test_forward_fill_applied_in_full_pipeline(self):
        depth_data = [
            {"name": "RPM", "values": [
                {"time": 1000, "depth": 10.0, "value": 80.0},
                {"time": 2000, "depth": 20.0, "value": None},
            ]}
        ]
        bh = _make_borehole(depth_data=depth_data)
        result = bh.get_depth_data()

        assert result[1]["RPM"] == 80.0  # forward-filled

    def test_result_sorted_by_timestamp(self):
        depth_data = [
            {"name": "WOB", "values": [
                {"time": 3000, "depth": 30.0, "value": 1},
                {"time": 1000, "depth": 10.0, "value": 2},
            ]}
        ]
        bh = _make_borehole(depth_data=depth_data)
        result = bh.get_depth_data()

        assert result[0]["timestamp"] == 1000
        assert result[1]["timestamp"] == 3000

    def test_multiple_feeds_merged_correctly(self):
        depth_data = [
            {"name": "RPM", "values": [{"time": 1000, "depth": 10.0, "value": 60.0}]},
            {"name": "WOB", "values": [{"time": 1000, "depth": 10.0, "value": 200.0}]},
        ]
        bh = _make_borehole(depth_data=depth_data)
        result = bh.get_depth_data()

        assert len(result) == 1
        assert result[0]["RPM"] == 60.0
        assert result[0]["WOB"] == 200.0
