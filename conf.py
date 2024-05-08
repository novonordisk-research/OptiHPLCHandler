import os
import shutil
import subprocess

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
release = "3.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]

# Making the class diagrams
# Approach inspired by https://pythonhosted.org/theape/documentation/developer/explorations/explore_graphs/explore_pyreverse.html # noqa: E501
os.makedirs("./_readthedocs/html/_static/", exist_ok=True)
class_diagram_files = ["empower_instrument_method", "empower_handler"]
for file in class_diagram_files:
    # Might be more readable with shlex.split as in the link above.
    subprocess.call(
        [
            "pyreverse",
            "-A",
            "-S",
            "-o",
            "html",
            "-p",
            file,
            "./src/OptiHPLCHandler/" + file + ".py",
        ]
    )  # Crating the class diagrams
    shutil.move(
        "classes_" + file + ".html", "_readthedocs/html/_static/" + file + ".html"
    )  # Moving the class diagrams so that sphinx can find them
