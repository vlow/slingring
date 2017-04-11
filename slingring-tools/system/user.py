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

from os import geteuid
from os import getegid
import pwd
import grp


def get_user():
    """
    Gets the executing user.
    :return: The user name
    """
    user_id = geteuid()
    return pwd.getpwuid(user_id).pw_name


def get_user_group():
    """
    Gets the executing group name.
    :return: The name of the primary user group for the executing user.
    """
    group_id = getegid()
    return grp.getgrgid(group_id).gr_name
