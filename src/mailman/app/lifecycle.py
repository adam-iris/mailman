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

"""Application level list creation."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'create_list',
    'remove_list',
    ]


import os
import errno
import shutil
import logging

from zope.component import getUtility

from mailman.config import config
from mailman.interfaces.address import IEmailValidator
from mailman.interfaces.domain import (
    BadDomainSpecificationError, IDomainManager)
from mailman.interfaces.listmanager import IListManager
from mailman.interfaces.member import MemberRole
from mailman.interfaces.styles import IStyleManager
from mailman.interfaces.usermanager import IUserManager
from mailman.utilities.modules import call_name


log = logging.getLogger('mailman.error')



def create_list(fqdn_listname, owners=None, style_name=None):
    """Create the named list and apply styles.

    The mailing may not exist yet, but the domain specified in `fqdn_listname`
    must exist.

    :param fqdn_listname: The fully qualified name for the new mailing list.
    :type fqdn_listname: string
    :param owners: The mailing list owners.
    :type owners: list of string email addresses
    :param style_name: The name of the style to apply to the newly created
        list.  If not given, the default is taken from the configuration file.
    :type style_name: string
    :return: The new mailing list.
    :rtype: `IMailingList`
    :raises BadDomainSpecificationError: when the hostname part of
        `fqdn_listname` does not exist.
    :raises ListAlreadyExistsError: when the mailing list already exists.
    :raises InvalidEmailAddressError: when the fqdn email address is invalid.
    """
    if owners is None:
        owners = []
    # This raises InvalidEmailAddressError if the address is not a valid
    # posting address.  Let these percolate up.
    getUtility(IEmailValidator).validate(fqdn_listname)
    listname, domain = fqdn_listname.split('@', 1)
    if domain not in getUtility(IDomainManager):
        raise BadDomainSpecificationError(domain)
    mlist = getUtility(IListManager).create(fqdn_listname)
    style = getUtility(IStyleManager).get(
        config.styles.default if style_name is None else style_name)
    if style is not None:
        style.apply(mlist)
    # Coordinate with the MTA, as defined in the configuration file.
    call_name(config.mta.incoming).create(mlist)
    # Create any owners that don't yet exist, and subscribe all addresses as
    # owners of the mailing list.
    user_manager = getUtility(IUserManager)
    for owner_address in owners:
        address = user_manager.get_address(owner_address)
        if address is None:
            user = user_manager.create_user(owner_address)
            address = list(user.addresses)[0]
        mlist.subscribe(address, MemberRole.owner)
    return mlist



def remove_list(mlist):
    """Remove the list and all associated artifacts and subscriptions."""
    fqdn_listname = mlist.fqdn_listname
    # Delete the mailing list from the database.
    getUtility(IListManager).delete(mlist)
    # Do the MTA-specific list deletion tasks
    call_name(config.mta.incoming).delete(mlist)
    # Remove the list directory, if it exists.
    try:
        shutil.rmtree(os.path.join(config.LIST_DATA_DIR, fqdn_listname))
    except OSError as error:
        if error.errno != errno.ENOENT:
            raise
