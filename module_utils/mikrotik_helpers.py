# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""   """

import re

from ansible.module_utils.network.mikrotik.valid import hasstring, haslist, \
    hasdict, haskey
from ansible.module_utils.network.mikrotik.strings import wtrim

def branchfix(data):
    """
    """
    if hasstring(data):
        return re.sub(r'\s\s+', ' ', data.strip()).replace('/ ', '/')

    return ''


def exportfix(data):
    """Converts the multilined exported configuration of a router
    to single line.

    :param data: (str) Exported configuration
    :returns: (str) Configuration
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
    """Converts array of properties to list

    :param data: (str / list) List or Comma/Space seperated properties
    :returns: (list) List of properties
    """
    if haslist(data):
        return data

    if hasstring(data):
        return wtrim(data.replace(',', ' ')).split(' ')

    return []


def propvals_to_dict(data):
    """action_dict
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


def dict_to_propvals(data, disabled=True, comment=True):
    """action_make
    """
    if not hasdict(data):
        return ''

    results = ''

    if not disabled:
        if 'disabled' in data:
            del data['disabled']

    if not comment:
        if 'comment' in data:
            del data['comment']

    for var in data:
        results += ' ' + var + '=' + data[var]

    return results.strip()


def valuefix(data):
    """
    """

    if data == 'yes':
        return 'true'

    if data == 'no':
        return 'false'

    return data

def propvals_diff_getvalues(propvals, getvalues):
    """
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
