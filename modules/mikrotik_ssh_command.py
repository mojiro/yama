#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" Executes a single command. Optionally outputs the results to file. """

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.mikrotik.strings import tofile
import ansible.module_utils.network.mikrotik.mikrotik as mikrotik

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
            port=dict(required=False, type='int', default=22),
            username=dict(required=False, default='admin'),
            password=dict(required=False),
            pkeyfile=dict(required=False),
            branchfile=dict(required=False, default='mikrotik/branch.json'),
            db_conffile=dict(required=False, default='mikrotik/mongodb.json'),
            command=dict(required=True),
            raw=dict(required=False, default=False),
            output=dict(required=False)
        )
    )

    router = mikrotik.Router(
        module.params['hostname'],
        module.params['port'],
        module.params['username'],
        module.params['password'],
        module.params['pkeyfile'],
        PATH + '/' + module.params['branchfile'],
        PATH + '/' + module.params['db_conffile']
    )

    if router.connect():
        unreachable = 0
        result = router.command(module.params['command'],
                                module.params['raw'])

        if result and module.params['output']:
            if tofile(module.params['output'], result):
                changed = 1
            else:
                messages.append('Unable to create Output File.')

    router.disconnect()

    if router.errc():
        messages.append(router.errors())

    if messages:
        failed = 1

    module.exit_json(changed=changed, unreachable=unreachable, failed=failed,
                     result=result, msg=' '.join(messages))


if __name__ == '__main__':
    main()
