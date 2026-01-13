from roak_sdk.semantics.asset import Asset


class GenericAsset(Asset):
    STANDARD_FEEDS = []  # unknown until user sets

    def _resolve_feeds(self, feeds):
        if feeds == "ALL":
            return self.get_feeds()
        if feeds is None:
            raise ValueError(
                "GenericAsset requires you to provide specific feeds or 'ALL'."
            )
        return feeds

    def get_data(self, feeds=None, start=None, end=None):
        resolved_feeds = self._resolve_feeds(feeds)
        return self._client.fetch_data(
            self._guid, feeds=resolved_feeds, start=start, end=end
        )

    def get_feeds(self):
        return self._client.get_feeds(self._guid)
