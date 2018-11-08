# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""String related functions"""

import base64
import re
import csv
import json
import yaml

from ansible.module_utils.network.mikrotik.exception import getexcept
from ansible.module_utils.network.mikrotik.valid import hasstring, haslist, \
    isdir, isfile


def ifnull(data, payload=''):
    """Equivalent to IFNULL of MySQL.

    :param data: Input to be checked
    :param payload: payload to return if input is empty
    :return: data or payload
    """
    if hasstring(data):
        return data
    return payload


def wtrim(data):
    """Trim white space.

    :param data: (str) Input to be trimmed
    :return: (str) The input trimmed
    """
    if hasstring(data):
        return re.sub(r'\s+', ' ', data).strip()
    return ''


def tofile(path, lines):
    """Saves lines to file.

    :param path: (str) File to write
    :param lines: (list) List of lines to write
    :return: (bool) True or False
    """
    if not isdir('/'.join(path.split('/')[:-1]), True):
        return False
    if not haslist(lines):
        return False
    try:
        handler = open(path, 'w')
        for line in lines:
            handler.write(line + '\n')
        handler.close()
        return True
    except Exception:
        return getexcept()
    return False


def csv_parse(lines):
    """Converts the CSV-expected input to array.

    :param lines: (str / [str]) CSV input - it can either linefeeded string or
                                list
    :return: ([str]) String Array or None on error
    """
    if not lines:
        return None
    if not haslist(lines):
        if hasstring(lines):
            lines = lines.split('\n')
        else:
            return None
    try:
        return list(csv.reader(lines, delimiter=',', quotechar='"'))
    except Exception:
        getexcept()
        return None


def readfile(filename):
    """Read file from disk.

    :param filename: (str) Filename
    :return: (str) File contents, if fails returns None
    """
    if not isfile(filename):
        return None
    results = None
    try:
        with open(filename) as handler:
            results = handler.read()
    except IOError:
        return None
    return results


def readjson(filename):
    """Loads the JSON file into a dictionary.

    :param filename: (str) Filename to load JSON from
    :return: (dict) File contents in dict, None if fails
    """
    if not isfile(filename):
        return None
    results = None
    try:
        with open(filename) as handler:
            results = json.load(handler)
    except (IOError, ValueError):
        return None
    return results
