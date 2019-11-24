#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Yama: Downloads files and directories from remote host using SFTP.
<ansible.modules.remote_management.yama.sftp_download>"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.yama.sftp_client import SFTPClient


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
            username=dict(required=False, type='str', default='root'),
            password=dict(required=False, type='str'),
            pkey_string=dict(required=False, type='str'),
            pkey_file=dict(required=False, type='str'),
            remote=dict(required=True, type='str'),
            local=dict(required=True, type='str')
        )
    )

    host = module.params['host']
    port = module.params['port']
    username = module.params['username']
    password = module.params['password']
    pkey_string = module.params['pkey_string']
    pkey_file = module.params['pkey_file']

    device = SFTPClient(host, port=port, username=username, password=password,
                        pkey_string=pkey_string, pkey_file=pkey_file)

    if device.connect():
        unreachable = 0
        result = device.download(module.params['remote'],
                                 module.params['local'])

    if device.errc():
        failed = 1

    device.disconnect()
    messages.append(device.errors())
    module.exit_json(changed=changed, unreachable=unreachable, failed=failed,
                     result=result, msg=' '.join(messages))


if __name__ == '__main__':
    main()
