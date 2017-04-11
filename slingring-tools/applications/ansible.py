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
import tempfile

import yaml

from system import key
from system.command import run_command
from system.command import run_command_piped
from system.pipe import PipeThread


def run_playbook(playbook_location, verbose, vault_pass=None):
    """
    Runs a playbook in a change root.

    :param playbook_location: The location of the playbook file.
    :param verbose: True, if a more verbose output should be used.
    :param vault_pass: If the playbook references an encrypted Ansible vault, this is the password to decrypt it.
    """
    # Some distributions (e.g. Arch) have fewer bin paths in the PATH variable.
    # This causes plain ubuntu/debian-chroots to fail. Since this is what
    # Ansible does, so we extend the path accordingly.
    env = os.environ.copy()
    env["PATH"] += ':/usr/sbin:/sbin:/bin'

    inventory_file_path = os.path.join(playbook_location, 'hosts')
    playbook_file_path = os.path.join(playbook_location, 'main.yml')
    vars_reference = '@' + os.path.join(playbook_location, 'slingring_vars.yml')
    user_vars_reference = '@' + os.path.join(playbook_location, 'slingring_user_vars.yml')
    secret_user_vars_reference = '@' + os.path.join(playbook_location, 'slingring_user_secrets.yml')
    cmd = ['sudo', 'ansible-playbook', '--inventory', inventory_file_path,
           playbook_file_path, '--extra-vars', vars_reference, '--extra-vars', user_vars_reference]
    with tempfile.TemporaryDirectory() as tempdir:
        if vault_pass:
            cmd.append('--extra-vars')
            cmd.append(secret_user_vars_reference)
            cmd.append('--vault-password-file')
            random_string = key.create_random_password(8)
            pipe_path = os.path.join(tempdir, random_string)
            cmd.append(pipe_path)
            PipeThread(pipe_path, vault_pass).start()
        run_command(cmd, 'ansible_phase', verbose, env)


def write_vars_file(path, user_vars, namespace):
    """
    Writes a user vars file to the given location.
    :param path: the target path (including file name)
    :param user_vars: the vars as a dict
    :param namespace: the namespace used in the yaml file (e.g. 'uservars' -> uservars.var1, uservars.var2 etc.)
    """
    effective_dict = dict({namespace: user_vars})
    yaml_file = open(path, 'w')
    yaml.safe_dump(effective_dict, yaml_file, default_flow_style=False)


def write_vars_vault_file(path, user_vars, password, namespace, phase_key, verbose):
    """
    Writes a user vars file encrypted to the given location.
    :param path: the target path (including file name)
    :param user_vars: the vars as a dict
    :param password: the password to encrypt the vault file with
    :param namespace: the namespace used in the yaml file (e.g. 'uservars' -> uservars.var1, uservars.var2 etc.)
    :param phase_key: a message key which describes the current phase. This is used if something fails.
    :param verbose: True, if a more verbose output is desired.
    """
    effective_dict = dict({namespace: user_vars})
    file_content = yaml.dump(effective_dict, default_flow_style=False)
    with tempfile.TemporaryDirectory() as tempdir:
        random_string = key.create_random_password(8)
        pipe_path = os.path.join(tempdir, random_string)

        # start a thread writing to a named pipe @ pipe_path in background, so we don't block
        pipe_thread = PipeThread(pipe_path, password)
        pipe_thread.start()

        source_command = ['echo', file_content]
        sink_command = ['ansible-vault', 'encrypt', '--output', path, '--vault-password-file', pipe_path]
        run_command_piped(source_command, sink_command, phase_key, verbose)
