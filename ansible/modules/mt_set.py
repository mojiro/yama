#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Yama: Sets values to host.
<ansible.modules.remote_management.yama.mt_set>"""

import os
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.yama.strings import ifnull
from ansible.module_utils.remote_management.yama.mikrotik import Router

PATH = '/etc/ansible/config'


def main():
    """
    """
    messages = []
    result = []
    changed = 0
    unreachable = 1
    failed = 0
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True, type='str'),
            port=dict(required=False, type='int', default=22),
            username=dict(required=False, type='str', default='admin'),
            password=dict(required=False, type='str'),
            pkey_string=dict(required=False, type='str'),
            pkey_file=dict(required=False, type='str'),
            branch=dict(required=True, type='str'),
            action=dict(required=True, type='str'),
            propvals=dict(required=False, type='str'),
            find=dict(required=False, type='str'),
            branch_file=dict(required=False, type='str',
                             default='yama/mikrotik_branch.json')
        )
    )

    host = module.params['host']
    port = module.params['port']
    username = module.params['username']
    password = module.params['password']
    pkey_string = module.params['pkey_string']
    pkey_file = module.params['pkey_file']
    branch_file = os.path.join(PATH, module.params['branch_file'])

    device = Router(host, port=port, username=username, password=password,
                    pkey_string=pkey_string, pkey_file=pkey_file,
                    branch_file=branch_file)

    if device.connect():
        unreachable = 0
        branch = module.params['branch']
        action = module.params['action']
        propvals = module.params['propvals']
        find = ifnull(module.params['find'], '')

        if action == 'add':
            result = device.addentry(branch, propvals)

        elif action == 'remove':
            result = device.removeentry(branch, find)

        elif action == 'set':
            result = device.setvalues(branch, propvals, find)

        if result:
            changed = 1

    if device.errc():
        failed = 1

    device.disconnect()
    messages.append(device.errors())
    module.exit_json(changed=changed, unreachable=unreachable, failed=failed,
                     result=result, msg=' '.join(messages))


if __name__ == '__main__':
    main()
