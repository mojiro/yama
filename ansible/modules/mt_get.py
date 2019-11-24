#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Yama: Retrieves values from host. Optionally outputs the results to file.
<ansible.modules.remote_management.yama.mt_get>"""

import os
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.yama.strings import writefile, \
    ifnull
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
            properties=dict(required=True),
            find=dict(required=False, type='str'),
            output=dict(required=False, type='str'),
            format=dict(required=False, type='str', default='json'),
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
        csvout = format == 'csv'
        result = device.getvalues(module.params['branch'],
                                  module.params['properties'],
                                  ifnull(module.params['find'], ''),
                                  csvout=csvout)

        if result:
            if module.params['output']:
                if not writefile(module.params['output'], result):
                    messages.append('Unable to create Output File.')

    if device.errc():
        failed = 1

    device.disconnect()
    messages.append(device.errors())
    messages.append(str(globals()))
    module.exit_json(changed=changed, unreachable=unreachable, failed=failed,
                     result=result, msg=' '.join(messages))


if __name__ == '__main__':
    main()
