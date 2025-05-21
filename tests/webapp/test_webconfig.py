"""
:filename: tests.webapp.test_webconfig.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests for WebSiteData.

.. _This file is part of WhakerPy: https://whakerpy.sourceforge.io
..
    -------------------------------------------------------------------------

    Copyright (C) 2023-2025 Brigitte Bigi
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
import unittest
import json
import tempfile

from whakerpy.webapp.webconfig import WebSiteData

# ---------------------------------------------------------------------------


class TestWebSiteData(unittest.TestCase):

    def setUp(self):
        # Prepare old-format JSON
        self.old_fd, self.old_path = tempfile.mkstemp(suffix='.json')
        old_data = {
            "pagespath": "html",
            "index.html": {"title": "Home", "main": "index.htm", "header": True, "footer": False},
            "about.html": {"title": "About", "main": "about.htm", "header": False, "footer": True}
        }
        with os.fdopen(self.old_fd, 'w', encoding='utf-8') as f:
            json.dump(old_data, f)

        # Prepare new-format JSON
        self.new_fd, self.new_path = tempfile.mkstemp(suffix='.json')
        new_data = {"WhakerPy": old_data}
        with os.fdopen(self.new_fd, 'w', encoding='utf-8') as f:
            json.dump(new_data, f)

    def tearDown(self):
        os.remove(self.old_path)
        os.remove(self.new_path)

    # -----------------------------------------------------------------------

    def test_get_default_page_old(self):
        data = WebSiteData(self.old_path)
        self.assertEqual(data.get_default_page(), "index.html")

    # -----------------------------------------------------------------------

    def test_get_default_page_new(self):
        data = WebSiteData(self.new_path)
        self.assertEqual(data.get_default_page(), "index.html")

    # -----------------------------------------------------------------------

    def test_filename(self):
        data = WebSiteData(self.old_path)
        # main_path defaults to "", so result should end with the main filename
        self.assertTrue(data.filename("index.html").endswith("index.htm"))
        self.assertEqual(data.filename("missing.html"), "")

    # -----------------------------------------------------------------------

    def test_title(self):
        data = WebSiteData(self.old_path)
        self.assertEqual(data.title("index.html"), "Home")
        self.assertEqual(data.title("missing.html"), "")

    # -----------------------------------------------------------------------

    def test_has_header(self):
        data = WebSiteData(self.old_path)
        self.assertTrue(data.has_header("index.html"))
        self.assertFalse(data.has_header("about.html"))
        self.assertFalse(data.has_header("missing.html"))

    # -----------------------------------------------------------------------

    def test_has_footer(self):
        data = WebSiteData(self.old_path)
        self.assertFalse(data.has_footer("index.html"))
        self.assertTrue(data.has_footer("about.html"))
        self.assertFalse(data.has_footer("missing.html"))

    # -----------------------------------------------------------------------

    def test_is_page(self):
        """Test that is_page returns True for existing pages and False otherwise."""
        data = WebSiteData(self.old_path)
        self.assertTrue(data.is_page("index.html"))
        self.assertFalse(data.is_page("missing.html"))

    # -----------------------------------------------------------------------

    def test_dunder_contains(self):
        data = WebSiteData(self.old_path)
        self.assertIn("index.html", data)
        self.assertNotIn("unknown.html", data)

    # -----------------------------------------------------------------------

    def test_dunder_len(self):
        data = WebSiteData(self.old_path)
        self.assertEqual(len(data), 2)

    # -----------------------------------------------------------------------

    def test_dunder_iter(self):
        data = WebSiteData(self.old_path)
        self.assertListEqual(list(data), ["index.html", "about.html"] )

    # -----------------------------------------------------------------------

    def test_dunder_format(self):
        data = WebSiteData(self.old_path)
        self.assertEqual(format(data), str(data))

    # -----------------------------------------------------------------------

    def test_missing_pagespath_raises(self):
        # JSON without pagespath
        fd, path = tempfile.mkstemp(suffix='.json')
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump({"other": {}}, f)
        with self.assertRaises(ValueError):
            WebSiteData(path)
        os.remove(path)

    # -----------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()




