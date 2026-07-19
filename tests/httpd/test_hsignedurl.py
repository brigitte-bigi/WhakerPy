"""
:filename: tests.httpd.test_hsignedurl.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests for the SignedURL manager in package httpd.

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
import time
import unittest

from whakerpy.httpd.hsignedurl import SignedURL

# ---------------------------------------------------------------------------


class TestSignedURL(unittest.TestCase):

    def setUp(self):
        self.config = {
            "signed_url": {
                "secret": "top-secret",
                "ttl": 60,
                "protect": [{"prefix": "/private/", "suffix": ""}],
                "query_keys": {"ts": "ts", "sig": "sig"}
            }
        }

    # -----------------------------------------------------------------------

    def test_configure(self):
        signer = SignedURL()
        settings = signer.configure(self.config)
        self.assertEqual(settings["ttl"], 60)
        self.assertEqual(settings["protect"], [{"prefix": "/private/", "suffix": ""}])

    # -----------------------------------------------------------------------

    def test_configure_disabled_when_key_missing(self):
        signer = SignedURL()
        settings = signer.configure({})
        self.assertIsNone(settings["ttl"])
        self.assertEqual(settings["protect"], [])
        with self.assertRaises(ValueError):
            signer.sign("/text.html", 60)

    # -----------------------------------------------------------------------

    def test_configure_not_a_dict_raises(self):
        signer = SignedURL()
        with self.assertRaises(TypeError):
            signer.configure({"signed_url": "not-a-dict"})

    # -----------------------------------------------------------------------

    def test_configure_missing_secret_raises(self):
        signer = SignedURL()
        with self.assertRaises((TypeError, ValueError)):
            signer.configure({"signed_url": {"ttl": 60, "protect": []}})

    # -----------------------------------------------------------------------

    def test_configure_missing_ttl_raises(self):
        signer = SignedURL()
        with self.assertRaises((TypeError, ValueError)):
            signer.configure({"signed_url": {"secret": "s", "protect": []}})

    # -----------------------------------------------------------------------

    def test_configure_protect_not_a_list_raises(self):
        signer = SignedURL()
        with self.assertRaises(ValueError):
            signer.configure({"signed_url": {"secret": "s", "ttl": 60, "protect": "nope"}})

    # -----------------------------------------------------------------------

    def test_configure_custom_query_keys(self):
        signer = SignedURL()
        cfg = {
            "signed_url": {
                "secret": "s", "ttl": 60, "protect": [],
                "query_keys": {"ts": "t", "sig": "s2"}
            }
        }
        signer.configure(cfg)
        signed = signer.sign("/text.html", 60)
        self.assertIn("t=", signed)
        self.assertIn("s2=", signed)

    # -----------------------------------------------------------------------

    def test_match_protect(self):
        signer = SignedURL()
        signer.configure(self.config)
        protect = [{"prefix": "/private/", "suffix": ".html"}]
        self.assertTrue(signer.match_protect("/private/page.html", protect))
        self.assertFalse(signer.match_protect("/private/page.js", protect))
        self.assertFalse(signer.match_protect("/public/page.html", protect))

    # -----------------------------------------------------------------------

    def test_match_protect_ignores_invalid_rules(self):
        signer = SignedURL()
        protect = ["not-a-dict", {"prefix": 1, "suffix": 2}]
        self.assertFalse(signer.match_protect("/private/page.html", protect))

    # -----------------------------------------------------------------------

    def test_match_protect_wrong_types_raise(self):
        signer = SignedURL()
        with self.assertRaises(TypeError):
            signer.match_protect(123, [])
        with self.assertRaises(TypeError):
            signer.match_protect("/private/", "not-a-list")

    # -----------------------------------------------------------------------

    def test_sign_and_verify_round_trip(self):
        signer = SignedURL()
        signer.configure(self.config)
        signed = signer.sign("/private/page.html", 60)
        path, query = signed.split("?", 1)
        self.assertEqual(path, "/private/page.html")
        self.assertTrue(signer.verify(path, query, 60))

    # -----------------------------------------------------------------------

    def test_sign_not_configured_raises(self):
        signer = SignedURL()
        with self.assertRaises(ValueError):
            signer.sign("/page.html", 60)

    # -----------------------------------------------------------------------

    def test_sign_invalid_path_raises(self):
        signer = SignedURL()
        signer.configure(self.config)
        with self.assertRaises(ValueError):
            signer.sign("", 60)

    # -----------------------------------------------------------------------

    def test_sign_invalid_ttl_raises(self):
        signer = SignedURL()
        signer.configure(self.config)
        with self.assertRaises((TypeError, ValueError)):
            signer.sign("/page.html", 0)
        with self.assertRaises(TypeError):
            signer.sign("/page.html", "60")

    # -----------------------------------------------------------------------

    def test_verify_not_configured_raises(self):
        signer = SignedURL()
        with self.assertRaises(ValueError):
            signer.verify("/page.html", "ts=1&sig=abc", 60)

    # -----------------------------------------------------------------------

    def test_verify_wrong_types_raise(self):
        signer = SignedURL()
        signer.configure(self.config)
        with self.assertRaises(TypeError):
            signer.verify(123, "", 60)
        with self.assertRaises(TypeError):
            signer.verify("/page.html", 123, 60)

    # -----------------------------------------------------------------------

    def test_verify_missing_query_params(self):
        signer = SignedURL()
        signer.configure(self.config)
        self.assertFalse(signer.verify("/page.html", "", 60))
        self.assertFalse(signer.verify("/page.html", "ts=123", 60))
        self.assertFalse(signer.verify("/page.html", "sig=abc", 60))

    # -----------------------------------------------------------------------

    def test_verify_malformed_timestamp(self):
        signer = SignedURL()
        signer.configure(self.config)
        self.assertFalse(signer.verify("/page.html", "ts=notanumber&sig=abc", 60))

    # -----------------------------------------------------------------------

    def test_verify_tampered_signature(self):
        signer = SignedURL()
        signer.configure(self.config)
        signed = signer.sign("/private/page.html", 60)
        path, query = signed.split("?", 1)
        tampered_query = query[:-1] + ("0" if query[-1] != "0" else "1")
        self.assertFalse(signer.verify(path, tampered_query, 60))

    # -----------------------------------------------------------------------

    def test_verify_tampered_path(self):
        signer = SignedURL()
        signer.configure(self.config)
        signed = signer.sign("/private/page.html", 60)
        _, query = signed.split("?", 1)
        self.assertFalse(signer.verify("/private/other.html", query, 60))

    # -----------------------------------------------------------------------

    def test_verify_expired(self):
        signer = SignedURL()
        signer.configure(self.config)
        real_time = time.time
        try:
            time.time = lambda: real_time() - 120
            signed = signer.sign("/private/page.html", 60)
        finally:
            time.time = real_time
        path, query = signed.split("?", 1)
        self.assertFalse(signer.verify(path, query, 60))

    # -----------------------------------------------------------------------

    def test_verify_future_timestamp_rejected(self):
        signer = SignedURL()
        signer.configure(self.config)
        real_time = time.time
        try:
            time.time = lambda: real_time() + 120
            signed = signer.sign("/private/page.html", 60)
        finally:
            time.time = real_time
        path, query = signed.split("?", 1)
        self.assertFalse(signer.verify(path, query, 60))

    # -----------------------------------------------------------------------

    def test_load_missing_file_raises(self):
        signer = SignedURL()
        with self.assertRaises(IOError):
            signer.load("/no/such/file.json")

    # -----------------------------------------------------------------------

    def test_load_invalid_argument_types_raise(self):
        signer = SignedURL()
        with self.assertRaises((TypeError, ValueError)):
            signer.load(123)

    # -----------------------------------------------------------------------

    def test_load_json_file(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"WhakerPy": self.config}, f)
        try:
            signer = SignedURL()
            settings = signer.load(path)
            self.assertEqual(settings["ttl"], 60)
            signed = signer.sign("/private/page.html", 60)
            path_part, query = signed.split("?", 1)
            self.assertTrue(signer.verify(path_part, query, 60))
        finally:
            os.remove(path)

    # -----------------------------------------------------------------------

    def test_load_json_file_invalid_json_raises(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("{not valid json")
        try:
            signer = SignedURL()
            with self.assertRaises(ValueError):
                signer.load(path)
        finally:
            os.remove(path)

    # -----------------------------------------------------------------------

    def test_load_json_file_missing_whakerpy_section_raises(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(self.config, f)
        try:
            signer = SignedURL()
            with self.assertRaises(KeyError):
                signer.load(path)
        finally:
            os.remove(path)

    # -----------------------------------------------------------------------

    def test_load_json_file_whakerpy_not_a_dict_raises(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"WhakerPy": ["not", "a", "dict"]}, f)
        try:
            signer = SignedURL()
            with self.assertRaises(TypeError):
                signer.load(path)
        finally:
            os.remove(path)

    # -----------------------------------------------------------------------

    def test_check_ttl_seconds(self):
        with self.assertRaises(TypeError):
            SignedURL.check_ttl_seconds("60")
        with self.assertRaises(ValueError):
            SignedURL.check_ttl_seconds(0)
        with self.assertRaises(ValueError):
            SignedURL.check_ttl_seconds(-1)
        SignedURL.check_ttl_seconds(60)  # no raise

    # -----------------------------------------------------------------------

    def test_check_non_empty_string(self):
        with self.assertRaises(TypeError):
            SignedURL.check_non_empty_string(123)
        with self.assertRaises(ValueError):
            SignedURL.check_non_empty_string("")
        SignedURL.check_non_empty_string("ok")  # no raise

    # -----------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
