# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys
import os

sys.path.insert(0, os.path.abspath("../../"))


project = 'PigeonPy'
copyright = '2026, Cuypers, J. L.; Körner, J.'
author = 'Cuypers, J. L.; Körner, J.'
release = '0.1'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

""" TABLE LIKE DEPICTION 
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints"
]

napoleon_google_docstring = False
napoleon_numpy_docstring = True

autosummary_generate = True

autodoc_member_order = "bysource"

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "inherited-members": True,
    "show-inheritance": True,
}

templates_path = ['_templates']
"""

""" TOC LIKE DEPICTION """
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.apidoc',
    #'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    #'sphinx_autodoc_typehints'
]

apidoc_modules = [
    {
        "path": "../../pigeonpy",
        "destination": "generated",
        "max_depth": 4,
        "separate_modules": True,
        "module_first": True,
        "automodule_options": {
            "members",
            "show-inheritance",
        },
    },
]

napoleon_google_docstring = False
napoleon_numpy_docstring = True

autosummary_generate = True

autodoc_member_order = 'bysource'  # show members in source order
autodoc_default_options = {
    'members': True,
    'undoc-members': False,
    'inherited-members': True,
    'show-inheritance': True,
}

templates_path = ['_templates']
exclude_patterns = ['build', 'Thumbs.db', '.DS_Store'] # '_build', 'Thumbs.db', '.DS_Store'



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
# html_static_path = ['static']
