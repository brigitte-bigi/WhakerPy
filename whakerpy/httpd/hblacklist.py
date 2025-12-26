"""
:filename: whakerpy.httpd.hblacklist.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Manager of a list of websites to be blacklisted.

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
import os
import json
import logging

# ---------------------------------------------------------------------------


class Blacklist:
    """Manager of a list of blacklisted websites.

    A blacklist is a set of URL paths that can be blacklisted by a website,
    managed as a persistent set of URL paths to be rejected.

    The blacklist stores URL paths as strings, for example:
        - /bot.html
        - /admin/
        - /foo/bar

    A match can be:
        - exact match
        - parent-path match

    Example:
        If '/admin' is in the blacklist, then '/admin', '/admin/', and
        '/admin/page.html' are considered blacklisted.

    """

    def __init__(self) -> None:
        """Create an empty blacklist."""
        self.__blacklist = set()

    # -----------------------------------------------------------------------

    def load(self, filepath: str, json_key: str = "blacklist") -> int:
        """Load blacklist entries from a file.

        If filepath ends with '.json', entries are loaded from the given json_key.
        Otherwise, entries are loaded from a text file (one entry per line).

        :param filepath: (str) Path of the file.
        :param json_key: (str) Key of the blacklist list in JSON files.
        :raises: TypeError: filepath is not a string.
        :raises: IOError: file does not exist.
        :raises: ValueError: JSON content is invalid, or json_key is not a list.
        :return: (int) Number of loaded entries.

        """
        if type(filepath) is not str:
            raise TypeError("Blacklist filepath must be a string.")
        if os.path.exists(filepath) is False:
            raise IOError(f"Blacklist file {filepath} does not exist.")

        if filepath.lower().endswith(".json"):
            return self.__load_json(filepath, json_key)

        return self.__load_text(filepath)

    # -----------------------------------------------------------------------

    def match(self, value: str) -> bool:
        """Return True if a blacklist entry is found inside the given string.

        This method is intended for headers like User-Agent.
        Each blacklist entry is a plain string token.
        Matching rule: substring search.

        :param value: (str) A string to test (example: a User-Agent header).
        :return: (bool) True if blacklisted, False otherwise.

        """
        if type(value) is not str:
            raise TypeError("Value must be a string.")

        for entry in self.__blacklist:
            if entry in value:
                return True

        return False

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __contains__(self, item):
        """Return True if the given URL path exists in the blacklist."""
        return item in self.__blacklist

    def __str__(self):
        return str(self.__blacklist)

    def __repr__(self):
        return "Blacklist: " + str(self.__blacklist)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __load_text(self, filepath: str) -> int:
        items: set[str] = set()
        with open(filepath, "r", encoding="utf-8") as fp:
            for line in fp:
                s = line.strip()
                if len(s) == 0 or s.startswith("#"):
                    continue
                items.add(s)
        self.__blacklist = items
        return len(items)

    # -----------------------------------------------------------------------

    def __load_json(self, filepath: str, json_key: str) -> int:
        with open(filepath, "r", encoding="utf-8") as fp:
            try:
                _full_data = json.load(fp)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON file: {filepath}") from e

        # Search for the WhakerPy section in the JSON config file.
        if "WhakerPy" not in _full_data:
            # Introduced in WhakerPy 1.2
            raise KeyError(
                f"{filepath!r} is missing the required 'WhakerPy' section."
            )
        _section = _full_data["WhakerPy"]
        if isinstance(_section, dict) is False:
            raise TypeError("JSON key 'WhakerPy' must be a dict.")

        # Then search for the "blacklist" section in the "WhakerPy" section.
        items = _section.get(json_key, [])
        if isinstance(items, list) is False:
            raise TypeError(f"JSON key '{json_key}' must be a list.")

        out: set[str] = set()
        for it in items:
            if isinstance(it, str) is True and len(it) > 0:
                out.add(it)
                logging.info("Blacklisted entry '" + it + "'")

        self.__blacklist = out
        return len(out)
