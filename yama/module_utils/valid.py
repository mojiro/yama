# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Several validation functions in one module <module_utils.valid>"""

import os
import re
from ansible.module_utils.yama.exception import getexcept


def hasstring(data):
    """It validates that given input is a string with content.

    :param data: (str) Input string.
    :return: (bool) True or False.
    """
    if not data:
        return False
    if isinstance(data, basestring):
        return True
    if isinstance(data, str):
        return True
    return False


def haslist(data):
    """It validates that given input is a list with content.

    :param data: (str) Input list.
    :return: (bool) True or False.
    """
    if not data:
        return False
    if isinstance(data, list):
        return True
    return False


def hasdict(data):
    """It validates that given input is a dictionary with content.

    :param data: (str) Input dictionary.
    :return: (bool) True or False.
    """
    if not data:
        return False
    if isinstance(data, dict):
        return True
    return False


def haskey(data, key, instance=None):
    """It validates that given key exists in data dictionary but also it
    contains data.

    :param data: (dict) Input dictionary.
    :param key: (str) Key to be checked.
    :param instance: (instance) Instance to check.
    :return: (bool) True or False.
    """
    if not hasdict(data):
        return False
    if not hasstring(key):
        return False
    if key in data:
        if data[key]:
            if instance:
                if isinstance(data[key], instance):
                    return True
            else:
                return True
    return False


def haskeys(data, keys):
    """It validates that given keys exist in data dictionary but also they
    contain data.

    :param data: (dict) Input dictionary.
    :param keys: (list) List of keys to be checked.
    :return: (bool) True or False.
    """
    if not hasdict(data):
        return False
    if not haslist(keys):
        return False
    for key in keys:
        if key not in data:
            return False
        if not data[key]:
            return False
    return True


def isdir(data, makedirs=False):
    """Directory validation and auto-creation.

    :param data: (str) Directory.
    :return: (bool) True or False.
    """
    if not hasstring(data):
        return False
    if makedirs:
        if not os.path.isdir(data):
            try:
                os.makedirs(data)
            except Exception:
                return getexcept()
    return os.path.isdir(data)


def isfile(data):
    """File validation.

    :param data: (str) Filename.
    :return: (bool) True or False.
    """
    if not hasstring(data):
        return False
    return os.path.isfile(data)


def ismacaddress(data):
    """MAC Address validation.

    :param data: (str) MAC Address.
    :return: (bool) True or False.
    """
    if not hasstring(data):
        return False
    regex = re.compile(r'^([0-9abcdef]{2}:){5}[0-9abcdef]{2}$')
    if regex.match(data.lower()):
        return True
    return False


def isip(data):
    """IP (v4/v6) Address validation.

    :param data: (str) IP (v4/v6) Address.
    :return: (bool) True or False.
    """
    return isipv4(data) or isipv6(data)


def isipv4(data):
    """IPv4 Address validation.

    :param data: (str) IPv4 Address.
    :return: (bool) True or False.
    """
    if not hasstring(data):
        return False
    regex = re.compile(r'^((25[0-5]|[01]?[0-9]{1,2}|2[0-4][0-9])\.){3}(25[0-5]'
                       r'|[01]?[0-9]{1,2}|2[0-4][0-9])$')
    if regex.match(data):
        return True
    return False


def isipv6(data):
    """IPv6 Address validation.

    :param data: (str) IPv6 Address.
    :return: (bool) True or False.
    """
    if not hasstring(data):
        return False
    regex = re.compile(r'^(?!.*::.*::)(?:(?!:)|:(?=:))(?:[0-9a-f]{0,4}(?:(?<=:'
                       r':)|(?<!::):)){6}(?:[0-9a-f]{0,4}(?:(?<=::)|(?<!::):)['
                       r'0-9a-f]{0,4}(?:(?<=::)|(?<!:)|(?<=:)(?<!::):)|(?:25[0'
                       r'-4]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-4]|2[0-4]\d|'
                       r'1\d\d|[1-9]?\d)){3})$')
    if regex.match(data.lower()):
        return True
    return False


def ishostname(data):
    """Hostname validation.

    :param data: (str) Hostname.
    :return: (bool) True or False.
    """
    if not hasstring(data):
        return False
    if len(data) > 255:
        return False
    regex = re.compile(r'^([0-9a-z-]+\.?)+$')
    if regex.match(data.lower()):
        return True
    return False


def ishost(data):
    """IP Address and Host validation.

    :param data: (str) IP (v4/v6) Address or Hostname.
    :return: (bool) True or False.
    """
    return isip(data) or ishostname(data)


def isport(data):
    """TCP/UDP Port validation.

    :param data: (int / long) Port.
    :return: (bool) True or False.
    """
    if not isinstance(data, (int, long)):
        try:
            data = int(data)
        except Exception:
            return getexcept()
    if data < 1 or data > 65536:
        return False
    return True


def isusername(data):
    """Username validation.

    :param data: (str) Username.
    :return: (bool) True or False.
    """
    if not hasstring(data):
        return False
    regex = re.compile(r'^([0-9a-z-_]+\.?)*[0-9a-z-_]+$')
    if regex.match(data.lower()):
        return True
    return False


def isemail(data):
    """Email validation.

    :param data: (str) Email.
    :return: (bool) True or False.
    """
    if not hasstring(data):
        return False
    regex = re.compile(r'^[0-9a-z-_.+]+@([0-9a-z-]+\.?)+$')
    if regex.match(data.lower()):
        return True
    return False
