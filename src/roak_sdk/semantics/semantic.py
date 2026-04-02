from __future__ import annotations

from typing import Any

from roak_sdk.clients.client_registry import ClientRegistry
from roak_sdk.clients.semantic_client import SemanticClient


def _snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class Semantic:
    """
    Base class for ROAK semantic objects (Projects, Wells, Boreholes, etc.).
    
    Provides dynamic attribute access from API response data.
    Use snake_case names (e.g., `owner_id`, `start_date`) to access camelCase API fields.
    """

    def __init__(self, data: dict, registry: ClientRegistry) -> None:
        """
        Initialize Semantic from API response data.

        Args:
            data (dict): Data from the API.
            registry (ClientRegistry): Registry for obtaining client instances.
        """
        self._data = data
        self._registry = registry
        self._semantic_client = registry.get(SemanticClient)

        # Core identifiers set explicitly for IDE support
        self.guid: str = data["guid"]
        self.name: str = data["name"]

    def __getattr__(self, name: str) -> Any:
        """
        Dynamically access API fields using snake_case or camelCase names.
        
        E.g., obj.owner_id or obj.ownerId both look up data["ownerId"]
        """
        # Avoid recursion for internal attributes
        if name.startswith('_'):
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")
        
        # Try direct lookup first (for camelCase access)
        if name in self._data:
            return self._data[name]
        
        # Try converting snake_case to camelCase
        camel_name = _snake_to_camel(name)
        if camel_name in self._data:
            return self._data[camel_name]
        
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name='{self.name}', guid='{self.guid}')"
    
    def get_attributes(self) -> dict:
        """
        Get the locally cached attribute dictionary.

        Returns:
            dict: Raw data dictionary.
        """
        return self._data

    def refresh_attributes(self) -> dict:
        """
        Fetch semantic attributes for this semantic and merge into ``_data``.

        Expects the API payload shape to be paged, with the attribute list in
        ``payload["content"]``.

        Returns:
            dict: Updated attributes dictionary.

        Raises:
            KeyError: If ``content`` is missing from the API payload.
            TypeError: If ``content`` is not iterable as expected.
        """
        content = self._semantic_client.get_attributes(self.guid)

        for item in content:
            key = item.get("name")
            if isinstance(key, str):
                self._data[key] = item.get("value")

        if "guid" in self._data:
            self.guid = self._data["guid"]
        if "name" in self._data:
            self.name = self._data["name"]

        return self._data

    def get_last_values(self) -> list[dict]:
        """Get one last-reading summary row per feed for this semantic.

        Returns rows with:
            - feedname
            - last_value
            - unit (unit.name)
            - record_time
        """
        content = self._semantic_client.get_feeds(self.guid)
        

        result: list[dict] = []
        for feed in content:
            if not isinstance(feed, dict):
                continue

            reading = feed.get("lastReceivedReading") or feed.get("lastSentReading") or {}
            unit = feed.get("unit") or {}

            result.append(
                {
                    "feedname": feed.get("name"),
                    "last_value": reading.get("data") if isinstance(reading, dict) else None,
                    "unit": unit.get("name") if isinstance(unit, dict) else None,
                    "record_time": reading.get("recordingTime") if isinstance(reading, dict) else None,
                }
            )

        return result