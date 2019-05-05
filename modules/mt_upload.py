#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""   """

from ansible.module_utils.basic import AnsibleModule
import ansible.module_utils.network.mikrotik.sftp_client as sftp_client


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
            username=dict(required=False, type='str', default='root'),
            password=dict(required=False, type='str'),
            pkeyfile=dict(required=False, type='str'),
            local=dict(required=True, type='str'),
            remote=dict(required=True, type='str')
        )
    )

    router = mikrotik.sftp_client(
        module.params['host'],
        module.params['port'],
        module.params['username'],
        module.params['password'],
        module.params['pkeyfile']
    )

    if router.connect():
        unreachable = 0
        result = router.upload(module.params['local'], module.params['remote'])

        # Should check if files got "changed"

    if router.errc():
        failed = 1

    router.disconnect()
    messages.append(router.errors())
    module.exit_json(changed=changed, unreachable=unreachable, failed=failed,
                     result=result, msg=' '.join(messages))


if __name__ == '__main__':
    main()
