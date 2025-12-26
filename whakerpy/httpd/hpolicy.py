# -*- coding: UTF-8 -*-
"""
:filename: whakerpy.httpd.hpolicy.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Central HTTP policy (blacklist + signed URL) for both HTTPD and WSGI.

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

from __future__ import annotations

from .hblacklist import Blacklist
from .hsignedurl import SignedURL
from .hutils import HTTPDHandlerUtils

# ---------------------------------------------------------------------------


class HTTPDPolicy:
    """Apply HTTP security policies consistently in HTTPD and WSGI.

    This class centralizes the decision to accept or reject a request,
    based on:
    - blacklist (User-Agent and/or path)
    - signed URL verification (missing/invalid/expired)
    
    It must be instantiated once and configured once.

    """

    def __init__(self):
        """Create the policy with default (disabled) configuration.
        
        """
        # Persistent set of URL paths to reject early in the handler.
        self.__blacklist = Blacklist()
        # Signed URLs
        self.__signed_url = SignedURL()

        self.__blacklist_enabled = False
        self.__signed_url_cfg = {"ttl": None, "protect": []}

    # -----------------------------------------------------------------------

    def configure(self, config: dict) -> None:
        """Configure the policy from a configuration dict.

        Expected keys:
        - "blacklist": optional (filepath or json dict, depending on Blacklist.load)
        - "signed_url": optional (filepath or json dict, depending on SignedURL.load)
        
        If a key is missing, the corresponding policy is disabled.

        :param config: (dict) The configuration data.

        """
        if type(config) is not dict:
            raise TypeError("HTTPDPolicy.configure: config must be a dict.")

        self.__blacklist_enabled = False
        if "blacklist" in config and config["blacklist"] is not None:
            self.__blacklist.configure(config, "blacklist")
            self.__blacklist_enabled = True

        self.__signed_url_cfg = {"ttl": None, "protect": []}
        if "signed_url" in config and config["signed_url"] is not None:
            self.__signed_url_cfg = self.__signed_url.configure(config, "signed_url")

    # -----------------------------------------------------------------------

    def check(self, path: str, query_string: str, headers) -> tuple:
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
        if type(path) is not str:
            raise TypeError("HTTPDPolicy.check: path must be a string.")
        if type(query_string) is not str:
            raise TypeError("HTTPDPolicy.check: query_string must be a string.")

        user_agent = self._get_user_agent(headers)

        # 1) Blacklist
        if self.__blacklist_enabled is True:
            if self.__blacklist.match(path) is True or self.__blacklist.match(user_agent) is True:
                content, status = HTTPDHandlerUtils.blacklisted_page_answer()
                return False, content, status, "text/html"

        # 2) Signed URLs
        ttl_seconds = self.__signed_url_cfg.get("ttl", None)
        if ttl_seconds is not None:
            protect = self.__signed_url_cfg.get("protect", [])
            if self.__signed_url.match_protect(path, protect) is True:
                if self.__signed_url.verify(path, query_string, ttl_seconds) is False:
                    content, status = HTTPDHandlerUtils.signed_url_page_answer()
                    return False, content, status, "text/html"

        return True, None, None, None

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _get_user_agent(self, headers) -> str:
        """Extract User-Agent from headers/environ.

        :param headers: (Any) Object or dict supporting get().
        :return: (str) User-Agent or empty string.

        """
        if headers is None:
            return ""

        # http.server headers: "User-Agent"
        try:
            ua = headers.get("User-Agent", "")
            if type(ua) is str and len(ua) > 0:
                return ua
        except:
            pass

        # WSGI environ: "HTTP_USER_AGENT"
        try:
            ua = headers.get("HTTP_USER_AGENT", "")
            if type(ua) is str and len(ua) > 0:
                return ua
        except:
            pass

        return ""
