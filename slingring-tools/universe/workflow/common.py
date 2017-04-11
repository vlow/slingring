import os
import time

from resources.messages import get as _
from universe.workflow.tools.interaction import retrieve_variables_from_user


def gather_variables_from_user(seed_dictionary):
    """
    Gathers the variables defined in the given description.
    :param seed_dictionary: The seed universe file contents (as a dictionary).
    :return: the retrieved user vars, the retrieved user secrets as dictionaries
             or None, None if no variables are defined in the description.
    """
    if 'variables' in seed_dictionary:
        print('')
        print(_('input-header'))
        return retrieve_variables_from_user(seed_dictionary['variables'])
    else:
        return None, None


def create_slingring_vars_dict(user_name, user_group, user_home, mirror, universe_name, universe_version):
    """
    Creates the Slingring vars dictionary from the given values.
    :param user_name: The user name
    :param user_group: The user's primary group
    :param user_home: The user's home directory within the chroot
    :param mirror: The debootstrap mirror
    :param universe_name: The universe name
    :param universe_version: The universe version
    :return: The Slingring vars dictionary.
    """
    return {'user_name': user_name, 'user_group': user_group,
            'user_home': user_home, 'mirror': mirror,
            'universe_name': universe_name, 'universe_version': str(universe_version),
            'current_date': str(time.strftime('%Y/%m/%d'))}


def get_seed_directory_from_argument(seed_argument):
    if os.path.isdir(seed_argument):
        return seed_argument
    else:
        return os.path.dirname(seed_argument)


def print_spaced(text):
    """
    Prints the text with a new line before and after it.
    :param text: The text.
    """
    print('\n{}\n'.format(text))
