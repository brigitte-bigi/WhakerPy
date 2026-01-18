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
import re
from urllib.parse import urlsplit
from urllib.parse import urlunsplit
from urllib.parse import parse_qsl
from urllib.parse import urlencode

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

    def finalize_html(self, content: bytes) -> bytes:
        """Finalize an outgoing HTML page.

        This method applies outbound policies that must not be implemented
        inside Response classes.

        Current behavior:
        - If signed URLs are enabled, sign protected links found in:
          - href="..."
          - action="..."

        :param content: (bytes) HTML content.
        :return: (bytes) Updated HTML content.

        """
        if isinstance(content, (bytes, bytearray)) is False:
            raise TypeError("HTTPDPolicy.finalize_html: content must be bytes.")

        ttl_seconds = self.__signed_url_cfg.get("ttl", None)
        if ttl_seconds is None:
            return content

        protect = self.__signed_url_cfg.get("protect", [])
        if isinstance(protect, list) is False or len(protect) == 0:
            return content

        html = content.decode("utf-8", errors="replace")

        def _should_skip(value: str) -> bool:
            if len(value) == 0:
                return True
            v = value.lower()
            if v.startswith("#"):
                return True
            if v.startswith("http://") or v.startswith("https://"):
                return True
            if v.startswith("mailto:"):
                return True
            if v.startswith("javascript:"):
                return True
            if v.startswith("data:"):
                return True
            return False

        def _is_already_signed(query: str) -> bool:
            if len(query) == 0:
                return False
            q = ("&" + query).lower()
            return ("&ts=" in q) and ("&sig=" in q)

        def _sign_value(value: str) -> str:
            if _should_skip(value) is True:
                return value

            parts = urlsplit(value)
            path = parts.path
            if self.__signed_url.match_protect(path, protect) is False:
                return value

            if _is_already_signed(parts.query) is True:
                return value

            extra_params = []
            if len(parts.query) > 0:
                for k, v in parse_qsl(parts.query, keep_blank_values=True):
                    if k in ("ts", "sig"):
                        continue
                    extra_params.append((k, v))

            signed = self.__signed_url.sign(path, ttl_seconds)
            signed_parts = urlsplit(signed)

            final_query = signed_parts.query
            if len(extra_params) > 0:
                extra = urlencode(extra_params, doseq=True)
                if len(final_query) > 0:
                    final_query = final_query + "&" + extra
                else:
                    final_query = extra

            return urlunsplit((
                signed_parts.scheme or parts.scheme,
                signed_parts.netloc or parts.netloc,
                signed_parts.path,
                final_query,
                parts.fragment
            ))

        def _repl(m):
            attr = m.group(1)
            quote = m.group(2)
            val = m.group(3)
            return attr + "=" + quote + _sign_value(val) + quote

        html = re.sub(r'(href|action)\s*=\s*([\'"])(.*?)\2', _repl, html, flags=re.IGNORECASE)
        return html.encode("utf-8")

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
