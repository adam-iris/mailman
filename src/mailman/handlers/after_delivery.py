# Copyright (C) 1998-2014 by the Free Software Foundation, Inc.
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

"""Perform some bookkeeping after a successful post."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'AfterDelivery',
    ]


from zope.interface import implementer

from mailman.core.i18n import _
from mailman.interfaces.handler import IHandler
from mailman.utilities.datetime import now



@implementer(IHandler)
class AfterDelivery:
    """Perform some bookkeeping after a successful post."""

    name = 'after-delivery'
    description = _('Perform some bookkeeping after a successful post.')

    def process(self, mlist, msg, msgdata):
        """See `IHander`."""
        mlist.last_post_time = now()
        mlist.post_id += 1
