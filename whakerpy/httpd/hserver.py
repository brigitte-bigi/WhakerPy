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
from .hpolicy import HTTPDPolicy

# ---------------------------------------------------------------------------


class BaseHTTPDServer(http.server.ThreadingHTTPServer):
    """A base class for any custom HTTPD server.

     It adds a dictionary of the HTML page's bakery this server can handle
     and the name of the default page.

     :Example:
     >>> s = BaseHTTPDServer(server_address, app_handler)
     >>> s.configure(app="AppName", blacklist=["SomeBot"])

    This server stores:
    - dynamic pages ("_pages") used by the bakery system,
    - the default page name ("_default"),
    - an optional HTTP policy with:
        1. a persistent blacklist of URL paths used by HTTPDHandler
          to reject abusive requests as early as possible.
        2. a set of signed URLs

    """

    def __init__(self, *args, **kwargs):
        """Create the server instance and add custom members.

        """
        super(BaseHTTPDServer, self).__init__(*args, **kwargs)
        self._pages = dict()
        self._default = "index.html"
        self._policy = HTTPDPolicy()

    # -----------------------------------------------------------------------

    def configure(self, **kwargs) -> None:
        """Configure the server.

        1. Configure policy....
        2. Add bakeries for dynamic HTML pages : The created pages are instances
        of the BaseResponseRecipe class.

        Optional keys in config dict:
            - "app": application name
            - "blacklist": list of blacklisted URL paths
            - "signed_url": signed URL path

        :param kwargs: (dict) Configuration dictionary.

        """
        self._policy.configure({
                "blacklist": kwargs.get("blacklist", None),
                "signed_url": kwargs.get("signed_url", None)
                })
        self._create_pages(**kwargs)

    # -----------------------------------------------------------------------

    def policy_check(self, path: str, query_string: str, headers) -> tuple:
        """Check the request against policies and return decision and response.

        Returned values are:
            - allowed: (bool) True if request is accepted
            - content: (bytes|None) HTML bytes if rejected, otherwise None
            - status: (HTTPDStatus|None) Status if rejected, otherwise None
            - mime_type: (str|None) Mime if rejected, otherwise None

        :param path: (str) Normalized URL path (without query).
        :param query_string: (str) Raw query string (without '?').
        :param headers: (Any) Request headers or environ. Must support ".get(...)".
        :return: (tuple) (allowed, content, status, mime_type)

        """
        return self._policy.check(path, query_string, headers)

    # -----------------------------------------------------------------------
    # The pages this server is serving
    # -----------------------------------------------------------------------

    def default(self):
        """Return the default page name, used when a URL ends with '/'."""
        return self._default

    # -----------------------------------------------------------------------

    def page_bakery(self,
                    page_name: str,
                    headers: dict,
                    events: dict,
                    has_to_return_data: bool = False) -> tuple:
        """Return the page content and response status.

        This method bakes a page and optionally finalizes outgoing HTML.

        :param page_name: (str) Requested page name.
        :param headers: (dict) HTTP request headers.
        :param events: (dict) Event values (POST).
        :param has_to_return_data: (bool) True if returning data, False if returning HTML.
        :return: (tuple) (content, status)

        """
        content, status = HTTPDHandlerUtils.bakery(
            self._pages,
            page_name,
            headers,
            events,
            has_to_return_data
        )

        if has_to_return_data is False:
            content = self._policy.finalize_html(content)

        return content, status

    # -----------------------------------------------------------------------

    def _create_pages(self, **kwargs):
        """To be overridden. Add bakeries for dynamic HTML pages.

        The created pages are instances of the BaseResponseRecipe class.
        Below is an example on how to override this method:

        :example:
        if app == "main":
            self._pages["index.html"] = BaseResponseRecipe("index.html", HTMLTree("Index"))
            self._pages["foo.html"] = WebResponseRecipe("foo.html", HTMLTree("Foo"))
        elif app == "test":
            self._pages["test.html"] = BaseResponseRecipe("test.html", HTMLTree("test"))

        """
        raise NotImplementedError
