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

from common.paths import local_home


def local_templates_root_path():
    return os.path.join(local_home(), '.slingring/templates')


def global_templates_root_path():
    return '/usr/share/slingring/templates'


def template_location(template_name):
    local_image_path = os.path.join(local_templates_root_path(), template_name)
    if os.path.exists(local_image_path):
        return local_image_path

    global_image_path = os.path.join(global_templates_root_path(), template_name)
    if os.path.exists(global_image_path):
        return global_image_path

    return None


def template_file_location_in_seed(seed_path):
    return os.path.join(seed_path, 'template.yml')


def template_file_location(template_name):
    return os.path.join(template_location(template_name), 'template.yml')


def universe_file_location(template_name):
    return os.path.join(template_location(template_name), 'universe.yml')
