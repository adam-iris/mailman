# Copyright (C) 2009-2014 by the Free Software Foundation, Inc.
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

"""Start the administrative HTTP server."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'RESTRunner',
    ]


import signal
import logging
import threading

from mailman.core.runner import Runner
from mailman.rest.wsgiapp import make_server


log = logging.getLogger('mailman.http')



class RESTRunner(Runner):
    # Don't install the standard signal handlers because as defined, they
    # won't actually stop the TCPServer started by .serve_forever().
    is_queue_runner = False

    def __init__(self, name, slice=None):
        """See `IRunner`."""
        super(RESTRunner, self).__init__(name, slice)
        # Both the REST server and the signal handlers must run in the main
        # thread; the former because of SQLite requirements (objects created
        # in one thread cannot be shared with the other threads), and the
        # latter because of Python's signal handling semantics.
        #
        # Unfortunately, we cannot issue a TCPServer shutdown in the main
        # thread, because that will cause a deadlock.  Yay.   So what we do is
        # to use the signal handler to notify a shutdown thread that the
        # shutdown should happen.  That thread will wake up and stop the main
        # server.
        self._server = make_server()
        self._event = threading.Event()
        def stopper(event, server):
            event.wait()
            server.shutdown()
        self._thread = threading.Thread(
            target=stopper, args=(self._event, self._server))
        self._thread.start()

    def run(self):
        """See `IRunner`."""
        self._server.serve_forever()

    def signal_handler(self, signum, frame):
        super(RESTRunner, self).signal_handler(signum, frame)
        if signum in (signal.SIGTERM, signal.SIGINT, signal.SIGUSR1):
            # Set the flag that will terminate the TCPserver loop.
            self._event.set()

    def _one_iteration(self):
        # Just keep going
        if self._thread.is_alive():
            self._thread.join(timeout=0.1)
        return 1

    def _snooze(self, filecnt):
        pass
