# Sphinx configuration for ROAK SDK public documentation.

import os
import sys

# Point to the SDK source so autodoc can import the modules
sys.path.insert(0, os.path.abspath("../../src"))

# -- Project info -------------------------------------------------------------
project = "ROAK SDK"
copyright = "2026, ROAK"
author = "ROAK Team"
release = "0.1.0"

# -- Extensions ---------------------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",       # Pull docstrings from code
    "sphinx.ext.napoleon",      # Support Google/NumPy-style docstrings
    "sphinx.ext.viewcode",      # Add [source] links
    "sphinx.ext.intersphinx",   # Cross-reference Python stdlib docs
    "sphinx.ext.githubpages",   # Emit .nojekyll for GitHub Pages
]

# -- Autodoc settings ---------------------------------------------------------
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "inherited-members": True,       # Show methods inherited from parent classes
    "exclude-members": "__init__",   # Hide constructors (internal detail)
}

# Show type hints in the description, not the signature
autodoc_typehints = "description"

# Do not sort alphabetically; keep source order
autodoc_member_order = "bysource"

# -- Napoleon settings --------------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False

# -- Intersphinx --------------------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- HTML output --------------------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "display_version": True,
    "navigation_depth": 3,
    "collapse_navigation": False,
}

html_title = "ROAK SDK Documentation"
html_short_title = "ROAK SDK"

# Build canonical docs URL automatically in GitHub Actions.
_repo_slug = os.environ.get("GITHUB_REPOSITORY", "")
if "/" in _repo_slug:
    _owner, _repo = _repo_slug.split("/", 1)
    html_baseurl = f"https://{_owner}.github.io/{_repo}/"
else:
    html_baseurl = ""

# -- General ------------------------------------------------------------------
source_suffix = ".rst"
master_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"
