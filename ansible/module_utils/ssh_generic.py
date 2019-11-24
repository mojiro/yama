# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Yama: Module for SSH connections.
<ansible.module_utils.remote_management.yama.ssh_generic>"""

from ansible.module_utils.remote_management.yama.ssh_client import SSHClient
from ansible.module_utils.remote_management.yama.valid import hasstring, \
    haslist


class SSHGeneric(SSHClient):
    """A class that will handle all SSH operations.
    """

    commandsets = [
        {
            'vendor':  'mikrotik',
            'command': '/system resource print',
            'result':  'platform: MikroTik'},
        {
            'vendor':  'ubiquity',
            'command': 'ls -1 /bin/ubntbox',
            'result':  '/bin/ubntbox'},
        {
            'vendor':  'raspberrypi',
            'command': 'cat /etc/os-release',
            'result':  'ID=raspbian'},
        {
            'vendor':  'linux',
            'command': 'uname -m',
            'result':  ['x86', 'x64', 'x86_64']},
        {
            'vendor':  'openwrt',
            'command': '',
            'result':  ''},
        {
            'vendor':  'cisco',
            'command': '',
            'result': ''}
    ]

    def getvendor(self):
        """
        """
        vendor = None

        for commandset in self.commandsets:
            if not (hasstring(commandset['command']) and
                    (hasstring(commandset['result']) or
                     haslist(commandset['result']))):
                continue

            lines = self.command(commandset['command'])

            if hasstring(commandset['result']):
                for line in lines:
                    if line == commandset['result']:
                        vendor = commandset['vendor']
                        break

            elif haslist(commandset['result']):
                for line in lines:
                    if line in commandset['result']:
                        vendor = commandset['vendor']
                        break

            if vendor:
                break

        if not vendor:
            vendor = 'unknown'

        return vendor
