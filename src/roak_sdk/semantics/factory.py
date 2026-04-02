"""
Factory functions for creating semantic objects from API data.
"""
from roak_sdk.clients.client_registry import ClientRegistry
from roak_sdk.semantics.assets.well import Well
from roak_sdk.semantics.assets.borehole import Borehole
from roak_sdk.semantics.asset import Asset


# Asset type constants
ASSET_TYPE_WELL = "GWM_WELL"
ASSET_TYPE_BOREHOLE = "MWD_BOREHOLE"

def make_asset(data: dict, registry: ClientRegistry) -> Asset:
    """
    Factory function to create the correct asset type based on data.

    Args:
        data (dict): Asset data from the API.
        registry (ClientRegistry): Registry for obtaining client instances.

    Returns:
        Asset: Well, Borehole, Rig, or generic Asset based on typeGuid.
    """
    type_guid = data.get("typeGuid", "")

    if ASSET_TYPE_WELL in type_guid:
        return Well(data, registry)
    elif ASSET_TYPE_BOREHOLE in type_guid:
        return Borehole(data, registry)
    else:
        return Asset(data, registry)
