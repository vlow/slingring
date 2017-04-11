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

import getpass


def retrieve_variables_from_user(variable_dict):
    """
    Takes a variables dictionary from a universe description and
    asks all variables from the user. Variables which' secret flag
    has been set to True are gathered without echo and returned separately.
    :param variable_dict: The variables dict as specified in the universe description.
    :return: the retrieved user vars, the retrieved user secrets as dictionaries
    """
    retrieved_user_vars = dict()
    retrieved_user_secrets = dict()
    for variable in variable_dict:
        if "secret" in variable and variable['secret'] is True:
            retrieved_user_secrets[variable['name']] = getpass.getpass(
                prompt=variable['description'] + ' (will not be echoed): ')
        else:
            retrieved_user_vars[variable['name']] = input(variable['description'] + ': ')
    return retrieved_user_vars, retrieved_user_secrets


def yes_no_prompt(question, default="yes"):
    """

    :param question:
    :param default:
    :return:
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        print(question + prompt)
        choice = input().strip().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' "
                  "(or 'y' or 'n').\n")
