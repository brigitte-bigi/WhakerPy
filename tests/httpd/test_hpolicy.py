"""
:filename: tests.httpd.test_hpolicy.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests for the HTTPDPolicy in package httpd.

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

from whakerpy.httpd.hpolicy import HTTPDPolicy
from whakerpy.httpd.hsignedurl import SignedURL

# ---------------------------------------------------------------------------


class TestHTTPDPolicy(unittest.TestCase):

    def setUp(self):
        self.policy = HTTPDPolicy()

    # -----------------------------------------------------------------------

    def test_configure_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            self.policy.configure("not-a-dict")

    # -----------------------------------------------------------------------

    def test_configure_empty_disables_all(self):
        self.policy.configure({})
        allowed, content, status, mime_type = self.policy.check("/anything", "", {})
        self.assertTrue(allowed)
        self.assertIsNone(content)
        self.assertIsNone(status)
        self.assertIsNone(mime_type)

    # -----------------------------------------------------------------------

    def test_check_wrong_types_raise(self):
        self.policy.configure({})
        with self.assertRaises(TypeError):
            self.policy.check(123, "", {})
        with self.assertRaises(TypeError):
            self.policy.check("/page.html", 123, {})

    # -----------------------------------------------------------------------

    def test_check_blacklisted_path(self):
        self.policy.configure({"blacklist": ["/admin"]})
        allowed, content, status, mime_type = self.policy.check("/admin/panel", "", {})
        self.assertFalse(allowed)
        self.assertEqual(status.code, 418)
        self.assertEqual(mime_type, "text/html")
        self.assertIsInstance(content, bytes)

    # -----------------------------------------------------------------------

    def test_check_blacklisted_user_agent(self):
        self.policy.configure({"blacklist": ["EvilBot"]})
        allowed, content, status, mime_type = self.policy.check(
            "/page.html", "", {"User-Agent": "Mozilla/5.0 EvilBot/1.0"})
        self.assertFalse(allowed)
        self.assertEqual(status.code, 418)

    # -----------------------------------------------------------------------

    def test_check_not_blacklisted(self):
        self.policy.configure({"blacklist": ["/admin"]})
        allowed, content, status, mime_type = self.policy.check("/index.html", "", {})
        self.assertTrue(allowed)
        self.assertIsNone(content)

    # -----------------------------------------------------------------------

    def test_check_signed_url_required_and_missing(self):
        self.policy.configure({
            "signed_url": {
                "secret": "s3cr3t",
                "ttl": 60,
                "protect": [{"prefix": "/private/", "suffix": ""}],
                "query_keys": {"ts": "ts", "sig": "sig"}
            }
        })
        allowed, content, status, mime_type = self.policy.check("/private/doc.html", "", {})
        self.assertFalse(allowed)
        self.assertEqual(status.code, 404)
        self.assertEqual(mime_type, "text/html")

    # -----------------------------------------------------------------------

    def test_check_signed_url_valid(self):
        cfg = {
            "signed_url": {
                "secret": "s3cr3t",
                "ttl": 60,
                "protect": [{"prefix": "/private/", "suffix": ""}],
                "query_keys": {"ts": "ts", "sig": "sig"}
            }
        }
        self.policy.configure(cfg)
        signer = SignedURL()
        signer.configure(cfg)
        signed = signer.sign("/private/doc.html", 60)
        path, query = signed.split("?", 1)
        allowed, content, status, mime_type = self.policy.check(path, query, {})
        self.assertTrue(allowed)
        self.assertIsNone(content)

    # -----------------------------------------------------------------------

    def test_check_signed_url_unprotected_path_ignored(self):
        self.policy.configure({
            "signed_url": {
                "secret": "s3cr3t",
                "ttl": 60,
                "protect": [{"prefix": "/private/", "suffix": ""}],
                "query_keys": {"ts": "ts", "sig": "sig"}
            }
        })
        allowed, content, status, mime_type = self.policy.check("/public/doc.html", "", {})
        self.assertTrue(allowed)

    # -----------------------------------------------------------------------

    def test_finalize_html_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            self.policy.finalize_html("not-bytes")

    # -----------------------------------------------------------------------

    def test_finalize_html_disabled_returns_unchanged(self):
        self.policy.configure({})
        content = b'<a href="/private/doc.html">doc</a>'
        self.assertEqual(self.policy.finalize_html(content), content)

    # -----------------------------------------------------------------------

    def test_finalize_html_no_protect_returns_unchanged(self):
        self.policy.configure({
            "signed_url": {
                "secret": "s3cr3t", "ttl": 60, "protect": [],
                "query_keys": {"ts": "ts", "sig": "sig"}
            }
        })
        content = b'<a href="/private/doc.html">doc</a>'
        self.assertEqual(self.policy.finalize_html(content), content)

    # -----------------------------------------------------------------------

    def test_finalize_html_signs_protected_links(self):
        self.policy.configure({
            "signed_url": {
                "secret": "s3cr3t", "ttl": 60,
                "protect": [{"prefix": "/private/", "suffix": ""}],
                "query_keys": {"ts": "ts", "sig": "sig"}
            }
        })
        content = b'<a href="/private/doc.html">doc</a>'
        result = self.policy.finalize_html(content).decode("utf-8")
        self.assertIn("ts=", result)
        self.assertIn("sig=", result)

    # -----------------------------------------------------------------------

    def test_finalize_html_signs_action_attribute(self):
        self.policy.configure({
            "signed_url": {
                "secret": "s3cr3t", "ttl": 60,
                "protect": [{"prefix": "/private/", "suffix": ""}],
                "query_keys": {"ts": "ts", "sig": "sig"}
            }
        })
        content = b'<form action="/private/submit.html"></form>'
        result = self.policy.finalize_html(content).decode("utf-8")
        self.assertIn("ts=", result)

    # -----------------------------------------------------------------------

    def test_finalize_html_skips_unprotected_links(self):
        self.policy.configure({
            "signed_url": {
                "secret": "s3cr3t", "ttl": 60,
                "protect": [{"prefix": "/private/", "suffix": ""}],
                "query_keys": {"ts": "ts", "sig": "sig"}
            }
        })
        content = b'<a href="/public/doc.html">doc</a>'
        result = self.policy.finalize_html(content).decode("utf-8")
        self.assertEqual(result, '<a href="/public/doc.html">doc</a>')

    # -----------------------------------------------------------------------

    def test_finalize_html_skips_special_link_schemes(self):
        self.policy.configure({
            "signed_url": {
                "secret": "s3cr3t", "ttl": 60,
                "protect": [{"prefix": "", "suffix": ""}],
                "query_keys": {"ts": "ts", "sig": "sig"}
            }
        })
        cases = [
            '<a href="#anchor">a</a>',
            '<a href="https://example.org/private/">a</a>',
            '<a href="mailto:me@example.org">a</a>',
            '<a href="javascript:void(0)">a</a>',
            '<a href="data:text/plain,hi">a</a>',
            '<a href="">a</a>',
        ]
        for html in cases:
            content = html.encode("utf-8")
            self.assertEqual(self.policy.finalize_html(content).decode("utf-8"), html)

    # -----------------------------------------------------------------------

    def test_finalize_html_does_not_resign_already_signed_link(self):
        self.policy.configure({
            "signed_url": {
                "secret": "s3cr3t", "ttl": 60,
                "protect": [{"prefix": "/private/", "suffix": ""}],
                "query_keys": {"ts": "ts", "sig": "sig"}
            }
        })
        content = b'<a href="/private/doc.html?ts=1&sig=abc">doc</a>'
        result = self.policy.finalize_html(content).decode("utf-8")
        self.assertEqual(result, '<a href="/private/doc.html?ts=1&sig=abc">doc</a>')

    # -----------------------------------------------------------------------

    def test_finalize_html_preserves_extra_query_params(self):
        self.policy.configure({
            "signed_url": {
                "secret": "s3cr3t", "ttl": 60,
                "protect": [{"prefix": "/private/", "suffix": ""}],
                "query_keys": {"ts": "ts", "sig": "sig"}
            }
        })
        content = b'<a href="/private/doc.html?lang=fr">doc</a>'
        result = self.policy.finalize_html(content).decode("utf-8")
        self.assertIn("lang=fr", result)
        self.assertIn("ts=", result)
        self.assertIn("sig=", result)

    # -----------------------------------------------------------------------

    def test_get_user_agent_from_http_server_headers(self):
        ua = self.policy._get_user_agent({"User-Agent": "Mozilla/5.0"})
        self.assertEqual(ua, "Mozilla/5.0")

    # -----------------------------------------------------------------------

    def test_get_user_agent_from_wsgi_environ(self):
        ua = self.policy._get_user_agent({"HTTP_USER_AGENT": "Mozilla/5.0"})
        self.assertEqual(ua, "Mozilla/5.0")

    # -----------------------------------------------------------------------

    def test_get_user_agent_none_headers(self):
        self.assertEqual(self.policy._get_user_agent(None), "")

    # -----------------------------------------------------------------------

    def test_get_user_agent_missing(self):
        self.assertEqual(self.policy._get_user_agent({}), "")

    # -----------------------------------------------------------------------

    def test_get_user_agent_object_without_get_returns_empty(self):
        self.assertEqual(self.policy._get_user_agent(object()), "")

    # -----------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
