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
release = '0.9.0'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',        # import docstrings from modules
    'sphinx.ext.autosummary',    # generate summary pages (nice API index)
    'sphinx.ext.napoleon',       # numpy/google style docstrings -> autodoc
    'sphinx.ext.viewcode',       # add links to source code
    'sphinx_autodoc_typehints'   # show type hints in function signatures
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
