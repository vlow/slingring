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

from tempfile import gettempdir

import applications.schroot as schroot
import system.user as user
import universe.workflow.tools.chroot as chroot
from os import path
from common import configuration
from resources.messages import get as _
from universe.workflow.common import gather_variables_from_user, create_slingring_vars_dict, print_spaced, \
    get_seed_directory_from_argument
from universe.workflow.tools.paths import source_universe_file_path, copy_seed_to_local_home, installation_file_path, \
    schroot_config_file_path, initializer_directory_path, designated_universe_path, colliding_paths_exist


def install_universe_by_args(args):
    """"
    Installs a new universe from a universe description.
    :param args: The command line arguments as parsed by argparse.
                 This is expected to contain the following information:
                    - seed: The path to the universe seed directory as string.
                    - temp: An alternative temp directory for debootstrapping (must not contain spaces).
                    - verbose: True, for more verbose output.
    """
    install_universe(args.seed, args.temp, args.verbose)


def install_universe(seed_path, temp_dir, verbose):
    """"
    Installs a new universe from a universe description.
    :param seed_path: The path to the universe seed directory as string.
    :param temp_dir: An alternative temp directory for debootstrapping (must not contain spaces).
    :param verbose: True, for more verbose output.
    """
    source_seed_directory = get_seed_directory_from_argument(seed_path)
    source_seed_universe_path = source_universe_file_path(source_seed_directory)
    _validate_seed_path_exists(source_seed_universe_path, seed_path)

    seed_dictionary = configuration.read_seed_file(source_seed_universe_path)
    universe_name = seed_dictionary['name']
    temp_dir = _get_temp_dir_from_argument(temp_dir)

    _validate_paths_for_collision(universe_name)

    print(_('start').format(universe_name))

    # Phase 1: Retrieve Ansible variable files from the user now, so we don't need user interaction after this point
    user_vars, user_secrets = gather_variables_from_user(seed_dictionary)

    # Phase 2: Copy the universe description to our local home in ~/.slingring and write the installation file
    #          The installation file contains the directory of the chroot, so the 'remove' operation finds it,
    #          even if the installation fails.
    print_spaced(_('coffee-time'))
    universe_path = designated_universe_path(universe_name)
    copy_seed_to_local_home(source_seed_directory, universe_name)
    configuration.write_installation_configuration(installation_file_path(universe_name), universe_path)

    # Phase 3: Run debootstrap to create the chroot
    print(_('debootstrap').format(seed_dictionary['suite'], seed_dictionary['arch']))
    chroot.bootstrap(universe_path, seed_dictionary, verbose, temp_dir)

    if verbose:
        print()

    # Phase 4: Create schroot config (setup) file.
    print(_('schroot'))
    schroot_config_path = schroot_config_file_path(universe_name)

    user_name = user.get_user()
    user_group = user.get_user_group()
    schroot.create_schroot_config(universe_name, schroot_config_path,
                                  universe_path, user_name, user_group, 'schroot-config-phase', verbose)

    # Phase 4.1: We must run one command in the schroot. Since we create schroots with the setup-profile
    #            This will copy all necessary files like /etc/passwd, /etc/shadow etc. to the chroot.
    print(_('prepare-chroot'))
    user_home = chroot.create_user_home(user_name, user_group, universe_name, verbose)

    # The runtime-profile will mount the x11 unix socket into the schroot, so the mount point must exist.
    chroot.create_x11_socket_dir(universe_name, verbose)

    # Phase 4.2: Since everything is set up now, we set schroot config to (runtime) after first command.
    #            This will prevent subsequent schroot calls from overwriting the 'copyfiles' (e.g. /etc/passwd).
    schroot.change_schroot_profile(universe_name, schroot_config_path, 'slingring-runtime',
                                   'enable-runtime-profile-phase', verbose)

    # Phase 5: Run the initializer scripts. These are shell scripts provided by the author of the universe description.
    #          Their task is to prepare the chroot for the Ansible playbooks (install Python, create _apt user for
    #          Debian based distros etc.)
    initializer_directory = initializer_directory_path(universe_name)
    chroot.run_initializers(initializer_directory, universe_path, universe_name, user_name, user_group, verbose)

    # Phase 6: Run the Ansible playbook on our chroot.
    slingring_vars = create_slingring_vars_dict(user_name, user_group, user_home, seed_dictionary['mirror'],
                                                universe_name,
                                                seed_dictionary['version'])
    if verbose:
        print()
    chroot.run_ansible(universe_name, universe_path, user_vars,
                       user_secrets, slingring_vars, verbose)

    if ' ' in universe_name:
        quote = '"'
    else:
        quote = ''

    print_spaced(_('done').format(quote, universe_name, quote))


def _validate_seed_path_exists(seed_file_path, seed_path):
    if not path.exists(seed_file_path):
        print(_('seed-not-exists').format(seed_path))
        exit(1)


def _validate_paths_for_collision(universe_name):
    if colliding_paths_exist(universe_name):
        print(_('colliding-paths'))
        exit(1)


def _get_temp_dir_from_argument(temp_dir_argument):
    if temp_dir_argument is not None:
        temp_dir = temp_dir_argument
    else:
        temp_dir = gettempdir()
    if ' ' in temp_dir:
        print(_('spaces-in-temp-error'))
        exit(1)
    return temp_dir
