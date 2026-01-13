class Semantic:
    """
    Universal base class for all semantic entities in the ROAK SDK.

    Parent of Project, Site, and Asset.
    Provides consistent identity access via get_guid() and get_name().
    """

    def __init__(self, guid: str, name: str, client=None):
        """
        Args:
            guid (str): The unique identifier for this entity.
            name (str): Human-readable name.
            client (object, optional): API client used for communication.
        """
        self._guid = guid
        self._name = name
        self._client = client  # Can be None (e.g., Site), or shared (e.g., RigClient)

    def get_guid(self) -> str:
        """Return the globally unique identifier (GUID) of this entity."""
        return self._guid

    def get_name(self) -> str:
        """Return the human-readable name of this entity."""
        return self._name

    def get_client(self):
        """Return the client instance associated with this entity, if it has any."""
        return self._client

    def load_feeds(self):
        """
        Loads feed values from the API and creates attributes dynamically.

        This method is designed safe if feeds are added, removed, or renamed in the API.
        """

        client = self.get_client()
        if not client:
            raise RuntimeError(
                f"{self.__class__.__name__} has no client — cannot load feeds."
            )

        if not hasattr(client, "fetch_feeds"):
            raise AttributeError(
                f"Client {client.__class__.__name__} does not support fetch_feeds()."
            )

        # API call
        feed_dict = client.fetch_feeds(self.get_guid())

        if not isinstance(feed_dict, dict):
            raise ValueError(
                f"Expected fetch_feeds() to return dict, got {type(feed_dict)}"
            )

        # store raw feeds
        self._feeds = feed_dict

        # create variables dynamically
        for key, value in feed_dict.items():
            safe_key = str(key).strip().replace(" ", "_")
            setattr(self, safe_key, value)

        return feed_dict
