"""
:filename: test_status.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary: Tests for HTTPD status in package httpd.

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

import unittest

from whakerpy.httpd.hstatus import HTTPDValueError
from whakerpy.httpd.hstatus import HTTPDStatus

# ---------------------------------------------------------------------------


class TestHTTPDExceptions(unittest.TestCase):

    def test_status_value_errors(self):
        try:
            raise HTTPDValueError("value")
        except ValueError as e:
            self.assertTrue(isinstance(e, HTTPDValueError))
            self.assertTrue("0377" in str(e))
            self.assertEqual(377, e.status)

# ---------------------------------------------------------------------------


class TestHTTPDStatus(unittest.TestCase):

    def test_check(self):
        # Check success
        self.assertEqual(100, HTTPDStatus.check(100))
        self.assertEqual(200, HTTPDStatus.check("200"))

        # Check fail
        with self.assertRaises(HTTPDValueError):
            HTTPDStatus.check("AZERTY")
        with self.assertRaises(HTTPDValueError):
            HTTPDStatus.check(84)

    def test_init(self):
        s = HTTPDStatus()
        self.assertEqual(str(s), "200")
        self.assertTrue(s == 200)
        self.assertEqual(200, s)

    def test_get_set(self):
        s = HTTPDStatus()
        s.code = 404
        self.assertEqual(404, s)
        self.assertEqual(404, s.code)

        with self.assertRaises(HTTPDValueError):
            s.code = "azerty"
        with self.assertRaises(HTTPDValueError):
            s.code = 1974

    def test_str(self):
        s = HTTPDStatus()
        self.assertEqual(str(s), "200")
        self.assertEqual(repr(s), "200 OK")
