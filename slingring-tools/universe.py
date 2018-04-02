#!/usr/bin/python3

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
import argparse

from universe.workflow.creation import install_universe_by_args
from universe.workflow.deletion import remove_universe_by_args
from universe.workflow.export import export_universe_by_args
from universe.workflow.listing import list_universes_by_args
from universe.workflow.update import update_universe_by_args
from universe.workflow.upgrade import upgrade_universe_by_args


def main():
    process_cli_arguments()


def process_cli_arguments():
    """
    Parses the command line arguments and calls the according
    function for the requested operation or shows the CLI help
    if no operation has been requested.
    """
    parser = argparse.ArgumentParser(description="universe manages the slingring universes installed on this system.")
    parser.add_argument('-v', '--verbose', action='store_true')

    subparsers = parser.add_subparsers(help='the desired operation', dest='operation', metavar='operation')

    list_parser = subparsers.add_parser('list', help='list installed universes')
    list_parser.set_defaults(func=list_universes_by_args)

    install_parser = subparsers.add_parser('install', help='installs a new universe from a seed')
    install_parser.add_argument('seed', metavar='DIRECTORY', type=str,
                                help='the seed directory to build the universe from')
    install_parser.add_argument('-t', '--temp', type=str, help='the temp directory to use (defaults to system temp)')
    install_parser.set_defaults(func=install_universe_by_args)

    export_parser = subparsers.add_parser('export', help='exports a universe for long term storage or as backup')
    export_parser.add_argument('universe', help='the universe which should be exported')
    export_parser.set_defaults(func=export_universe_by_args)

    remove_parser = subparsers.add_parser('remove', help='removes an existing universe')
    remove_parser.add_argument('universe', help='the universe which should be removed')
    remove_parser.set_defaults(func=remove_universe_by_args)

    update_parser = subparsers.add_parser('update', help='re-runs the Ansible playbook for an existing universe')
    update_parser.add_argument('universe', help='the universe which should be updated')
    update_parser.set_defaults(func=update_universe_by_args)

    upgrade_parser = subparsers.add_parser('upgrade', help='upgrades an existing universe to a new seed version')
    upgrade_parser.add_argument('universe', help='the universe which should be upgraded')
    upgrade_parser.add_argument('seed', metavar='DIRECTORY', type=str,
                                help='the seed directory to upgrade the universe to')
    upgrade_parser.set_defaults(func=upgrade_universe_by_args)

    args = parser.parse_args()

    if not args.operation:
        parser.print_help()
        exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
