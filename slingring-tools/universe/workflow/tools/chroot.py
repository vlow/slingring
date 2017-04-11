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
from tempfile import TemporaryDirectory

import applications.ansible as ansible
import applications.debootstrap as debootstrap
import applications.schroot as schroot
import system.key as key
import system.mount as mnt
from resources.messages import get as _
from system.command import run_command
from universe.workflow.tools.paths import playbook_directory_path, playbook_user_vars_path, \
    playbook_slingring_vars_path, \
    playbook_user_secrets_path, playbook_hosts_file_path, initializer_target_path, initializer_target_path_in_chroot, \
    user_home_in_chroot


def run_ansible(universe_name, chroot_path, user_vars, user_secrets, slingring_vars, verbose):
    """
    Runs the universe playbook on the given chroot.
    :param universe_name: The universe name.
    :param chroot_path: The path to the chroot.
    :param user_vars: A dictionary containing user vars (key: name, value: value)
    :param user_secrets: A dictionary containing user secrets (key: name, value: value)
    :param slingring_vars: A dictionary containing slingring vars (key: name, value: value)
    :param verbose: True, if a more verbose output is desired.
    """
    print(_('config-files'))
    with open(playbook_hosts_file_path(universe_name), 'w') as hosts_file:
        hosts_file.write('"{}" {}'.format(chroot_path, " ansible_connection=chroot"))

    # create ansible variable files
    playbook_directory = playbook_directory_path(universe_name)
    run_command(['mkdir', '-p', playbook_directory], 'create-cache-dir-phase', verbose)
    ansible.write_vars_file(playbook_user_vars_path(universe_name), user_vars, 'user_vars')
    ansible.write_vars_file(playbook_slingring_vars_path(universe_name), slingring_vars, 'slingring')

    if user_secrets:
        password = key.create_random_password(20)
        ansible.write_vars_vault_file(
            playbook_user_secrets_path(universe_name), user_secrets, password, 'user_secrets',
            'write-user-secret-phase', verbose)
    else:
        password = None

    # mount chroot
    print(_('mount-chroot'))
    try:
        mount(chroot_path, verbose)
        # run ansible
        print(_('ansible'))
        ansible.run_playbook(playbook_directory, verbose, password)
        print(_('umount-chroot'))
    finally:
        umount(chroot_path, verbose)


def bootstrap(chroot_path, seed_dictionary, verbose, temp_dir=None):
    """
    Bootstraps a chroot into the given directory. If the parent base directory
    does not exist, it will be created.
    :param chroot_path: The path of the created chroot.
    :param seed_dictionary: The universe description as a dictionary.
    :param verbose: True, if a more verbose output is desired.
    :param temp_dir:
    """
    run_command(['sudo', 'mkdir', '-p', chroot_path], 'create-base-directory-phase', verbose)
    image_variant = seed_dictionary['variant'] if 'variant' in seed_dictionary else None
    debootstrap_dir = TemporaryDirectory(dir=temp_dir)
    with debootstrap_dir as debootstrap_dir_path:
        base_image_path = os.path.join(debootstrap_dir_path, 'base_image')
        mnt.mount('none', debootstrap_dir_path, 'tmpfs-mount-phase', verbose, fstype='tmpfs')

        # create a dedicated directory inside the tmpfs, so we can mv it later
        run_command(['sudo', 'mkdir', base_image_path], 'create-base-temp-directory-phase', verbose)
        debootstrap.debootstrap(base_image_path, seed_dictionary['arch'], image_variant, seed_dictionary['suite'],
                                seed_dictionary['mirror'],
                                'debootstrap-phase', verbose)

        run_command(['sudo', 'mv', base_image_path, '-T', chroot_path], 'mv-debootstrap-dir-phase', verbose)
        mnt.umount(debootstrap_dir_path, 'tmpfs-umount-phase', verbose)


def create_user_home(user_name, user_group, schroot_name, verbose):
    """
    Creates the user home for the given user within the given schroot.
    :param user_name: The user name
    :param user_group: The user's primary group
    :param schroot_name: The name of the schroot
    :param verbose: True, if a more verbose output is desired.
    :return: The path to the user home within the chroot (e.g. /home/username).
    """
    user_home = user_home_in_chroot(user_name)
    schroot.execute_in_schroot(schroot_name, 'mkdir {}'.format(user_home), True, 'prepare-chroot-phase', verbose)
    schroot.execute_in_schroot(schroot_name, 'chown {}:{} {}'.format(user_name, user_group, user_home), True,
                               'prepare-chroot-phase', verbose)
    return user_home


def mount(chroot_path, verbose):
    """
    Mounts the host systems virtual filesystems into the chroot.
    :param chroot_path: The chroot path.
    :param verbose: True, if a more verbose output is desired.
    """
    mnt.mount('/proc', chroot_path + '/proc', 'mount-phase', verbose, False, 'proc')
    mnt.mount('/sys', chroot_path + '/sys', 'mount-phase', verbose, False, 'sysfs')
    mnt.mount('/dev', chroot_path + '/dev', 'mount-phase', verbose, True)
    mnt.mount('/dev/pts', chroot_path + '/dev/pts', 'mount-phase', verbose, True)


def umount(chroot_path, verbose):
    """
    Unmounts the virtual filesystems withing the chroot.
    :param chroot_path: The chroot.
    :param verbose: True, if a more verbose output is desired.
    """
    mnt.umount(chroot_path + '/proc', 'umount-phase', verbose)
    mnt.umount(chroot_path + '/sys', 'umount-phase', verbose)
    mnt.umount(chroot_path + '/dev/pts', 'umount-phase', verbose)
    mnt.umount(chroot_path + '/dev', 'umount-phase', verbose)


def run_initializers(source_directory, chroot_directory, schroot_name, user_name, user_group, verbose):
    """
    Runs the initializer scripts from a given source directory within a given schroot.
    The scripts will be run as root but the user name and group of the slingring user will
    be available as environment variables SLINGRING_USER_NAME and SLINGRING_USER_GROUP.
    :param source_directory: The directory in which the initializer scripts lie.
    :param chroot_directory: The path to the chroot root directory.
    :param schroot_name: The schroot name.
    :param user_name: The slingring user.
    :param user_group: The slingring user's primary group.
    :param verbose: True, if a more verbose output is desired.
    """
    initializers_path = initializer_target_path(chroot_directory)
    initializers_path_in_chroot = initializer_target_path_in_chroot()
    schroot.execute_in_schroot(schroot_name, 'mkdir -p ' + initializers_path_in_chroot, True,
                               'initializers-phase', verbose)
    initializer_scripts = _copy_initializers_to_chroot(source_directory, initializers_path, verbose)
    env = _create_env(user_name, user_group)
    for script in initializer_scripts:
        script_path = os.path.join(initializers_path_in_chroot, script)
        schroot.execute_in_schroot(schroot_name, 'chmod +x ' + script_path, True, 'initializers-phase', verbose,
                                   env=env)
        schroot.execute_in_schroot(schroot_name, script_path, True, 'initializers-phase', verbose, env=env)


def _copy_initializers_to_chroot(source_directory, target_directory, verbose):
    copied_initializer_scripts = []
    for file in os.listdir(source_directory):
        file_path = os.path.join(source_directory, file)
        run_command(['sudo', 'cp', file_path, target_directory], 'copy-initializers-phase', verbose)
        copied_initializer_scripts.append(file)
    return sorted(copied_initializer_scripts)


def _create_env(user_name, user_group):
    return {'SLINGRING_USER_NAME': user_name,
            'SLINGRING_USER_GROUP': user_group}
