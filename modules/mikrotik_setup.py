#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" Imports hosts to inventory """

from ansible.module_utils.basic import AnsibleModule
import ansible.module_utils.network.mikrotik.mongodb as mongodb

PATH = '/etc/ansible/config'


def main():
    messages = []
    result = []
    changed = 0
    failed = 0
    unreachable = 1
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(required=True),
            db_conffile=dict(required=False, default='mikrotik/mongodb.json')
        )
    )

    inventory = mongodb.Database(PATH + '/' + module.params['db_conffile'])

    if inventory.connect():
        unreachable = 0

        if inventory.addhost(module.params['hostname']):
            changed = 1

    inventory.disconnect()

    if inventory.errc():
        messages.append(inventory.errors())
        failed = 1

    module.exit_json(changed=changed, unreachable=unreachable, failed=failed,
                     result=result, msg=' '.join(messages))


if __name__ == '__main__':
    main()
