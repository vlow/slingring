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

from seed.workflow.creation import create_seed
from seed.workflow.listing import list_templates


def main():
    parse_arguments()


def parse_arguments():
    parser = argparse.ArgumentParser(description='seed bootstraps new slingring universe seeds.')
    subparsers = parser.add_subparsers(help='the desired operation', dest='operation', metavar='operation')

    list_parser = subparsers.add_parser('list', help='list available templates')
    list_parser.set_defaults(func=list_templates)

    create_parser = subparsers.add_parser('create', help='create new universe from installed template')
    create_parser.set_defaults(func=create_seed)

    create_parser.add_argument('name', metavar='NAME', type=str, help='the desired name of the new universe')
    create_parser.add_argument('directory', metavar='DIRECTORY', type=str,
                               help='the directory in which the universe description shall be created', nargs='?',
                               default='./')
    create_parser.add_argument('-t', '--template', type=str, default='default')

    args = parser.parse_args()

    if not args.operation:
        parser.print_help()
        exit(1)

    args.func(args)


if __name__ == '__main__':
    main()
