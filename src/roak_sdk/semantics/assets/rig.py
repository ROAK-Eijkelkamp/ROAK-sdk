from roak_sdk.semantics.asset import Asset


class Rig(Asset):
    STANDARD_FEEDS = [
        "Depth",
        "Rotation Speed",
        "Rotation Pressure",
        "Bit Force",
        "Pullup Pressure",
    ]

    def _resolve_feeds(self, feeds):
        """Return STANDARD_FEEDS if feeds is None or 'ALL', otherwise return provided feeds."""
        if feeds is None or feeds == "ALL":
            return self.STANDARD_FEEDS
        return feeds

    def get_data(self, feeds=None, start=None, end=None):
        resolved_feeds = self._resolve_feeds(feeds)
        return self._client.fetch_data(
            self._guid, feeds=resolved_feeds, start=start, end=end
        )

    def get_boreholes(self):
        """
        Use the RigClient to fetch all Boreholes for this rig.
        """

        return self._client.get_boreholes_for_rig(self._guid)
