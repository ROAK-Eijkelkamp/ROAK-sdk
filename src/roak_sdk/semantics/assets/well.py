from __future__ import annotations

from roak_sdk.semantics.asset import Asset
from roak_sdk.config import DEFAULT_WELL_FEEDS

class Well(Asset):
    """Represents a Well asset."""

    DEFAULT_FEEDS = DEFAULT_WELL_FEEDS
    DEFAULT_TIMEFRAME_DAYS = 1 # Wells typically need recent data