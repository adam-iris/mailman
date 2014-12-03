# Copyright (C) 2012-2014 by the Free Software Foundation, Inc.
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

"""Test notifications."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    ]


import os
import shutil
import tempfile
import unittest

from zope.component import getUtility

from mailman.app.lifecycle import create_list
from mailman.config import config
from mailman.interfaces.languages import ILanguageManager
from mailman.interfaces.member import MemberRole
from mailman.interfaces.usermanager import IUserManager
from mailman.testing.helpers import get_queue_messages, subscribe, subscribe_ex
from mailman.testing.layers import ConfigLayer



class TestNotifications(unittest.TestCase):
    """Test notifications."""

    layer = ConfigLayer
    maxDiff = None

    def setUp(self):
        self._mlist = create_list('test@example.com')
        self._mlist.welcome_message_uri = 'mailman:///welcome.txt'
        self._mlist.display_name = 'Test List'
        self.var_dir = tempfile.mkdtemp()
        config.push('template config', """\
        [paths.testing]
        template_dir: {0}/templates
        """.format(self.var_dir))
        # Populate the template directories with a few fake templates.
        path = os.path.join(self.var_dir, 'templates', 'site', 'en')
        os.makedirs(path)
        with open(os.path.join(path, 'welcome.txt'), 'w') as fp:
            print("""\
Welcome to the $list_name mailing list.

    Posting address: $fqdn_listname
    Help and other requests: $list_requests
    Your name: $user_name
    Your address: $user_address
    Your options: $user_options_uri""", file=fp)
        # Write a list-specific welcome message.
        path = os.path.join(self.var_dir, 'templates', 'lists',
                            'test@example.com', 'xx')
        os.makedirs(path)
        with open(os.path.join(path, 'welcome.txt'), 'w') as fp:
            print('You just joined the $list_name mailing list!', file=fp)
        # Let assertMultiLineEqual work without bounds.
        self.maxDiff = None

    def tearDown(self):
        config.pop('template config')
        shutil.rmtree(self.var_dir)

    def test_welcome_message(self):
        subscribe(self._mlist, 'Anne', email='anne@example.com')
        # Now there's one message in the virgin queue.
        messages = get_queue_messages('virgin')
        self.assertEqual(len(messages), 1)
        message = messages[0].msg
        self.assertEqual(str(message['subject']),
                         'Welcome to the "Test List" mailing list')
        self.assertMultiLineEqual(message.get_payload(), """\
Welcome to the Test List mailing list.

    Posting address: test@example.com
    Help and other requests: test-request@example.com
    Your name: Anne Person
    Your address: anne@example.com
    Your options: http://example.com/anne@example.com
""")

    def test_more_specific_welcome_message_nonenglish(self):
        # mlist.welcome_message_uri can contain placeholders for the fqdn list
        # name and language.
        self._mlist.welcome_message_uri = (
            'mailman:///$listname/$language/welcome.txt')
        # Add the xx language and subscribe Anne using it.
        manager = getUtility(ILanguageManager)
        manager.add('xx', 'us-ascii', 'Xlandia')
        # We can't use the subscribe_ex() helper because that would send the
        # welcome message before we set the member's preferred language.
        address = getUtility(IUserManager).create_address(
            'anne@example.com', 'Anne Person')
        address.preferences.preferred_language = 'xx'
        self._mlist.subscribe(address)
        # Now there's one message in the virgin queue.
        messages = get_queue_messages('virgin')
        self.assertEqual(len(messages), 1)
        message = messages[0].msg
        self.assertEqual(str(message['subject']),
                         'Welcome to the "Test List" mailing list')
        self.assertMultiLineEqual(
            message.get_payload(),
            'You just joined the Test List mailing list!')

    def test_no_welcome_message_to_owners(self):
        # Welcome messages go only to mailing list members, not to owners.
        member = subscribe_ex(
            self._mlist, 'Anne', MemberRole.owner, email='anne@example.com')
        member.preferences.preferred_language = 'xx'
        # There is no welcome message in the virgin queue.
        messages = get_queue_messages('virgin')
        self.assertEqual(len(messages), 0)

    def test_no_welcome_message_to_nonmembers(self):
        # Welcome messages go only to mailing list members, not to nonmembers.
        member = subscribe_ex(
            self._mlist, 'Anne', MemberRole.nonmember,
            email='anne@example.com')
        member.preferences.preferred_language = 'xx'
        # There is no welcome message in the virgin queue.
        messages = get_queue_messages('virgin')
        self.assertEqual(len(messages), 0)

    def test_no_welcome_message_to_moderators(self):
        # Welcome messages go only to mailing list members, not to moderators.
        member = subscribe_ex(
            self._mlist, 'Anne', MemberRole.moderator,
            email='anne@example.com')
        member.preferences.preferred_language = 'xx'
        # There is no welcome message in the virgin queue.
        messages = get_queue_messages('virgin')
        self.assertEqual(len(messages), 0)
