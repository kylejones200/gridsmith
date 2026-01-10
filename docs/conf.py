"""Sphinx configuration for GridSmith documentation.

This configuration enables ReadTheDocs to build documentation from Markdown files.
"""

import os
import sys

# Add src to path for autodoc
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# Configuration file for the Sphinx documentation builder
project = "GridSmith"
copyright = "2025, GridSmith Contributors"
author = "GridSmith Contributors"
release = "0.1.0"

extensions = [
    "myst_parser",  # Parse Markdown files
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",  # Support Google/NumPy docstrings
]

# The suffix(es) of source filenames
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# The master toctree document
# Note: index.md will be the main entry point, Sphinx will auto-detect it
master_doc = "index"

# Set source directory for Sphinx
html_context = {
    "display_github": True,
    "github_user": "kylejones200",
    "github_repo": "gridsmith",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

# Source directory
templates_path = ["_templates"]

# List of patterns to ignore
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**/.archive/**"]

# HTML output options
html_theme = "sphinx_rtd_theme"
html_static_path = []
html_show_sourcelink = True

# Enable MyST parser features
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_admonition",
    "html_image",
]

# MyST parser options
myst_heading_anchors = 3

