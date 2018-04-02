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

import os
import shutil

from common.configuration import ConfigurationHandler
from common.paths import local_home


def local_configuration_dir():
    return os.path.join(local_home(), '.slingring')


def local_multiverse_dir():
    return os.path.join(local_configuration_dir(), 'multiverse')


def local_universe_dir(universe_name):
    return os.path.join(local_multiverse_dir(), universe_name)


def installation_file_path(universe_name):
    return os.path.join(local_universe_dir(universe_name), 'installation.yml')


def universe_file_path(universe_name):
    return os.path.join(local_universe_dir(universe_name), 'universe.yml')


def playbook_directory_path(universe_name):
    return os.path.join(local_universe_dir(universe_name), 'ansible/')


def playbook_user_vars_path(universe_name):
    return os.path.join(playbook_directory_path(universe_name), "slingring_user_vars.yml")


def playbook_user_secrets_path(universe_name):
    return os.path.join(playbook_directory_path(universe_name), "slingring_user_secrets.yml")


def playbook_slingring_vars_path(universe_name):
    return os.path.join(playbook_directory_path(universe_name), "slingring_vars.yml")


def playbook_hosts_file_path(universe_name):
    return os.path.join(playbook_directory_path(universe_name), "hosts")


def initializer_target_path(chroot_directory):
    return os.path.join(chroot_directory, 'root/initializers')


def initializer_target_path_in_chroot():
    return '/root/initializers'


def user_home_in_chroot(user_name):
    return os.path.join("/home", user_name)


def schroot_config_directory_path():
    return '/etc/schroot/chroot.d'


def schroot_config_file_name(universe_name):
    return universe_name + '.conf'


def schroot_config_file_path(universe_name):
    return os.path.join(schroot_config_directory_path(), schroot_config_file_name(universe_name))


def initializer_directory_path(universe_name):
    return os.path.join(local_universe_dir(universe_name), 'initializer/')


def designated_universe_path(universe_name):
    return os.path.join(designated_universe_base(), universe_name)


def designated_universe_base():
    return ConfigurationHandler().get_config_value('universe-directory')


def copy_seed_to_local_home(source_dir, name):
    local_cache_directory = local_universe_dir(name)
    shutil.copytree(source_dir, local_cache_directory)
    return local_cache_directory


def source_universe_file_path(source_directory):
    return os.path.join(source_directory, 'universe.yml')


def session_mount_point(universe_name):
    session_dir = '{}-seu-session'.format(universe_name)
    return os.path.join('/run/schroot/mount/', session_dir)


def colliding_paths_exist(universe_name):
    universe_path = designated_universe_path(universe_name)
    if colliding_local_or_schroot_paths_exist(universe_name) or os.path.exists(universe_path):
        return True
    return False


def colliding_local_or_schroot_paths_exist(universe_name):
    designated_local_path = local_universe_dir(universe_name)
    designated_schroot_path = schroot_config_file_path(universe_name)

    if os.path.exists(designated_local_path) or \
            os.path.exists(designated_schroot_path):
        return True
    return False
