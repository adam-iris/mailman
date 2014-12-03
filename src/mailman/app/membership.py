# Copyright (C) 2007-2014 by the Free Software Foundation, Inc.
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

"""Application support for membership management."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'add_member',
    'delete_member',
    'handle_SubscriptionEvent',
    ]


from email.utils import formataddr
from zope.component import getUtility

from mailman.app.notifications import (
    send_goodbye_message, send_welcome_message)
from mailman.core.i18n import _
from mailman.email.message import OwnerNotification
from mailman.interfaces.bans import IBanManager
from mailman.interfaces.member import (
    MemberRole, MembershipIsBannedError, NotAMemberError, SubscriptionEvent)
from mailman.interfaces.usermanager import IUserManager
from mailman.utilities.i18n import make



def add_member(mlist, record, role=MemberRole.member):
    """Add a member right now.

    The member's subscription must be approved by whatever policy the list
    enforces.

    :param mlist: The mailing list to add the member to.
    :type mlist: `IMailingList`
    :param record: a subscription request record.
    :type record: RequestRecord
    :param role: The membership role for this subscription.
    :type role: `MemberRole`
    :return: The just created member.
    :rtype: `IMember`
    :raises AlreadySubscribedError: if the user is already subscribed to
        the mailing list.
    :raises InvalidEmailAddressError: if the email address is not valid.
    :raises MembershipIsBannedError: if the membership is not allowed.
    """
    # Check to see if the email address is banned.
    if IBanManager(mlist).is_banned(record.email):
        raise MembershipIsBannedError(mlist, record.email)
    # Make sure there is a user linked with the given address.
    user_manager = getUtility(IUserManager)
    user = user_manager.make_user(record.email, record.display_name)
    # Encrypt the password using the currently selected hash scheme.
    user.preferences.preferred_language = record.language
    # Subscribe the address, not the user.
    address = user_manager.get_address(record.email)
    if address is None or address.user is not user:
        raise AssertionError(
            'User should have had linked address: {0}'.format(address))
    member = mlist.subscribe(address, role)
    member.preferences.delivery_mode = record.delivery_mode
    # Create the member and set the appropriate preferences.
    member.preferences.preferred_language = record.language
    member.preferences.delivery_mode = record.delivery_mode
    return member



def delete_member(mlist, email, admin_notif=None, userack=None):
    """Delete a member right now.

    :param mlist: The mailing list to remove the member from.
    :type mlist: `IMailingList`
    :param email: The email address to unsubscribe.
    :type email: string
    :param admin_notif: Whether the list administrator should be notified that
        this member was deleted.
    :type admin_notif: bool, or None to let the mailing list's
        `admin_notify_mchange` attribute decide.
    :raises NotAMemberError: if the address is not a member of the
        mailing list.
    """
    if userack is None:
        userack = mlist.send_goodbye_message
    if admin_notif is None:
        admin_notif = mlist.admin_notify_mchanges
    # Delete a member, for which we know the approval has been made.
    member = mlist.members.get_member(email)
    if member is None:
        raise NotAMemberError(mlist, email)
    language = member.preferred_language
    member.unsubscribe()
    # And send an acknowledgement to the user...
    if userack:
        send_goodbye_message(mlist, email, language)
    # ...and to the administrator.
    if admin_notif:
        user = getUtility(IUserManager).get_user(email)
        display_name = user.display_name
        subject = _('$mlist.display_name unsubscription notification')
        text = make('adminunsubscribeack.txt',
                    mailing_list=mlist,
                    listname=mlist.display_name,
                    member=formataddr((display_name, email)),
                    )
        msg = OwnerNotification(mlist, subject, text,
                                roster=mlist.administrators)
        msg.send(mlist)



def handle_SubscriptionEvent(event):
    if not isinstance(event, SubscriptionEvent):
        return
    # Only send a notification message if the mailing list is configured to do
    # so, and the member being added is a list member (as opposed to a
    # moderator, non-member, or owner).
    member = event.member
    if member.role is not MemberRole.member:
        return
    mlist = member.mailing_list
    if not mlist.send_welcome_message:
        return
    send_welcome_message(mlist, member, member.preferred_language)
