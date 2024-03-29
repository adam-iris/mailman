# Copyright (C) 2006-2014 by the Free Software Foundation, Inc.
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

"""Model for preferences."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'Preferences',
    ]


from sqlalchemy import Boolean, Column, Integer, Unicode
from zope.component import getUtility
from zope.interface import implementer

from mailman.database.model import Model
from mailman.database.types import Enum
from mailman.interfaces.languages import ILanguageManager
from mailman.interfaces.member import DeliveryMode, DeliveryStatus
from mailman.interfaces.preferences import IPreferences



@implementer(IPreferences)
class Preferences(Model):
    """See `IPreferences`."""

    __tablename__ = 'preferences'

    id = Column(Integer, primary_key=True)
    acknowledge_posts = Column(Boolean)
    hide_address = Column(Boolean)
    _preferred_language = Column('preferred_language', Unicode)
    receive_list_copy = Column(Boolean)
    receive_own_postings = Column(Boolean)
    delivery_mode = Column(Enum(DeliveryMode))
    delivery_status = Column(Enum(DeliveryStatus))

    def __repr__(self):
        return '<Preferences object at {0:#x}>'.format(id(self))

    @property
    def preferred_language(self):
        if self._preferred_language is None:
            return None
        return getUtility(ILanguageManager)[self._preferred_language]

    @preferred_language.setter
    def preferred_language(self, language):
        if language is None:
            self._preferred_language = None
        # Accept both a language code and a `Language` instance.
        try:
            self._preferred_language = language.code
        except AttributeError:
            self._preferred_language = language
