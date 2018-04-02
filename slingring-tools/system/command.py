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

from subprocess import PIPE
from subprocess import Popen
from subprocess import run

from resources.messages import get as _


def _command_print(cmd_output, phase, command, verbose, pipe_command=None):
    if cmd_output.returncode:
        if verbose:
            print(_('cmd-error-verbose').format(phase))
        else:
            print(_('cmd-error').format(phase))
            print()
            print(_('stdout').format(phase))
            print(cmd_output.stdout)
            print()
            print(_('stderr').format(phase))
            print(cmd_output.stderr)
        print(_('failed-command').format(' '.join(command)))
        if pipe_command:
            print(_('failed-pipe-command').format(' '.join(pipe_command)))
    return cmd_output


def run_command(command, phase_key, verbose, env=None, shell=False):
    """
    Runs a command on the local machine. The stdout/stderr is hidden, unless an error
    occurs. In that case, an error message containing the stderr is shown and a
    ProcessFailedException is raised. If the verbose flag is set to True, stdout
    and stderr are directly piped to this applications stdout.
    :param command: The command to run as list (e.g. ['ls', '-l', '/etc'])
    :param phase_key: a message key which describes the current phase. This is used if something fails.
    :param verbose: True, if a more verbose output is desired.
    :param env: A dictionary of environment variables for the given command.
    :param shell: Run the command in a shell. Allows use of shell features.
    :return: The process output of the command.
    """
    if verbose:
        result = _command_print(run(command, env=env, shell=shell), phase_key, command, verbose)
    else:
        result = _command_print(run(command, env=env, stdout=PIPE, stderr=PIPE, shell=shell), phase_key, command,
                                verbose)
    if result.returncode:
        raise ProcessFailedException(command, result)

    return result


def run_command_piped(source_command, sink_command, phase_key, verbose, env=None):
    """
    Runs a command piped, so that it's output is piped into another command. Behaves
    like run_command otherwise.
    :param source_command: The command on the source side of the pipe as a list.
    :param sink_command: The command on the sink side of the pipe as a list.
    :param phase_key: a message key which describes the current phase. This is used if something fails.
    :param verbose: True, if a more verbose output is desired.
    :param env: A dictionary of environment variables for the given command.
    :return: The process output of the command.
    """
    source_process = Popen(source_command, stdout=PIPE, env=env)
    if verbose:
        stdout = None
    else:
        stdout = PIPE

    sink_process = Popen(sink_command, stdin=source_process.stdout, stdout=stdout, env=env)
    sink_process.communicate()
    _command_print(sink_process, phase_key, source_command, verbose, pipe_command=sink_command)


def get_command_output(command, phase_key, env=None):
    """
    Runs a command on the local machine. The stdout/stderr is hidden, unless an error
    occurs. In that case, an error message containing the stderr is shown and a
    ProcessFailedException is raised.
    :param command: The command to run as list (e.g. ['ls', '-l', '/etc'])
    :param phase_key: a message key which describes the current phase. This is used if something fails.
    :param env: A dictionary of environment variables for the given command.
    :return: The output of the command as a string.
    """
    result = run_command(command, phase_key, False, env)
    return result.stdout.decode('UTF-8')


class ProcessFailedException(Exception):
    pass

    def __init__(self, command, result):
        """
        :param command: the failed command.
        :param result: the command result.
        """
        self.command = command
        self.result = result
