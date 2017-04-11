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

from random import SystemRandom
import string


def create_random_password(length):
    """
    Creates a random password string with the given length.
    :param length: the password string length
    :return: a random password string
    """
    alphabet = string.ascii_letters + string.digits
    rng = SystemRandom()
    return ''.join(rng.choice(alphabet) for i in range(length))
