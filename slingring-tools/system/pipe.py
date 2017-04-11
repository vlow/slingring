# (c) 2017, Florian Engel <florian.engel@turbocache3000.de>
#
# This file is part of Slingring
#
# Slingring is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Slingring is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Slingring.  If not, see <http://www.gnu.org/licenses/>.

########################################################

import threading
import os


class PipeThread(threading.Thread):
    def __init__(self, pipe_path, password):
        """
        This is a simple helper construct which creates a
        named pipe at pipe_path, containing a password.
        This can be used as a somewhat more safe input for
        programs which accept passwords from a file. That way,
        the password is never actually written to the disk.
        After the PipeThread has been created, it must be started
        via the 'run' function.
        :param pipe_path: The path where the pipe should be created.
        :param password: The password which should be the content of the named pipe.
        """
        threading.Thread.__init__(self)
        self.pipe_path = pipe_path
        self.password = password

    def run(self):
        """
        Starts the thread.
        """
        os.mkfifo(self.pipe_path)
        with open(self.pipe_path, 'w') as pipe:
            pipe.write(self.password)
