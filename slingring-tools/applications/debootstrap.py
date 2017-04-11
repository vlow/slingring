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


def debootstrap(path, architecture, variant, suite, mirror, phase, verbose):
    """
    Creates a Debian-based chroot in the given location.

    Find more details about the possible parameters in man debootstrap(8)

    :param path: The target path (e.g. /seu/chrootname). Will be created if it does not exist.
    :param architecture: The architecture (e.g. amd64, i386)
    :param variant: the bootstrap variant (e.g. minbase)
    :param suite: the suite name (e.g. xenial for ubuntu 16.04 lts)
    :param mirror: the image mirror (e.g. http://de.archive.ubuntu.com/ubuntu)
    :param phase: a message key which describes the current phase. This is used if something fails.
    :param verbose: True, if a more verbose output is desired.
    """
    if variant is not None:
        variant_cmd = '--variant=' + variant
    else:
        variant_cmd = ''

    arch_cmd = '--arch=' + architecture

    cmd = ['sudo', 'debootstrap', variant_cmd, arch_cmd, suite, path, mirror]

    run_command(cmd, phase, verbose)
