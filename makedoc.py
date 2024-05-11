# -*- coding: UTF-8 -*-
# makedoc.py
# Summary: Create the documentation of WhakerPy, using ClammingPy 1.7+ library.
# Usage: python makedoc.py
#
# This file is part of WhakerPy tool.
# (C) 2023-2024 Brigitte Bigi, Laboratoire Parole et Langage, Aix-en-Provence, France.
#
# Use of this software is governed by the GNU Affero Public License, version 3.
#
# WhakerPy is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# WhakerPy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with WhakerPy. If not, see <https://www.gnu.org/licenses/>.
#
# This banner notice must not be removed.
#
# ---------------------------------------------------------------------------

import sys
import logging

import whakerpy
try:
    import clamming
except ImportError:
    print("This program requires `ClammingPy` documentation generator.")
    print("It can be installed with: pip install ClammingPy.")
    print("See <https://clamming.sf.net/> for details.")
    sys.exit(-1)

# ---------------------------------------------------------------------------
logging.getLogger().setLevel(0)

# List of modules to be documented.
packages = list()
packages.append(clamming.ClamsPack(whakerpy.htmlmaker))
packages.append(clamming.ClamsPack(whakerpy.httpd))
packages.append(clamming.ClamsPack(whakerpy.webapp))

# Options for HTML exportation
html_export = clamming.HTMLDocExport()
html_export.software = 'WhakerPy ' + whakerpy.__version__
html_export.url = 'https://whakerpy.sf.net'
html_export.copyright = whakerpy.__copyright__
html_export.title = 'WhakerPy doc'
# ... statics is the relative path to a folder with custom CSS, JS, etc.
html_export.statics = './statics'
# ... the favicon and icon are files in the statics folder
html_export.favicon = 'whakerpy32x32.ico'
html_export.icon = 'whakerpy.png'
# ... the theme corresponds to a statics/<theme>.css file or "light" or "dark"
html_export.theme = 'light'
# ... path to 'wexa_statics' folder, relatively to "docs"
html_export.wexa_statics = "./Whakerexa-0.3/wexa_statics"

# Export documentation into HTML files.
# One .html file = one documented class.
clamming.ClamsPack.html_export_packages(packages, "docs", html_export)

# Export documentation into a Markdown file.
# One .md file = one documented module.
clamming.ClamsPack.markdown_export_packages(packages, "docs", html_export)
