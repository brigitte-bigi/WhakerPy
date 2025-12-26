"""
:filename: whakerpy.webapp.webwsgi.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: Create a HTTPD localhost server.

.. _This file is part of WhakerPy: https://whakerpy.sourceforge.io
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

The "environ" parameter is a dictionary. Here are examples of "environ"
key/values:

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

import os
import types
import logging

from ..httpd import HTTPDStatus
from ..httpd import HTTPDHandlerUtils
from ..httpd import BaseResponseRecipe
from ..httpd import Blacklist
from ..httpd.hsignedurl import SignedURL

from .webconfig import WebSiteData
from .webresponse import WebSiteResponse

# ---------------------------------------------------------------------------
# A wsgi application, for the web.
# ---------------------------------------------------------------------------


class WSGIApplication(object):
    """Create the default application for an UWSGI server.

    WSGI response is created from given "environ" parameters and communicated
    with start_response.

    This class checks if the request comes from a blacklisted URL ASAP.

    """

    def __init__(self, default_path: str = "", default_filename: str = "index.html",
                 web_page_maker=WebSiteResponse, default_web_json: str = None):
        """Initialize the WSGIApplication instance.

        :param default_path: (str) Default root path for static or dynamic pages
        :param default_filename: (str) Default filename to serve if none is provided
        :param web_page_maker: (callable) A callable used to generate dynamic pages
        :param default_web_json: (str) Path to the JSON file for dynamic page definitions

        """
        self.__default_path = default_path
        self.__default_file = default_filename
        self.__blacklist = Blacklist()
        self.__signed_url = SignedURL()
        self.__signed_url_cfg = {"ttl": None, "protect": []}

        web_json_path = None
        if default_web_json is not None:
            web_json_path = os.path.join(self.__default_path, default_web_json)
        self.__dynamic_pages = (web_page_maker, web_json_path)
        self._pages = dict()

        if default_web_json is not None:
            try:
                self.__blacklist.load(self.__dynamic_pages[1], json_key='blacklist')
            except Exception as e:
                logging.error(f"Blacklist disabled: {e}")
            try:
                self.__signed_url_cfg = self.__signed_url.load(self.__dynamic_pages[1], json_key='signed_url')
            except Exception as e:
                logging.error(f"Signed URLs disabled: {e}")

    # -----------------------------------------------------------------------

    def __call__(self, environ, start_response):
        """Handle WSGI requests.

        Process the incoming "environ" dictionary and respond using the given
        start_response callable.

        :param environ: (dict) WSGI environment dictionary with request data
        :param start_response: (callable) Function to start the HTTP response
        :return: (bytes|iterable) Response content to send back to the client

        """
        if 'HTTP_ACCEPT' in environ:
            environ['Accept'] = environ['HTTP_ACCEPT']

        handler_utils = HTTPDHandlerUtils(environ, environ["PATH_INFO"], self.__default_file)

        # Resolve the requested file path and page name
        requested_path = handler_utils.get_path()
        filepath = self.__default_path + handler_utils.get_path()
        # Normalize paths with multiple slashes
        filepath = filepath.replace("//", "/")
        page_name = handler_utils.get_page_name()

        # Check immediately for a blacklisted URL
        content, status, headers = self.__reject_blacklist(requested_path, environ, filepath)
        if content is not None:
            start_response(repr(status), headers)
            return [content]

        # Check for a signed URL
        content, status, headers = self.__reject_unsigned(environ, handler_utils, filepath, requested_path)
        if content is not None:
            start_response(repr(status), headers)
            return [content]

        # If the requested file is a static one
        use_cache = True
        if os.path.exists(filepath) is True:
            content, status = handler_utils.static_content(filepath)

        # If the requested file doesn't exist in the given default path
        elif os.path.isfile(handler_utils.get_path()[1:]) is True:
            content, status = handler_utils.static_content(handler_utils.get_path()[1:])

        # else, it's a dynamic page
        else:
            content, status = self.__serve_dynamic_content(page_name, filepath, environ, handler_utils)
            use_cache = False

        # Check if content is a generator (created with 'yield' for large files)
        if isinstance(content, types.GeneratorType):
            headers = HTTPDHandlerUtils.build_default_headers(
                filepath, content, browser_cache=use_cache, varnish=use_cache)
            start_response(repr(status), headers)
            # Either consume the iterator and return a large amount of bytes,
            return [c for c in content]
            # or return the iterator (is this supported?)
            # return content

        # Return bytes
        headers = HTTPDHandlerUtils.build_default_headers(
            filepath, content, browser_cache=use_cache, varnish=use_cache)
        start_response(repr(status), headers)
        return [content]

    # -----------------------------------------------------------------------

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

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __create_dynamic_page(self, page_name: str) -> None:
        """Create page dynamically from the json config file.

        :param page_name: (str) Name of the page to bake

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

    # -----------------------------------------------------------------------

    def __serve_dynamic_content(self, page_name: str, filepath: str, environ, handler_utils) -> tuple:
        """Handle requests for dynamic content or return a 404 if not found."""
        # Create dynamic page if necessary
        if self.__dynamic_pages[1] is not None and page_name not in self._pages:
            self.__create_dynamic_page(page_name)

        # Return 404 if the page does not exist or the path is invalid
        if page_name not in self._pages or filepath != f"{self.__default_path}/{page_name}":
            status = HTTPDStatus(404)
            content = status.to_html(encode=True, msg_error=f"Page not found: {filepath}")
        else:
            # Process dynamic content. Events are empty if POST request.
            events, accept = handler_utils.process_post(environ['wsgi.input'])
            content, status = HTTPDHandlerUtils.bakery(
                self._pages, page_name, environ['PATH_INFO'], events,
                HTTPDHandlerUtils.has_to_return_data(accept)
            )
        return content, status

    # ---------------------------------------------------------------------------

    def __reject_blacklist(self, requested_path: str, environ: dict, filepath: str):
        """Reject requests matching blacklist rules.

        :param environ: (dict) WSGI environment.
        :param filepath: (str) Resolved file path (used for headers).
        :return: (tuple) (content, status, headers) or (None, None, None).

        """
        user_agent = environ.get("HTTP_USER_AGENT", "")

        if self.__blacklist.match(requested_path) is True or self.__blacklist.match(user_agent) is True:
            logging.warning(f"Blacklisted agent {user_agent} and/or url {requested_path}.")
            content, status = HTTPDHandlerUtils.blacklisted_page_answer()
            headers = HTTPDHandlerUtils.build_default_headers(
                filepath, content, browser_cache=False, varnish=False
            )
            return content, status, headers

        return None, None, None

    # ---------------------------------------------------------------------------

    def __reject_unsigned(self, environ: dict, handler_utils, filepath: str, requested_path: str):
        """Reject requests that require a signed URL but do not verify.

        If signed URLs are disabled (ttl is None), do not reject.

        :param environ: (dict) WSGI environment.
        :param handler_utils: (HTTPDHandlerUtils) Built from environ.
        :param filepath: (str) Resolved file path (used for headers).
        :param requested_path: (str) URL path without query.
        :return: (tuple) (content, status, headers) or (None, None, None).

        """
        ttl_seconds = self.__signed_url_cfg.get("ttl", None)
        protect = self.__signed_url_cfg.get("protect", [])

        if ttl_seconds is None:
            return None, None, None

        if self.__signed_url.match_protect(requested_path, protect) is False:
            return None, None, None

        query_string = environ.get("QUERY_STRING", "")
        if self.__signed_url.verify(requested_path, query_string, ttl_seconds) is True:
            return None, None, None

        content, status = HTTPDHandlerUtils.signed_url_page_answer()
        headers = handler_utils.build_default_headers(
            filepath, content, browser_cache=False, varnish=False
        )
        return content, status, headers

    # ---------------------------------------------------------------------------
    # Overloads
    # ---------------------------------------------------------------------------

    def __contains__(self, page_name: str) -> bool:
        """Check if a page name exists in the application.

        :param page_name: (str) Name of the page to check
        :return: (bool) True if the page exists, False otherwise

        """
        return page_name in self._pages
