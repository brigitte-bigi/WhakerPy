"""
:filename: test_handler.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests for HTTPD handler in package httpd.

.. _This file is part of WhakerPy: https://sppas.org/
..
    -------------------------------------------------------------------------

    Copyright (C) 2011-2023 Brigitte Bigi
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
import unittest

from whakerpy.httpd.handler import HTTPDHandler

# ---------------------------------------------------------------------------


class TestHTTPDHandler(unittest.TestCase):

    def test_filter_path(self):
        default_path = "index.html"

        # Correct path
        path = "/documents/hello.html"
        filepath, page_name = HTTPDHandler.filter_path(path, default_path)
        self.assertEqual(filepath, path)
        self.assertEqual(page_name, "hello.html")

        # Path ending with '/'
        path = "/documents/"
        filepath, page_name = HTTPDHandler.filter_path(path, default_path)
        self.assertEqual(filepath, "/documents/index.html")
        self.assertEqual(page_name, default_path)

        # Other path ending with '/'
        path = "http://localhost:8080/documents/"
        filepath, page_name = HTTPDHandler.filter_path(path, default_path)
        self.assertEqual(filepath, "http://localhost:8080/documents/index.html")
        self.assertEqual(page_name, default_path)

        # Path ending with '/' with query string
        path = "/home/user/documents/?wexa_color=light"
        filepath, page_name = HTTPDHandler.filter_path(path, default_path)
        self.assertEqual(filepath, "/home/user/documents/index.html")
        self.assertEqual(page_name, default_path)

        # Existing path, not ending by '/'
        path = os.getcwd()
        filepath, page_name = HTTPDHandler.filter_path(path, default_path)
        self.assertEqual(filepath, path + "/index.html")
        self.assertEqual(page_name, default_path)

        # Non-existing path, not ending by '/'
        path = "/home/user/documents"
        filepath, page_name = HTTPDHandler.filter_path(path, default_path)
        self.assertEqual(filepath, path + "/index.html")
        self.assertEqual(page_name, default_path)

        # No path
        filepath, page_name = HTTPDHandler.filter_path("", default_path)
        self.assertEqual(filepath, "/index.html")
        self.assertEqual(page_name, default_path)
