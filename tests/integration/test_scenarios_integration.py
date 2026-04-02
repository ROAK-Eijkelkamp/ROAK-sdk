from __future__ import annotations

import os
from datetime import datetime, timezone

import pytest

from roak_sdk import Roak
from roak_sdk.roak_error import TenantNotFoundError


pytestmark = pytest.mark.integration


def _utc_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def _date_from_env(name: str, default_value: str) -> datetime:
    return _utc_date(os.getenv(name, default_value))


def _build_roak(integration_env: dict[str, str], tenant: str | None = None, multi: bool = False) -> Roak:
    base_url = integration_env["multi_base_url"] if multi else integration_env["base_url"]
    return Roak(
        username=integration_env["username"],
        password=integration_env["password"],
        base_url=base_url,
        tenant=tenant,
    )


def test_count_customer_wells_scenario(integration_env: dict[str, str]) -> None:
    roak = _build_roak(integration_env)

    asset_types = roak.get_asset_types()
    assert len(asset_types) >= 1

    customer_name = os.getenv("ROAK_CUSTOMER_NAME", "Royal Eijkelkamp")
    customer = roak.get_customer_by_name(customer_name, allow_first_match=True)
    wells = customer.get_wells()
    assert len(wells) >= 1

    start = _date_from_env("ROAK_START_DATE", "2024-06-01")
    end = _date_from_env("ROAK_END_DATE", "2024-06-02")
    well_data = wells[0].get_data(start_datetime=start, end_datetime=end, feeds=["diverPressure"])
    assert isinstance(well_data, list)


def test_get_well_data_scenario(integration_env: dict[str, str]) -> None:
    roak = _build_roak(integration_env)

    project_name = os.getenv("ROAK_PROJECT_NAME", "Gerard Test")
    well_guid = os.getenv("ROAK_WELL_GUID", "548006ef-28bd-4b0e-9f17-8234e1db9f64")
    start = _date_from_env("ROAK_START_DATE", "2024-06-01")
    end = _date_from_env("ROAK_END_DATE", "2024-06-02")

    projects = roak.get_projects()
    assert len(projects) >= 1

    project = roak.get_project_by_name(project_name, allow_first_match=True)
    assets = project.get_assets()
    assert len(assets) >= 1

    well = project.get_well_by_guid(well_guid)
    well_data = well.get_data(start_datetime=start, end_datetime=end)
    assert isinstance(well_data, list)

    feeds = well.get_feeds()
    assert len(feeds) >= 1


def test_site_well_data_scenario(integration_env: dict[str, str]) -> None:
    roak = _build_roak(integration_env)

    site_name = os.getenv("ROAK_SITE_NAME", "Home")
    site = roak.get_site_by_name(site_name, allow_first_match=True)

    wells = site.get_wells()
    assert len(wells) >= 1

    attributes = wells[0].get_attributes()
    refreshed_attributes = wells[0].refresh_attributes()
    last_values = wells[0].get_last_values()

    assert isinstance(attributes, dict)
    assert isinstance(refreshed_attributes, dict)
    assert isinstance(last_values, list)


def test_get_rig_data_scenario(integration_env: dict[str, str]) -> None:
    roak = _build_roak(integration_env)

    rig_name = os.getenv("ROAK_RIG_NAME", "SOLSA_MWD")
    borehole_name = os.getenv("ROAK_BOREHOLE_NAME", "test aq1")

    start = _date_from_env("ROAK_RIG_START_DATE", "2024-04-11")
    end = _date_from_env("ROAK_RIG_END_DATE", "2024-04-12")

    rig = roak.get_rig_by_name(rig_name, allow_first_match=True)
    boreholes = rig.get_boreholes()
    assert len(boreholes) >= 1

    borehole = rig.get_borehole_by_name(borehole_name, allow_first_match=True)
    feeds = borehole.get_feeds()
    assert len(feeds) >= 1

    selected_feeds = [name for name in ["rotation_pressure", "torque"] if name in {f["name"] for f in feeds}]
    if len(selected_feeds) == 0:
        selected_feeds = [feeds[0]["name"]]

    borehole_data = borehole.get_data(feeds=selected_feeds, start_datetime=start, end_datetime=end)
    roak.set_request_timeout(-1)
    rig_data = rig.get_data(start_datetime=start, end_datetime=end)
    depth_data = borehole.get_depth_data()

    assert isinstance(borehole_data, list)
    assert isinstance(rig_data, list)
    assert isinstance(depth_data, list)


def test_get_data_through_modem_scenario(integration_env: dict[str, str]) -> None:
    roak = _build_roak(integration_env)

    modem_guid_300 = os.getenv("ROAK_MODEM_GUID_300", "43501505")
    modem_guid_400 = os.getenv("ROAK_MODEM_GUID_400", "51418045")
    diver_name = os.getenv("ROAK_DIVER_NAME", "FY747")

    start = _date_from_env("ROAK_MODEM_START_DATE", "2026-01-29")
    end = _date_from_env("ROAK_MODEM_END_DATE", "2026-01-31")

    requested_feeds = ["diverPressure", "diverTemperature", "baroPressure", "baroTemperature"]

    modem_400 = roak.get_modem_by_guid(modem_guid_400)
    modem_400_data = modem_400.get_data_through_children(
        feeds=requested_feeds,
        start_datetime=start,
        end_datetime=end,
    )
    assert isinstance(modem_400_data, dict)

    children = modem_400.get_children()
    diver_children = [child for child in children if child.name == diver_name]
    if diver_children:
        diver_data = diver_children[0].get_data(
            feeds=["diverPressure", "diverTemperature"],
            start_datetime=start,
            end_datetime=end,
        )
        assert isinstance(diver_data, list)

    modem_300 = roak.get_modem_by_guid(modem_guid_300)
    modem_300_data = modem_300.get_data_through_children(
        feeds=requested_feeds,
        start_datetime=start,
        end_datetime=end,
    )
    assert isinstance(modem_300_data, dict)


def test_multi_tenant_scenario_main_and_rd(integration_env: dict[str, str]) -> None:
    tenant_main = os.getenv("ROAK_MULTI_TENANT_PRIMARY", "MAIN")
    tenant_secondary = os.getenv("ROAK_MULTI_TENANT_SECONDARY", "RD")

    roak_main = _build_roak(integration_env, tenant=tenant_main, multi=True)
    try:
        roak_rd = _build_roak(integration_env, tenant=tenant_secondary, multi=True)
    except TenantNotFoundError:
        pytest.skip(
            f"Tenant '{tenant_secondary}' is not available for this user. "
            "Set ROAK_MULTI_TENANT_SECONDARY to a valid tenant name/id."
        )

    main_customers = roak_main.get_customers()
    rd_customers = roak_rd.get_customers()

    assert len(main_customers) >= 1
    assert len(rd_customers) >= 1

    main_wells = main_customers[0].get_wells()
    rd_wells = rd_customers[0].get_wells()

    assert isinstance(main_wells, list)
    assert isinstance(rd_wells, list)
