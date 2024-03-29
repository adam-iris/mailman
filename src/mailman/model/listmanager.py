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

"""A mailing list manager."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'ListManager',
    ]


from zope.event import notify
from zope.interface import implementer

from mailman.database.transaction import dbconnection
from mailman.interfaces.address import InvalidEmailAddressError
from mailman.interfaces.listmanager import (
    IListManager, ListAlreadyExistsError, ListCreatedEvent, ListCreatingEvent,
    ListDeletedEvent, ListDeletingEvent)
from mailman.model.mailinglist import MailingList
from mailman.model.mime import ContentFilter
from mailman.utilities.datetime import now



@implementer(IListManager)
class ListManager:
    """An implementation of the `IListManager` interface."""

    @dbconnection
    def create(self, store, fqdn_listname):
        """See `IListManager`."""
        fqdn_listname = fqdn_listname.lower()
        listname, at, hostname = fqdn_listname.partition('@')
        if len(hostname) == 0:
            raise InvalidEmailAddressError(fqdn_listname)
        list_id = '{0}.{1}'.format(listname, hostname)
        notify(ListCreatingEvent(fqdn_listname))
        mlist = store.query(MailingList).filter_by(_list_id=list_id).first()
        if mlist:
            raise ListAlreadyExistsError(fqdn_listname)
        mlist = MailingList(fqdn_listname)
        mlist.created_at = now()
        store.add(mlist)
        notify(ListCreatedEvent(mlist))
        return mlist

    @dbconnection
    def get(self, store, fqdn_listname):
        """See `IListManager`."""
        listname, at, hostname = fqdn_listname.partition('@')
        list_id = '{0}.{1}'.format(listname, hostname)
        return store.query(MailingList).filter_by(_list_id=list_id).first()

    @dbconnection
    def get_by_list_id(self, store, list_id):
        """See `IListManager`."""
        return store.query(MailingList).filter_by(_list_id=list_id).first()

    @dbconnection
    def delete(self, store, mlist):
        """See `IListManager`."""
        fqdn_listname = mlist.fqdn_listname
        notify(ListDeletingEvent(mlist))
        store.query(ContentFilter).filter_by(mailing_list=mlist).delete()
        store.delete(mlist)
        notify(ListDeletedEvent(fqdn_listname))

    @property
    @dbconnection
    def mailing_lists(self, store):
        """See `IListManager`."""
        for mlist in store.query(MailingList).order_by(
                MailingList._list_id).all():
            yield mlist

    @dbconnection
    def __iter__(self, store):
        """See `IListManager`."""
        for mlist in store.query(MailingList).all():
            yield mlist

    @property
    @dbconnection
    def names(self, store):
        """See `IListManager`."""
        result_set = store.query(MailingList)
        for mail_host, list_name in result_set.values(MailingList.mail_host,
                                                      MailingList.list_name):
            yield '{0}@{1}'.format(list_name, mail_host)

    @property
    @dbconnection
    def list_ids(self, store):
        """See `IListManager`."""
        result_set = store.query(MailingList)
        for list_id in result_set.values(MailingList._list_id):
            assert isinstance(list_id, tuple) and len(list_id) == 1
            yield list_id[0]

    @property
    @dbconnection
    def name_components(self, store):
        """See `IListManager`."""
        result_set = store.query(MailingList)
        for mail_host, list_name in result_set.values(MailingList.mail_host,
                                                      MailingList.list_name):
            yield list_name, mail_host
