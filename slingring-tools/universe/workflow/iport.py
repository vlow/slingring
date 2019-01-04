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
from tempfile import TemporaryDirectory

from common.configuration import read_configuration
from resources.messages import get as _
from system.command import run_command
from universe.workflow.tools.paths import colliding_paths_exist, colliding_local_or_schroot_paths_exist, \
    local_multiverse_dir


def import_universe_by_args(args):
    """
    Imports a universe from a compressed image.
    :param args: The command line arguments as parsed by argparse.
                 This is expected to contain the following information:
                    - import_file: The name of the universe which should be exported.
                    - verbose: True, for more verbose output.
    """
    import_universe(args.import_file, args.verbose)


def import_universe(import_file, verbose):
    """
    Imports a universe from a compressed image.
    :param import_file: The name of the universe which should be exported.
    :param verbose: True, for more verbose output.
    """
    print(_('import-intro').format(import_file))

    # create temp directory
    with TemporaryDirectory() as import_temp_dir:
        run_command(['tar', '-xf', import_file, '-C', import_temp_dir, 'export.yml'], 'extract-export-file-phase',
                    verbose)

        # parse export file
        universe_name = read_configuration(import_temp_dir + '/' + 'export.yml')['universe']

        # check for name collision
        if colliding_paths_exist(universe_name) or colliding_local_or_schroot_paths_exist(universe_name):
            print(_('universe-exists-already'))
            exit(1)

        # create multiverse record
        # todo: make sure local configuration directory exists, otherwise this will fail if it is the first universe
        multiverse_directory = local_multiverse_dir()
        run_command(['tar', '-xPf', import_file, '-C', multiverse_directory,
                     '/multiverse-config/' + universe_name, '--strip-components=1'], 'extract-export-file-phase',
                    verbose)
        # todo: correct the installation path if ours differs

    # create mapping files
    # unpack schroot files
    # unpack files to target - transforming slingring_user to local user
    # change owner centric files to current owner
