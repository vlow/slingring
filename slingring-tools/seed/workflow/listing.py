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

import seed.workflow.tools.paths as paths
from resources.messages import get as _


def list_templates(args):
    """
    Lists all templates on the local machine.
    :param args: The command line arguments as parsed by argparse.
                 This is actually unused, but required by argparse.
    """
    local_images, global_images = _get_images()
    _print_templates(local_images, 'local-images')
    _print_templates(global_images, 'global-images')


def _print_templates(images, key):
    if images:
        print(_(key))
        for image_name in images:
            print('   - {}'.format(image_name))


def _get_images_by_path(path):
    if os.path.exists(path):
        paths_in_image_directory = os.listdir(path)
        return [image_path for image_path in paths_in_image_directory if
                os.path.isdir(os.path.join(path, image_path))]
    else:
        return None


def _get_images():
    local_images_path = paths.local_templates_root_path()
    local_images = _get_images_by_path(local_images_path)
    global_images_path = paths.global_templates_root_path()
    global_images = _get_images_by_path(global_images_path)
    return local_images, global_images
