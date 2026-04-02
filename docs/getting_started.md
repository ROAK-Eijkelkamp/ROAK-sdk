# Getting Started with the ROAK SDK

This guide is aimed at first-time users. It covers the most common flows in a simple and clear way.

---

## What You Need

- Python 3.10 through 3.12
- A virtual environment (`venv` or `.venv`)
- A ROAK username and password
- Access to a ROAK environment URL (e.g. `https://dev.roak.com`)

---

## Installation

Create and activate a virtual environment first, then install the SDK in editable
mode:

```bash
python -m venv .venv
```

On Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

```bash
pip install -e .
```

For development tools (pytest, dotenv, pandas):

```bash
pip install -e ".[dev]"
```

The supported runtime versions are intentionally narrow so that the same setup
works reliably across the team.

---

## Setting Up Credentials

Store your credentials in a `.env` file:

```
ROAK_USERNAME=your_username
ROAK_PASSWORD=your_password
ROAK_BASE_URL=https://dev.roak.com
```

Load them in your script:

```python
import os
from dotenv import load_dotenv

load_dotenv()

ROAK_USERNAME = os.getenv("ROAK_USERNAME")
ROAK_PASSWORD = os.getenv("ROAK_PASSWORD")
ROAK_BASE_URL = os.getenv("ROAK_BASE_URL", "https://dev.roak.com")
```

---

## Connecting

```python
from roak_sdk import Roak

roak = Roak(
    username=ROAK_USERNAME,
    password=ROAK_PASSWORD,
    base_url=ROAK_BASE_URL,
)
```

Add `debug=True` to see the HTTP requests being made — useful when troubleshooting:

```python
roak = Roak(username=ROAK_USERNAME, password=ROAK_PASSWORD, base_url=ROAK_BASE_URL, debug=True)
```

You can also control request timeouts when creating the SDK instance. Pass a custom
timeout in seconds, or disable timeouts entirely with `None` or `-1` if you know a
query can take a long time:

```python
roak = Roak(
    username=ROAK_USERNAME,
    password=ROAK_PASSWORD,
    base_url=ROAK_BASE_URL,
    request_timeout=60,
)

roak_no_timeout = Roak(
    username=ROAK_USERNAME,
    password=ROAK_PASSWORD,
    base_url=ROAK_BASE_URL,
    request_timeout=-1,
)
```

If you need to change it after creation, call:

```python
roak.set_request_timeout(120)
roak.set_request_timeout(-1)
```

---

## Getting Well Data

This is the most common use case for companies with groundwater monitoring wells.

```python
from datetime import datetime, timezone

START_DATE = datetime(2024, 6, 1, tzinfo=timezone.utc)
END_DATE   = datetime(2024, 6, 2, tzinfo=timezone.utc)

# Navigate: project → well → data
project = roak.get_project_by_name("My Project")
well    = project.get_well_by_guid("548006ef-28bd-4b0e-9f17-8234e1db9f64")

data = well.get_data(start_datetime=START_DATE, end_datetime=END_DATE)
```

If you already know the well GUID and do not need project context first, you can
look it up directly from the facade:

```python
well = roak.get_well_by_guid("<your_well_guid>")
data = well.get_data(start_datetime=START_DATE, end_datetime=END_DATE)
```

To request specific data feeds only:

```python
data = well.get_data(
    start_datetime=START_DATE,
    end_datetime=END_DATE,
    feeds=["diverPressure", "diverTemperature"],
)
```

---

## Well Data Through a Site

Sites work like projects — they share the same methods.

```python
site  = roak.get_site_by_name("Home")
wells = site.get_wells()

print([well.name for well in wells])

data = wells[0].get_data(start_datetime=START_DATE, end_datetime=END_DATE)
```

You can also inspect the latest known value for all feeds on a well:

```python
latest = wells[0].get_last_values()
# Returns: [{"feedname": "...", "last_value": "...", "unit": "...", "record_time": ...}, ...]
```

---

## Drilling Rig and Borehole Data

For drilling companies wanting to compare borehole efficiency across rigs.

```python
from datetime import datetime, timezone

START = datetime(2024, 4, 11, tzinfo=timezone.utc)
END   = datetime(2026, 4, 12, tzinfo=timezone.utc)

rig       = roak.get_rig_by_name("SOLSA_MWD")
boreholes = rig.get_boreholes()

borehole  = rig.get_borehole_by_name("test aq1")
feeds     = borehole.get_feeds()

data      = borehole.get_data(
    feeds=["rotation_pressure", "torque"],
    start_datetime=START,
    end_datetime=END,
)
```

Borehole data keyed by time **and** depth is available via:

```python
import pandas as pd

depth_data = borehole.get_depth_data()
df = pd.DataFrame(depth_data)
print(df.head())
```

If you already know the borehole GUID or exact name, you can also access it
directly from the facade:

```python
borehole = roak.get_borehole_by_guid("<your-borehole-guid>")

alternative = roak.get_borehole_by_name(
    "test aq1",
    allow_first_match=True,
)
```

You can also list account-wide wells and boreholes directly:

```python
wells = roak.get_wells()
boreholes = roak.get_boreholes()
```

---

## Modem-Only Access

For users who only know their modem IDs and have no project/well context.

```python
modem = roak.get_modem_by_guid("51418045")

# Get data from all child devices attached to this modem
data = modem.get_data_through_children(
    feeds=["diverPressure", "diverTemperature", "baroPressure", "baroTemperature"],
    start_datetime=START_DATE,
    end_datetime=END_DATE,
)

# Or target a specific child device directly
children = modem.get_children()
diver    = next(x for x in children if x.name == "FY747")

diver_data = diver.get_data(
    feeds=["diverPressure", "diverTemperature"],
    start_datetime=START_DATE,
    end_datetime=END_DATE,
)
```

---

## Multi-Tenant Access

Some ROAK accounts span multiple tenants. Pass the main ROAK URL and your
multi-tenant credentials when connecting — the rest of the API works the same way.

```python
roak = Roak(
    username=MULTI_TENANT_USERNAME,
    password=MULTI_TENANT_PASSWORD,
    tenant="MAIN"
)
```

---

## Handling Ambiguous Name Lookups

By default, a name lookup that matches more than one result raises an error:

```python
# Raises ValueError if "Home" matches multiple sites
site = roak.get_site_by_name("Home")
```

If you know you want the first match, pass `allow_first_match=True`:

```python
site = roak.get_site_by_name("Home", allow_first_match=True)
```

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ValueError: start_datetime is required` | Called `get_data()` without a start time | Always pass both `start_datetime` and `end_datetime` |
| `TypeError: start_datetime must be a timezone-aware datetime or int millis` | Passed a naive `datetime` | Add `tzinfo=timezone.utc` to your datetime |
| `ValueError: ... allow_first_match=True` | Name lookup returned more than one match | Use a more specific name or pass `allow_first_match=True` |

---

## Where to Go Next

- [Full API Reference](sphinx/_build/html/index.html) — all classes and methods
- [Architecture overview](architecture.md) — how the SDK is structured internally
