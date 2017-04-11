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

from system.command import run_command


def mount(source, mount_point, phase_key, verbose, bind=False, fstype=None):
    """
    Mounts a given source onto an mount point.
    :param source: The source (e.g. /dev/sda1)
    :param mount_point: The mount point (e.g. /mnt/disk1)
    :param phase_key: a message key which describes the current phase. This is used if something fails.
    :param verbose: True, if a more verbose output is desired.
    :param bind: If bind option shall be used.
    :param fstype: The filesystem type.
    """
    mount_cmd = ['sudo', 'mount']
    if bind:
        mount_cmd.append('-o')
        mount_cmd.append('bind')
    if fstype:
        mount_cmd.append('-t')
        mount_cmd.append(fstype)
    mount_cmd.append(source)
    mount_cmd.append(mount_point)

    run_command(mount_cmd, phase_key, verbose)


def umount(mount_point, phase_key, verbose):
    """
    Unmounts a mount point.
    :param mount_point: The mount point (e.g. /mnt/disk1)
    :param phase_key: a message key which describes the current phase. This is used if something fails.
    :param verbose: True, if a more verbose output is desired.
    """
    umount_cmd = ['sudo', 'umount', mount_point]
    run_command(umount_cmd, phase_key, verbose)


def contains_active_mount_point(mount_point):
    """
    Checks if the given mount point contains an active mount. E.g. if /mnt/ is given and
    something is mounted in /mnt/foo/bar, this will return True
    :param mount_point: The directory to check.
    :return: True, if something is mounted beneath the given mount_point.
    """
    output = run_command('mount', 'mount-check', False).stdout.decode('utf-8')
    return mount_point in output
