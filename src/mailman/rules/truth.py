# Copyright (C) 2008-2014 by the Free Software Foundation, Inc.
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

"""A rule which always matches."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'Truth',
    ]


from zope.interface import implementer

from mailman.core.i18n import _
from mailman.interfaces.rules import IRule



@implementer(IRule)
class Truth:
    """Look for any previous rule match."""

    name = 'truth'
    description = _('A rule which always matches.')
    record = False

    def check(self, mlist, msg, msgdata):
        """See `IRule`."""
        return True
