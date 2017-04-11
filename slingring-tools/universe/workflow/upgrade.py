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

from applications.schroot import change_schroot_name
from common import configuration
from resources.messages import get as _
from system.command import run_command
from universe.workflow.common import get_seed_directory_from_argument
from universe.workflow.tools.interaction import yes_no_prompt
from universe.workflow.tools.paths import installation_file_path, universe_file_path, local_universe_dir, \
    source_universe_file_path, copy_seed_to_local_home, schroot_config_file_path, colliding_local_or_schroot_paths_exist
from universe.workflow.update import update_universe


def upgrade_universe_by_args(args):
    """"
    Replaces the local seed of an existing universe with a newer
    version and runs the Ansible playbook on the given universe's chroot.
    :param args: The command line arguments as parsed by argparse.
                 This is expected to contain the following information:
                    - seed: The path to the universe seed directory as string.
                    - universe: The name of the universe
                    - verbose: True, for more verbose output.
    """
    upgrade_universe(args.seed, args.universe, args.verbose)


def upgrade_universe(seed_path, universe_name, verbose):
    """
    Replaces the local seed of an existing universe with a newer
    version and runs the Ansible playbook on the given universe's chroot.
    :param seed_path: The path to the universe seed directory as string.
    :param universe_name: The name of the universe
    :param verbose: True, for more verbose output.
    """
    old_universe_name = universe_name

    local_installation_path = local_universe_dir(old_universe_name)

    if not os.path.exists(local_installation_path):
        print(_('universe-does-not-exist'))
        exit(1)

    # read current information
    old_installation_configuration_path = installation_file_path(old_universe_name)
    universe_path = configuration.read_configuration(old_installation_configuration_path)['location']

    seed_universe_file_path = universe_file_path(old_universe_name)
    old_seed_dictionary = configuration.read_seed_file(seed_universe_file_path)

    # read new information
    source_seed_directory = get_seed_directory_from_argument(seed_path)
    source_seed_universe_path = source_universe_file_path(source_seed_directory)
    new_seed_dictionary = configuration.read_seed_file(source_seed_universe_path)
    new_universe_name = new_seed_dictionary['name']

    if not yes_no_prompt(_('upgrade-warning').format(new_seed_dictionary['version'], old_seed_dictionary['version'])):
        exit(1)
    else:
        print()

    # validate
    _validate_seed_dictionaries(old_seed_dictionary, new_seed_dictionary)
    if old_universe_name != new_universe_name:
        _validate_paths_for_collision(new_universe_name)

    # replace old seed with new seed
    run_command(['rm', '-rf', local_installation_path], 'remove-local-seed-phase', verbose)
    copy_seed_to_local_home(source_seed_directory, new_universe_name)
    new_installation_configuration_path = installation_file_path(new_universe_name)
    configuration.write_installation_configuration(new_installation_configuration_path, universe_path)

    # take care of the schroot config in case of a universe rename
    if old_universe_name != new_universe_name:
        change_schroot_name(old_universe_name, new_universe_name, schroot_config_file_path(old_universe_name),
                            schroot_config_file_path(new_universe_name), 'rename-schroot-phase', verbose)

    # run the new Ansible playbook on the universe as if we just updated
    update_universe(new_universe_name, verbose)


def _validate_seed_dictionaries(old_seed_dict, new_seed_dict):
    if old_seed_dict['arch'] != new_seed_dict['arch']:
        print(_('different_arch_error'))
        exit(1)
    if old_seed_dict['suite'] != new_seed_dict['suite']:
        print(_('different_suite_error'))
        exit(1)
    if old_seed_dict['variant'] != new_seed_dict['variant']:
        print(_('different_variant_error'))
        exit(1)
    if old_seed_dict['name'] != new_seed_dict['name']:
        if not yes_no_prompt(_('different_name_warning').format(old_seed_dict['name'], new_seed_dict['name']),
                             default='no'):
            exit(1)
        else:
            print()
    if old_seed_dict['version'] == new_seed_dict['version']:
        if not yes_no_prompt(_('same_version_warning'), default='no'):
            exit(1)
        else:
            print()


def _validate_paths_for_collision(universe_name):
    if colliding_local_or_schroot_paths_exist(universe_name):
        print(_('colliding-paths'))
        exit(1)
