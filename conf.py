# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "OptiHPLCHandler"
copyright = (
    "2023, Søren Furbo, Samual Burnage, Erik Trygg, Jacob Kofoed, Søren Bertelsen"
)
author = "Søren Furbo, Samual Burnage, Erik Trygg, Jacob Kofoed, Søren Bertelsen"
release = "2.5.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]

# Extensions
extensions = ["sphinx.ext.autodoc"]

import os, sys

sys.path.append(os.path.abspath("./src"))
