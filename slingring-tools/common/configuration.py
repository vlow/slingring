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

import yaml

mandatory_attributes = ['arch', 'mirror', 'name', 'suite']

_default_config = {
    "universe-directory": "/var/lib/slingring"
}


class ConfigurationHandler:
    """
    A simple helper class which retrieves
    configuration values from sources with different priorities:

        1. Process Configuration (injectable)
        2. Local Configuration (~/.slingring/configuration.yml)
        3. Global Configuration (/etc/slingring/configuration.yml)

    When a configuration file has been parsed once, its contents are
    cached and will be quickly available in subsequent calls.
    """

    def __init__(self):
        self._process_config = {}
        self._local_config = None
        self._global_config = None

    def get_config_value(self, key):
        """
        Gets the value from the configuration source with
        the highest priority.
        :param key: The key of the desired value.
        :return: The desired value.
        """
        config_value = self._get_process_config_value(key)
        if config_value:
            return config_value
        config_value = self._get_local_config_value(key)
        if config_value:
            return config_value
        config_value = self._get_global_config_value(key)
        if config_value:
            return config_value
        return self._get_default_config_value(key)

    def set_config_value(self, key, value):
        """
        Sets a configuration value in the process configuration.
        :param key: The configuration key.
        :param value: The configuration value.
        """
        self._process_config[key] = value

    def _get_process_config_value(self, key):
        if key in self._process_config:
            return self._process_config[key]
        return None

    def _get_local_config_value(self, key):
        if not self._local_config:
            self._load_local_config()
        if key in self._local_config:
            return self._local_config[key]
        return None

    def _get_global_config_value(self, key):
        if not self._global_config:
            self._load_global_config()
        if key in self._global_config:
            return self._global_config[key]
        return None

    @staticmethod
    def _get_default_config_value(key):
        return _default_config[key]

    def _load_local_config(self):
        local_home = os.getenv('HOME')
        local_config_path = os.path.join(local_home, '.slingring', 'configuration.yaml')
        self._local_config = _load_yaml_file_safely(local_config_path)

    def _load_global_config(self):
        global_config_path = os.path.join('/etc', 'slingring', 'configuration.yaml')
        self._global_config = _load_yaml_file_safely(global_config_path)


def read_seed_file(path):
    """
    Reads a seed yaml configuration file and returns its content as dictionary.
    Performs checks for mandatory attributes and throws an MissingAttributesError
    if attributes are missing.
    :param path: the path to the configuration file
    :return: the file content as object
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    configuration = _load_yaml_file(path)

    # validation
    if not all(attribute in configuration for attribute in mandatory_attributes):
        raise MissingAttributesError(set(mandatory_attributes) - set(configuration.keys()))

    return configuration


def write_installation_configuration(path, location):
    _write_yaml_file(path, {'location': location})


def read_configuration(path):
    """
    Reads the configuration file from the given path.
    Raises a FileNotFoundError, if the path does not exist.
    :param path: The location of the configuration file.
    :return: The contents of the configuration as a dictionary.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    return _load_yaml_file(path)


def _load_yaml_file_safely(path):
    if os.path.exists(path):
        return _load_yaml_file(path)
    return {}


def _load_yaml_file(path):
    """
    Reads a yaml configuration file and returns its content as dictionary.
    :param path: the path to the configuration file
    :return: the file content as object
    """
    yaml_file = open(path, 'r')
    configuration = yaml.safe_load(yaml_file)
    return configuration


def _write_yaml_file(path, content):
    """
    Reads a yaml configuration file and returns its content as dictionary.
    :param path: the path to the configuration file
    :return: the file content as object
    """
    yaml_file = open(path, 'w')
    yaml.safe_dump(content, yaml_file, default_flow_style=False)


class MissingAttributesError(Exception):
    def __init__(self, missing_attributes):
        self.missing_attributes = missing_attributes
