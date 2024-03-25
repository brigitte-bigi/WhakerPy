# -*- coding: UTF-8 -*-
# makedoc.py
# Summary: Create the documentation of WhakerPy, using Clamming 1.3+ library.
# Usage: python makedoc.py
#
# This file is part of WhakerPy tool.
# (C) 2023-2024 Brigitte Bigi, Laboratoire Parole et Langage,
# Aix-en-Provence, France.
#
# Use of this software is governed by the GNU Public License, version 3.
#
# Clamming is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Clamming is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Clamming. If not, see <https://www.gnu.org/licenses/>.
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
    print("This program requires `Clamming` documentation generator.")
    print("It can be installed with: pip install Clamming.")
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
html_export.statics = 'statics'
html_export.favicon = 'whakerpy32x32.ico'
html_export.icon = 'whakerpy.png'
html_export.theme = 'light'

# Export documentation into HTML files.
# One .html file = one documented class.
clamming.ClamsPack.html_export_packages(packages, "docs", html_export)

# Export documentation into a Markdown file.
# One .md file = one documented module.
clamming.ClamsPack.markdown_export_packages(packages, "docs", html_export)
