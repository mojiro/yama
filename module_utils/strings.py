# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Module String Helpers <module_utils.strings>

String related functions."""

import re
import csv
import json
import yaml
from ansible.module_utils.network.mikrotik.exception import getexcept
from ansible.module_utils.network.mikrotik.valid import hasstring, haslist, \
    isdir, isfile


def ifnull(data, payload=''):
    """Equivalent to IFNULL of MySQL.

    :param data: (str) Input to be checked.
    :param payload: (str) Payload to return if input is empty.
    :return: (str) Data or payload.
    """
    if hasstring(data):
        return data
    return payload


def wtrim(data):
    """Trim white space.

    :param data: (str) Input to be trimmed.
    :return: (str) The input trimmed.
    """
    if hasstring(data):
        return re.sub(r'\s+', ' ', data).strip()
    return ''


def csv_parse(lines):
    """Converts the CSV-expected input to array.

    :param lines: (str / [str]) CSV input - it can either linefeeded string or
        list.
    :return: ([str]) String Array or None on error.
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


def writefile(filename, lines):
    """Saves lines to file.

    :param filename: (str) File to write.
    :param lines: (list) List of lines to write.
    :return: (bool) True on success, False on failure.
    """
    if not isdir('/'.join(filename.split('/')[:-1]), True):
        return False
    if not haslist(lines):
        return False
    try:
        handler = open(filename, 'w')
        for line in lines:
            handler.write(line + '\n')
        handler.close()
        return True
    except Exception:
        return getexcept()
    return False


def readfile(filename):
    """Loads file from disk.

    :param filename: (str) File to read.
    :return: (str) File contents, if fails returns None.
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


def writejson(filename, data):
    """Saves the (dict) data to JSON file.

    :param filename: (str) Filename to write JSON to.
    :param data: (dict) Dict to save to JSON file.
    :return: (bool) True on success, False on failure.
    """
    if not hasstring(filename):
        return False
    if not isdir('/'.join(filename.split('/')[:-1]), True):
        return False
    if not isinstance(data, dict):
        return False
    try:
        with open(filename, 'w') as handler:
            json.dump(data, handler)
    except IOError:
        return getexcept()
    return True


def readjson(filename):
    """Loads the JSON file into a dictionary.

    :param filename: (str) Filename to load JSON from.
    :return: (dict) File contents in dict, None if fails.
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
    """Loads the YAML file into a dictionary.

    :param filename: (str) Filename to load YAML from.
    :return: (dict) File contents in dict, None if fails.
    """
    if not isfile(filename):
        return None
    results = None
    try:
        with open(filename) as handler:
            results = yaml.safe_load(handler)
    except (IOError, ValueError):
        return None
    return results
