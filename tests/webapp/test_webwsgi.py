"""
:filename: tests.webapp.test_webwsgi.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests for the WSGIApplication in package webapp.

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

from whakerpy.webapp.webwsgi import WSGIApplication
from whakerpy.httpd.hresponse import BaseResponseRecipe

# ---------------------------------------------------------------------------


class FakeRecipe(BaseResponseRecipe):
    """A minimal recipe whose baked status can be forced.

    It exercises the GET handling of the WSGI application without relying on
    a real page: the events it receives are recorded and the status returned
    when baking is the one requested at construction time.

    """

    def __init__(self, name="somepage.html", forced_status=200):
        self._forced_status = forced_status
        self.received_events = None
        super().__init__(name=name)

    def _process_events(self, events, **kwargs) -> bool:
        self.received_events = events
        self._status.code = self._forced_status
        return False

# ---------------------------------------------------------------------------


def make_get_environ(path: str, query_string: str = ""):
    """Build the minimal WSGI environ dictionary for a GET request.

    :param path: (str) The requested path (PATH_INFO)
    :param query_string: (str) The query string, without the leading '?'
    :return: (dict) A WSGI environment dictionary

    """
    return {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": path,
        "QUERY_STRING": query_string,
        "wsgi.input": BytesIO(b""),
    }

# ---------------------------------------------------------------------------


class TestWSGIApplicationGet(unittest.TestCase):

    def setUp(self):
        self.captured_status = None
        self.captured_headers = None

    def start_response(self, status, headers):
        self.captured_status = status
        self.captured_headers = headers

    # -----------------------------------------------------------------------

    def test_get_query_string_parsed_as_events(self):
        recipe = FakeRecipe(name="somepage.html", forced_status=200)
        application = WSGIApplication(default_path="")
        application.add_page("somepage.html", recipe)

        environ = make_get_environ("/somepage.html", "name=Brigitte")
        content = application(environ, self.start_response)

        self.assertEqual(recipe.received_events, {"name": "Brigitte"})
        self.assertTrue(self.captured_status.startswith("200"))
        self.assertIsInstance(content[0], bytes)

    # -----------------------------------------------------------------------

    def test_get_unhandled_events_status_205_becomes_200(self):
        recipe = FakeRecipe(name="somepage.html", forced_status=205)
        application = WSGIApplication(default_path="")
        application.add_page("somepage.html", recipe)

        environ = make_get_environ("/somepage.html", "unknown=1")
        application(environ, self.start_response)

        self.assertTrue(self.captured_status.startswith("200"))

    # -----------------------------------------------------------------------

    def test_get_without_query_string_has_empty_events(self):
        recipe = FakeRecipe(name="somepage.html", forced_status=200)
        application = WSGIApplication(default_path="")
        application.add_page("somepage.html", recipe)

        environ = make_get_environ("/somepage.html", "")
        application(environ, self.start_response)

        self.assertEqual(recipe.received_events, dict())
        self.assertTrue(self.captured_status.startswith("200"))


# ---------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
