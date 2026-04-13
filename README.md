# ROAK SDK

Python SDK for interacting with the ROAK API. Provides a high-level interface to access projects, wells, boreholes, rigs, modems, and their associated data.

Current release status: **Beta (v0.1.0)**.

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

Install via local install:

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

For user-facing documentation, start with [Getting Started](docs/getting_started.md).

For concrete usage examples, see the scripts in the [scenarios](scenarios) folder.

The generated Sphinx documentation contains the full API reference for the user-facing classes and methods.

### Rebuilding Documentation

If you make changes to the source code and want to regenerate the documentation:

```bash
# Install Sphinx (if not already installed)
.venv/Scripts/python.exe -m pip install sphinx sphinx-rtd-theme

# Rebuild the docs
.venv/Scripts/python.exe -m sphinx -b html docs/sphinx docs/sphinx/_build/html
```

After the build completes, open the generated documentation at `docs/sphinx/_build/html/index.html` in your browser.
