from __future__ import annotations

from .base_client import BaseClient


class SemanticClient(BaseClient):
    """Client for generic semantic API operations."""

    def get_attributes(self, semantic_guid: str) -> dict | list[dict]:
        """
        Fetch all known ROAK attributes for a semantic by GUID.

        Args:
            semantic_guid (str): GUID of the semantic object.

        Returns:
            dict | list[dict]: Attributes payload from the API.
        """
        url = f"{self.base_url}/api/semantics/{semantic_guid}/attributes"
        return self._request(url)

    def get_feeds(self, semantic_guid: str) -> dict:
        """Fetch feeds for a semantic by GUID."""
        url = f"{self.base_url}/api/semantics/{semantic_guid}/feeds"
        return self._request(url)