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
import datetime
import glob
import os
import shutil
import subprocess

from jinja2 import Undefined, Environment

import applications.figlet as figlet
from common.configuration import read_configuration
from resources.messages import get as _
from seed.workflow.tools.paths import template_file_location_in_seed, template_file_location, template_location, \
    universe_file_location


def create_seed(args):
    """"
    Creates a new universe seed from a template.
    :param args: The command line arguments as parsed by argparse.
                 This is expected to contain the following information:
                    - name: The intended name for the seed.
                    - directory: The root directory in which the seed should be created.
                                 The complete resulting directory is root + name.
                    - template: The template name (e.g. 'default'). The template will be
                                loaded from the local home. If it cannot be found in the
                                local home, it will be taken from the global share.
    """
    universe_name = args.name
    root_dir = args.directory
    template_name = args.template

    seed_dir = os.path.join(args.directory, args.name)

    _validate_template(template_name)

    if os.path.exists(seed_dir):
        print(_('directory-exists').format(universe_name, root_dir))
        exit(1)

    _copy_base_image(universe_name, template_name, root_dir)

    # Fill in templates, if filters are defined.
    template_path = template_file_location(template_name)
    if os.path.exists(template_path):
        template_config = read_configuration(template_path)
        template_filter_expressions = template_config.get('template_filter', [])
        if template_filter_expressions:
            template_blacklist_expressions = template_config.get('template_blacklist', [])
            result_dir = os.path.join(root_dir, universe_name)
            template_files = _find_template_files(result_dir, template_filter_expressions,
                                                  template_blacklist_expressions)
            variables = _get_variable_dict(args.name)
            for file in template_files:
                _fill_in_template(file, variables)


def _validate_template(template_name):
    template_path = template_location(template_name)
    if not template_path or not os.path.exists(template_path):
        print(_('template-not-found').format(template_name))
        exit(1)
    universe_file_path = universe_file_location(template_name)
    if not os.path.exists(universe_file_path):
        print(_('template-invalid').format(template_name))
        exit(1)


def _copy_base_image(universe_name, template_name, root_dir):
    source_dir = template_location(template_name)
    target_dir = os.path.join(root_dir, universe_name)
    shutil.copytree(source_dir, target_dir)

    # the template file is only for the bootstrapper and should not be part of the seed.
    template_file_path = template_file_location_in_seed(target_dir)
    subprocess.call(['rm', template_file_path])


def _find_template_files(seed_path, filter_expressions, blacklist_expressions):
    filter_files = set()
    blacklist_files = set()
    for expression in filter_expressions:
        expression_path = os.path.join(seed_path, expression)
        filter_files = filter_files.union(glob.glob(expression_path, recursive=True))
    for expression in blacklist_expressions:
        expression_path = os.path.join(seed_path, expression)
        blacklist_files = blacklist_files.union(glob.glob(expression_path, recursive=True))
    return [file for file in filter_files if file not in blacklist_files]


def _get_variable_dict(universe_name):
    now = datetime.datetime.now()
    version = '{}.{}.0'.format(now.year, now.month)
    name_ascii_art = figlet.get_ascii_art_text(universe_name)

    return {'bootstrap': {'universe_name': universe_name,
                          'universe_version': version,
                          'ascii_art': {'universe_name': name_ascii_art}}}


def _fill_in_template(file_location, value_dict):
    with open(file_location, 'r') as file:
        file_contents = file.read()
        filled_out_content = env.from_string(file_contents).render(value_dict)

    with open(file_location, 'w') as file:
        file.write(filled_out_content)


env = Environment(block_start_string='<%', block_end_string='%>', variable_start_string='<<', variable_end_string='>>',
                  comment_start_string='<#', comment_end_string='#>')
