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
import configparser
import os
import tempfile

from system.command import run_command


def create_schroot_config(name, path, directory, user, group, phase, verbose):
    """
    Creates a new schroot config file.
    :param name: The schroot name.
    :param path: The path of the new schroot config file.
    :param directory: The chroot directory.
    :param user: The user which will be allowed to enter the schroot
    :param group: The group which will be allowed to enter the schroot
    :param phase: a message key which describes the current phase. This is used if something fails.
    :param verbose: True, if a more verbose output is desired.
    """
    config = configparser.ConfigParser()
    description = name + ' Slingring Universe'
    config.add_section(name)
    config[name]['description'] = description
    config[name]['type'] = "directory"
    config[name]['directory'] = directory
    config[name]['users'] = user
    config[name]['groups'] = group
    config[name]['root-users'] = user
    config[name]['root-groups'] = "root"
    config[name]['profile'] = "slingring-setup"
    _write_config_file_as_root(config, path, phase, verbose)


def execute_in_schroot(name, command, sudo, phase, verbose, env=None):
    """
    Executes the given command string in the given schroot.
    :param name: The schroot name.
    :param command: The command as a single string.
    :param sudo: True, if the command shall be executed as root.
    :param phase: a message key which describes the current phase. This is used if something fails.
    :param verbose: True, if a more verbose output is desired.
    :param env: A dictionary containing environment variables which should be present within the schroot
                for the time of execution (e.g. { 'VARIABLE': 'content' })
    """
    effective_command = []
    if sudo:
        effective_command.append('sudo')
    effective_command.append('schroot')
    effective_command.append('-c')
    effective_command.append(name)
    effective_command.append('--directory')
    effective_command.append('/')
    effective_command.append('--')
    effective_command.append('/bin/bash')
    effective_command.append('-c')
    environment_exports = str()
    if env:
        for variable_name, variable_value in env.items():
            environment_exports += "export {}={};".format(variable_name, variable_value)
    effective_command.append(environment_exports + command)
    run_command(effective_command, phase, verbose)


def change_schroot_profile(name, path, profile, phase, verbose):
    """
    Changes the profile configured for the given schroot.
    :param name: The schroot name.
    :param path: The path to the schroot configuration.
    :param profile: The name of the desired profile.
    :param phase: a message key which describes the current phase. This is used if something fails.
    :param verbose: True, if a more verbose output is desired.
    """
    config = configparser.ConfigParser()
    config.read(path)
    config[name]['profile'] = profile
    _write_config_file_as_root(config, path, phase, verbose)


def change_schroot_name(current_name, new_name, current_path, new_path, phase, verbose):
    """
    Changes the name of the schroot config to the given value. Also renames the config file.
    :param current_name: The current schroot name.
    :param new_name: The new schroot name.
    :param current_path: The current path to the schroot configuration.
    :param new_path: The new path to the schroot configuration.
    :param phase: a message key which describes the current phase. This is used if something fails.
    :param verbose: True, if a more verbose output is desired.
    """
    config = configparser.ConfigParser()
    config.read(current_path)
    config.add_section(new_name)
    config[new_name] = config[current_name]
    config[new_name]['description'] = new_name + ' Slingring Universe'
    config.remove_section(current_name)
    run_command(['sudo', 'rm', current_path], phase, verbose)
    _write_config_file_as_root(config, new_path, phase, verbose)


def _write_config_file_as_root(config_parser, path, phase, verbose):
    with tempfile.TemporaryDirectory() as tempdir:
        file_name = os.path.join(tempdir, 'temp.conf')
        with open(file_name, 'w') as temp_file:
            config_parser.write(temp_file, space_around_delimiters=False)
        command = ['sudo', 'cp', file_name, path]
        run_command(command, phase, verbose)
