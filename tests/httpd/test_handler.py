"""
:filename: tests.httpd.test_handler.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests for HTTPD handler in package httpd.

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

import os
import types
import unittest
from io import BytesIO

from whakerpy.httpd import HTTPDHandlerUtils
from whakerpy.httpd import BaseResponseRecipe
from whakerpy.httpd.hstatus import HTTPDStatus

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

        # Existing path, not ending by '/'... is invalid.
        path = os.getcwd()
        filepath, page_name = HTTPDHandlerUtils.filter_path(path, default_path)
        self.assertEqual(filepath, path)
        self.assertEqual(page_name, default_path)

        # Non-existing path, not ending by '/'... is invalid
        path = "/home/user/documents"
        filepath, page_name = HTTPDHandlerUtils.filter_path(path, default_path)
        self.assertEqual(filepath, path)
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
            ("hello.txt", "text/plain"),
            ("style.css", "text/css"),
            ("index.html", "text/html"),
            ("data.json", "application/json"),
            ("app.js", "text/javascript"),
            ("logo.png", "image/png"),
            ("video.mp4", "video/mp4")
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

    # ---------------------------------------------------------------------------

    def test_get_path_and_page_name(self):
        handler_utils = HTTPDHandlerUtils({}, "/documents/hello.html")
        self.assertEqual(handler_utils.get_path(), "/documents/hello.html")
        self.assertEqual(handler_utils.get_page_name(), "hello.html")

    # ---------------------------------------------------------------------------

    def test_has_to_return_data(self):
        self.assertTrue(HTTPDHandlerUtils.has_to_return_data("application/json"))
        self.assertTrue(HTTPDHandlerUtils.has_to_return_data("image/png"))
        self.assertTrue(HTTPDHandlerUtils.has_to_return_data("video/mp4"))
        self.assertTrue(HTTPDHandlerUtils.has_to_return_data("audio/mpeg"))
        self.assertTrue(HTTPDHandlerUtils.has_to_return_data("application/ogg"))
        self.assertFalse(HTTPDHandlerUtils.has_to_return_data("text/html"))

    # ---------------------------------------------------------------------------

    def test_parse_query_string(self):
        self.assertEqual(HTTPDHandlerUtils.parse_query_string(""), dict())
        self.assertEqual(HTTPDHandlerUtils.parse_query_string(None), dict())
        self.assertEqual(
            HTTPDHandlerUtils.parse_query_string("a=1&b=2"),
            {"a": "1", "b": "2"})
        self.assertEqual(
            HTTPDHandlerUtils.parse_query_string("a="),
            {"a": ""})

    # ---------------------------------------------------------------------------

    def test_blacklisted_page_answer(self):
        content, status = HTTPDHandlerUtils.blacklisted_page_answer()
        self.assertEqual(status.code, 418)
        self.assertIsInstance(content, bytes)

    # ---------------------------------------------------------------------------

    def test_signed_url_page_answer(self):
        content, status = HTTPDHandlerUtils.signed_url_page_answer()
        self.assertEqual(status.code, 404)
        self.assertIsInstance(content, bytes)

    # ---------------------------------------------------------------------------

    def test_getsize_from_iterator(self):
        def gen():
            yield b"hello "
            yield b"world"

        total_size, new_iterator = HTTPDHandlerUtils.getsize_from_iterator(gen())
        self.assertEqual(total_size, 11)
        self.assertEqual(b"".join(new_iterator), b"hello world")

    # ---------------------------------------------------------------------------

    def test_build_default_headers_no_cache(self):
        headers = dict(HTTPDHandlerUtils.build_default_headers("style.css"))
        self.assertEqual(headers["Content-Type"], "text/css")
        self.assertEqual(headers["Cache-Control"], "no-cache,no-store,must-revalidate,max-age=0")
        self.assertEqual(headers["Pragma"], "no-cache")
        self.assertEqual(headers["Expires"], "0")

    # ---------------------------------------------------------------------------

    def test_build_default_headers_browser_cache(self):
        headers = dict(HTTPDHandlerUtils.build_default_headers(
            "style.css", browser_cache=True, varnish=True))
        self.assertEqual(headers["Content-Type"], "text/css")
        self.assertNotIn("Cache-Control", headers)

    # ---------------------------------------------------------------------------

    def test_build_default_headers_with_generator_content(self):
        def gen():
            yield b"abcd"
            yield b"ef"

        headers = dict(HTTPDHandlerUtils.build_default_headers("data.bin", content=gen()))
        self.assertEqual(headers["Content-Length"], "6")

    # ---------------------------------------------------------------------------

    def test_process_post_get_method_in_wsgi_environ_is_ignored(self):
        handler_utils = HTTPDHandlerUtils({"REQUEST_METHOD": "GET"}, "/page.html")
        events, accept = handler_utils.process_post(BytesIO(b""))
        self.assertEqual(events, dict())
        self.assertEqual(accept, "text/html")

    # ---------------------------------------------------------------------------

    def test_process_post_no_content_type(self):
        handler_utils = HTTPDHandlerUtils({}, "/page.html")
        events, accept = handler_utils.process_post(BytesIO(b""))
        self.assertEqual(events, dict())

    # ---------------------------------------------------------------------------

    def test_process_post_urlencoded_form(self):
        body = b"name=Brigitte&city=Aix"
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "Content-Length": str(len(body))}
        handler_utils = HTTPDHandlerUtils(headers, "/page.html")
        events, accept = handler_utils.process_post(BytesIO(body))
        self.assertEqual(events, {"name": "Brigitte", "city": "Aix"})

    # ---------------------------------------------------------------------------

    def test_process_post_json_body(self):
        import json
        body = json.dumps({"a": 1, "b": "two"}).encode("utf-8")
        headers = {"Content-Type": "application/json",
                   "Content-Length": str(len(body))}
        handler_utils = HTTPDHandlerUtils(headers, "/page.html")
        events, accept = handler_utils.process_post(BytesIO(body))
        self.assertEqual(events, {"a": 1, "b": "two"})

    # ---------------------------------------------------------------------------

    def test_process_post_invalid_json_body_logs_and_keeps_raw(self):
        body = b"{not valid json"
        headers = {"Content-Type": "application/json",
                   "Content-Length": str(len(body))}
        handler_utils = HTTPDHandlerUtils(headers, "/page.html")
        events, accept = handler_utils.process_post(BytesIO(body))
        self.assertEqual(events, "{not valid json")

    # ---------------------------------------------------------------------------

    def test_process_post_auth_token_header(self):
        body = b"a=1"
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "Content-Length": str(len(body)),
                   "X-Auth-Token": "Bearer abc123"}
        handler_utils = HTTPDHandlerUtils(headers, "/page.html")
        events, accept = handler_utils.process_post(BytesIO(body))
        self.assertEqual(events["token"], "abc123")

    # ---------------------------------------------------------------------------

    def test_process_post_accept_header_prefers_html(self):
        body = b"a=1"
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "Content-Length": str(len(body)),
                   "Accept": "text/html,application/xhtml+xml"}
        handler_utils = HTTPDHandlerUtils(headers, "/page.html")
        events, accept = handler_utils.process_post(BytesIO(body))
        self.assertEqual(accept, "text/html")

    # ---------------------------------------------------------------------------

    def test_process_post_accept_header_json(self):
        body = b"{}"
        headers = {"Content-Type": "application/json",
                   "Content-Length": str(len(body)),
                   "Accept": "application/json"}
        handler_utils = HTTPDHandlerUtils(headers, "/page.html")
        events, accept = handler_utils.process_post(BytesIO(body))
        self.assertEqual(accept, "application/json")

    # ---------------------------------------------------------------------------

    def test_process_post_multipart_text_file_upload(self):
        boundary = "----WebKitFormBoundaryABC"
        content_type = "multipart/form-data; boundary=" + boundary
        body = (
            "------WebKitFormBoundaryABC--\r\n"
            'Content-Disposition: form-data; name="file"; filename="hello.txt"\r\n'
            "Content-Type: text/plain\r\n"
            "\r\n"
            "Hello World\r\n"
            "------WebKitFormBoundaryABC--\r\n"
        ).encode("utf-8")
        headers = {"Content-Type": content_type, "Content-Length": str(len(body))}
        handler_utils = HTTPDHandlerUtils(headers, "/upload")
        events, accept = handler_utils.process_post(BytesIO(body))
        self.assertEqual(events["upload_file"]["filename"], "hello.txt")
        self.assertEqual(events["upload_file"]["mime_type"], "text/plain")
        self.assertEqual(events["upload_file"]["file_content"], "Hello World")

    # ---------------------------------------------------------------------------

    def test_process_post_multipart_binary_file_upload(self):
        boundary = "----WebKitFormBoundaryABC"
        content_type = "multipart/form-data; boundary=" + boundary
        header_part = (
            "------WebKitFormBoundaryABC--\r\n"
            'Content-Disposition: form-data; name="file"; filename="img.bin"\r\n'
            "Content-Type: application/octet-stream\r\n"
            "\r\n"
        ).encode("utf-8")
        binary_payload = bytes([0, 1, 2, 255, 254, 253])
        footer_part = "\r\n------WebKitFormBoundaryABC--\r\n".encode("utf-8")
        body = header_part + binary_payload + footer_part
        headers = {"Content-Type": content_type, "Content-Length": str(len(body))}
        handler_utils = HTTPDHandlerUtils(headers, "/upload")
        events, accept = handler_utils.process_post(BytesIO(body))
        self.assertEqual(events["upload_file"]["filename"], "img.bin")
        self.assertEqual(events["upload_file"]["mime_type"], "application/octet-stream")
        self.assertTrue(events["upload_file"]["file_content"].startswith(binary_payload))

    # ---------------------------------------------------------------------------

    def test_bakery_page_not_found(self):
        content, status = HTTPDHandlerUtils.bakery(dict(), "missing.html", {}, {})
        self.assertEqual(status.code, 404)
        self.assertIsInstance(content, bytes)

    # ---------------------------------------------------------------------------

    def test_bakery_returns_html_content(self):
        page = BaseResponseRecipe(name="index.html")
        pages = {"index.html": page}
        content, status = HTTPDHandlerUtils.bakery(pages, "index.html", {}, {})
        self.assertIsInstance(content, bytes)
        self.assertEqual(status.code, page.status.code)

    # ---------------------------------------------------------------------------

    def test_bakery_returns_data_content(self):
        page = BaseResponseRecipe(name="index.html")
        page._data = {"key": "value"}
        pages = {"index.html": page}
        content, status = HTTPDHandlerUtils.bakery(
            pages, "index.html", {}, {}, has_to_return_data=True)
        self.assertEqual(content, b'{"key": "value"}')
        self.assertEqual(page.get_data(), "{}")  # reset after baking

    # ---------------------------------------------------------------------------

    def test_bakery_status_as_plain_int(self):
        class PlainIntStatusRecipe(BaseResponseRecipe):
            def _process_events(self, events, **kwargs):
                self._status = 205
                return False

        page = PlainIntStatusRecipe(name="index.html")
        pages = {"index.html": page}
        content, status = HTTPDHandlerUtils.bakery(pages, "index.html", {}, {})
        self.assertIsInstance(status, HTTPDStatus)
        self.assertEqual(status.code, 205)

    # ---------------------------------------------------------------------------

    def test_bakery_invalid_status_type_raises(self):
        class InvalidStatusRecipe(BaseResponseRecipe):
            def _process_events(self, events, **kwargs):
                self._status = "not-a-status"
                return False

        page = InvalidStatusRecipe(name="index.html")
        pages = {"index.html": page}
        with self.assertRaises(TypeError):
            HTTPDHandlerUtils.bakery(pages, "index.html", {}, {})
