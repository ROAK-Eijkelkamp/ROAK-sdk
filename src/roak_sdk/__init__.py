"""
roak_sdk package initializer.
This will print a message when the package is imported to verify installation.
"""

__version__ = "0.1.0"

# --- Public classes and clients ---
from .semantics.assets.well import Well
from .semantics.assets.rig import Rig
from .semantics.assets.borehole import Borehole
from .semantics.project import Project
from .semantics.assets.generic_asset import GenericAsset
from .clients.asset_client import AssetClient
from .clients.well_client import WellClient
from .clients.rig_client import RigClient
from .clients.project_client import ProjectClient


from roak_sdk.roak import Roak
from roak_sdk.auth import Auth


# --- Public factory function ---


def roak(user: str, password, base_url=None) -> Roak:
    """
    Create and return a ready-to-use Roak SDK client.

    Args:
        user (str): Username.
        password (str): Password.
        base_url (str | None): Custom API URL (tenant).
                               Defaults to (https://royaleijkelkamp.roak.com) if not provided.
    """
    return Roak(user=user, password=password, base_url=base_url)


# This makes autocomplete cleaner and defines the public part of the API:
__all__ = [
    "roak",
    "Roak",
    "Auth",
    "Well",
    "Rig",
    "WellClient",
    "RigClient",
    "ProjectClient",
]
