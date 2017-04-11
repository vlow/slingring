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

import system.mount as mount
from common import configuration
from resources.messages import get as _
from system.command import run_command
from universe.workflow.tools.paths import installation_file_path, schroot_config_file_path, local_universe_dir, \
    session_mount_point


def remove_universe_by_args(args):
    """
    Removes a universe from the local machine.
    :param args: The command line arguments as parsed by argparse.
                 This is expected to contain the following information:
                    - universe: The name of the universe which should be removed.
                    - verbose: True, for more verbose output.
    """
    remove_universe(args.universe, args.verbose)


def remove_universe(universe_name, verbose):
    """
    Removes a universe from the local machine.
    :param universe_name: The name of the universe which should be removed.
    :param verbose: True, for more verbose output.
    """
    print(_('remove-intro').format(universe_name))

    installation_configuration_path = installation_file_path(universe_name)

    if not os.path.exists(installation_configuration_path):
        print(_('universe-does-not-exist'))
        exit(1)

    installation_path = configuration.read_configuration(installation_configuration_path)['location']
    schroot_path = schroot_config_file_path(universe_name)

    if mount.contains_active_mount_point(session_mount_point(universe_name)) \
            or mount.contains_active_mount_point(installation_path):
        print(_('still-mounted-error'))
        exit(1)

    if os.path.exists(installation_path):
        run_command(['sudo', 'rm', '-rf', installation_path], 'deletion-phase', verbose)
        print(_('installation-path-removed'))
    else:
        print(_('installation-path-does-not-exist'))

    if os.path.exists(schroot_path):
        run_command(['sudo', 'rm', schroot_path], 'deletion-phase', verbose)
        print(_('schroot-config-removed'))
    else:
        print(_('schroot-config-does-not-exist'))

    local_universe_path = local_universe_dir(universe_name)
    if os.path.exists(local_universe_path):
        run_command(['rm', '-rf', local_universe_path], 'deletion-phase', verbose)
        print(_('local-cache-removed'))
    else:
        print(_('local-cache-does-not-exist'))
