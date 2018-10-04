#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""   """

from ansible.module_utils.basic import AnsibleModule
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
            local=dict(required=True),
            remote=dict(required=True)
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

    if router.connect('sftp'):
        unreachable = 0
        result = router.upload(module.params['local'], module.params['remote'])

    if router.errc():
        failed = 1

    router.disconnect()
    messages.append(router.errors())
    module.exit_json(changed=changed, unreachable=unreachable, failed=failed,
                     result=result, msg=' '.join(messages))


if __name__ == '__main__':
    main()
