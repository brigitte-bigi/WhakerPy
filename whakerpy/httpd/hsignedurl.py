# -*- coding: UTF-8 -*-
"""
:filename: whakerpy.httpd.hsignedurl.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Sign and verify ephemeral URLs (stateless, no cookie, no storage).

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

import hashlib
import hmac
import time
from urllib.parse import parse_qs

# ---------------------------------------------------------------------------


class SignedURL:
    """Sign and verify ephemeral URLs.

    A signed URL is:
        <path>?<ts_key>=<unix_ts>&<sig_key>=<signature>

    The signature is HMAC-SHA256 on:
        path + "\\n" + unix_ts

    No cookie. No server-side storage. Python standard library only.

    :example:
    >>> signer = SignedURL(secret='YOUR_PRIVATE_SECRET')
    >>> url = signer.sign('/text_12345.html', ttl_seconds=120)
    >>> ok = signer.verify('/text_12345.html', query_string, ttl_seconds=120)

    """

    def __init__(self, secret: str, ts_key: str = "ts", sig_key: str = "sig"):
        """Create the SignedURL helper.

        :param secret: (str) Secret used to sign URLs. Must remain private.
        :param ts_key: (str) Query parameter name for the timestamp.
        :param sig_key: (str) Query parameter name for the signature.

        """
        if type(secret) is not str:
            raise TypeError("SignedURL secret must be a string.")
        if len(secret) == 0:
            raise ValueError("SignedURL secret must not be empty.")
        if type(ts_key) is not str:
            raise TypeError("SignedURL ts_key must be a string.")
        if type(sig_key) is not str:
            raise TypeError("SignedURL sig_key must be a string.")
        if len(ts_key) == 0 or len(sig_key) == 0:
            raise ValueError("SignedURL keys must not be empty.")

        self.__secret = secret.encode("utf-8")
        self.__ts_key = ts_key
        self.__sig_key = sig_key

    # -----------------------------------------------------------------------

    def sign(self, path: str, ttl_seconds: int) -> str:
        """Return a signed URL for the given path.

        :param path: (str) URL path (example: 'text_123.html').
        :param ttl_seconds: (int) Lifetime in seconds. The timestamp is "now".
        :return: (str) Signed URL (path + query).

        """
        if type(path) is not str:
            raise TypeError("SignedURL path must be a string.")
        if type(ttl_seconds) is not int:
            raise TypeError("SignedURL ttl_seconds must be an int.")
        if ttl_seconds <= 0:
            raise ValueError("SignedURL ttl_seconds must be > 0.")

        normalized_path = self.__normalize_path(path)
        now_ts = int(time.time())
        signature = self.__hmac_signature(normalized_path, now_ts)

        # TTL is not embedded; verification checks "now - ts <= ttl_seconds".
        # The caller must provide ttl_seconds again at verify() time.
        return "{:s}?{:s}={:d}&{:s}={:s}".format(
            normalized_path, self.__ts_key, now_ts, self.__sig_key, signature
        )

    # -----------------------------------------------------------------------

    def verify(self, path: str, query_string: str, ttl_seconds: int) -> bool:
        """Verify that (path, query_string) contains a valid signature.

        :param path: (str) URL path without query (example: '/text_123.html').
        :param query_string: (str) Raw query string (example: 'ts=...&sig=...').
        :param ttl_seconds: (int) Accepted lifetime in seconds.
        :return: (bool) True if valid, False otherwise.

        """
        if type(path) is not str:
            raise TypeError("SignedURL path must be a string.")
        if type(query_string) is not str:
            raise TypeError("SignedURL query_string must be a string.")
        if type(ttl_seconds) is not int:
            raise TypeError("SignedURL ttl_seconds must be an int.")
        if ttl_seconds <= 0:
            raise ValueError("SignedURL ttl_seconds must be > 0.")

        normalized_path = self.__normalize_path(path)

        ts_value, sig_value = self.__extract_ts_sig(query_string)
        if ts_value is None or sig_value is None:
            return False

        now_ts = int(time.time())
        if ts_value > now_ts:
            return False
        if (now_ts - ts_value) > ttl_seconds:
            return False

        expected_sig = self.__hmac_signature(normalized_path, ts_value)
        return hmac.compare_digest(expected_sig, sig_value)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __normalize_path(self, path: str) -> str:
        p = path
        if "?" in p:
            p = p.split("?", 1)[0]
        if p.startswith("/") is False:
            p = "/" + p
        while "//" in p:
            p = p.replace("//", "/")
        return p

    def __hmac_signature(self, path: str, unix_ts: int) -> str:
        payload = "{:s}\n{:d}".format(path, unix_ts).encode("utf-8")
        digest = hmac.new(self.__secret, payload, hashlib.sha256).hexdigest()
        return digest

    def __extract_ts_sig(self, query_string: str) -> tuple[int | None, str | None]:
        if len(query_string) == 0:
            return None, None

        qs = parse_qs(query_string, keep_blank_values=True)

        if self.__ts_key not in qs:
            return None, None
        if self.__sig_key not in qs:
            return None, None

        ts_list = qs.get(self.__ts_key, [])
        sig_list = qs.get(self.__sig_key, [])

        if len(ts_list) != 1 or len(sig_list) != 1:
            return None, None

        ts_raw = ts_list[0]
        sig_raw = sig_list[0]

        try:
            ts_value = int(ts_raw)
        except ValueError:
            return None, None

        if type(sig_raw) is not str:
            return None, None
        if len(sig_raw) == 0:
            return None, None

        return ts_value, sig_raw
