"""
:filename: tests.httpd.test_handler.py
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

from whakerpy.httpd import HTTPDHandlerUtils

# ---------------------------------------------------------------------------


class TestHTTPDHandler(unittest.TestCase):

    def test_filter_path(self):
        default_path = "index.html"

        # Correct path
        path = "/documents/hello.html"
        filepath, page_name = HTTPDHandlerUtils.filter_path(path, default_path)
        self.assertEqual(filepath, path)
        self.assertEqual(page_name, "hello.html")

        # Path ending with '/'
        path = "/documents/"
        filepath, page_name = HTTPDHandlerUtils.filter_path(path, default_path)
        self.assertEqual(filepath, "/documents/index.html")
        self.assertEqual(page_name, default_path)

        # Other path ending with '/'
        path = "http://localhost:8080/documents/"
        filepath, page_name = HTTPDHandlerUtils.filter_path(path, default_path)
        self.assertEqual(filepath, "http://localhost:8080/documents/index.html")
        self.assertEqual(page_name, default_path)

        # Path ending with '/' with query string
        path = "/home/user/documents/?wexa_color=light"
        filepath, page_name = HTTPDHandlerUtils.filter_path(path, default_path)
        self.assertEqual(filepath, "/home/user/documents/index.html")
        self.assertEqual(page_name, default_path)

        # Existing path, not ending by '/'
        path = os.getcwd()
        filepath, page_name = HTTPDHandlerUtils.filter_path(path, default_path)
        self.assertEqual(filepath, path + "/index.html")
        self.assertEqual(page_name, default_path)

        # Non-existing path, not ending by '/'
        path = "/home/user/documents"
        filepath, page_name = HTTPDHandlerUtils.filter_path(path, default_path)
        self.assertEqual(filepath, path + "/index.html")
        self.assertEqual(page_name, default_path)

        # No path
        filepath, page_name = HTTPDHandlerUtils.filter_path("", default_path)
        self.assertEqual(filepath, "/index.html")
        self.assertEqual(page_name, default_path)

    # ---------------------------------------------------------------------------

    def test_mime_type(self):
        default_value = "unknown"

        # empty path
        path = ""
        mime_type = HTTPDHandlerUtils.get_mime_type(path)
        self.assertEqual(mime_type, default_value)

        # basic files
        paths = [
            ("hello.txt", "text/plain"), ("style.css", "text/css"), ("index.html", "text/html"),
            ("data.json", "application/json"), ("app.js", "application/javascript"),
            ("logo.png", "image/png"), ("video.mp4", "video/mp4")
        ]

        for file, correct_type in paths:
            guess_type = HTTPDHandlerUtils.get_mime_type(file)
            self.assertEqual(guess_type, correct_type)

        # full path
        path = "/application/documents/dark.css"
        mime_type = HTTPDHandlerUtils.get_mime_type(path)
        self.assertEqual(mime_type, "text/css")

        # wrong path
        path = '/application/documents'
        mime_type = HTTPDHandlerUtils.get_mime_type(path)
        self.assertEqual(mime_type, default_value)

    # ---------------------------------------------------------------------------

    def test_static_content(self):
        path = "/application/example.html"

        # wrong header parameter type
        header = 92
        with self.assertRaises(TypeError):
            HTTPDHandlerUtils(header, path)

        # file doesn't exist
        header = {'CONTENT_TYPE': "text/html"}
        handler_utils = HTTPDHandlerUtils(header, path)
        content, status = handler_utils.static_content(path)
        self.assertEqual(status, 404)
        self.assertEqual(type(content), bytes)

        # file is a folder
        path = os.getcwd()
        handler_utils = HTTPDHandlerUtils(header, path)
        content, status = handler_utils.static_content(path)
        self.assertEqual(status, 403)
        self.assertEqual(type(content), bytes)

        # correct case
        path = os.path.join(os.getcwd(), __file__)
        header['CONTENT_TYPE'] = "application/x-python-code"
        handler_utils = HTTPDHandlerUtils(header, path)
        content, status = handler_utils.static_content(path)
        self.assertEqual(status, 200)
        self.assertEqual(type(content), bytes)
