# Copyright (C) 2011-2014 by the Free Software Foundation, Inc.
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

"""Tests for the subscription service."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'TestJoin',
    'TestSubscriptionWorkflow',
    ]


import uuid
import unittest

from zope.component import getUtility

from mailman.app.lifecycle import create_list
from mailman.app.subscriptions import SubscriptionWorkflow
from mailman.interfaces.address import InvalidEmailAddressError
from mailman.interfaces.subscriptions import (
    MissingUserError, ISubscriptionService)
from mailman.interfaces.mailinglist import SubscriptionPolicy
from mailman.interfaces.usermanager import IUserManager
from mailman.testing.layers import ConfigLayer



class TestJoin(unittest.TestCase):
    layer = ConfigLayer

    def setUp(self):
        self._mlist = create_list('test@example.com')
        self._service = getUtility(ISubscriptionService)

    def test_join_user_with_bogus_id(self):
        # When `subscriber` is a missing user id, an exception is raised.
        with self.assertRaises(MissingUserError) as cm:
            self._service.join('test.example.com', uuid.UUID(int=99))
        self.assertEqual(cm.exception.user_id, uuid.UUID(int=99))

    def test_join_user_with_invalid_email_address(self):
        # When `subscriber` is a string that is not an email address, an
        # exception is raised.
        with self.assertRaises(InvalidEmailAddressError) as cm:
            self._service.join('test.example.com', 'bogus')
        self.assertEqual(cm.exception.email, 'bogus')



class TestSubscriptionWorkflow(unittest.TestCase):
    layer = ConfigLayer

    def setUp(self):
        self._mlist = create_list('test@example.com')
        self._anne = 'anne@example.com'
        self._user_manager = getUtility(IUserManager)

    def test_preverified_address_joins_open_list(self):
        # The mailing list has an open subscription policy, so the subscriber
        # becomes a member with no human intervention.
        self._mlist.subscription_policy = SubscriptionPolicy.open
        anne = self._user_manager.create_address(self._anne, 'Anne Person')
        self.assertIsNone(anne.verified_on)
        self.assertIsNone(anne.user)
        self.assertIsNone(self._mlist.subscribers.get_member(self._anne))
        workflow = SubscriptionWorkflow(
            self._mlist, anne,
            pre_verified=True, pre_confirmed=False, pre_approved=False)
        # Run the state machine to the end.  The result is that her address
        # will be verified, linked to a user, and subscribed to the mailing
        # list.
        list(workflow)
        self.assertIsNotNone(anne.verified_on)
        self.assertIsNotNone(anne.user)
        self.assertIsNotNone(self._mlist.subscribers.get_member(self._anne))
