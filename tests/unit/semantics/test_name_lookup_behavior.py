from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from roak_sdk.clients.asset_client import AssetClient
from roak_sdk.clients.device_client import DeviceClient
from roak_sdk.clients.project_client import ProjectClient
from roak_sdk.clients.rig_client import RigClient
from roak_sdk.clients.semantic_client import SemanticClient
from roak_sdk.roak_error import AmbiguousAssetMatchError, AssetNotFoundError
from roak_sdk.semantics.devices.rig import Rig
from roak_sdk.semantics.project import Project
from tests.conftest import StubRegistry


class _NamedObj:
    def __init__(self, name: str) -> None:
        self.name = name


def test_project_get_asset_by_name_passes_allow_first_match_flag() -> None:
    project_client = MagicMock(spec=ProjectClient)
    project_client.get_asset_by_name.return_value = {
        "guid": "well-1",
        "name": "Well A",
        "typeGuid": "GWM_WELL",
    }
    registry = StubRegistry(
        {
            SemanticClient: MagicMock(spec=SemanticClient),
            ProjectClient: project_client,
            AssetClient: MagicMock(spec=AssetClient),
        }
    )
    project = Project({"guid": "proj-1", "name": "Project A"}, registry)

    project.get_asset_by_name("Well A", asset_type="GWM_WELL", allow_first_match=True)

    project_client.get_asset_by_name.assert_called_once_with(
        "proj-1",
        "Well A",
        "GWM_WELL",
        allow_first_match=True,
    )


def test_project_get_well_by_name_passes_type_and_allow_first_match() -> None:
    project_client = MagicMock(spec=ProjectClient)
    project_client.get_asset_by_name.return_value = {
        "guid": "well-1",
        "name": "Well A",
        "typeGuid": "GWM_WELL",
    }
    registry = StubRegistry(
        {
            SemanticClient: MagicMock(spec=SemanticClient),
            ProjectClient: project_client,
            AssetClient: MagicMock(spec=AssetClient),
        }
    )
    project = Project({"guid": "proj-1", "name": "Project A"}, registry)

    project.get_well_by_name("Well A", allow_first_match=True)

    project_client.get_asset_by_name.assert_called_once_with(
        "proj-1",
        "Well A",
        "GWM_WELL",
        allow_first_match=True,
    )


def test_project_get_borehole_by_name_passes_type_and_allow_first_match() -> None:
    project_client = MagicMock(spec=ProjectClient)
    project_client.get_asset_by_name.return_value = {
        "guid": "bh-1",
        "name": "BH-1",
        "typeGuid": "MWD_BOREHOLE",
    }
    registry = StubRegistry(
        {
            SemanticClient: MagicMock(spec=SemanticClient),
            ProjectClient: project_client,
            AssetClient: MagicMock(spec=AssetClient),
        }
    )
    project = Project({"guid": "proj-1", "name": "Project A"}, registry)

    project.get_borehole_by_name("BH-1", allow_first_match=True)

    project_client.get_asset_by_name.assert_called_once_with(
        "proj-1",
        "BH-1",
        "MWD_BOREHOLE",
        allow_first_match=True,
    )


def test_project_get_site_by_name_passes_type_and_allow_first_match() -> None:
    project_client = MagicMock(spec=ProjectClient)
    project_client.get_asset_by_name.return_value = {
        "guid": "site-1",
        "name": "Site A",
        "typeGuid": "ED_SITE",
    }
    registry = StubRegistry(
        {
            SemanticClient: MagicMock(spec=SemanticClient),
            ProjectClient: project_client,
            AssetClient: MagicMock(spec=AssetClient),
        }
    )
    project = Project({"guid": "proj-1", "name": "Project A"}, registry)

    project.get_site_by_name("Site A", allow_first_match=True)

    project_client.get_asset_by_name.assert_called_once_with(
        "proj-1",
        "Site A",
        "ED_SITE",
        allow_first_match=True,
    )


def test_rig_get_borehole_by_name_raises_on_multiple_by_default() -> None:
    registry = StubRegistry(
        {
            SemanticClient: MagicMock(spec=SemanticClient),
            AssetClient: MagicMock(spec=AssetClient),
            DeviceClient: MagicMock(spec=DeviceClient),
            RigClient: MagicMock(spec=RigClient),
        }
    )
    rig = Rig({"guid": "rig-1", "name": "Rig A"}, registry)
    rig.get_boreholes = MagicMock(return_value=[_NamedObj("BH-1"), _NamedObj("BH-1")])

    with pytest.raises(AmbiguousAssetMatchError, match="allow_first_match=True"):
        rig.get_borehole_by_name("BH-1")


def test_rig_get_borehole_by_name_returns_first_when_allowed() -> None:
    registry = StubRegistry(
        {
            SemanticClient: MagicMock(spec=SemanticClient),
            AssetClient: MagicMock(spec=AssetClient),
            DeviceClient: MagicMock(spec=DeviceClient),
            RigClient: MagicMock(spec=RigClient),
        }
    )
    rig = Rig({"guid": "rig-1", "name": "Rig A"}, registry)
    first = _NamedObj("BH-1")
    second = _NamedObj("BH-1")
    rig.get_boreholes = MagicMock(return_value=[first, second])

    result = rig.get_borehole_by_name("BH-1", allow_first_match=True)

    assert result is first


def test_rig_get_borehole_by_name_raises_when_not_found() -> None:
    registry = StubRegistry(
        {
            SemanticClient: MagicMock(spec=SemanticClient),
            AssetClient: MagicMock(spec=AssetClient),
            DeviceClient: MagicMock(spec=DeviceClient),
            RigClient: MagicMock(spec=RigClient),
        }
    )
    rig = Rig({"guid": "rig-1", "name": "Rig A"}, registry)
    rig.get_boreholes = MagicMock(return_value=[_NamedObj("BH-1")])

    with pytest.raises(AssetNotFoundError, match="not found"):
        rig.get_borehole_by_name("BH-404")
