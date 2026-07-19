"""
:filename: tests.httpd.test_hblacklist.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests for the Blacklist manager in package httpd.

.. _This file is part of WhakerPy: https://whakerpy.sourceforge.io
..
    -------------------------------------------------------------------------

    Copyright (C) 2023-2026 Brigitte Bigi, CNRS
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

import json
import os
import tempfile
import unittest

from whakerpy.httpd.hblacklist import Blacklist

# ---------------------------------------------------------------------------


class TestBlacklist(unittest.TestCase):

    def test_configure(self):
        b = Blacklist()
        n = b.configure({"blacklist": ["/admin", "BadBot"]})
        self.assertEqual(n, 2)
        self.assertIn("/admin", b)
        self.assertIn("BadBot", b)

    # -----------------------------------------------------------------------

    def test_configure_default_key(self):
        b = Blacklist()
        n = b.configure({"blacklist": ["/admin"]}, "blacklist")
        self.assertEqual(n, 1)

    # -----------------------------------------------------------------------

    def test_configure_missing_key(self):
        b = Blacklist()
        n = b.configure({})
        self.assertEqual(n, 0)

    # -----------------------------------------------------------------------

    def test_configure_not_a_list_raises(self):
        b = Blacklist()
        with self.assertRaises(TypeError):
            b.configure({"blacklist": "/admin"})

    # -----------------------------------------------------------------------

    def test_configure_ignores_empty_and_non_str_entries(self):
        b = Blacklist()
        n = b.configure({"blacklist": ["", "/admin", 42, None]})
        self.assertEqual(n, 1)
        self.assertIn("/admin", b)

    # -----------------------------------------------------------------------

    def test_configure_replaces_previous_entries(self):
        b = Blacklist()
        b.configure({"blacklist": ["/admin"]})
        b.configure({"blacklist": ["/bot.html"]})
        self.assertNotIn("/admin", b)
        self.assertIn("/bot.html", b)

    # -----------------------------------------------------------------------

    def test_match_exact_and_substring(self):
        b = Blacklist()
        b.configure({"blacklist": ["/admin", "EvilBot"]})
        self.assertTrue(b.match("/admin"))
        self.assertTrue(b.match("/admin/page.html"))
        self.assertTrue(b.match("Mozilla/5.0 EvilBot/1.0"))
        self.assertFalse(b.match("/index.html"))
        self.assertFalse(b.match("Mozilla/5.0"))

    # -----------------------------------------------------------------------

    def test_match_empty_blacklist(self):
        b = Blacklist()
        self.assertFalse(b.match("/admin"))
        self.assertFalse(b.match(""))

    # -----------------------------------------------------------------------

    def test_match_not_a_string_raises(self):
        b = Blacklist()
        with self.assertRaises(TypeError):
            b.match(123)

    # -----------------------------------------------------------------------

    def test_dunder_str_and_repr(self):
        b = Blacklist()
        b.configure({"blacklist": ["/admin"]})
        self.assertIn("/admin", str(b))
        self.assertTrue(repr(b).startswith("Blacklist:"))

    # -----------------------------------------------------------------------

    def test_load_filepath_not_a_string_raises(self):
        b = Blacklist()
        with self.assertRaises(TypeError):
            b.load(123)

    # -----------------------------------------------------------------------

    def test_load_missing_file_raises(self):
        b = Blacklist()
        with self.assertRaises(IOError):
            b.load("/no/such/file.txt")

    # -----------------------------------------------------------------------

    def test_load_text_file(self):
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("/admin\n")
            f.write("# a comment line\n")
            f.write("\n")
            f.write("BadBot\n")
        try:
            b = Blacklist()
            n = b.load(path)
            self.assertEqual(n, 2)
            self.assertIn("/admin", b)
            self.assertIn("BadBot", b)
        finally:
            os.remove(path)

    # -----------------------------------------------------------------------

    def test_load_json_file(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"WhakerPy": {"blacklist": ["/admin", "BadBot"]}}, f)
        try:
            b = Blacklist()
            n = b.load(path)
            self.assertEqual(n, 2)
            self.assertIn("/admin", b)
        finally:
            os.remove(path)

    # -----------------------------------------------------------------------

    def test_load_json_file_invalid_json_raises(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("{not valid json")
        try:
            b = Blacklist()
            with self.assertRaises(ValueError):
                b.load(path)
        finally:
            os.remove(path)

    # -----------------------------------------------------------------------

    def test_load_json_file_missing_whakerpy_section_raises(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"blacklist": ["/admin"]}, f)
        try:
            b = Blacklist()
            with self.assertRaises(KeyError):
                b.load(path)
        finally:
            os.remove(path)

    # -----------------------------------------------------------------------

    def test_load_json_file_whakerpy_not_a_dict_raises(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"WhakerPy": ["not", "a", "dict"]}, f)
        try:
            b = Blacklist()
            with self.assertRaises(TypeError):
                b.load(path)
        finally:
            os.remove(path)

    # -----------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
