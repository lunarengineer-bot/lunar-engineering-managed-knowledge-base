"""Set up auto documentation build."""
import babygitr
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#module-sphinx.ext.autodoc
# sphinx.ext.autodoc

project = babygitr.__name__
author = 
copyright = 
version = babygitr.__version__
release = 
extensions = ['autodoc', 'myst_parser', 'nbsphinx']
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
    '.ipynb': 'jupyter'
}
source_encoding = 'utf-8-sig'
# Do I need to dork with this?
# source_parsers = {'.md': 'recommonmark.parser.CommonMarkParser'}
root_doc = 'index'

html_theme = https://www.sphinx-doc.org/en/master/usage/theming.html
html_theme_options = theme specific https://www.sphinx-doc.org/en/master/usage/theming.html#builtin-themes

html_style = optional path to style.csvv


html_sidebars
"""
Builtin sidebar templates that can be rendered are:

    localtoc.html – a fine-grained table of contents of the current document

    globaltoc.html – a coarse-grained table of contents for the whole documentation set, collapsed

    relations.html – two links to the previous and next documents

    sourcelink.html – a link to the source of the current document, if enabled in html_show_sourcelink

    searchbox.html – the “quick search” box

Example:

html_sidebars = {
   '**': ['globaltoc.html', 'sourcelink.html', 'searchbox.html'],
   'using/windows': ['windowssidebar.html', 'searchbox.html'],
}

w"""
html_show_copyright
html_math_renderer

man_pages = [
    (root_doc, 'test', u'test Documentation',
     [author], 1)
]