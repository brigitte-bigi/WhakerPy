"""
:filename: whakerpy.webapp.webwsgi.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Create a HTTPD localhost server.

.. _This file was part of WhakerPy: https://whakerpy.sf.net
    -------------------------------------------------------------------------

    Copyright (C) 2023-2024 Brigitte Bigi
    Laboratoire Parole et Langage, Aix-en-Provence, France

    Use of this software is governed by the GNU Public License, version 3.

    WhakerPy is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    WhakerPy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with WhakerPy. If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------

"""

import os

from ..httpd import HTTPDHandler
from ..httpd import HTTPDStatus

# ---------------------------------------------------------------------------
# Error's responses
# ---------------------------------------------------------------------------

ERROR = "Unknown"
HTTPD_500 = [
'<!DOCTYPE html>',
'<html>',
'  <head>',
'    <meta charset="utf-8">',
'    <title>Error 500</title>',
'  </head>',
'  <body>',
'    <h1>Internal Server Error 500. </h1>',
'    <p>The system returned the following error message: {}.</p>'.format(ERROR),
'    <p>Please send this message by e-mail to Brigitte Bigi: <contact@sppas.org></p>',
'  </body>',
'</html>'
]

# ---------------------------------------------------------------------------
# A wsgi application, for the web.
# ---------------------------------------------------------------------------


class WSGIApplication(object):
    """Create de default application for an UWSGI server.

    WSGI response is created from given "environ" parameters and communicated
    with start_response. The "environ" parameter is a dictionary. Here are
    examples of "environ" key/values:

    - 'REQUEST_METHOD': 'GET'
    - 'REQUEST_URI': '/information.html',
    - 'PATH_INFO': '/information.html',
    - 'QUERY_STRING': '',
    - 'SERVER_PROTOCOL': 'HTTP/1.1',
    - 'SCRIPT_NAME': '',
    - 'SERVER_NAME': 'macpro-1.home',
    - 'SERVER_PORT': '9090',
    - 'UWSGI_ROUTER': 'http',
    - 'REMOTE_ADDR': '127.0.0.1',
    - 'REMOTE_PORT': '26095',
    - 'HTTP_HOST': 'localhost:9090',
    - 'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0',
    - 'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    - 'HTTP_ACCEPT_LANGUAGE': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    - 'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br',
    - 'HTTP_REFERER': 'http://localhost:9090/contributeurs.html',
    - 'HTTP_DNT': '1', 'HTTP_CONNECTION': 'keep-alive',
    - 'HTTP_UPGRADE_INSECURE_REQUESTS': '1',
    - 'HTTP_SEC_FETCH_DEST': 'document',
    - 'HTTP_SEC_FETCH_MODE': 'navigate',
    - 'HTTP_SEC_FETCH_SITE': 'same-origin',
    - 'HTTP_SEC_FETCH_USER': '?1',

    """

    def __init__(self, default_path: str = "", default_filename: str = "index.html"):
        self.__default_path = default_path
        self.__default_file = default_filename

    def __call__(self, environ, start_response):
        content = None
        _error = "Unknown error..."
        status = HTTPDStatus()
        status.code = 500

        # Get the expected filename
        filename, page_name = HTTPDHandler.filter_path(environ["PATH_INFO"], default_path=self.__default_file)
        filename = self.__default_path + filename
        if os.path.isdir(filename):
            # Do it again...
            filename, page_name = HTTPDHandler.filter_path(environ["PATH_INFO"] + "/", default_path=self.__default_file)
            filename = self.__default_path + filename

        # Get its mimetype
        mime_type = HTTPDHandler.get_mime_type(filename)

        # If the requested file is a static one
        if os.path.exists(filename) is True:
            try:
                content, status = HTTPDHandler.static_content(filename, mime_type)
                start_response(repr(status), [('Content-Type', mime_type)])
            except Exception as e:
                content = None
                _error = str(e)

        if content is None:
            status.code = 404
            start_response(repr(status), [('Content-Type', 'text/html; charset=utf-8')])
            content = ['<!DOCTYPE html><html><meta charset="utf-8"><title>Error 404</title>'.encode('utf-8'),
                       "<p>Requested pagename={} was not found.</p></p>".format(page_name).encode('utf-8'),
                       '<p>Error 404: The requested file {:s} does not exist.</p>'.format(filename).encode('utf-8'),
                       '<p>More error infos: {:s}</p>'.format(_error).encode('utf-8'),
                       ]

        if content is not None:
            return content

        start_response(repr(status), [('Content-Type', 'text/html; charset=utf-8')])
        return [line.encode("utf-8") for line in HTTPD_500]
