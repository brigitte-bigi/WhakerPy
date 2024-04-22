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

        # Path ending with '/'
        path = "/documents/"
        filename, page_name = HTTPDHandler.filter_path(path, default_path)
        self.assertEqual(filename, "/documents/index.html")
        self.assertEqual(page_name, "documents/")  ### ???

        # Path ending with '/'
        path = "http://localhost:8080/documents/"
        filename, page_name = HTTPDHandler.filter_path(path, default_path)
        self.assertEqual(filename, "http://localhost:8080/documents/index.html")
        self.assertEqual(page_name, "http://localhost:8080/documents/")  ### ???

        # Path ending with '/' with query string
        path = "/home/user/documents/?wexa_color=light"
        filename, page_name = HTTPDHandler.filter_path(path, default_path)
        self.assertEqual(filename, "/home/user/documents/index.html")
        self.assertEqual(page_name, "home/user/documents/")  ### ???

        # Existing path, not ending by '/'
        path = os.getcwd()
        filename, page_name = HTTPDHandler.filter_path(path, default_path)
        self.assertEqual(filename, path + "/index.html")
        self.assertEqual(page_name, "home/user/documents/")

        # Non-existing path, not ending by '/'
        path = "/home/user/documents"
        filename, page_name = HTTPDHandler.filter_path(path, default_path)
        self.assertEqual(filename, path + "/index.html")
        self.assertEqual(page_name, "home/user/documents/")

        # No path
        filename, page_name = HTTPDHandler.filter_path("", default_path)
        self.assertEqual(filename, "index.html")
        self.assertEqual(page_name, "")


