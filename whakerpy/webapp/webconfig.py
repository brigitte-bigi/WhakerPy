"""
:filename: whakerpy.webapp.webconfig.py
:author:   Mathias Cazals, Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Store config data of a webapp from a JSON file.

.. _This file was part of SPPAS: https://sppas.org/ and migrated in WhakerPy,
.. on 2023-12-08.
    -------------------------------------------------------------------------

     ___   __    __    __    ___
    /     |  \  |  \  |  \  /              the automatic
    \__   |__/  |__/  |___| \__             annotation and
       \  |     |     |   |    \             analysis
    ___/  |     |     |   | ___/              of speech

    Copyright (C) 2011-2023 Brigitte Bigi
    Laboratoire Parole et Langage, Aix-en-Provence, France

    Use of this software is governed by the GNU Public License, version 3.

    SPPAS is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    SPPAS is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with SPPAS. If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------

"""

import codecs
import os
import json

# ---------------------------------------------------------------------------


class WebSiteData:
    """Storage class of a webapp configuration, extracted from a JSON file.

    For each dynamic page of a webapp, this class contains the filename of
    the page - the one of the URL, its title and the local filename of its
    body->main content.

    Below is an example of a page description in the JSON parsed file:
        "index.html": {
        "title": "Home",
        "main": "index.htm",
        "header": true,
        "footer": true
        }

    """

    # Default JSON file describing location of all body "main" sections
    DEFAULT_CONFIG_FILE = "webapp.json"

    def __init__(self, json_filename=DEFAULT_CONFIG_FILE):
        """Create a WebSiteData instance.

        :param json_filename: (str) Configuration filename.

        """
        # Path to page files
        self._main_path = ""
        # Filename of the default page
        self._default = ""

        # Information of each page: filename, title, body main filename
        self._pages = dict()
        with codecs.open(json_filename, "r", "utf-8") as json_file:
            data = json.load(json_file)
            self._main_path = data["pagespath"]
            for key in data:
                if key != "pagespath":
                    self._pages[key] = data[key]
                    if len(self._default) == 0:
                        self._default = key

    # -----------------------------------------------------------------------

    def get_default_page(self) -> str:
        """Return the name of the default page."""
        return self._default

    # -----------------------------------------------------------------------

    def filename(self, page: str) -> str:
        """Return the filename of a given page.

        :param page: (str) Name of an HTML page
        :return: (str)

        """
        if page in self._pages:
            main_name = self._pages[page]["main"]
            return os.path.join(self._main_path, main_name)

        return ""

    # -----------------------------------------------------------------------

    def title(self, page: str) -> str:
        """Return the title of a given page.

        :param page: (str) Name of an HTML page
        :return: (str)

        """
        if page in self._pages:
            if "title" in self._pages[page]:
                return self._pages[page]["title"]

        return ""

    # -----------------------------------------------------------------------

    def has_header(self, page: str) -> bool:
        """Return True if the given page should have the header.

        :param page: (str) Name of an HTML page
        :return: (bool)

        """
        if page in self._pages:
            if "header" in self._pages[page].keys():
                return self._pages[page]["header"]

        return False

    # -----------------------------------------------------------------------

    def has_footer(self, page: str) -> bool:
        """Return True if the given page should have the footer.

        :param page: (str) Name of an HTML page
        :return: (bool)

        """
        if page in self._pages:
            if "footer" in self._pages[page]:
                return self._pages[page]["footer"]

        return False

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    def __iter__(self):
        for a in self._pages:
            yield a

    def __len__(self):
        return len(self._pages)

    def __contains__(self, value):
        """Value is a page name."""
        return value in self._pages
