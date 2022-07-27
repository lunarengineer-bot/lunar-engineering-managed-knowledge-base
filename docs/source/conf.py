"""Set up auto documentation build."""

from importlib import metadata

# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#module-sphinx.ext.autodoc
# sphinx.ext.autodoc
babygitr_metadata = metadata.metadata("babygitr")
project = babygitr_metadata["Name"]
author = babygitr_metadata["Author"]
copyright = babygitr_metadata["Copyright"]
version = babygitr_metadata["Version"]
release = babygitr_metadata["Version"]
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "myst_parser",
    "nbsphinx",
]
source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
    ".ipynb": "jupyter",
}
source_encoding = "utf-8-sig"
templates_path = ["_templates"]
html_static_path = ["_static"]
# Do I need to dork with this?
# source_parsers = {'.md': 'recommonmark.parser.CommonMarkParser'}
root_doc = "index"

html_theme = "alabaster"
html_theme_options = {
    "logo": "logo.png",
    "github_user": "bitprophet",
    "github_repo": "alabaster",
    "description": babygitr_metadata["Description"],
    "fixed_sidebar": True,
}
# html_style = optional path to style.csvv


html_sidebars = {
    "**": ["globaltoc.html", "sourcelink.html", "searchbox.html"]
    #    'using/windows': ['windowssidebar.html', 'searchbox.html'],
}

# html_show_copyright
# html_math_renderer

# man_pages = [
#     (root_doc, 'test', u'test Documentation',
#      [author], 1)
# ]
