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

import system.mount as mount
from common import configuration
from resources.messages import get as _
from system.command import run_command
from system.user import get_user, get_user_group
from universe.workflow.tools.paths import installation_file_path, session_mount_point, schroot_config_directory_path, \
    schroot_config_file_name, local_configuration_dir, user_home_in_chroot


def export_universe_by_args(args):
    """
    Exports a universe as a compressed image, which can be used for
    long term storage or as a simple backup.
    :param args: The command line arguments as parsed by argparse.
                 This is expected to contain the following information:
                    - universe: The name of the universe which should be exported.
                    - verbose: True, for more verbose output.
    """
    export_universe(args.universe, args.verbose)


def export_universe(universe_name, verbose):
    """
    Exports a universe as a compressed image, which can be used for
    long term storage or as a simple backup.
    :param universe_name: The name of the universe which should be exported.
    :param verbose: True, for more verbose output.
    """
    print(_('export-intro').format(universe_name))

    installation_configuration_path = installation_file_path(universe_name)

    if not os.path.exists(installation_configuration_path):
        print(_('universe-does-not-exist'))
        exit(1)

    installation_path = configuration.read_configuration(installation_configuration_path)['location']

    if mount.contains_active_mount_point(session_mount_point(universe_name)) \
            or mount.contains_active_mount_point(installation_path):
        print(_('still-mounted-error'))
        exit(1)

    with TemporaryDirectory() as export_temp_dir:
        # create maps
        user_name = get_user()
        owner_map_file_path = os.path.join(export_temp_dir, 'slingring_export_owner_map')
        with open(owner_map_file_path, 'w') as owner_map_file:
            owner_map_file.write('{} slingring_user:323232'.format(user_name))

        user_group = get_user_group()
        group_map_file_path = os.path.join(export_temp_dir, 'slingring_export_group_map')
        with open(group_map_file_path, 'w') as group_map_file:
            group_map_file.write('{} slingring_group:232323'.format(user_group))

        # todo escape . in usernames for regex
        # touch file
        etc_passwd_for_export_file_path = os.path.join(export_temp_dir, 'slingring_export_etc_passwd')
        run_command(['sudo', 'touch', etc_passwd_for_export_file_path], 'etc-passwd-creation-phase', verbose)
        # chmod file
        run_command(['sudo', 'chmod', '600', etc_passwd_for_export_file_path], 'etc-passwd-creation-phase', verbose)
        # sed /etc/passwd > file
        etc_passwd_path = os.path.join(installation_path, '/etc/passwd')
        run_command(
            [
                'sudo sh -c \'sed "s/^' + user_name + ':\([^:]:[0-9]*:[0-9]*\):[^:]*:[^:]*:\([^:]*\)/' +
                'slingring_user:\\1:Slingring User:slingring_home:\\2/" ' +
                etc_passwd_path + ' > ' + etc_passwd_for_export_file_path + '\''], 'etc-passwd-creation-phase', verbose,
            shell=True)

        # touch file
        etc_shadow_for_export_file_path = os.path.join(export_temp_dir, 'slingring_export_etc_shadow')
        run_command(['sudo', 'touch', etc_shadow_for_export_file_path], 'etc-shadow-creation-phase', verbose)
        # chmod file
        run_command(['sudo', 'chmod', '600', etc_shadow_for_export_file_path], 'etc-shadow-creation-phase', verbose)
        # sed /etc/shadow > file
        etc_shadow_path = os.path.join(installation_path, '/etc/shadow')
        run_command(
            ['sudo sh -c \'sed s/^' + user_name + ':[^:]*:/slingring_user:pw_hash:/ ' + etc_shadow_path + ' > ' +
             etc_shadow_for_export_file_path + '\''], 'etc-shadow-creation-phase', verbose, shell=True)

        # touch file
        etc_group_for_export_file_path = os.path.join(export_temp_dir, 'slingring_export_etc_group')
        run_command(['sudo', 'touch', etc_group_for_export_file_path], 'etc-group-creation-phase', verbose)
        # chmod file
        run_command(['sudo', 'chmod', '600', etc_group_for_export_file_path], 'etc-group-creation-phase', verbose)
        # sed /etc/group > file
        etc_group_path = os.path.join(installation_path, '/etc/group')
        run_command(
            ['sudo sh -c \'sed s/^' + user_group + ':/slingring_group:/ ' + etc_group_path + ' | ' +
             'sed "s/\(..*:\)\(..*,\)\?\(' + user_name + '\)\(,..*\)\?/\\1\\2slingring_user\\4/"' +
             ' > ' + etc_group_for_export_file_path + '\''], 'etc-group-creation-phase', verbose, shell=True)

        # touch file
        etc_gshadow_for_export_file_path = os.path.join(export_temp_dir, 'slingring_export_etc_gshadow')
        run_command(['sudo', 'touch', etc_gshadow_for_export_file_path], 'etc-gshadow-creation-phase', verbose)
        # chmod file
        run_command(['sudo', 'chmod', '600', etc_gshadow_for_export_file_path], 'etc-gshadow-creation-phase', verbose)
        # sed /etc/group > file
        etc_gshadow_path = os.path.join(installation_path, '/etc/gshadow')
        run_command(
            ['sudo sh -c \'sed s/^' + user_group + ':/slingring_group:/ ' + etc_gshadow_path + ' | ' +
             'sed "s/\(..*:\)\(..*,\)\?\(' + user_name + '\)\(,..*\)\?/\\1\\2slingring_user\\4/"' +
             ' > ' + etc_gshadow_for_export_file_path + '\''], 'etc-gshadow-creation-phase', verbose, shell=True)

        # create export.yml
        # todo
        configuration._write_yaml_file(os.path.join(export_temp_dir, 'export.yml'), {'universe': universe_name})

        chroot_config_path = schroot_config_directory_path()
        chroot_config_file_name = schroot_config_file_name(universe_name)
        universe_parent_dir = os.path.dirname(installation_path)

        # manipulate /etc/shadow
        # /etc/gshadow
        # /etc/groups
        # /etc/passwd

        slingring_config_path = local_configuration_dir()

        # absolute path would overwrite join
        user_home = universe_name + user_home_in_chroot(user_name)

        run_command(
            ['sudo', 'tar', '--owner-map=' + owner_map_file_path, '--group-map=' + group_map_file_path, '-cvzf',
             "export.tar.gz",
             '--preserve-permissions',
             '--exclude=' + universe_name + '/etc/passwd',
             '--exclude=' + universe_name + '/etc/shadow',
             '--exclude=' + universe_name + '/etc/group',
             '--exclude=' + universe_name + '/etc/gshadow',
             '--transform=s:^' + user_home + '/:/universe-data/' + universe_name + '/home/slingring_user/:',
             '--transform=s:^' + user_home + ':/universe-data/' + universe_name + '/home/slingring_user:',
             '--transform=s:^' + universe_name + '/:/universe-data/' + universe_name + '/:',
             '--transform=s:^' + universe_name + '$:/universe-data:',
             '--transform=s:^multiverse/:/multiverse-config/:',
             '--transform=s:^multiverse$:/multiverse-config:',
             '--transform=s:^' + universe_name + '.conf$:/schroot-config/' + universe_name + '.conf:',
             '--transform=s:^' + 'slingring_export_etc_passwd$:/universe-data/' + universe_name + '/etc/passwd:',
             '--transform=s:^' + 'slingring_export_etc_shadow$:/universe-data/' + universe_name + '/etc/shadow:',
             '--transform=s:^' + 'slingring_export_etc_group$:/universe-data/' + universe_name + '/etc/group:',
             '--transform=s:^' + 'slingring_export_etc_gshadow$:/universe-data/' + universe_name + '/etc/gshadow:',
             '--transform=s:^' + 'slingring_export_etc_gshadow$:/universe-data/' + universe_name + '/etc/gshadow:',
             '-C', slingring_config_path, 'multiverse/' + universe_name,
             '-C', chroot_config_path, chroot_config_file_name,
             '-C', universe_parent_dir, universe_name,
             '-C', os.path.dirname(etc_passwd_for_export_file_path),
             os.path.basename(etc_passwd_for_export_file_path),
             '-C', os.path.dirname(etc_shadow_for_export_file_path),
             os.path.basename(etc_shadow_for_export_file_path),
             '-C', os.path.dirname(etc_group_for_export_file_path),
             os.path.basename(etc_group_for_export_file_path),
             '-C', os.path.dirname(etc_gshadow_for_export_file_path),
             os.path.basename(etc_gshadow_for_export_file_path),
             '-C', export_temp_dir, 'export.yml'], 'compress-phase', verbose)

        run_command(['sudo', 'chown', user_name + ':' + user_group, 'export.tar.gz'], 'ownership-phase', verbose)

        # if os.path.exists(installation_path):
        #     run_command(['sudo', 'rm', '-rf', installation_path], 'deletion-phase', verbose)
        #     print(_('installation-path-removed'))
        # else:
        #     print(_('installation-path-does-not-exist'))

        # if os.path.exists(schroot_path):
        #     run_command(['sudo', 'rm', schroot_path], 'deletion-phase', verbose)
        #     print(_('schroot-config-removed'))
        # else:
        #     print(_('schroot-config-does-not-exist'))

        # local_universe_path = local_universe_dir(universe_name)
        # if os.path.exists(local_universe_path):
        #     run_command(['rm', '-rf', local_universe_path], 'deletion-phase', verbose)
        #     print(_('local-cache-removed'))
        # else:
        #     print(_('local-cache-does-not-exist'))
