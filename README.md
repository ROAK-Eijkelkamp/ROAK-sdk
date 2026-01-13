# ROAK SDK (Python)

A Python Software Development Kit (SDK) for interacting with the **ROAK
data platform** at Royal Eijkelkamp.

This SDK provides a clean, object-oriented interface for authentication,
asset discovery, and time-series data retrieval from ROAK without
requiring users to interact directly with the REST API.

> ⚠️ **Status**: In development --- internship project (not
> production-ready)

------------------------------------------------------------------------

## About This Project

This SDK was developed as part of an internship at **Royal Eijkelkamp**
in collaboration with **HAN University of Applied Sciences**.

The primary goals are: - Provide a **clear and reusable Python
interface** to ROAK - Abstract away API complexity - Enable fast
scripting and data pipelines for ROAK users

Although the author's background is mainly **Java**, this project
focuses on applying **Python best practices** in a real-world SDK.

------------------------------------------------------------------------

## What the SDK Does

The ROAK SDK allows users to:

-   Authenticate securely with ROAK
-   Retrieve projects and assets
-   Fetch time-series measurement data
-   Work with ROAK concepts as Python objects

### Core Domain Objects

-   **Project** → Groups assets within ROAK\
-   **Well** → Water level and pressure measurements\
-   **Rig** → Drilling rigs\
-   **Borehole** → Depth-aligned measurements via rig data\
-   **GenericAsset** → Placeholder for unknown or future asset types

All API calls are handled internally by the SDK.

------------------------------------------------------------------------

## Documentation

📘 **Software Guidebook (SGB)**\
The full design, architecture, and implementation details are documented
in the Software Guidebook.

➡️ **Start with**: `docs/Software_Guidebook.md`

------------------------------------------------------------------------

## Installation

### Development Installation (recommended)

``` bash
pip install -e .
```

### Virtual Environment

``` bash
python -m venv .venv
.\.venv\Scripts\Activate
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## Basic Usage Example

``` python
from roak_sdk.roak import Roak
import os
from datetime import datetime, timedelta

username = "user@example.com"
password = os.getenv("ROAK_PASSWORD")

roak = Roak(user=username, password=password)

project = roak.get_project("TestProject")
wells = project.get_assets("well")

start = datetime.now() - timedelta(days=1)
end = datetime.now()

for well in wells:
    data = well.get_data(
        start=start,
        end=end,
        feeds=["waterLevelReference", "diverPressure"]
    )
    print(well.name, data)
```

------------------------------------------------------------------------

## Author

**Emil Garibov**\
Internship Project --- Royal Eijkelkamp\
HAN University of Applied Sciences
