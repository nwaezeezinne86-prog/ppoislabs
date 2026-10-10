"""Sphinx configuration for Lab 3."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# PROJECT_NAME, PROJECT_NUMBER, OUTPUT_LANGUAGE
project = "Fitness Tracker (Lab 3)"
author = "Нваезе Э.Р."
release = "1.0.0"
language = "en"

# autodoc reads docstrings the way Doxygen reads comments
extensions = [
    "sphinx.ext.autodoc",      # extract documentation from the code
    "sphinx.ext.napoleon",     # Google/NumPy style docstrings
    "sphinx.ext.viewcode",     # links to highlighted source (SOURCE_BROWSER)
]

# EXTRACT_ALL = YES -> undoc-members; EXTRACT_PRIVATE = NO -> no private-members
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
autodoc_member_order = "alphabetical"   # SORT_MEMBER_DOCS = YES
autodoc_typehints = "description"

exclude_patterns = ["_build"]
html_theme = "alabaster"
