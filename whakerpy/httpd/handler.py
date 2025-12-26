# -*- coding: UTF-8 -*-
"""
:filename: whakerpy.httpd.handler.py
:author:  Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: Manage an HTTPD handler for any web-based application.

.. _This file was initially part of SPPAS: https://sppas.org/
.. _This file is now part of WhakerPy: https://whakerpy.sourceforge.io
..
    -------------------------------------------------------------------------

    Copyright (C) 2023-2024 Brigitte Bigi, CNRS
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
import logging
import types
import http.server
import os.path

from .hstatus import HTTPDStatus
from .hutils import HTTPDHandlerUtils
from .hsignedurl import SignedURL

# ---------------------------------------------------------------------------


class HTTPDHandler(http.server.BaseHTTPRequestHandler):
    """Web-based application HTTPD handler.

    This class is used to handle the HTTP requests that arrive at the server.

    This class is instantiated by the server each time a request is received
    and then a response is created. This is an HTTPD handler for any Web-based
    application server. It parses the request and the headers, then call a
    specific method depending on the request type.

    In this handler, HTML pages are supposed to not be static. Instead,
    they are serialized from an HTMLTree instance -- so not read from disk.
    The server contains the page's bakery, the handler is then asking the
    server page's bakery to get the html content and response status.

    The parent server is supposed to have all the pages as members in a
    dictionary, i.e. it's a sppasBaseHTTPDServer. Each page has a bakery
    to create the response content. However, this handler can also be used
    with any other http.server.ThreadingHTTPServer.

    The currently supported HTTPD responses status are:

        - 200: OK
        - 205: Reset Content
        - 403: Forbidden
        - 404: Not Found -- also used for "expired"
        - 410: Gone
        - 418: I'm a teapot

    """

    def get_default_page(self, default: str = "index.html") -> str:
        """Retrieve the server default page name.

        This method first checks if the server has a callable 'default' method
        to determine the default page name. If not, it falls back to the
        provided default value.

        :param default: (str) The fallback default page name, if no server-specific
                               method is found. Defaults to "index.html".
        :return: (str) The name of the default page.

        """
        # Check if the server has a callable 'default' method.
        if hasattr(self.server, 'default') and callable(self.server.default):
            return self.server.default()

        # Fallback to the provided default page name.
        return default

    # -----------------------------------------------------------------------

    def _set_headers(self, status: int, mime_type: str = None) -> None:
        """Set the HTTPD response headers.

        :param status: (int) A response status.
        :param mime_type: (str) The mime type of the file response
        :raises: sppasHTTPDValueError

        """
        status = HTTPDStatus.check(status)
        self.send_response(status)

        if mime_type is not None:
            self.send_header('Content-Type', mime_type)

        self.end_headers()

    # -----------------------------------------------------------------------

    def _response(self, content, status: int, mime_type: str = None) -> None:
        """Make the appropriate HTTPD response.

        :param content: (bytes|iterator) The HTML response content or an iterator
                        yielding chunks of bytes.
        :param status: (int) The HTTPD status code of the response.
        :param mime_type: (str) The mime type of the file response.

        """
        self._set_headers(status, mime_type)

        if isinstance(content, types.GeneratorType) is True:
            # Write one chunk at a time
            for chunk in content:
                self.wfile.write(chunk)
        else:
            # Write the whole bytes content in once
            self.wfile.write(content)

        # Shutdown the server if status is 410.
        if status == 410:
            self.server.shutdown()

    # -----------------------------------------------------------------------

    def _bakery(self, handler_utils: HTTPDHandlerUtils, events: dict, mime_type: str) -> tuple:
        """Process the events and return the html page content or json data and status.

        :param handler_utils: (HTTPDhandlerUtils)
        :param events: (dict) key=event name, value=event value
        :param mime_type: (str) The mime type of the file response
        :return: tuple(bytes, HTTPDStatus) the content of the response the httpd status

        """
        # The server is not the custom one for a WhakerPy application.
        if hasattr(self.server, 'page_bakery') is False:
            return handler_utils.static_content(self.path[1:])

        # Get the response from any WhakerPy Bakery system
        content, status = self.server.page_bakery(handler_utils.get_page_name(), self.headers, events,
                                                  handler_utils.has_to_return_data(mime_type))
        return content, status

    # -----------------------------------------------------------------------
    # Override BaseHTTPRequestHandler classes.
    # -----------------------------------------------------------------------

    def do_HEAD(self) -> None:
        """Prepare the response to a HEAD request.

        """
        logging.debug("HEAD -- requested: {}".format(self.path))
        self._set_headers(200)

    # -----------------------------------------------------------------------

    def do_GET(self) -> None:
        """Prepare the response to a GET request.

        This method:
        - extracts the query string (before path normalization),
        - applies blacklist (if enabled),
        - applies signed URL verification (if enabled),
        - serves static files or generated HTML pages.

        """
        logging.debug(" ---- DO GET -- requested: {}".format(self.path))

        # Keep the raw request path because HTTPDHandlerUtils.get_path() removes "?..."
        raw_path = self.path

        # Extract the query string (everything after '?'), or empty string if none.
        query_string = ""
        if "?" in raw_path:
            query_string = raw_path.split("?", 1)[1]

        # Normalize path and prepare utilities (this will drop the query part from the path).
        handler_utils = HTTPDHandlerUtils(self.headers, raw_path, self.get_default_page())
        self.path = handler_utils.get_path()
        mime_type = HTTPDHandlerUtils.get_mime_type(self.path)

        # 1) Blacklist (same logic as do_POST: early reject, then return).
        if (hasattr(self.server, "match_blacklist") and
                self.server.match_blacklist(self.path) is True):
            content, status = HTTPDHandlerUtils.blacklisted_page_answer()
            self._response(content, status.code, "text/html")
            return

        # 2) Signed URL (early reject, then return).
        if (hasattr(self.server, "verify_signed_url") and
                self.server.verify_signed_url(self.path, query_string) is False):
            content, status = HTTPDHandlerUtils.signed_url_page_answer()
            self._response(content, status.code, "text/html")
            return

        # 3) Serve content
        # Static file first (even if HTML) when the file exists.
        if os.path.exists(handler_utils.get_path()) or os.path.exists(handler_utils.get_path()[1:]):
            content, status = handler_utils.static_content(self.path[1:])

        # Dynamic HTML page generated by the server.
        elif mime_type == "text/html":
            content, status = self._bakery(handler_utils, dict(), mime_type)

        # Unknown mime type: try to get a static file anyway.
        else:
            content, status = handler_utils.static_content(self.path[1:])

        # content can be either ['bytes'] or an iterator (depending on file size).
        self._response(content, status.code, mime_type)

    # -----------------------------------------------------------------------
    def do_POST(self) -> None:
        """Prepare the response to a POST request.

        This method:
        - extracts the query string (before path normalization),
        - applies blacklist (if enabled),
        - applies signed URL verification (if enabled),
        - reads POST body and generates the HTML response.

        """
        logging.debug(" ----- DO POST -- requested: {}".format(self.path))

        # Keep the raw request path because HTTPDHandlerUtils.get_path() removes "?..."
        raw_path = self.path

        # Extract the query string (everything after '?'), or empty string if none.
        query_string = ""
        if "?" in raw_path:
            query_string = raw_path.split("?", 1)[1]

        # Normalize path and prepare utilities (this will drop the query part from the path).
        handler_utils = HTTPDHandlerUtils(self.headers, raw_path, self.get_default_page())
        self.path = handler_utils.get_path()

        # 1) Blacklist (early reject, then return).
        if hasattr(self.server, "match_blacklist") and self.server.match_blacklist(self.path) is True:
            content, status = HTTPDHandlerUtils.blacklisted_page_answer()
            self._response(content, status.code, "text/html")
            return

        # 2) Signed URL (early reject, then return).
        if hasattr(self.server, "verify_signed_url") and self.server.verify_signed_url(self.path,
                                                                                       query_string) is False:
            content, status = HTTPDHandlerUtils.signed_url_page_answer()
            self._response(content, status.code, "text/html")
            return

        # 3) Process POST body and build the dynamic page.
        events, accept = handler_utils.process_post(self.rfile)
        content, status = self._bakery(handler_utils, events, accept)

        self._response(content, status.code, "text/html")

    # -----------------------------------------------------------------------

    def do_POST(self) -> None:
        """Prepare the response to a POST request.

        This method:
        - extracts the query string (before path normalization),
        - applies blacklist (if enabled),
        - applies signed URL verification (if enabled),
        - reads POST body and generates the HTML response.

        """
        logging.debug(" ----- DO POST -- requested: {}".format(self.path))

        # Keep the raw request path because HTTPDHandlerUtils.get_path() removes "?..."
        raw_path = self.path

        # Extract the query string (everything after '?'), or empty string if none.
        query_string = ""
        if "?" in raw_path:
            query_string = raw_path.split("?", 1)[1]

        # Normalize path and prepare utilities (this will drop the query part from the path).
        handler_utils = HTTPDHandlerUtils(self.headers, raw_path, self.get_default_page())
        self.path = handler_utils.get_path()

        # 1) Blacklist (early reject, then return).
        if (hasattr(self.server, "match_blacklist") and
                self.server.match_blacklist(self.path) is True):
            content, status = HTTPDHandlerUtils.blacklisted_page_answer()
            self._response(content, status.code, "text/html")
            return

        # 2) Signed URL (early reject, then return).
        if (hasattr(self.server, "verify_signed_url") and
                self.server.verify_signed_url(self.path, query_string) is False):
            content, status = HTTPDHandlerUtils.signed_url_page_answer()
            self._response(content, status.code, "text/html")
            return

        # 3) Process POST body and build the dynamic page.
        events, accept = handler_utils.process_post(self.rfile)
        content, status = self._bakery(handler_utils, events, accept)

        self._response(content, status.code, "text/html")

    # -----------------------------------------------------------------------

    def log_request(self, code='-', size='-') -> None:
        """Override. For a quiet handler pls!!!."""
        pass

