"""
:filename: tests.webapp.test_permissions.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests file permissions checker.

.. _This file is part of WhakerPy: https://whakerpy.sourceforge.io
..
    -------------------------------------------------------------------------

    Copyright (C) 2023-2024 Brigitte Bigi
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

import tempfile
import unittest
import os
import stat
import sys
from unittest import mock
from unittest.mock import patch

from whakerpy.httpd.permissions import UnixPermissions
from whakerpy.httpd.permissions import FileAccessChecker

# ---------------------------------------------------------------------------

if sys.platform != 'win32':

    class TestUnixPermissions(unittest.TestCase):

        def test_owner_property(self):
            p = UnixPermissions()
            self.assertEqual(p.owner, "owner")

        def test_group_property(self):
            p = UnixPermissions()
            self.assertEqual(p.group, "group")

        def test_others_property(self):
            p = UnixPermissions()
            self.assertEqual(p.others, "others")

        def test_contains(self):
            p = UnixPermissions()
            self.assertIn("owner", p)
            self.assertNotIn("some", p)

        def test_iteration_over_roles(self):
            """Test that the UnixPermissions class can be iterated over and returns valid roles."""
            permissions = UnixPermissions()
            expected_roles = ["owner", "group", "others"]
            self.assertEqual(list(permissions), expected_roles)

        def test_is_valid_role(self):
            """Test the is_valid_role method to ensure correct role validation."""
            p = UnixPermissions()
            self.assertTrue(p.is_valid_role("owner"))
            self.assertTrue(p.is_valid_role("group"))
            self.assertTrue(p.is_valid_role("others"))
            self.assertFalse(p.is_valid_role("admin"))  # Invalid role
            self.assertTrue(p.is_valid_role(p.owner))
            self.assertTrue(p.is_valid_role(p.group))
            self.assertTrue(p.is_valid_role(p.others))

        def test_context_manager_enter_exit(self):
            """Test that the context manager works correctly."""
            with UnixPermissions() as permissions:
                self.assertIsInstance(permissions, UnixPermissions)

        def test_context_manager_with_exception(self):
            """Test that the __exit__ method handles exceptions correctly."""
            with self.assertRaises(ValueError):
                with UnixPermissions():
                    raise ValueError("Intentional error")

        def test_exit_does_not_suppress_exception(self):
            """Ensure that exceptions inside the context block are not suppressed."""
            try:
                with UnixPermissions():
                    raise ValueError("An error occurred")
            except ValueError as e:
                self.assertEqual(str(e), "An error occurred")
            else:
                self.fail("Exception not raised")

    # ---------------------------------------------------------------------------


    class TestFileAccessChecker(unittest.TestCase):

        def setUp(self):
            """Set up a mock file and environment before each test."""
            # Create a mock file
            self.mock_filename = '/tmp/mock_file'
            open(self.mock_filename, 'w').close()

            # Mock file permissions and owner details
            self.mock_stat_result = mock.Mock()
            self.mock_stat_result.st_mode = stat.S_IRUSR | stat.S_IRGRP  # Read permissions for owner and group
            self.mock_stat_result.st_uid = os.geteuid()  # Current user is the owner
            self.mock_stat_result.st_gid = os.getegid()  # Current group

            # Patch os.stat to return the mock stat result
            self.patcher_stat = mock.patch('os.stat', return_value=self.mock_stat_result)
            self.mock_stat = self.patcher_stat.start()

        def tearDown(self):
            """Clean up after each test."""
            os.remove(self.mock_filename)
            self.patcher_stat.stop()

        def test_read_allowed_owner(self):
            """Test read permission for the file owner."""
            checker = FileAccessChecker(self.mock_filename)
            self.assertTrue(checker.read_allowed(who="owner"))

        def test_read_allowed_group(self):
            """Test read permission for the group."""
            checker = FileAccessChecker(self.mock_filename)
            self.assertTrue(checker.read_allowed(who="group"))

        def test_read_allowed_user_no_permissions(self):
            """Test read permission for a generic user without explicit rights."""
            # Mock file permissions: no read for group or others
            self.mock_stat_result.st_mode = stat.S_IRUSR  # Only owner has read permissions
            self.mock_stat_result.st_uid = os.geteuid()  # Current user is the owner
            self.mock_stat_result.st_gid = os.getegid()  # Current group

            checker = FileAccessChecker(self.mock_filename)

            # Patch getegid and geteuid to simulate a different user
            with mock.patch('os.getegid', return_value=-1), mock.patch('os.geteuid', return_value=-1):
                self.assertFalse(checker.read_allowed(who="others"))

        def test_invalid_who_argument(self):
            """Test passing an invalid value for the 'who' parameter."""
            checker = FileAccessChecker(self.mock_filename)
            with self.assertRaises(ValueError):
                checker.read_allowed(who="invalid")

        @mock.patch('os.path.exists', return_value=False)
        def test_file_not_found(self, mock_exists):
            """Test behavior when the file does not exist."""
            with self.assertRaises(FileNotFoundError):
                FileAccessChecker('/invalid/file/path')

        @mock.patch('os.path.exists', return_value=False)
        def test_grp_module_absent(self, mock_exists):
            """Test behavior when 'grp' module is unavailable."""
            with mock.patch('whakerpy.httpd.permissions.grp', None):
                with self.assertRaises(EnvironmentError):
                    FileAccessChecker(self.mock_filename)

        # -----------------------------------------------------------------------

        @patch("os.geteuid", return_value=1000)  # Mock effective user ID
        @patch("os.getegid", return_value=1000)  # Mock effective group ID
        @patch("os.stat")
        @patch("os.path.exists", return_value=True)
        def test_multiple_roles_check(self, mock_exists, mock_stat, mock_euid, mock_egid):
            # TODO
            return
            # Mock stat object
            mock_stat_result = os.stat_result((
                stat.S_IFREG | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH,  # File mode
                0, 0, 0,  # inode, dev, nlink
                1000,  # UID (owner)
                1000,  # GID (group)
                0, 0, 0, 0, 0  # atime, mtime, ctime, etc.
            ))
            mock_stat.return_value = mock_stat_result

            # Instance of FileAccessChecker for a valid file
            checker = FileAccessChecker("/path/to/file")

            # Test 'owner&group' - Should be True since both have read permission
            self.assertTrue(checker.read_allowed("owner&group"))

            # Test 'owner|others' - Should be True since at least 'others' has read permission
            self.assertTrue(checker.read_allowed("owner|others"))

            # Test 'group&others' - Should be True since both 'group' and 'others' have read permission
            self.assertTrue(checker.read_allowed("group&others"))

            # Test 'owner&group&others' - Should be True since all three have read permission
            self.assertTrue(checker.read_allowed("owner&group&others"))

            # Test 'owner&nonexistent' - Should raise ValueError due to invalid role
            with self.assertRaises(ValueError):
                checker.read_allowed("owner&nonexistent")

            # Test 'group&others|owner' - Complex case, should be True (group & others are True, owner OR is True)
            self.assertTrue(checker.read_allowed("group&others|owner"))

    # ---------------------------------------------------------------------------


    class TestIntegrationFileAccessChecker(unittest.TestCase):

        def test_read_allowed(self):
            """Test real file permissions for a generic user without explicit rights."""
            p = UnixPermissions()
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                filename = tmp_file.name

            try:
                # Change permissions to allow read for owner only, but deny for group and others
                # S_IRUSR : Read permission for the owner.
                # S_IRGRP : Read permission for the group.
                # S_IROTH : Read permission for others (i.e., users who are neither the owner nor in the group).
                os.chmod(filename, stat.S_IRUSR)  # Owner only can read, deny others
                checker = FileAccessChecker(filename)
                self.assertTrue(checker.read_allowed(who="owner"))
                self.assertFalse(checker.read_allowed(who="group"))
                self.assertFalse(checker.read_allowed(who="others"))
                self.assertTrue(checker.read_allowed(who=p.owner))
                self.assertFalse(checker.read_allowed(who=p.group))
                self.assertFalse(checker.read_allowed(who=p.others))

                # Change permissions to deny read for others
                os.chmod(filename, stat.S_IRGRP)  # read for the group
                checker = FileAccessChecker(filename)
                self.assertTrue(checker.read_allowed(who="group"))
                self.assertFalse(checker.read_allowed(who="others"))
                self.assertTrue(checker.read_allowed(who=p.group))
                self.assertFalse(checker.read_allowed(who=p.others))

            finally:
                os.remove(filename)  # Clean up the file even if the test fails

        # -----------------------------------------------------------------------

        def test_read_allowed_multiple_roles(self):
            p = UnixPermissions()

            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                filename = tmp_file.name

            try:
                os.chmod(filename, stat.S_IRUSR)  # Owner only can read
                checker = FileAccessChecker(filename)
                self.assertTrue(checker.read_allowed(who="owner|group"))
                self.assertTrue(checker.read_allowed(who=f"{p.owner}|group"))
                self.assertTrue(checker.read_allowed(who="owner|others"))
                self.assertTrue(checker.read_allowed(who=f"{p.owner}|{p.others}"))
                self.assertTrue(checker.read_allowed(who="owner|group|others"))
                self.assertFalse(checker.read_allowed(who="owner&group"))
                self.assertFalse(checker.read_allowed(who="owner&others"))

                # Change permissions to deny read for others
                os.chmod(filename, stat.S_IRGRP)  # read for the group only
                checker = FileAccessChecker(filename)
                self.assertTrue(checker.read_allowed(who="owner|group"))
                self.assertFalse(checker.read_allowed(who="owner|others"))
                self.assertTrue(checker.read_allowed(who="owner|group|others"))
                self.assertFalse(checker.read_allowed(who="owner&group"))
                self.assertFalse(checker.read_allowed(who="owner&others"))
                self.assertFalse(checker.read_allowed(who="group&others"))
                self.assertFalse(checker.read_allowed(who="owner&group&others"))

            finally:
                os.remove(filename)  # Clean up the file even if the test fails
