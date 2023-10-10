"""
:filename: whakerpy.website.weblocalservere.py
:author:   Mathias Cazals, Brigitte Bigi
:contact:  develop@sppas.org
:summary:  Create a generic HTTPD localhost server.

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
    along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------

"""

import random

from whakerpy.httpd import HTTPDHandler
from whakerpy.httpd import BaseHTTPDServer
from whakerpy.htmlmaker import HTMLTree

from .webconfig import WebSiteData
from .webresponse import WebSiteResponse

# ---------------------------------------------------------------------------
# A website server, for local use only.
# ---------------------------------------------------------------------------


class WebSiteApplication(object):
    """Create and run a website applications.

    Allows to create a server and a response system in order to use HTTPD
    like a communication system between a web-browser and a python API.

    """

    def __init__(self, server_cls):
        """HTTPD Server initialization.

        Create the application for a Web Front-End based on httpd protocol.

        """
        self.__location = "localhost"
        httpd_port = random.randrange(80, 99)
        self.__port = httpd_port + (httpd_port*100)
        self.__server = None
        server_address = (self.__location, self.__port)

        self.__server = server_cls(server_address, HTTPDHandler)
        self.__server.create_pages()

    # -----------------------------------------------------------------------

    def client_url(self) -> str:
        """Return the client URL of this server."""
        return "http://{:s}:{:d}/".format(self.__location, self.__port)

    # -----------------------------------------------------------------------

    def run(self) -> int:
        """Run the application with a main loop.

        :return: (int) Exit status (0=normal)

        """
        try:
            # Start the main loop of the HTTP server
            self.__server.serve_forever()
            # Notice that the sppasHTTPDHandler can shut down the server --
            # allowed because it's a local application, not an internet service.
        except KeyboardInterrupt:
            # Stop the server
            self.__server.shutdown()

        # Return an exit status 0 = normal.
        return 0
