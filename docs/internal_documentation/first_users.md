# ROAK SDK for First Users

This SDK is a read-focused Python library for working with ROAK data. It helps you authenticate, find customers, projects, sites, rigs, modems, wells, and boreholes, and retrieve the data attached to them.

The supported setup is a Python virtual environment running Python 3.10 through
3.12, installed in editable mode with `pip install -e .`.

## What is included

- Logging in with a username, password, and optional tenant
- Looking up customers, projects, sites, rigs, modems, wells, and boreholes
- Reading asset metadata and current attributes
- Reading feed lists and historical data for wells, boreholes, rigs, and modems
- Getting depth-based borehole data and child-device data through modems
- Choosing a custom request timeout, or disabling it for long-running queries
- Installing the SDK in a virtual environment with `pip install -e .`

## What is not included

- Sending or uploading data back to ROAK
- Creating, updating, or deleting ROAK objects through the SDK
- Bulk import or sync workflows
- Direct database access

## Where to start

1. Read [docs/getting_started.md](getting_started.md) for installation and common usage examples.
2. Open the full API reference in [docs/sphinx/_build/html/index.html](sphinx/_build/html/index.html).
3. If you are new to the repo, read [docs/architecture.md](architecture.md) to understand how the SDK is structured.

## Quick path for new users

- Install the package.
- Create a virtual environment and install the package with `pip install -e .`.
- Set `ROAK_USERNAME`, `ROAK_PASSWORD`, and optionally `ROAK_BASE_URL` in your environment.
- Create a `Roak` instance.
- Set `request_timeout` if your query may take longer than the default, or use `None`/`-1` to disable it.
- Start with `get_customers()`, `get_projects()`, or `get_sites()` depending on your access.
- Use the specific asset methods to reach wells, boreholes, rig data, or modem data.

## Timeout control

If a request is expected to take longer than the default timeout, set it when you
create the SDK:

```python
roak = Roak(
	username=ROAK_USERNAME,
	password=ROAK_PASSWORD,
	request_timeout=60,
)
```

You can change it later too:

```python
roak.set_request_timeout(120)
```

To disable the timeout entirely, use `None` or `-1`.

## Notes

The SDK is designed for reading ROAK data and navigating ROAK assets. It is not a
write API, so sending data back to ROAK is not part of the current scope.
