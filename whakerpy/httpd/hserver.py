"""
:filename: whakerpy.httpd.server.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary: This is the Web-based application HTTPD server.

.. _This file is part of SPPAS: https://sppas.org/
..
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

import http.server

from .hutils import HTTPDHandlerUtils

# ---------------------------------------------------------------------------


class BaseHTTPDServer(http.server.ThreadingHTTPServer):
    """A base class for any custom HTTPD server.

     It adds a dictionary of the HTML page's bakery this server can handle
     and the name of the default page.

     :Example:
     >>> s = BaseHTTPDServer(server_address, app_handler)
     >>> s.create_pages()

    """

    def __init__(self, *args, **kwargs):
        """Create the server instance and add custom members.

        """
        super(BaseHTTPDServer, self).__init__(*args, **kwargs)
        self._pages = dict()
        self._default = "index.html"

    # -----------------------------------------------------------------------

    def default(self):
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

    def page_bakery(self, page_name: str, events: dict, has_to_return_data: bool = False) -> tuple:
        """Return the page content and response status.

        This method should be invoked after a POST request in order to
        take the events into account when baking the HTML page content.

        :param page_name: (str) Requested page name
        :param events: (dict) key=event name, value=event value
        :param has_to_return_data: (bool) False by default - Boolean to know if the server return data or html page

        :return: tuple(bytes, HTTPDStatus)

        """
        return HTTPDHandlerUtils.bakery(self._pages, page_name, events, has_to_return_data)
