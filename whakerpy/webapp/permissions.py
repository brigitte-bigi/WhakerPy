"""
:filename: whakerpy.webapp.permissions.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Check file permissions.

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

import os
import stat
try:
    import grp
except ImportError:
    # grp will be None if the module is unavailable
    grp = None

# ---------------------------------------------------------------------------


class FileAccessChecker:
    """Specialized class for checking file permissions on a specified file.

    This class provides methods to check if a user, group, or owner has specific
    access rights to a given file, such as read permissions.

    :example:
    >>> checker = FileAccessChecker('/path/to/file')
    >>> checker.read_allowed(who='owner')
    True
    >>> checker.read_allowed(who='group')
    False

    """

    def __init__(self, filename: str):
        """Initialize the FileAccessChecker with a specific file.

        The initialization ensures that the system supports group-related
        functionalities by checking for the availability of the 'grp' module.

        :param filename: (str) Path to the file to check.
        :raises: EnvironmentError: If 'grp' module is not available.
                 FileNotFoundError: If the file does not exist.

        """
        if grp is None:
            raise EnvironmentError("The 'grp' module is not available on this platform.")
        self.__filename = filename

        # Check if the file exists, raise an error if not
        if os.path.exists(self.__filename) is False:
            raise FileNotFoundError(f"File not found: {self.__filename}")

        # Get the file's status
        self.__file_stat = os.stat(self.__filename)

    # -----------------------------------------------------------------------

    def read_allowed(self, who: str = "others") -> bool:
        """Check if the given persons has read permission on the file.

        :param who: (str) Who to check permissions for: 'others', 'group', or 'owner'.
                    Defaults to 'others'.
        :return: (bool) True if read permission is granted, False otherwise.

        :raises: ValueError: If 'who' is invalid.

        """
        if who not in ["others", "group", "owner"]:
            raise ValueError("Invalid 'who' value. Must be 'others', 'group', or 'owner'.")

        # Get the current process user's ID and group ID
        current_uid = os.geteuid()  # Effective user ID of the current process
        current_gid = os.getegid()  # Effective group ID of the current process

        # Check owner, group, and others' permissions
        mode = self.__file_stat.st_mode
        owner_uid = self.__file_stat.st_uid
        group_gid = self.__file_stat.st_gid

        # Determine read permission based on 'who'
        if who == "owner" and current_uid == owner_uid:
            return bool(mode & stat.S_IRUSR)  # Owner read permission
        elif who == "group" and current_gid == group_gid:
            return bool(mode & stat.S_IRGRP)  # Group read permission
        elif who == "others":  # 'others' could be any user (owner, group, others)
            return bool(mode & stat.S_IROTH)  # Others' read permission
        return False

