# User Guide Intro
This document gives you the user a basic understanding on how to use the SDK in a meaningfull way.
There are a few examples below that can give you a good idea on how to get started.
I also will explain and show all methods and all optional variables you can use with said methods.
With this information you should be able to get started.

## **Import and basic setup**
*You could rename the sdk import to something shorter if you disire so.*

``` python
import roak_sdk  # required SDK library
import os         # optional, for safe password/username handling
from datetime import datetime, timedelta  # recommended for time-related operations
```

## Authentication with ROAK
*The username and password used here are the same ones you use to login to https://dev.roak.com or https://royaleijkelkamp.roak.com or your custom URL.* 

``` python
username = "your_email@example.com"
password = os.getenv("ROAK_PASSWORD")  # safer 
# or
password = "mypassword123"
```

## Create a ROAK client
*roak is the main entry point for accessing projects, sites, assets, and rigs or wells*
- ``roak = roak_sdk.roak(user=username, password=password)`` 

## Accessing Projects
*You can access all owned projects with multiple sites and assets stored in them and extract one specific one from a project using the name of that project*

``project = roak.get_project(name="myproject1")``

## Getting feeds
*Quick showcase on how to get feeds for data fetching or other uses that need feeds. Most assets have feeds that the user might know about or a user might need a feed that is not in the defaults*

**Note: you *must* have a object of the type of asset you want feeds from.**

```python
rig_guid = "YOUR_RIG_GUID_HERE"

rig = roak.get_rig(rig_guid)

# Get all feeds
rig_feeds = rig.get_feeds()

print(rig_feeds)

# or
print("\nRig feeds:")
for feed in rig_feeds:
    print(feed)
```



## Fetching Data
*Get all assets of a certain type (e.g., wells, rigs) in a project:*

``` python
all_wells = project.get_assets("well") # type can be "well","rig","borehole" and "generic_asset".
```

## Examples
```python
TODAY = datetime.today()
YESTERDAY = TODAY - timedelta(days=1)

all_rigs = project.get_assets("rig")

for rig in all_rigs:
    data = rig.get_data(
        start=YESTERDAY,
        end=TODAY,
        feeds=["Depth", "RealDepth"] # optional, empty = defaults, "ALL" = all feeds
    )
    print(f"Stored data from rig: {rig.name}, {data}")
```

``` python
# define a rig using a GUID
rig1_guid = "5c63cd4b-a2fd-42ab-a5a8-efeb38eeb4af"

# collects one rig's data using the GUID
rig1 = roak_client.get_rig(guid=rig1_guid)
print(rig1) # to see the rig object

# get all boreholes inside of the rig and put it in list/array
boreholes_rig1 = rig1.get_boreholes()
print(boreholes_rig1)
```

## Full Examples
Full Example 1: Flattening Data into a DataFrame
``` python

import roak_sdk
import os
from datetime import datetime, timedelta
import pandas as pd

TODAY = datetime.today()
LAST_MONTH = TODAY - timedelta(days=30)

# connect
password = os.getenv("ROAK_password")
username = "username@eijkelkamp.com"
roak_client = roak_sdk.roak(user=username, password=password)

# get all boreholes of the last month that belong to two specific rigs (MWD Test)
rig1_guid = "SOLSA_MWD"
rig2_guid = "5c63cd4b-a2fd-42ab-a5a8-efeb38eeb4af"

# collects one rig's data
rig1 = roak_client.get_rig(guid=rig1_guid)
print(rig1)

# get all boreholes inside of the rig and put it in list/array
boreholes_rig1 = rig1.get_boreholes()

borehole_data = boreholes_rig1[0].get_data(start=LAST_MONTH, end=TODAY)

# Prepare a flat list first
rows = []
for feed in borehole_data:
    feed_name = feed["name"]
    for v in feed["values"]:
        rows.append(
            {
                "time": v["time"],
                "datetime": pd.to_datetime(v["time"], unit="ms"),
                "depth": v.get("depth"),
                "feed": feed_name,
                "value": float(v["value"]),
            }
        )

df_flat = pd.DataFrame(rows)

# Pivot so that each feed becomes a column
df_pivot = df_flat.pivot_table(
    index=["time", "datetime", "depth"], columns="feed", values="value"
).reset_index()

# flatten index to columns after pivot
df_pivot.columns.name = None
df_pivot = df_pivot.sort_values("datetime").reset_index(drop=True)

print(df_pivot.head())
```

Full Example 2: Getting all owned welldata from a project
``` python
import roak_sdk
import os
from datetime import datetime, timedelta

TODAY = datetime.today()
YESTERDAY = TODAY - timedelta(days=1)

# connect
password = os.getenv("ROAK_PASSWORD")
username = "username@eijkelkamp.com"
roak = roak_sdk.roak(user=username, password=password)  

# gets a specific project
project = roak.get_project(name="Gerard Test")

all_wells = project.get_assets("well")

# get data per well
for well in all_wells:
    data = well.get_data(
        start=YESTERDAY, end=TODAY, feeds=["waterLevelReference", "diverPressure"]
    )
    print(f"Stored data from well: {well.name} , {data}")
```
# ROAK SDK Method Reference

This section lists all main methods users will likely use, with explanations of parameters, return values, and examples. Methods are grouped by class/type for clarity.

## **Roak Methods**

### `get_project(name: str) -> Project | list[Project]`
**Description:** Fetch project(s) via `ProjectClient`.  
- If `name` is provided, returns a single `Project` object.  
- If `name` is omitted or `None`, returns a list of `Project` objects.

**Parameters:**
- `name` (*str, optional*) — The project name to look up. If not provided, all projects are returned.

**Returns:**  
- `Project` (when `name` is provided)  
- `list[Project]` (when `name` is omitted)

**Example:**
```python
# Single project by name
project = roak.get_project("Project A")
print(project.get_name())

# All projects
projects = roak.get_project(None)
for p in projects:
    print(p.get_name())
```

---

### `get_project_guid(name: str) -> str`
**Description:** Look up the **GUID** of a project by its name.

**Parameters:**
- `name` (*str, required*) — The project name.

**Returns:**  
- `str` — The GUID of the project with the given name.

**Raises:**  
- `ValueError` — If a project with the given name is not found.

**Example:**
```python
guid = roak.get_project_guid("Project A")
print(f"Project GUID: {guid}")
```

---

### `get_well(guid: str) -> Well`
**Description:** Create a `Well` object for the given **well GUID**.  
(Uses `WellClient` inside `Roak`.)

**Parameters:**
- `guid` (*str, required*) — The well GUID.

**Returns:**  
- `Well` — A well object bound to the internal `WellClient`.

**Example:**
```python
well = roak.get_well("WELL_GUID_123")
data = well.get_data()  # uses default feeds and time range
print(data)
```

---

### `get_assets(asset_type: str, project_guid: str) -> list`
**Description:** Fetch all assets of a given type for a specific project, then return them as **SDK objects**.  
Internally, it calls the appropriate client’s `get_assets_for_project` and maps raw items to objects:
- "well" → `Well` (via `get_well`)
- "rig" → `Rig` (via `get_rig`)
- "borehole" → `Borehole` (via `get_borehole`)
- "generic" → `GenericAsset` (via `get_generic_asset`)

**Parameters:**
- `asset_type` (*str, required*) — One of: "well", "rig", "borehole", "generic".
- `project_guid` (*str, required*) — The project GUID to filter assets by.

**Returns:**  
- `list` — A list of instantiated asset objects of the requested type.

**Example:**
```python
# Get all wells for a given project
wells = roak.get_assets("well", "PROJECT_GUID_456")
for w in wells:
    print(w.get_name())

# Get all rigs for a project
rigs = roak.get_assets("rig", "PROJECT_GUID_456")
print(len(rigs), "rig(s) found")
```

---

### `get_borehole(guid: str) -> Borehole`
**Description:** Instantiate a `Borehole` object for the given **borehole GUID**.  
(Bound to `AssetClient` in this method.)

**Parameters:**
- `guid` (*str, required*) — The borehole GUID.

**Returns:**  
- `Borehole` — A borehole object connected to `AssetClient`.

**Example:**
```python
bh = roak.get_borehole("BH_GUID_789")
depth_data = bh.get_data()  # borehole overrides to depth endpoint
print(depth_data)
```

---

### `get_generic_asset(guid: str) -> GenericAsset`
**Description:** Instantiate a `GenericAsset` object for the given **asset GUID**.  
(Bound to `AssetClient` in this method.)

**Parameters:**
- `guid` (*str, required*) — The generic asset GUID.

**Returns:**  
- `GenericAsset` — A generic asset object connected to `AssetClient`.

**Example:**
```python
genericAsset = roak.get_generic_asset("GENERIC_GUID_101")
feeds = genericAsset.get_feeds()  # requires 'ALL' or explicit feeds depending on client
print(feeds)
```

---

### `get_rig(guid: str) -> Rig`
**Description:** Obtain a `Rig` object via `RigClient` for the given **rig GUID**.  
(Delegates to `self.rig_client.get_rig(guid)`.)

**Parameters:**
- `guid` (*str, required*) — The rig GUID.

**Returns:**  
- `Rig` — The rig object associated with the GUID.

**Example:**
```python
rig = roak.get_rig("RIG_GUID_202")
rig_data = rig.get_data()  # uses standard feeds unless overridden
print(rig_data)
```

---

### `get_boreholes() -> list[Borehole]`
**Description:** Fetch **all boreholes** owned by the user and return them as `Borehole` objects.  
Internally:
1. Retrieves raw assets with type `MWD_BOREHOLE` using `AssetClient`.
2. Deduplicates based on GUID.
3. Instantiates `Borehole` objects (bound to `RigClient` for depth data).

**Returns:**  
- `list[Borehole]` — Deduplicated list of boreholes.

**Example:**
```python
boreholes = roak.get_boreholes()
for b in boreholes:
    print(b.get_name(), b.get_guid())
```

---

## **Asset Client Methods**
The Asset client has some unqiue methods for calling the assets itself.

**Class:** BaseClient + Children (WellClient, RigClient, AssetClient, GenericAssetClient, ProjectClient)

### `fetch_assets_base(type_guid=None, scope_guid=None, query=None)`

**Description:** Fetch raw asset data from the ROAK API for a specific type, scope, or search query. Returns the unprocessed JSON data from the API.

**Parameters:**

* `type_guid` (*str*, required) — GUID of the asset type to filter by.
* `scope_guid` (*str*, optional) — GUID of the scope to filter by.
* `query` (*str*, optional) — Search query for asset names or metadata.

**Returns:** `dict | list` — Raw JSON response containing assets or metadata.

**Example:**

```python
assets_raw = asset_client.fetch_assets_base(type_guid="GWM_WELL")
print(assets_raw)
```

### `get_all_assets_per_type(type_guids)`

**Description:** Fetch and combine assets across multiple type GUIDs.

**Parameters:**

* `type_guids` (*list[str]*) — List of asset type GUIDs to fetch.

**Returns:** List of deduplicated asset dictionaries.

**Example:**

```python
all_assets = asset_client.get_all_assets_per_type(["GWM_WELL", "MWD_RIGS"])
print(all_assets)
```

### `get_asset_types()`

**Description:** Retrieve all available asset types from the ROAK API that the user has access to.

**Returns:** List or dict of asset type definitions.

**Example:**

```python
asset_types = asset_client.get_asset_types()
print(asset_types)
```

---

## **Client Methods**
These methods are passed from base_client to all clients so all assets have access to these methods.
##### **Example: well_client , rig_client (borehole uses rig_client) and generic_asset_client**


### `get_feeds()`

**Description:**  
Returns the list of feeds available for this asset.  
If the asset defines `STANDARD_FEEDS`, those are returned.  
If the user requests `"ALL"` or the asset has no predefined list, the method asks the client to fetch feeds dynamically from the API.

**Parameters:**  
*(none — the asset already knows its own GUID)*

**Returns:**  
`list[str]` — A list of feed names available for the asset.

**Example:**
```python
well = roak.get_well("ASSET_GUID")
feeds = well.get_feeds()
print(feeds)
```

### `fetch_assets(project_guid, asset_type)`

**Description:** Fetch assets for a project filtered by type. Essentially a convenience wrapper around ``get_assets_for_project.``

**Parameters:**

* project_guid (str, required) — GUID of the project

* asset_type (str, required) — Type of asset, e.g., "well"

**Returns:** List or dict

**Example:**
```python
assets = well_client.fetch_assets("project_guid_example", "well")
```

### `get_assets_for_project(project_guid, asset_type)`

**Description:** Fetch all assets of a given type for a project.

**Parameters:**

* project_guid (str, required) — GUID of the project

* asset_type (str, required) — Type of asset, e.g., "rig" , "well"

**Returns:** List or dict

**Example:**
```python
assets = rig_client.get_assets_for_project("project_guid_example", "rig")
print(assets)
```


---

## **Project Methods**

### `Project.get_assets(asset_type)`
Note: asset type can be: "well, rig , borehole or generic_asset" if you mistype you will get a unique error telling you.

**Description:** Fetch all assets of a given type for this project.

**Parameters:**

* `asset_type` (*str*, required)

**Returns:** List of asset objects

**Example:**

```python
wells = project.get_assets("well")
```

### `Project.add_site(site)`

**Description:** Add a Site object to the project.

**Parameters:**

* `site` (*Site*, required)

**Example:**

```python
project.add_site(my_site)
```

### `Project.get_sites()`

**Description:** Return all Site objects for this project.

**Returns:** List of Site objects

**Example:**

```python
sites = project.get_sites()
```

---

## **Asset / Semantic Methods**
Note: asset is the parent for a assets like: well, rig, generic_asset or borehole


### `Asset.get_start_time()`

**Description:** Return default start time (24 hours ago unless overridden).

**Returns:** datetime

**Example:**

```python
start = well.get_start_time()
```

### `Asset.get_end_time()`

**Description:** Return current datetime as default end time.

**Returns:** datetime

**Example:**

```python
end = well.get_end_time()
```

### `Asset.get_data(feeds=None, start=None, end=None)`

**Description:** Fetch data for this asset.

**Parameters:**

* `feeds` (*list[str]* or "ALL", optional)
* `start` (*datetime*, optional)
* `end` (*datetime*, optional)

**Returns:** List of feed dictionaries

**Example:**

```python
data = well.get_data(feeds=["Depth"], start="2025-11-01", end="2025-11-02")
```


### `Site.add_asset(asset)`

**Description:** Add an Asset object to this site.

**Parameters:**

* `asset` (*Asset*, required)

**Example:**

```python
site.add_asset(well)
```

### `Site.get_assets()`

**Description:** Return all Asset objects for this site.

**Returns:** List of Asset objects

**Example:**

```python
assets = site.get_assets()
```

---

## **Specific Asset Types**
Note: generic_asset overides some methods of its parent thats why ist listed here
### `GenericAsset.get_data(feeds=None, start=None, end=None)`

**Description:** Fetch data for a GenericAsset.

**Parameters:**

* `feeds` (*list[str]* or "ALL", optional)
* `start` (*datetime*, optional)
* `end` (*datetime*, optional)

**Returns:** List of feed dictionaries

**Example:**

```python
data = generic.get_data(feeds=["Depth"])
```

### `GenericAsset.get_feeds()`

**Description:** Fetch all feeds for a GenericAsset.

**Returns:** List of feed dictionaries

**Example:**

```python
feeds = generic.get_feeds()
```

