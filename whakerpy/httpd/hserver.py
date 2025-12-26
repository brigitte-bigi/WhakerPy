"""
:filename: whakerpy.httpd.server.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: This is the Web-based application HTTPD server.

.. _This file was initially part of SPPAS: https://sppas.org/
.. _This file is now part of WhakerPy: https://whakerpy.sourceforge.io
..
    -------------------------------------------------------------------------

    Copyright (C) 2023-2025 Brigitte Bigi, CNRS
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

import http.server

from .hutils import HTTPDHandlerUtils
from .hblacklist import Blacklist
from .. import SignedURL


# ---------------------------------------------------------------------------


class BaseHTTPDServer(http.server.ThreadingHTTPServer):
    """A base class for any custom HTTPD server.

     It adds a dictionary of the HTML page's bakery this server can handle
     and the name of the default page.

     :Example:
     >>> s = BaseHTTPDServer(server_address, app_handler)
     >>> s.create_pages()

    This server stores:
    - dynamic pages ("_pages") used by the bakery system,
    - the default page name ("_default"),
    - a persistent blacklist of URL paths ("_blacklist") used by HTTPDHandler
      to reject abusive requests as early as possible.

    Blacklist file format:
    - one URL path per line (example: /bot.html)
    - empty lines are ignored
    - lines starting with '#' are ignored

    """

    def __init__(self, *args, **kwargs):
        """Create the server instance and add custom members.

        """
        super(BaseHTTPDServer, self).__init__(*args, **kwargs)
        self._pages = dict()
        self._default = "index.html"

        # Persistent set of URL paths to reject early in the handler.
        self._blacklist = Blacklist()
        if "blacklist" in kwargs:
            self._blacklist.load(kwargs["blacklist"])

        # Signed URLs
        self._signed_url = SignedURL()
        self.__signed_url_cfg = {"ttl": None, "protect": []}
        if "signed_url" in kwargs:
            self.__signed_url_cfg = self._signed_url.load(kwargs["signed_url"])

    # -----------------------------------------------------------------------

    def match_blacklist(self, url: str) -> bool:
        """Return True if the given URL path matches the blacklist.

        The matching rules are:
            - exact match
            - parent path match (prefix, by path segments)

        The URL can include a query string; it is ignored.

        :param url: (str) URL path, like '/bot.html' or '/admin/page.html'.
        :raises: TypeError: if url is not a string.
        :return: (bool) True if blacklisted, False otherwise.

        """
        return self._blacklist.match(url)

    # -----------------------------------------------------------------------

    def match_protect(self, path: str, protect: list) -> bool:
        """Return True if the given path must be protected by a signed URL.

        Protection rules are defined as a list of dict:
            {"prefix": "...", "suffix": "..."}

        :param path: (str) URL path (with or without leading slash).
        :param protect: (list) Protection rules.
        :return: (bool)

        """
        return self._signed_url.match_protect(path, protect)

    # -----------------------------------------------------------------------
    # The pages this server is serving
    # -----------------------------------------------------------------------

    def default(self):
        """Return the default page name, used when a URL ends with '/'."""
        return self._default

    # -----------------------------------------------------------------------

    def create_pages(self, app: str = "app"):
        """To be overridden. Add bakeries for dynamic HTML pages.

        The created pages are instances of the BaseResponseRecipe class.
        Below is an example on how to override this method:

        :example:
        if app == "main":
            self._pages["index.html"] = BaseResponseRecipe("index.html", HTMLTree("Index"))
            self._pages["foo.html"] = WebResponseRecipe("foo.html", HTMLTree("Foo"))
        elif app == "test":
            self._pages["test.html"] = BaseResponseRecipe("test.html", HTMLTree("test"))

        :param app: (str) Any string definition for custom use

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def page_bakery(self, page_name: str, headers: dict, events: dict, has_to_return_data: bool = False) -> tuple:
        """Return the page content and response status.

        This method should be invoked after a POST request in order to
        take the events into account when baking the HTML page content.

        :param page_name: (str) Requested page name
        :param headers: (dict) The headers ot the http request
        :param events: (dict) key=event name, value=event value
        :param has_to_return_data: (bool) False by default - Boolean to know if the server return data or html page

        :return: tuple(bytes, HTTPDStatus)

        """
        return HTTPDHandlerUtils.bakery(self._pages, page_name, headers, events, has_to_return_data)
