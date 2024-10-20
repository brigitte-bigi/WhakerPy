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
from unittest import mock

from whakerpy.webapp.permissions import FileAccessChecker


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
        with mock.patch('whakerpy.webapp.permissions.grp', None):
            with self.assertRaises(EnvironmentError):
                FileAccessChecker(self.mock_filename)

    def test_integration_read_allowed_user_no_permissions(self):
        """Test real file permissions for a generic user without explicit rights."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            filename = tmp_file.name

        try:
            # Change permissions to allow read for owner only, but deny for group and others
            os.chmod(filename, stat.S_IRGRP)  # Owner only can read
            checker = FileAccessChecker(filename)
            self.assertFalse(checker.read_allowed(who="others"))  # Test for non-owner user permissions
        finally:
            os.remove(filename)  # Clean up the file even if the test fails

    def test_integration_read_allowed_others_no_permissions(self):
        """Test real file permissions for others without explicit rights."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            filename = tmp_file.name

        try:
            # Change permissions to deny read for others
            # S_IRUSR : Read permission for the owner.
            # S_IRGRP : Read permission for the group.
            # S_IROTH : Read permission for others (i.e., users who are neither the owner nor in the group).
            os.chmod(filename, stat.S_IRUSR)  # Owner only can read, deny others

            checker = FileAccessChecker(filename)
            self.assertFalse(checker.read_allowed(who="others"))  # Test for non-owner user
        finally:
            os.remove(filename)  # Clean up the file
