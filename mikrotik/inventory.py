#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""   """

import argparse
from ansible.module_utils.yama.valid import hasstring
import ansible.module_utils.network.mikrotik.mongodb as mongodb

CONFFILE = '/etc/ansible/config/mikrotik/mongodb.json'
args = None


def parse_cli_args():
    """Command line argument processing
    """
    parser = argparse.ArgumentParser(
        description='Produce an Ansible Inventory file based on MongoDB entries')

    parser.add_argument('--list', action='store_true',
                        default=True, help='List hosts (default: True)')

    parser.add_argument('--host', action='store',
                        help='Get all the variables about a specific host')

    return parser.parse_args()


def main():
    result = ''
    inventory = mongodb.Database(CONFFILE)

    if hasstring(args.host):
        result = inventory.gethost(args.host)

    elif args.list:
        result = inventory.getlist()

    print result


if __name__ == '__main__':
    args = parse_cli_args()
    main()
