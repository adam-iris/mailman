# Copyright (C) 2014 by the Free Software Foundation, Inc.
#
# This file is part of GNU Mailman.
#
# GNU Mailman is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# GNU Mailman is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# GNU Mailman.  If not, see <http://www.gnu.org/licenses/>.

"""Test the user manager."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'TestMakeUser',
    ]


import unittest

from zope.component import getUtility

from mailman.interfaces.usermanager import IUserManager
from mailman.testing.layers import ConfigLayer



class TestMakeUser(unittest.TestCase):
    layer = ConfigLayer

    def setUp(self):
        self._usermanager = getUtility(IUserManager)

    def test_make_new_user(self):
        # Neither the user nor address objects exist yet.
        self.assertIsNone(self._usermanager.get_user('anne@example.com'))
        self.assertIsNone(self._usermanager.get_address('anne@example.com'))
        user = self._usermanager.make_user('anne@example.com', 'Anne Person')
        self.assertIn('anne@example.com',
                      [address.email for address in user.addresses])
        addresses = list(user.addresses)
        self.assertEqual(len(addresses), 1)
        address = addresses[0]
        self.assertEqual(address.email, 'anne@example.com')
        self.assertEqual(address.display_name, 'Anne Person')
        self.assertEqual(address.user.display_name, 'Anne Person')
        self.assertIs(address.user, user)

    def test_make_linked_user(self):
        # The address exists, but there is no linked user.
        self.assertIsNone(self._usermanager.get_user('anne@example.com'))
        address = self._usermanager.create_address('anne@example.com')
        user = self._usermanager.make_user('anne@example.com', 'Anne Person')
        self.assertIsNotNone(address.user)
        self.assertIs(user, address.user)
        self.assertIn(address, user.addresses)
        self.assertEqual(user.display_name, 'Anne Person')

    def test_make_user_exists(self):
        user = self._usermanager.create_user('anne@example.com', 'Anne Person')
        other_user = self._usermanager.make_user('anne@example.com')
        self.assertIs(user, other_user)
