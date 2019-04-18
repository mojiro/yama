#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Sets values to host"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.mikrotik.strings import ifnull
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
            host=dict(required=True),
            port=dict(required=False, type='int', default=22),
            username=dict(required=False, default='admin'),
            password=dict(required=False),
            pkeyfile=dict(required=False),
            branchfile=dict(required=False, default='mikrotik/branch.json'),
            db_conffile=dict(required=False, default='mikrotik/mongodb.json'),
            branch=dict(required=True),
            action=dict(required=True),
            propvals=dict(required=False),
            find=dict(required=False)
        )
    )

    router = mikrotik.Router(
        module.params['host'],
        module.params['port'],
        module.params['username'],
        module.params['password'],
        module.params['pkeyfile'],
        PATH + '/' + module.params['branchfile'],
        PATH + '/' + module.params['db_conffile']
    )

    if router.connect():
        unreachable = 0
        branch = module.params['branch']
        action = module.params['action']
        propvals = module.params['propvals']
        find = ifnull(module.params['find'], '')

        if action == 'add':
            result = router.addentry(branch, propvals)

        elif action == 'remove':
            result = router.removeentry(branch, find)

        elif action == 'set':
            result = router.setvalues(branch, propvals, find)

        if result:
            changed = 1

    if router.errc():
        failed = 1

    router.disconnect()
    messages.append(router.errors())
    module.exit_json(changed=changed, unreachable=unreachable, failed=failed,
                     result=result, msg=' '.join(messages))


if __name__ == '__main__':
    main()
