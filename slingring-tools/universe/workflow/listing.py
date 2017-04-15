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

import universe.workflow.tools.paths as paths
from common import configuration
from resources.messages import get as _


def list_universes_by_args(args):
    """
    Lists all universes on the local machine.
    :param args: The command line arguments as parsed by argparse.
                 This is expected to contain the following information:
                    - verbose: True, for more verbose output.
    """
    list_universes(args.verbose)


def list_universes(verbose):
    """
    Lists all universes on the local machine.
    """
    multiverse_directory = _get_directories_in_multiverse()
    universe_list = []
    for universe in multiverse_directory:
        installation_file_path = paths.installation_file_path(universe)
        if os.path.exists(installation_file_path):
            install_path = configuration.read_configuration(installation_file_path)['location']
            if verbose:
                output = '   - {} ({})'.format(universe, install_path)
            else:
                output = '   - {}'.format(universe)
            universe_list.append(output)

    if universe_list:
        print(_('list-start'))
        for universe in universe_list:
            print(universe)
    else:
        print(_('no-universes-found'))

def _get_directories_in_multiverse():
    multiverse_directory_path = paths.local_multiverse_dir()
    if os.path.exists(multiverse_directory_path):
        return os.listdir(multiverse_directory_path)
    return []
