#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Imports facts to inventory"""

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
            host=dict(required=True, type='str'),
            port=dict(required=False, type='int', default=22),
            username=dict(required=False, type='str', default='admin'),
            password=dict(required=False, type='str'),
            pkeyfile=dict(required=False, type='str'),
            branchfile=dict(required=False, type='str',
                            default='mikrotik/branch.json'),
            db_conffile=dict(required=False, type='str',
                             default='mikrotik/mongodb.json'),
            branch=dict(required=True, type='str'),
            properties=dict(required=True),
            find=dict(required=False, type='str')
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
        result = router.getvalues(module.params['branch'],
                                  module.params['properties'],
                                  ifnull(module.params['find'], ''))

        if result:
            router.store(module.params['branch'], result)

    if router.errc():
        failed = 1

    router.disconnect()
    messages.append(router.errors())
    module.exit_json(changed=changed, unreachable=unreachable, failed=failed,
                     result=result, msg=' '.join(messages))


if __name__ == '__main__':
    main()
