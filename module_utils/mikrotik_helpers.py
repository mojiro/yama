# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Collection of helper functions for mikrotik module"""

import re
from ansible.module_utils.network.mikrotik.valid import hasstring, haslist, \
    hasdict, haskey
from ansible.module_utils.network.mikrotik.strings import wtrim


def branchfix(data):
    """Applies some fixes to branch part of the command.

    :param data: (str) Branch.
    :return: Branch fixed.
    """
    if hasstring(data):
        return re.sub(r'\s\s+', ' ', data.strip()).replace('/ ', '/')

    return ''


def exportfix(data):
    """Converts the multilined exported configuration of a router to single
    line.

    :param data: (str) Exported configuration.
    :return: (str) Configuration.
    """
    if not haslist(data):
        return []

    results = []
    buf = ''

    for line in data:
        if line[-2] == '\\':
            buf += line[:-2]

        else:
            results.append(buf + line)
            buf = ''

    return results


def properties_to_list(data):
    """Converts array of properties to list.

    :param data: (str / list) List or Comma/Space seperated properties.
    :return: (list) List of properties.
    """
    if haslist(data):
        return data

    if hasstring(data):
        return wtrim(data.replace(',', ' ')).split(' ')

    return []


def propvals_to_dict(data):
    """Converts string pairs of properties and values to structured dictionary.

    :param data: (str) Properties and values.
    :return: (dict) Structured dictionary.
    """
    if not hasstring(data):
        return {}

    results = {}

    regex = re.compile(r'(\S+=".+"|\S+=\S+)')
    matches = set(regex.findall(data))

    for match in matches:
        eql = match.find('=')

        results[match[0:eql]] = valuefix(match[eql+1:])

    return results


def dict_to_propvals(data):
    """Converts structured dictionary into string.

    :param data: (dict) Properties and values.
    :return: (str) String.
    """
    if not hasdict(data):
        return ''

    results = ''

    for var in data:
        results += ' ' + var + '=' + data[var]

    return results.strip()


def valuefix(data):
    """Applies some fixes to values.

    :param data: (str) Value input.
    :return: (str) Fixed value.
    """

    if data == 'yes':
        return 'true'

    if data == 'no':
        return 'false'

    return data


def propvals_diff_getvalues(propvals, getvalues):
    """Compares two different sets of properties and values.

    :param propvals: (dict) 1st set.
    :param getvalues: (dict) 2nd set.
    :return: (bool) True if they are same, False if not.
    """
    if not hasdict(propvals):
        return None

    if not haslist(getvalues):
        return True

    for prop in propvals:
        for getvalue in getvalues:
            if haskey(getvalue, prop):
                if propvals[prop] != getvalue[prop]:
                    return True

            else:
                return True

    return False
