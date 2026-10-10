"""Sphinx configuration for Lab 3 (equivalent of a Doxyfile)."""
import os
import sys

DOCS_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(DOCS_DIR, ".."))
sys.path.insert(0, PROJECT_ROOT)

project = "Fitness Tracker (Lab 3)"
author = "[Нваезе Э.Р.]"
release = "1.0.0"
language = "ru"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
autodoc_member_order = "alphabetical"
autodoc_typehints = "description"

exclude_patterns = ["_build"]
html_theme = "alabaster"
