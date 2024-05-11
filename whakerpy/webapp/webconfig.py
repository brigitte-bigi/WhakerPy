"""
:filename: whakerpy.webapp.webconfig.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Store config data of a webapp from a JSON file.

.. _This file is part of WhakerPy: https://whakerpy.sourceforge.io
..
    -------------------------------------------------------------------------

    Copyright (C) 2023-2024 Brigitte Bigi
    Laboratoire Parole et Langage, Aix-en-Provence, France

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------

"""

from __future__ import annotations
import codecs
import os
import json

from ..htmlmaker import HTMLTree
from ..httpd import BaseResponseRecipe
from .webresponse import WebSiteResponse

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

    def create_pages(self, web_response=WebSiteResponse, default_path: str = "") -> dict:
        """Instantiate all pages response from the json.

        :param web_response: (BaseResponseRecipe) the class to used to create the pages,
                            WebSiteResponse class used by default
        :param default_path: (str) None by default, the default path for all pages

        :return: (dict) a dictionary with key = page name and value = the response object

        """
        pages = dict()

        tree = HTMLTree("sample")
        for page_name in self._pages:
            page_path = os.path.join(default_path, self.filename(page_name))
            pages[page_name] = web_response(page_path, tree)

        return pages

    # -----------------------------------------------------------------------

    def bake_response(self, page_name: str, default: str = "") -> BaseResponseRecipe | None:
        """Return the bakery system to create the page dynamically.

        To be overridden by subclasses.

        :param page_name: (str) Name of an HTML page
        :param default: (str) The default path
        :return: (BaseResponseRecipe)

        """
        raise NotImplementedError

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
