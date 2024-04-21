# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.whakerpy.httpd.handler.py
:author:   Brigitte Bigi
:contributor: Florian Lopitaux
:contact:  contact@sppas.org
:summary:  Manage an HTTPD handler for any web-based application.

.. _This file is part of SPPAS: https://sppas.org/
..
    -------------------------------------------------------------------------

     ___   __    __    __    ___
    /     |  \  |  \  |  \  /              the automatic
    \__   |__/  |__/  |___| \__             annotation and
       \  |     |     |   |    \             analysis
    ___/  |     |     |   | ___/              of speech

    Copyright (C) 2011-2023  Brigitte Bigi
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

from __future__ import annotations
import os
import json
import logging
import codecs
import mimetypes
import http.server
from urllib.parse import parse_qsl

from .hstatus import HTTPDStatus

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
        - 404: Not Found
        - 410: Gone
        - 418: I'm not a teapot

    """

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

    def static_content(self, filename: str, mime_type: str) -> tuple:
        """Return the file content and the corresponding status.

        :param filename: (str) The path of the file to return
        :param mime_type: (str) The mime type of the file response

        :return: tuple(bytes, HTTPDStatus)

        """
        if os.path.exists(filename) is True:
            if os.path.isfile(filename) is True:
                content = HTTPDHandler.open_file_to_binary(filename, mime_type)
                return content, HTTPDStatus()

            else:
                content = bytes("<html><body>Error 403: Forbidden."
                                "The client can't have access to the requested {:s}."
                                "</body></html>".format(filename), "utf-8")

                status = HTTPDStatus()
                status.code = 403
                return content, status

        # it does not exist!
        content = bytes("<html><body>Error 404: Not found."
                        "The server does not have the requested {:s}."
                        "</body></html>".format(filename), "utf-8")

        status = HTTPDStatus()
        status.code = 404
        return content, status

    # -----------------------------------------------------------------------

    def _bakery(self, events: dict, mime_type: str) -> tuple:
        """Process the events and return the html page content or json data and status.

        :param events: (dict) key=event name, value=event value
        :param mime_type: (str) The mime type of the file response

        :return: tuple(bytes, HTTPDStatus) the content of the response the httpd status

        """
        # Test if the server is our
        if hasattr(self.server, 'page_bakery') is False:
            # Server is not the custom one for SPPAS wapp.
            return self.static_content(self.path[1:], mime_type)

        # Requested page name and page bakery for all the pages created
        # dynamically -- i.e. from an HTMLTree.
        page_name = os.path.basename(self.path)

        if mime_type == "application/json" or mime_type.startswith("image/") or mime_type.startswith("video/"):
            content, status = self.server.page_bakery(page_name, events, True)
        else:
            content, status = self.server.page_bakery(page_name, events)

        # but the HTML page may be static
        if status == 404:
            content, status = self.static_content(self.path[1:], mime_type)

        # if the user makes a mistake and set to the status an integer and not a HTTPDStatus
        if isinstance(status, int):
            code = status
            status = HTTPDStatus()
            status.code = code
        elif not isinstance(status, HTTPDStatus):
            raise TypeError("The status has to be an instance of HTTPDStatus (or int). Got: " + status)

        return content, status

    # -----------------------------------------------------------------------

    def _response(self, content: bytes, status: int, mime_type: str = None) -> None:
        """Make the appropriate HTTPD response.

        :param content: (bytes) The HTML response content
        :param status: (int) The HTTPD status code of the response
        :param mime_type: (str) The mime type of the file response

        """
        if status == 418:
            # 418: I'm not a teapot. Used as a response to a blocked request.
            # With no response content, the browser will display an empty page.
            self._set_headers(418, mime_type)
        elif status == 205:
            # 205 Reset Content. The request has been received. Tells the
            # user agent to reset the document which sent this request.
            # With no response content, the browser will continue to display
            # the current page.
            self._set_headers(205, mime_type)
        else:
            self._set_headers(status, mime_type)
            self.wfile.write(content)
            if status == 410:
                # 410 Gone. Only possible in the context of a local app.
                # On web, the server does not shut down when the client
                # is asking for!
                self.server.shutdown()

    # -----------------------------------------------------------------------
    # Override BaseHTTPRequestHandler classes.
    # -----------------------------------------------------------------------

    def do_HEAD(self) -> None:
        """Prepare the response to a HEAD request."""
        logging.debug("HEAD -- requested: {}".format(self.path))
        self._set_headers(200)

    # -----------------------------------------------------------------------

    def do_GET(self) -> None:
        """Prepare the response to a GET request.

        """
        logging.debug("GET -- requested: {}".format(self.path))

        # parse the path
        try:
            default = self.server.default()
            self.path = HTTPDHandler.filter_path(self.path, default_path=default)[0]
        except AttributeError:
            # Server is not the custom one for dynamic app.
            self.path = HTTPDHandler.filter_path(self.path)[0]

        mime_type = HTTPDHandler.get_mime_type(self.path)

        # The client requested an HTML page. Response content is created
        # by the server.
        if mime_type == "text/html":
            content, status = self._bakery(dict(), mime_type)
        else:
            # The client requested a css, a script, an image, a font, etc.
            # These are statics' content. The handler is reading it from disk,
            # and it makes the response itself.
            content, status = self.static_content(self.path[1:], mime_type)

        self._response(content, status.code, mime_type)

    # -----------------------------------------------------------------------

    def do_POST(self) -> None:
        """Prepare the response to a POST request.

        """
        logging.debug("POST -- requested: {}".format(self.path))

        # parse the path
        try:
            default = self.server.default()
            self.path = HTTPDHandler.filter_path(self.path, default_path=default)[0]
        except AttributeError:
            # Server is not the custom one for dynamic app.
            self.path = HTTPDHandler.filter_path(self.path)[0]

        # Parse the posted data
        events = HTTPDHandler.extract_body_content(self.rfile, self.headers.get('Content-Type'),
                                                   self.headers.get('Content-Length'))

        # Create the response
        accept_type = self.headers.get('Accept', "text/html")
        if "text/html" in accept_type:
            accept_type = "text/html"

        content, status = self._bakery(events, accept_type)
        self._response(content, status.code, accept_type)

    # -----------------------------------------------------------------------

    def log_request(self, code='-', size='-') -> None:
        """Override. For a quiet handler pls!!!."""
        pass

    # -----------------------------------------------------------------------
    # PUBLIC STATIC METHODS
    # -----------------------------------------------------------------------

    @staticmethod
    def get_mime_type(filename: str) -> str:
        """Returns the mime type of given file name or path.

        :param filename: (str) The name or path of the file

        :return: (str) The mime type of the file or 'unknown' if we can't find the type

        """
        mime_type, _ = mimetypes.guess_type(filename)

        if mime_type is not None:
            return mime_type
        else:
            return "unknown"

    # -----------------------------------------------------------------------

    @staticmethod
    def open_file_to_binary(filename: str, mime_type: str):
        """Open and read the given file and transform the content to bytes value.

        :param filename: (str) The path of the file to read
        :param mime_type: (str) The mime type of the file response

        :return: (bytes) the file content in bytes format

        """
        if mime_type is not None and (mime_type.startswith("text") or mime_type == "application/javascript"):
            with codecs.open(filename, "r", "utf-8") as fp:
                content = bytes("", "utf-8")

                for line in fp.readlines():
                    content += bytes(line, "utf-8")

                return content
        else:
            return open(filename, "rb").read()

    # -----------------------------------------------------------------------

    @staticmethod
    def filter_path(path: str, default_path: str = "index.html") -> tuple[str, str]:
        """Parse the path to return the correct filename and page name.

        :param path: (str) The path obtain from the request or environ
        :param default_path: (str) The default path to add if the path ends with '/'

        :return: (tuple[str, str]) the requested filename and the requested page name

        """
        # this block has to be before the '/' condition
        # example: http://localhost:8080/?wexa_color=light
        if "?" in path:
            path = path[:path.index("?")]

        filename = path
        if filename.endswith("/") is True:
            filename += default_path

        page_name = path
        if page_name.startswith('/'):
            page_name = page_name[1:]

        return filename, page_name

    # -----------------------------------------------------------------------

    @staticmethod
    def extract_body_content(content, content_type: str, content_length: str) -> dict:
        """Read and parse the body content of a POST request.
        
        :param content: (Binary object) the body of the POST request
        :param content_type: (str) the content type of the body, given (or not) in the request header
        :param content_length: (str) the content length of the body, given (or not) in the request header

        :return: (dict) the dictionary that contains the events to process,
                        or an empty dictionary if there is an error.

        """
        try:
            length = int(content_length)
        # if the length is None or not a string which contains an integer if somebody set the header with bad values
        except (TypeError, ValueError):
            length = 0

        # read file and print traceback
        data = content.read(length)

        try:
            data = data.decode("utf-8")
        except UnicodeError:  # the data is a binary file can't decode in utf-8 format (like image or video file)
            pass

        # if content-type is not defined in the header request
        if content_type is None or content_length == 0:
            data = dict()

        # parse uploaded file
        elif "multipart/form-data; boundary=" in content_type:
            filename, mime_type, content = HTTPDHandler.__extract_form_data_file(content_type, data)
            data = {'upload_file': {'filename': filename, 'mime_type': mime_type, 'file_content': content}}

        # parse json data from request.js
        elif "application/json" in content_type:
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                logging.error("Can't decode JSON POSTED data : {}".format(data))

        # otherwise try to parse text data from forms
        else:
            data = dict(parse_qsl(
                data,
                keep_blank_values=True,
                strict_parsing=False  # errors are silently ignored
            ))

        # return data parsed in python dictionary
        if "upload_file" in data:
            logging.debug(f"POST -- data: upload_file[{data['upload_file']['filename']}]")
        else:
            logging.debug("POST -- data: {}".format(data))

        return data

    # -----------------------------------------------------------------------

    @staticmethod
    def __extract_form_data_file(content_type: str, data: str | bytes) -> tuple[str, str, str]:
        # set special characters depending on if the uploaded file is in binary or utf-8 format
        if isinstance(data, bytes):
            data = str(data)
            end_line = "\\n"
            carriage_return = "\\r"
        else:
            end_line = "\n"
            carriage_return = "\r"

        # parse filename
        start_index_filename = data.index('filename="') + len('filename="')
        end_index_filename = start_index_filename + data[start_index_filename:].index('"')
        filename = data[start_index_filename:end_index_filename]

        # print("//// ATTENTION FILENAME ////")
        # print(filename)
        # print("//// ATTENTION FILENAME ////")

        # remove filename line
        data = data[end_index_filename:]

        # parse content-type
        start_index_type = data.index("Content-Type: ") + len("Content-Type: ")
        end_index_type = start_index_type + data[start_index_type:].index(end_line)
        mime_type = data[start_index_type:end_index_type]
        mime_type = mime_type.replace(carriage_return, '')

        # print("//// ATTENTION MIME-TYPE ////")
        # print(mime_type)
        # print("//// ATTENTION MIME-TYPE ////")

        # remove content-type line
        data = data[end_index_type + 1:]

        # parse file content
        start_boundary = content_type.index("boundary=") + len("boundary=")
        boundary = "--" + content_type[start_boundary:] + "--"

        start_content = data.index(end_line) + 1  # remove empty line
        end_content = data[start_content:].index(boundary)
        content = data[start_content:end_content]

        # print("//// ATTENTION FILE CONTENT ////")
        # print(content)
        # print("//// ATTENTION FILE CONTENT ////")

        return filename, mime_type, content
