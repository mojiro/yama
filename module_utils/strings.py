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
    """Equivalent to IFNULL of MySQL

    :param data: Input to be checked
    :param payload: payload to return if input is empty
    :returns: data or payload
    """
    if hasstring(data):
        return data
    return payload


def wtrim(data):
    """Trim white space

    :param data: (str) Input to be trimmed
    :returns: (str) The input trimmed
    """
    if hasstring(data):
        return re.sub(r'\s+', ' ', data).strip()
    return ''


def tofile(path, lines):
    """Saves to file

    :param path: (str) File to write
    :param lines: (list) List of lines to write
    :returns: (bool) True or False
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
    :returns: ([str]) String Array or None on error
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


def loadjson(path):
    """ Load JSON file

    :param path: Path of JSON file to load
    :returns: (dict) Dictionary with the JSON file contents
    """
    results = None
    if isfile(path):
        try:
            handler = open(path)
            results = json.load(handler)
            handler.close()
        except Exception:
            getexcept()
    return results


def readfile(filename, decode64=False):
    """Read file from disk, optionally decodes it from base64

    :param filename: (str) Filename
    :param decode64: (bool) If true, file contents will be decoded by base64
    :return: (str) File contents, if fails returns None
    """
    if not isfile(filename):
        return None
    results = None
    try:
        with open(filename) as handler:
            results = handler.read().strip()
    except IOError:
        return None
    if decode64:
        results = str(base64.b64decode(results), 'utf-8')
    return results


def readjson(filename):
    """Loads the JSON file into a dictionary

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


def readyaml(filename):
    """Loads the YAML file into a dictionary

    :param filename: (str) Filename to load YAML from
    :return: (dict) File contents in dict, None if fails
    """
    if not isfile(filename):
        return None
    results = None
    try:
        with open(filename) as handler:
            results = yaml.load(handler)
    except (IOError, ValueError):
        return None
    return results
