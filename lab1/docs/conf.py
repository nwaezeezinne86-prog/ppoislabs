"""Sphinx configuration for lab1 documentation."""
import os
import sys

DOCS_DIR = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(DOCS_DIR, "..", ".."))
sys.path.insert(0, REPO_ROOT)

project = "Lab1 - BigInt and Post Machine"
author = "Zinne"
release = "1.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

html_theme = "sphinx_rtd_theme"
master_doc = "index"
