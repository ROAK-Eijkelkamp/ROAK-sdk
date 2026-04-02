from __future__ import annotations

from unittest.mock import MagicMock, call

import pytest

import roak_sdk.roak as roak_module
from roak_sdk.config import CUSTOMER_TYPE, MODEM_TYPES, RIG_TYPES
from roak_sdk.roak_error import AssetTypeMismatchError
from roak_sdk.roak import Roak
from roak_sdk.semantics.asset import Asset
from roak_sdk.semantics.customer import Customer
from roak_sdk.semantics.assets.well import Well
from roak_sdk.semantics.assets.borehole import Borehole
from roak_sdk.semantics.devices.modem import Modem
from roak_sdk.semantics.devices.rig import Rig
from roak_sdk.semantics.project import Project
from roak_sdk.semantics.site import Site
from tests.conftest import StubRegistry


def test_roak_init_wires_auth_registry_and_roak_client(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_roak_client = MagicMock(name="RoakClientInstance")

    class FakeAuth:
        def __init__(self, username, password, base_url=None, tenant=None, request_timeout=None):
            self.username = username
            self.password = password
            self.base_url = base_url
            self.tenant = tenant
            self.request_timeout = request_timeout

        def authenticate(self):
            return {"authorization": "Bearer token"}

    class FakeRegistry:
        last_instance = None

        def __init__(self, headers, base_url, refresh_callback=None, debug=False, request_timeout=None):
            self.headers = headers
            self.base_url = base_url
            self.refresh_callback = refresh_callback
            self.debug = debug
            self.request_timeout = request_timeout
            FakeRegistry.last_instance = self

        def get(self, client_class):
            self.last_requested = client_class
            return fake_roak_client

        def refresh_tokens(self):
            return {"authorization": "Bearer refreshed"}

    monkeypatch.setattr(roak_module, "Auth", FakeAuth)
    monkeypatch.setattr(roak_module, "ClientRegistry", FakeRegistry)

    sdk = Roak(
        "user",
        "pass",
        base_url="https://example.test",
        tenant="tenant-a",
        debug=True,
        request_timeout=15,
    )

    assert sdk.headers == {"authorization": "Bearer token"}
    assert sdk._roak_client is fake_roak_client
    assert isinstance(sdk.auth, FakeAuth)
    assert FakeRegistry.last_instance.headers == {"authorization": "Bearer token"}
    assert FakeRegistry.last_instance.base_url == "https://example.test"
    assert callable(FakeRegistry.last_instance.refresh_callback)
    assert FakeRegistry.last_instance.debug is True
    assert FakeRegistry.last_instance.request_timeout == 15
    assert sdk.auth.request_timeout == 15


def test_roak_refresh_tokens_delegates_to_registry() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = MagicMock()
    sdk._registry.refresh_tokens.return_value = {"authorization": "Bearer refreshed"}

    result = sdk.refresh_tokens()

    assert result == {"authorization": "Bearer refreshed"}
    sdk._registry.refresh_tokens.assert_called_once_with()


def test_roak_internal_refresh_updates_headers() -> None:
    sdk = Roak.__new__(Roak)
    sdk.auth = MagicMock()
    sdk.auth.refresh_access_token.return_value = {"authorization": "Bearer refreshed"}

    result = sdk._refresh_tokens()

    assert result == {"authorization": "Bearer refreshed"}
    assert sdk.headers == {"authorization": "Bearer refreshed"}


def test_roak_set_request_timeout_updates_auth_and_registry() -> None:
    sdk = Roak.__new__(Roak)
    sdk.auth = MagicMock()
    sdk._registry = MagicMock()
    sdk._registry.update_request_timeout.return_value = 12.5

    result = sdk.set_request_timeout(12.5)

    assert result == 12.5
    assert sdk.request_timeout == 12.5
    assert sdk.auth.request_timeout == 12.5
    sdk._registry.update_request_timeout.assert_called_once_with(12.5)


def test_roak_set_request_timeout_can_disable_timeouts() -> None:
    sdk = Roak.__new__(Roak)
    sdk.auth = MagicMock()
    sdk._registry = MagicMock()
    sdk._registry.update_request_timeout.return_value = None

    result = sdk.set_request_timeout(-1)

    assert result is None
    assert sdk.request_timeout is None
    assert sdk.auth.request_timeout is None
    sdk._registry.update_request_timeout.assert_called_once_with(None)


@pytest.mark.parametrize(
    ("method_name", "type_guid"),
    [
        ("get_customer_by_name", CUSTOMER_TYPE),
        ("get_project_by_name", "ED_PROJECT"),
        ("get_site_by_name", "ED_SITE"),
        ("get_well_by_name", "GWM_WELL"),
        ("get_borehole_by_name", "MWD_BOREHOLE"),
    ],
)
def test_roak_by_name_methods_pass_allow_first_match(
    method_name: str,
    type_guid: str,
) -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_name_and_type.return_value = {
        "guid": "x-1",
        "name": "Alpha",
        "typeGuid": type_guid,
    }

    method = getattr(sdk, method_name)
    method("Alpha", allow_first_match=True)

    sdk._roak_client.get_asset_by_name_and_type.assert_called_once_with(
        name="Alpha",
        type_guid=type_guid,
        allow_first_match=True,
    )


def test_roak_get_rig_by_name_passes_allow_first_match() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_name_and_type.return_value = {
        "guid": "rig-1",
        "name": "Rig A",
        "typeGuid": RIG_TYPES[0],
    }

    sdk.get_rig_by_name("Rig A", allow_first_match=True)

    sdk._roak_client.get_asset_by_name_and_type.assert_called_once_with(
        name="Rig A",
        allow_first_match=True,
    )


def test_roak_get_rig_by_name_raises_on_non_rig_type() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_name_and_type.return_value = {
        "guid": "asset-1",
        "name": "Not Rig",
        "typeGuid": "NOT_A_RIG",
    }

    with pytest.raises(AssetTypeMismatchError, match="not a Rig"):
        sdk.get_rig_by_name("Not Rig")


def test_roak_get_modem_by_guid_raises_on_non_modem_type() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_guid.return_value = {
        "guid": "asset-1",
        "name": "Not Modem",
        "typeGuid": "NOT_A_MODEM",
    }

    with pytest.raises(AssetTypeMismatchError, match="not a Modem"):
        sdk.get_modem_by_guid("asset-1")


def test_roak_get_site_by_guid_returns_site() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_guid.return_value = {
        "guid": "s-1",
        "name": "Site 1",
        "typeGuid": "ED_SITE",
    }

    site = sdk.get_site_by_guid("s-1")

    assert isinstance(site, Site)
    assert site.guid == "s-1"
    assert site.name == "Site 1"
    sdk._roak_client.get_asset_by_guid.assert_called_once_with(guid="s-1")


def test_roak_get_asset_by_guid_returns_well_from_factory() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_guid.return_value = {
        "guid": "w-1",
        "name": "Well 1",
        "typeGuid": "GWM_WELL",
    }

    asset = sdk.get_asset_by_guid("w-1")

    assert isinstance(asset, Well)
    assert asset.guid == "w-1"
    sdk._roak_client.get_asset_by_guid.assert_called_once_with(guid="w-1")


def test_roak_get_asset_by_guid_returns_generic_asset_for_unknown_type() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_guid.return_value = {
        "guid": "asset-1",
        "name": "Generic Asset",
        "typeGuid": "SOME_UNKNOWN_TYPE",
    }

    asset = sdk.get_asset_by_guid("asset-1")

    assert type(asset) is Asset
    assert asset.guid == "asset-1"
    sdk._roak_client.get_asset_by_guid.assert_called_once_with(guid="asset-1")


def test_roak_get_asset_by_name_passes_type_and_allow_first_match() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_name_and_type.return_value = {
        "guid": "w-1",
        "name": "Well 1",
        "typeGuid": "GWM_WELL",
    }

    asset = sdk.get_asset_by_name("Well 1", asset_type="GWM_WELL", allow_first_match=True)

    assert isinstance(asset, Well)
    assert asset.guid == "w-1"
    sdk._roak_client.get_asset_by_name_and_type.assert_called_once_with(
        name="Well 1",
        type_guid="GWM_WELL",
        allow_first_match=True,
    )


def test_roak_get_asset_by_name_returns_generic_asset_for_unknown_type() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_name_and_type.return_value = {
        "guid": "asset-1",
        "name": "Generic Asset",
        "typeGuid": "SOME_UNKNOWN_TYPE",
    }

    asset = sdk.get_asset_by_name("Generic Asset")

    assert type(asset) is Asset
    assert asset.guid == "asset-1"
    sdk._roak_client.get_asset_by_name_and_type.assert_called_once_with(
        name="Generic Asset",
        type_guid=None,
        allow_first_match=False,
    )


def test_roak_get_well_by_guid_returns_well() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_guid.return_value = {
        "guid": "w-1",
        "name": "Well 1",
        "typeGuid": "GWM_WELL",
    }

    well = sdk.get_well_by_guid("w-1")

    assert isinstance(well, Well)
    assert well.guid == "w-1"
    assert well.name == "Well 1"
    sdk._roak_client.get_asset_by_guid.assert_called_once_with(guid="w-1")


def test_roak_get_well_by_guid_raises_on_non_well_type() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_guid.return_value = {
        "guid": "asset-1",
        "name": "Not Well",
        "typeGuid": "MWD_BOREHOLE",
    }

    with pytest.raises(AssetTypeMismatchError, match="not a Well"):
        sdk.get_well_by_guid("asset-1")


def test_roak_get_well_by_name_returns_well() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_name_and_type.return_value = {
        "guid": "w-1",
        "name": "Well 1",
        "typeGuid": "GWM_WELL",
    }

    well = sdk.get_well_by_name("Well 1")

    assert isinstance(well, Well)
    assert well.guid == "w-1"
    assert well.name == "Well 1"
    sdk._roak_client.get_asset_by_name_and_type.assert_called_once_with(
        name="Well 1",
        type_guid="GWM_WELL",
        allow_first_match=False,
    )


def test_roak_get_well_by_name_raises_on_non_well_type() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_name_and_type.return_value = {
        "guid": "asset-1",
        "name": "Not Well",
        "typeGuid": "MWD_BOREHOLE",
    }

    with pytest.raises(AssetTypeMismatchError, match="not a Well"):
        sdk.get_well_by_name("Not Well")


def test_roak_get_borehole_by_guid_returns_borehole() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_guid.return_value = {
        "guid": "bh-1",
        "name": "Borehole 1",
        "typeGuid": "MWD_BOREHOLE",
    }

    borehole = sdk.get_borehole_by_guid("bh-1")

    assert isinstance(borehole, Borehole)
    assert borehole.guid == "bh-1"
    assert borehole.name == "Borehole 1"
    sdk._roak_client.get_asset_by_guid.assert_called_once_with(guid="bh-1")


def test_roak_get_borehole_by_guid_raises_on_non_borehole_type() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_guid.return_value = {
        "guid": "asset-1",
        "name": "Not Borehole",
        "typeGuid": "GWM_WELL",
    }

    with pytest.raises(AssetTypeMismatchError, match="not a Borehole"):
        sdk.get_borehole_by_guid("asset-1")


def test_roak_get_borehole_by_name_returns_borehole() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_name_and_type.return_value = {
        "guid": "bh-1",
        "name": "Borehole 1",
        "typeGuid": "MWD_BOREHOLE",
    }

    borehole = sdk.get_borehole_by_name("Borehole 1")

    assert isinstance(borehole, Borehole)
    assert borehole.guid == "bh-1"
    assert borehole.name == "Borehole 1"
    sdk._roak_client.get_asset_by_name_and_type.assert_called_once_with(
        name="Borehole 1",
        type_guid="MWD_BOREHOLE",
        allow_first_match=False,
    )


def test_roak_get_borehole_by_name_raises_on_non_borehole_type() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_name_and_type.return_value = {
        "guid": "asset-1",
        "name": "Not Borehole",
        "typeGuid": "GWM_WELL",
    }

    with pytest.raises(AssetTypeMismatchError, match="not a Borehole"):
        sdk.get_borehole_by_name("Not Borehole")


def test_roak_get_rig_by_guid_returns_rig() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_guid.return_value = {
        "guid": "r-1",
        "name": "Rig 1",
        "typeGuid": RIG_TYPES[0],
    }

    rig = sdk.get_rig_by_guid("r-1")

    assert isinstance(rig, Rig)
    assert rig.guid == "r-1"
    assert rig.name == "Rig 1"
    sdk._roak_client.get_asset_by_guid.assert_called_once_with(guid="r-1")


def test_roak_get_rig_by_guid_raises_on_non_rig_type() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_guid.return_value = {
        "guid": "asset-1",
        "name": "Not Rig",
        "typeGuid": "NOT_A_RIG",
    }

    with pytest.raises(AssetTypeMismatchError, match="not a Rig"):
        sdk.get_rig_by_guid("asset-1")


def test_roak_get_modem_by_name_delegates_to_get_modem_by_guid() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_guid.return_value = {
        "guid": "modem-serial-123",
        "name": "modem-serial-123",
        "typeGuid": MODEM_TYPES[0],
    }

    modem = sdk.get_modem_by_name("modem-serial-123")

    assert isinstance(modem, Modem)
    assert modem.guid == "modem-serial-123"
    assert modem.name == "modem-serial-123"
    sdk._roak_client.get_asset_by_guid.assert_called_once_with(guid="modem-serial-123")


def test_roak_get_modem_by_name_raises_on_non_modem_type() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()
    sdk._roak_client.get_asset_by_guid.return_value = {
        "guid": "asset-1",
        "name": "Not Modem",
        "typeGuid": "NOT_A_MODEM",
    }

    with pytest.raises(AssetTypeMismatchError, match="not a Modem"):
        sdk.get_modem_by_name("asset-1")


def test_roak_collection_methods_return_expected_semantic_types() -> None:
    sdk = Roak.__new__(Roak)
    sdk._registry = StubRegistry()
    sdk._roak_client = MagicMock()

    sdk._roak_client.get_customers.return_value = [
        {"guid": "c-1", "name": "Customer 1", "typeGuid": CUSTOMER_TYPE}
    ]
    sdk._roak_client.get_projects.return_value = [
        {"guid": "p-1", "name": "Project 1", "typeGuid": "ED_PROJECT"}
    ]
    sdk._roak_client.get_assets.side_effect = [
        [{"guid": "s-1", "name": "Site 1", "typeGuid": "ED_SITE"}],
        [{"guid": "w-1", "name": "Well 1", "typeGuid": "GWM_WELL"}],
        [{"guid": "bh-1", "name": "Borehole 1", "typeGuid": "MWD_BOREHOLE"}],
    ]
    sdk._roak_client.get_rigs.return_value = [
        {"guid": "r-1", "name": "Rig 1", "typeGuid": RIG_TYPES[0]}
    ]
    sdk._roak_client.get_modems.return_value = [
        {"guid": "m-1", "name": "Modem 1", "typeGuid": MODEM_TYPES[0]}
    ]

    customers = sdk.get_customers()
    projects = sdk.get_projects()
    sites = sdk.get_sites()
    wells = sdk.get_wells()
    boreholes = sdk.get_boreholes()
    rigs = sdk.get_rigs()
    modems = sdk.get_modems()

    assert all(isinstance(item, Customer) for item in customers)
    assert all(isinstance(item, Project) for item in projects)
    assert all(isinstance(item, Site) for item in sites)
    assert all(isinstance(item, Well) for item in wells)
    assert all(isinstance(item, Borehole) for item in boreholes)
    assert all(isinstance(item, Rig) for item in rigs)
    assert all(isinstance(item, Modem) for item in modems)
    assert sdk._roak_client.get_assets.call_args_list == [
        call(type_guid="ED_SITE"),
        call(type_guid="GWM_WELL"),
        call(type_guid="MWD_BOREHOLE"),
    ]
