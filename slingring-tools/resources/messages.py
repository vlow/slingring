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

_msg = {

    # universe

    'start':
        'Initializing "{}" universe.',

    'update-start':
        'Updating "{}" universe. This will re-run the Ansible playbook on the chroot.',

    'list-start':
        'These are the available universes on this system:',

    'no-universes-found':
        '''There are not yet any universes on this system.
Use 'universe create' to create your first universe.''',

    'input-header':
        '''This universe seed requests additional information. If you
obtained this universe seed from an unsafe source, make sure to
check all included playbooks before providing credentials of any kind!

Information requested by the universe seed:''',

    'coffee-time':
        'That\'s it! Your universe will be ready shortly. Time to get a cup of coffee.',

    'debootstrap':
        'Bootstrapping "{} ({})" base layout...',

    'schroot':
        'Setting up schroot...',

    'prepare-chroot':
        'Preparing chroot...',

    'config-files':
        'Creating variable files for Ansible...',

    'mount-chroot':
        'Mounting virtual filesystems into chroot...',

    'ansible':
        'Running Ansible playbook...',

    'umount-chroot':
        'Unmounting virtual filesystems...',

    'done':
        '''Done! Everything looks good. Open a portal to your new universe using:

        $ slingring {}{}{}

Don't have too much fun ;)''',

    'update-done':
        '''Done! Everything looks good. Open a portal to your updated universe using:

        $ slingring {}{}{}

Don't have too much fun ;)''',

    'cmd-error-verbose':
        'An error occurred while {}. The above output might help to identify the problem.',

    'cmd-error':
        'An error occurred while {}. This is output might help to identify the problem:',

    'exec-in-schroot-phase':
        'executing a command in the schroot',

    'debootstrap-phase':
        'debootstrapping the image',

    'create-base-directory-phase':
        'creating the universe base directory',

    'tmpfs-mount-phase':
        'mounting the tmpfs for the debootstrap process',

    'tmpfs-umount-phase':
        'unmounting the tmpfs used for the debootstrap process',

    'copy-initializers-phase': 'copying the initializer scripts to the chroot',

    'initializers-phase': 'running the initializer scripts in the chroot',

    'create-base-temp-directory-phase':
        'creating the universe base temp directory',

    'enable-runtime-profile-phase':
        'enabling the schroot runtime profile',

    'schroot-config-phase':
        'creating the Schroot config files',

    'prepare-chroot-phase':
        'preparing the chroot',

    'ansible-phase':
        'running the Ansible playbook',

    'mount-phase':
        'mounting the virtual file systems into the chroot',

    'umount-phase':
        'unmounting the virtual file systems',

    'stdout':
        'Output of stdout:',

    'stderr':
        'Output of stderr:',

    'failed-command':
        'The failed command was: {}',

    'failed-pipe-command':
        'Piped into: {}',

    'remove-intro':
        'Removing the "{}" universe...',

    'still-mounted-error':
        '''There are still mount-points active in the universe.
Please make sure that all portals are closed and
unmount all remaining mount-points manually.
The output of the 'mount' command might help you.''',

    'installation-path-removed': 'Chroot removed.',

    'installation-path-does-not-exist': 'Chroot does not exist.',

    'schroot-config-removed': 'Schroot configuration removed.',

    'schroot-config-does-not-exist': 'Schroot configuration does not exist.',

    'local-cache-removed': 'Universe configuration removed.',

    'local-cache-does-not-exist': 'Universe configuration does not exist.',

    'universe-does-not-exist':
        'Error: The given universe does not exist. Use the \'list\' operation to see a list of all existing universes '
        'on this computer.',

    'colliding-paths': '''Error: There are colliding paths. There may not be two universes or an existing
schroot config with the same name. You can change the name in the universe.yml file
or remove the existing universe / schroot config.''',

    'spaces-in-temp-error': '''Error: Due to an unfixed bug in debootstrap, the path to the temp directory must
       not contain spaces. Please use the -t parameter to choose a temp directory
       without spaces in its path.''',

    'upgrade-warning': '''Warning: While it is best practice to make new seed versions backwards compatible,
         there is no guarantee that the author of this seed did this. Make sure to only upgrade
         your universe if the author of this version ({}) explicitly lists your current
         version ({}) as compatible.

Do you want to proceed?''',

    'different_arch_error': '''Error: The seed you are trying to upgrade your universe to uses another base
       architecture. It is not possible to change the architecture of a universe
       by upgrading.''',

    'different_suite_error': '''Error: The seed you are trying to upgrade your universe to uses another distribution
       suite. It is not possible to change the distribution suite of a universe
       by upgrading.''',

    'different_variant_error': '''Error: The seed you are trying to upgrade your universe to uses another distribution
       variant. It is not possible to change the distribution variant of a universe
       by upgrading.''',

    'different_name_warning': '''Warning: The seed you are trying to upgrade your universe to has another name specified:

            Current name: {}
            New name: {}

Do you want to proceed?''',

    'same_version_warning': '''Warning: The seed you are trying to upgrade your universe to has the same version.
         If you are simply trying to re-run the Ansible playbook, please use the 'update' command.
         It is HIGHLY RECOMMENDED to use different version strings for different seed versions.

Do you want to proceed?''',

    # seed

    'create-ascii-art-text-phase':
        'creating the ascii-art',

    'local-images': 'Local images:',

    'global-images': 'Global images:',

    'directory-exists': '''Error: A directory named '{}' already exists in '{}'.
Please remove/rename the directory or choose another universe name.''',

    'template-not-found': 'Error: The \'{}\' template cannot be found. Ensure it is not misspelled or re-install it.',
    'template-invalid': 'Error: The \'{}\' template is invalid: The universe.yml file is missing.'

}


def get(key):
    """
    Gets the string resource for the given key.
    :param key: The key.
    :return: The according string resource.
    """
    if key in _msg:
        return _msg[key]
    else:
        return key
