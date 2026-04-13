# ROAK SDK

Python SDK for interacting with the ROAK API. Provides a high-level interface to access projects, wells, boreholes, rigs, modems, and their associated data.

## Requirements

- Python 3.10 through 3.12
- A virtual environment (`venv` or `.venv`)
- `requests>=2.31,<3`

## Installation

Create and activate a virtual environment first, then install the package in editable mode:

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

For development dependencies (pytest, dotenv, pandas):

```bash
pip install -e ".[dev]"
``` 

Supported runtime and development versions are kept intentionally narrow so the
same setup works across the team without environment drift.

## Quick Start

```python
from roak_sdk import Roak

roak = Roak(username="your_username", password="your_password")

# Get all projects
projects = roak.get_projects()

# Get wells within a project
wells = projects[0].get_wells()

# Get data from a well
data = wells[0].get_data()

# Get feeds available on an asset
feeds = wells[0].get_feeds()
```

## Documentation

Full API documentation is pre-built and ready to view. Open the documentation here:

[Open Documentation in Browser](open-documentation.cmd)

For a short introduction aimed at first-time users, see [First Users](docs/first_users.md).

If you need to adjust long-running request behavior, see [Getting Started](docs/getting_started.md) for `request_timeout` and `set_request_timeout()`.

Production readiness checklist for rollout planning:

[Production Readiness Checklist](docs/production_readiness_checklist.md)

This shows the complete API reference with all user-facing classes and methods.

### Rebuilding Documentation

If you make changes to the source code and want to regenerate the documentation:

```bash
# Install Sphinx (if not already installed)
.venv/Scripts/python.exe -m pip install sphinx sphinx-rtd-theme

# Rebuild the docs
.venv/Scripts/python.exe -m sphinx -b html docs/sphinx docs/sphinx/_build/html
```
