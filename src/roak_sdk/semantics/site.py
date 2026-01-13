from roak_sdk.semantics.semantic import Semantic


class Site(Semantic):
    """
    Represents a site in ROAK.
    A Site may contain multiple Assets but does not directly talk to the API.
    WORK IN PROGRESS
    """

    def __init__(self, guid: str, name: str):  # needs a client for load_feeds
        super().__init__(guid, name, client=None)
        self._assets: list = []  # list of assets inside of this site

    def add_asset(self, asset):
        self._assets.append(asset)

    def get_assets(self):
        return self._assets
