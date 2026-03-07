# Sphix configuration file
import os
import sys
sys.path.insert(0, os.path.abspath(".."))  # Adjust if jdxi_editor is deeper

# Project information
project = "JDXi Editor"
copyright = "2025, JDXi Editor"
author = "JDXi Editor"

# General configuration
extensions = ["sphinx.ext.autodoc", "sphinx.ext.viewcode", "sphinx.ext.napoleon",]

# HTML configuration    
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_theme_options = {
    "logo_only": True,
    "display_version": False,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "vcs_pageview_mode": "",
    "style_nav_header_background": "white",
}