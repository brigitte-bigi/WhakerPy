"""
:filename: tests.httpd.test_hhandler.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests for the HTTPDHandler in package httpd.

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

import unittest
from io import BytesIO

from whakerpy.httpd.handler import HTTPDHandler
from whakerpy.httpd.hstatus import HTTPDStatus

# ---------------------------------------------------------------------------


def make_handler(server, command: str, path: str, headers: dict = None, body: bytes = b""):
    """Instantiate an HTTPDHandler without going through a real socket.

    BaseHTTPRequestHandler.__init__ parses a request straight off a socket,
    which does not exist in a unit test. Bypassing __init__ and setting the
    attributes it would normally have set is the standard way to unit test
    a http.server handler.

    """
    handler = HTTPDHandler.__new__(HTTPDHandler)
    handler.server = server
    handler.client_address = ("127.0.0.1", 0)
    handler.command = command
    handler.path = path
    handler.request_version = "HTTP/1.1"
    handler.headers = headers if headers is not None else {}
    handler.rfile = BytesIO(body)
    handler.wfile = BytesIO()
    handler.close_connection = True
    return handler

# ---------------------------------------------------------------------------


class FakeBakeryServer:
    """A minimal WhakerPy-like server exposing page_bakery()."""

    def __init__(self, content: bytes = b"<html>baked</html>", status: int = 200):
        self.content = content
        self.status = status
        self.received = None

    def page_bakery(self, page_name, headers, events, has_to_return_data):
        self.received = (page_name, events, has_to_return_data)
        return self.content, HTTPDStatus(self.status)

# ---------------------------------------------------------------------------


class TestHTTPDHandler(unittest.TestCase):

    def test_do_head(self):
        handler = make_handler(object(), "HEAD", "/index.html")
        handler.do_HEAD()
        self.assertTrue(handler.wfile.getvalue().startswith(b"HTTP/1.0 200 OK"))

    # -----------------------------------------------------------------------

    def test_get_default_page_from_server(self):
        class ServerWithDefault:
            def default(self):
                return "home.html"

        handler = make_handler(ServerWithDefault(), "GET", "/")
        self.assertEqual(handler.get_default_page(), "home.html")

    # -----------------------------------------------------------------------

    def test_get_default_page_fallback(self):
        handler = make_handler(object(), "GET", "/")
        self.assertEqual(handler.get_default_page("index.html"), "index.html")

    # -----------------------------------------------------------------------

    def test_do_get_static_file(self):
        handler = make_handler(object(), "GET", "/tests/httpd/test_hhandler.py")
        handler.do_GET()
        response = handler.wfile.getvalue()
        self.assertTrue(response.startswith(b"HTTP/1.0 200 OK"))
        self.assertIn(b"Content-Type: text/x-python", response)

    # -----------------------------------------------------------------------

    def test_do_get_static_file_missing(self):
        handler = make_handler(object(), "GET", "/tests/httpd/no_such_file.py")
        handler.do_GET()
        self.assertTrue(handler.wfile.getvalue().startswith(b"HTTP/1.0 404 Not Found"))

    # -----------------------------------------------------------------------

    def test_do_get_dynamic_page_via_bakery(self):
        server = FakeBakeryServer(content=b"<html>dynamic</html>", status=200)
        handler = make_handler(server, "GET", "/somepage.html")
        handler.do_GET()
        response = handler.wfile.getvalue()
        self.assertTrue(response.startswith(b"HTTP/1.0 200 OK"))
        self.assertTrue(response.endswith(b"<html>dynamic</html>"))
        self.assertEqual(server.received[0], "somepage.html")

    # -----------------------------------------------------------------------

    def test_do_get_query_string_parsed_as_events(self):
        server = FakeBakeryServer()
        handler = make_handler(server, "GET", "/somepage.html?name=Brigitte")
        handler.do_GET()
        self.assertEqual(server.received[1], {"name": "Brigitte"})

    # -----------------------------------------------------------------------

    def test_do_get_unhandled_events_status_205_becomes_200(self):
        server = FakeBakeryServer(status=205)
        handler = make_handler(server, "GET", "/somepage.html?unknown=1")
        handler.do_GET()
        self.assertTrue(handler.wfile.getvalue().startswith(b"HTTP/1.0 200 OK"))

    # -----------------------------------------------------------------------

    def test_do_get_rejected_by_policy(self):
        class PolicyServer:
            def policy_check(self, path, query_string, headers):
                return False, b"blocked", HTTPDStatus(418), "text/html"

        handler = make_handler(PolicyServer(), "GET", "/admin.html")
        handler.do_GET()
        response = handler.wfile.getvalue()
        self.assertTrue(response.startswith(b"HTTP/1.0 418 I'm a Teapot"))
        self.assertTrue(response.endswith(b"blocked"))

    # -----------------------------------------------------------------------

    def test_do_get_allowed_by_policy(self):
        class PolicyServer(FakeBakeryServer):
            def policy_check(self, path, query_string, headers):
                return True, None, None, None

        server = PolicyServer()
        handler = make_handler(server, "GET", "/somepage.html")
        handler.do_GET()
        self.assertTrue(handler.wfile.getvalue().startswith(b"HTTP/1.0 200 OK"))

    # -----------------------------------------------------------------------

    def test_do_get_shutdown_on_status_410(self):
        class GoneServer(FakeBakeryServer):
            def __init__(self):
                super().__init__(content=b"bye", status=410)
                self.shutdown_called = False

            def shutdown(self):
                self.shutdown_called = True

        server = GoneServer()
        handler = make_handler(server, "GET", "/bye.html")
        handler.do_GET()
        self.assertTrue(server.shutdown_called)

    # -----------------------------------------------------------------------

    def test_do_post_dynamic_page_via_bakery(self):
        server = FakeBakeryServer(content=b"<html>posted</html>", status=200)
        body = b"a=1&b=2"
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "Content-Length": str(len(body))}
        handler = make_handler(server, "POST", "/form.html", headers=headers, body=body)
        handler.do_POST()
        response = handler.wfile.getvalue()
        self.assertTrue(response.startswith(b"HTTP/1.0 200 OK"))
        self.assertTrue(response.endswith(b"<html>posted</html>"))
        page_name, events, has_to_return_data = server.received
        self.assertEqual(page_name, "form.html")
        self.assertEqual(events, {"a": "1", "b": "2"})
        self.assertFalse(has_to_return_data)

    # -----------------------------------------------------------------------

    def test_do_post_rejected_by_policy(self):
        class PolicyServer:
            def policy_check(self, path, query_string, headers):
                return False, b"blocked", HTTPDStatus(418), "text/html"

        handler = make_handler(PolicyServer(), "POST", "/admin.html")
        handler.do_POST()
        response = handler.wfile.getvalue()
        self.assertTrue(response.startswith(b"HTTP/1.0 418 I'm a Teapot"))

    # -----------------------------------------------------------------------

    def test_do_get_no_bakery_server_serves_static_content(self):
        handler = make_handler(object(), "GET", "/tests/httpd/test_hhandler.py")
        handler.do_GET()
        self.assertTrue(handler.wfile.getvalue().startswith(b"HTTP/1.0 200 OK"))

    # -----------------------------------------------------------------------

    def test_log_request_is_silent(self):
        handler = make_handler(object(), "GET", "/index.html")
        # Must not raise and must not print anything to stdout/stderr.
        handler.log_request()

    # -----------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
