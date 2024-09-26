"""
:filename: whakerpy.webapp.webwsgi.py
:author: Brigitte Bigi, Florian Lopitaux
:contact: contact@sppas.org
:summary: Create a HTTPD localhost server.

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

import os

from ..httpd import HTTPDStatus
from ..httpd import HTTPDHandlerUtils
from ..httpd import BaseResponseRecipe

from .webconfig import WebSiteData
from .webresponse import WebSiteResponse

# ---------------------------------------------------------------------------
# A wsgi application, for the web.
# ---------------------------------------------------------------------------


class WSGIApplication(object):
    """Create the default application for an UWSGI server.

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

    def __init__(self, default_path: str = "", default_filename: str = "index.html",
                 web_page_maker=WebSiteResponse, default_web_json: str = None):

        self.__default_path = default_path
        self.__default_file = default_filename
        self.__dynamic_pages = (web_page_maker, os.path.join(self.__default_path, default_web_json))
        self._pages = dict()

    # ---------------------------------------------------------------------------

    def __call__(self, environ, start_response):
        if 'HTTP_ACCEPT' in environ:
            environ['Accept'] = environ['HTTP_ACCEPT']

        # Get the expected filename
        handler_utils = HTTPDHandlerUtils(environ, environ["PATH_INFO"], self.__default_file)
        filepath = self.__default_path + handler_utils.get_path()
        # provide urls with several "/" instead of a single one
        filepath = filepath.replace("//", "/")
        page_name = handler_utils.get_page_name()

        # If the requested file is a static one
        if os.path.exists(filepath) is True:
            content, status = handler_utils.static_content(filepath)

        # If the requested file doesn't exist in the given default path (like the request.js)
        elif os.path.isfile(handler_utils.get_path()[1:]) is True:
            content, status = handler_utils.static_content(handler_utils.get_path()[1:])

        # else, it's a dynamic page
        else:
            # create dynamic page in web json (if given)
            if self.__dynamic_pages[1] is not None and page_name not in self._pages:
                self.__create_web_page(page_name)

            # if the page doesn't exist even after the dynamic creation, or wrong path
            if page_name not in self._pages or filepath != f"{self.__default_path}/{page_name}":
                status = HTTPDStatus(404)
                content = status.to_html(encode=True, msg_error=f"Page not found : {filepath}")
            else:
                # read and parse data if it's a POST request, empty events if it's not
                events, accept = handler_utils.process_post(environ['wsgi.input'])

                # bakery the response
                content, status = HTTPDHandlerUtils.bakery(self._pages, page_name, environ['PATH_INFO'], events,
                                                           HTTPDHandlerUtils.has_to_return_data(accept))

        # send response to the client
        headers = [
                ('Content-Type', HTTPDHandlerUtils.get_mime_type(filepath)),
                ('Cache-Control', 'max-age=0')   # Disable Varnish
            ]
        start_response(repr(status), headers)
        return [content]

    # ---------------------------------------------------------------------------

    def __create_web_page(self, page_name: str) -> None:
        """Create page dynamically from the json config file.

        """
        web_data = self.__dynamic_pages[0]

        if hasattr(web_data, 'bake_response'):
            data = web_data(self.__dynamic_pages[1])
            page = data.bake_response(page_name, default=self.__default_path)

            if page is not None:
                self._pages[page_name] = page

        else:
            data = WebSiteData(self.__dynamic_pages[1])
            if page_name in data:
                self._pages[page_name] = web_data(page_name)

    # ---------------------------------------------------------------------------

    def add_page(self, page_name: str, response: BaseResponseRecipe) -> bool:
        """Add a page to the list of available pages.

        False is returned if the page already exists or the response has a wrong type.

        :param page_name: (str) the name of the page
        :param response: (BaseResponseRecipe) the response object of the page (has to inherited of BaseResponseRecipe)
        :return: (bool) True if we successfully added the page

        """
        if page_name in self._pages.keys():
            return False

        if isinstance(response, BaseResponseRecipe) is False:
            return False

        self._pages[page_name] = response
        return True

    # ---------------------------------------------------------------------------

    def __contains__(self, item):
        return item in self._pages
