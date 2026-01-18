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
import os
import json
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

    def __init__(self):
        """Create the SignedURL helper.

        """
        self.__secret = None
        self.__ts_key = ""
        self.__sig_key = ""

    # -----------------------------------------------------------------------

    def configure(self, config: dict, json_key: str = "signed_url") -> dict:
        """Configure the signed URLs.

        :param config: (dict) Configuration dictionary.
        :param json_key: (str) Key of the signed URLs list in dict.
        :raises: TypeError: invalid argument type.
        :raises: ValueError: dict content is invalid, or json_key is not a str.
        :return: (dict) Loaded settings: {"ttl": int, "protect": list}.

        """
        # "signed_url" section must be a dict: it contains secret/ttl/protect/query_keys.
        _cfg = config.get(json_key, None)

        # If missing: SignedURL disabled => reset and return empty config.
        if _cfg is None:
            self.__secret = None
            self.__ts_key = ""
            self.__sig_key = ""
            return {"ttl": None, "protect": []}

        if isinstance(_cfg, dict) is False:
            raise TypeError(f"JSON key '{json_key}' must be a dict.")

        # Extract data
        # ------------
        # Required values.
        _secret = _cfg.get("secret", "")
        self.check_non_empty_string(_secret)
        _ttl_seconds = _cfg.get("ttl")
        self.check_ttl_seconds(_ttl_seconds)
        _protect = _cfg.get("protect")
        if isinstance(_protect, (list, tuple)) is False:
            raise ValueError("signed_url.protect must be a list.")

        # Optional: override query parameter names for ts/sig.
        _query_keys = _cfg.get("query_keys", {})
        if isinstance(_query_keys, dict) is False:
            raise ValueError("signed_url.query_keys must be a dict.")
        ts_key = _query_keys.get("ts", self.__ts_key)
        self.check_non_empty_string(ts_key)
        sig_key = _query_keys.get("sig", self.__sig_key)
        self.check_non_empty_string(sig_key)

        # Apply config to this instance (stateless: only updates local fields).
        self.__secret = _secret.encode("utf-8")
        self.__ts_key = ts_key
        self.__sig_key = sig_key

        # Return non-secret settings for the caller (guard/application).
        return {"ttl": _ttl_seconds, "protect": _protect}

    # -----------------------------------------------------------------------

    def load(self, filepath: str, json_key: str = "signed_url") -> dict:
        """Load signed URL configuration entries from a file.

        Entries are loaded from the given json_key.

        :param filepath: (str) Path of the file.
        :param json_key: (str) Key of the signed URLs dict in JSON files.
        :raises: TypeError: invalid argument type.
        :raises: IOError: file does not exist.
        :raises: ValueError: JSON content is invalid, or json_key is not a str.
        :return: (dict) Loaded settings: {"ttl": int, "protect": list}.

        """
        self.check_non_empty_string(filepath)
        self.check_non_empty_string(json_key)
        if os.path.exists(filepath) is False:
            raise IOError(f"SignedURL configuration file {filepath} does not exist.")

        # Delegate JSON parsing/validation to a single private method.
        # It updates __secret/__ts_key/__sig_key and returns ttl/protect.
        return self.__load_json(filepath, json_key)

    # -----------------------------------------------------------------------

    def match_protect(self, path: str, protect: list) -> bool:
        """Return True if the given path must be protected by a signed URL.

        Protection rules are defined as a list of dict:
            {"prefix": "...", "suffix": "..."}

        :param path: (str) URL path (with or without leading slash).
        :param protect: (list) Protection rules.
        :return: (bool)

        """
        if type(path) is not str:
            raise TypeError("SignedURL path must be a string.")
        if isinstance(protect, (list, tuple)) is False:
            raise TypeError("SignedURL protect must be a list.")

        normalized_path = self.__normalize_path(path)

        for rule in protect:
            if isinstance(rule, dict) is False:
                continue

            prefix = rule.get("prefix", "")
            suffix = rule.get("suffix", "")

            if type(prefix) is not str or type(suffix) is not str:
                continue

            if normalized_path.startswith(prefix) and normalized_path.endswith(suffix):
                return True

        return False

    # -----------------------------------------------------------------------

    def sign(self, path: str, ttl_seconds: int) -> str:
        """Return a signed URL for the given path.

        :param path: (str) URL path (example: 'text_123.html').
        :param ttl_seconds: (int) Lifetime in seconds. The timestamp is "now".
        :raises: TypeError: invalid argument type.
        :raises: ValueError: invalid argument value.
        :return: (str) Signed URL (path + query).

        """
        if self.__secret is None:
            raise ValueError("SignedURL is not configured (secret is missing).")

        self.check_non_empty_string(path)
        self.check_ttl_seconds(ttl_seconds)

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
        if self.__secret is None:
            raise ValueError("SignedURL is not configured (secret is missing).")

        if type(path) is not str:
            raise TypeError("SignedURL path must be a string.")
        if type(query_string) is not str:
            raise TypeError("SignedURL query_string must be a string.")
        self.check_ttl_seconds(ttl_seconds)

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

    # -----------------------------------------------------------------------

    def __hmac_signature(self, path: str, unix_ts: int) -> str:
        payload = "{:s}\n{:d}".format(path, unix_ts).encode("utf-8")
        digest = hmac.new(self.__secret, payload, hashlib.sha256).hexdigest()
        return digest

    # -----------------------------------------------------------------------

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

    # -----------------------------------------------------------------------

    def __load_json(self, filepath: str, json_key: str) -> dict:
        """Load signed URL configuration from a JSON file.

        It reads config values and updates this instance fields.
        Expected JSON structure:
            {
                "WhakerPy": {
                    "signed_url": {
                        "secret": "...",
                        "ttl": 3600,
                        "protect": [...],
                        "query_keys": {"ts": "ts", "sig": "sig"}
                    }
                }
            }

        :param filepath:
        :param json_key:
        :raises: ValueError:
        :raises: KeyError:
        :raises: TypeError:
        :return: (dict)   {"ttl": <int>, "protect": <list>}

        """
        with open(filepath, "r", encoding="utf-8") as fp:
            try:
                _full_data = json.load(fp)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON file: {filepath}") from e

        # "WhakerPy" top-level section is mandatory for all WhakerPy web configs.
        if "WhakerPy" not in _full_data:
            # Introduced in WhakerPy 1.2
            raise KeyError(
                f"{filepath!r} is missing the required 'WhakerPy' section."
            )
        _section = _full_data["WhakerPy"]
        if isinstance(_section, dict) is False:
            raise TypeError("JSON key 'WhakerPy' must be a dict.")

        return self.configure(_section)

    # -----------------------------------------------------------------------

    @staticmethod
    def check_ttl_seconds(value: int):
        if type(value) is not int:
            raise TypeError("SignedURL ttl_seconds must be an int.")
        if value <= 0:
            raise ValueError("SignedURL ttl_seconds must be > 0.")

    # -----------------------------------------------------------------------

    @staticmethod
    def check_non_empty_string(value: str):
        if type(value) is not str:
            raise TypeError(f"Given '{value}' must be a string.")
        if len(value) == 0:
            raise ValueError(f"Given '{value}' must be non-empty.")

