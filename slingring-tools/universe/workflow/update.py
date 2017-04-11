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

import system.user as user
import universe.workflow.tools.chroot as chroot
from common import configuration
from resources.messages import get as _
from universe.workflow.common import create_slingring_vars_dict, gather_variables_from_user, print_spaced
from universe.workflow.tools.paths import installation_file_path, universe_file_path, user_home_in_chroot, \
    local_universe_dir


def update_universe_by_args(args):
    """"
    Re-runs the Ansible playbook saved in the local Slingring home
    for the given universe on its chroot.
    :param args: The command line arguments as parsed by argparse.
                 This is expected to contain the following information:
                    - universe: The name of the universe
                    - verbose: True, for more verbose output.
    """
    update_universe(args.universe, args.verbose)


def update_universe(universe_name, verbose):
    """"
    Re-runs the Ansible playbook saved in the local Slingring home
    for the given universe on its chroot.
    :param universe_name: The name of the universe
    :param verbose: True, for more verbose output.
    """
    local_installation_path = local_universe_dir(universe_name)

    if not os.path.exists(local_installation_path):
        print(_('universe-does-not-exist'))
        exit(1)

    installation_configuration_path = installation_file_path(universe_name)
    universe_path = configuration.read_configuration(installation_configuration_path)['location']

    seed_universe_file_path = universe_file_path(universe_name)
    seed_dictionary = configuration.read_seed_file(seed_universe_file_path)

    print(_('update-start').format(universe_name))

    # retrieve ansible variable files from the user
    user_vars, user_secrets = gather_variables_from_user(seed_dictionary)

    print_spaced(_('coffee-time'))

    user_name = user.get_user()
    user_group = user.get_user_group()
    user_home = user_home_in_chroot(user_name)

    slingring_vars = create_slingring_vars_dict(user_name, user_group, user_home, seed_dictionary['mirror'],
                                                universe_name,
                                                seed_dictionary['version'])

    chroot.run_ansible(universe_name, universe_path, user_vars, user_secrets,
                       slingring_vars, verbose)

    if ' ' in universe_name:
        quote = '"'
    else:
        quote = ''

    print_spaced(_('update-done').format(quote, universe_name, quote))
