# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Path related functions"""

from ansible.module_utils.network.mikrotik.exception import getexcept
from ansible.module_utils.network.mikrotik.valid import hasstring, haslist, \
    isdir, isfile


def pathsplit(data, verify=True):
    """
    """
    if not hasstring(data):
        return None

    path = data.strip().split('/')
    directory = path[:-1]
    files = [path[-1]]

    if path[-1] == '*':
        files = ['*']

        if verify and isdir(directory):

    return (directory, files)
