# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Yama: Module for SSH connections.
<ansible.module_utils.remote_management.yama.ssh_client>"""

import StringIO
import socket
import paramiko
from ansible.module_utils.remote_management.yama.ssh_common import SSHCommon
from ansible.module_utils.remote_management.yama.exception import getexcept
from ansible.module_utils.remote_management.yama.valid import hasstring, \
    haslist


class SSHClient(SSHCommon):
    """A class that will handle all SSH operations.
    """

    history = []

    def __init__(self, host, port=22, username='root', password='',
                 pkey_string='', pkey_file=''):
        """Initializes a SSHClient object.
        """
        self.history = []

        super(SSHClient, self).__init__(host, port, username, password,
                                        pkey_string, pkey_file)

    def connect(self, timeout=30):
        """Connects to remote host via SSH.

        :param timeout: (int) Connection timeout.
        :return: (bool) Connection status.
        """
        if not isinstance(timeout, int) or timeout < 0:
            timeout = 30

        if self.status < 0:
            return self.err(1, self.status)

        if self.status == 1:
            if self.checkconnection():
                return True

        try:
            if self.pkey_string:
                handler = StringIO.StringIO(self.pkey_string)
                self.pkey = paramiko.RSAKey.from_private_key(handler)
                handler.close()
            elif self.pkey_file:
                self.pkey = paramiko.RSAKey.from_private_key_file(
                    self.pkey_file)

            self.connection = paramiko.SSHClient()
            self.connection.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())

            if self.pkey:
                self.ssh_auth = 2
                self.connection.connect(hostname=self.host,
                                        port=self.port,
                                        username=self.username,
                                        pkey=self.pkey,
                                        timeout=timeout)
            else:
                self.ssh_auth = 1
                self.connection.connect(hostname=self.host,
                                        port=self.port,
                                        username=self.username,
                                        password=self.password,
                                        timeout=timeout,
                                        allow_agent=False,
                                        look_for_keys=False)

            self.status = 1
            return True

        except socket.error:
            _, message = getexcept()
            err_code = 2

        except paramiko.AuthenticationException:
            _, message = getexcept()
            err_code = 3

        except paramiko.BadHostKeyException:
            _, message = getexcept()
            err_code = 4

        except paramiko.SSHException:
            _, message = getexcept()
            err_code = 5

        except Exception:
            _, message = getexcept()
            err_code = 6

        return self.err(err_code, message)

    def command(self, command, raw=False, connect=True, hasstdout=True):
        """Executes the <command> on the remote host and returns the results.

        :param command: (str) The command that has to be executed.
        :param raw: (bool) Returns all results without filtering lines that
            start with #.
        :param connect: (bool) Connects to host, if it is not connected already.
        :param hasstdout: (bool) Is it expected the command to give output?
        :return: (list) The execution result.
        """
        status = 0

        self.history.append(command)

        if not hasstring(command):
            self.err(1)
            return None

        if self.status < 1 and connect:
            if self.connect():
                status = 1

        if self.status < 1:
            self.err(2, self.status)
            return None

        if self.reseterrors:
            self.err0()

        lines = []

        try:
            # stdin, stdout, stderr = ...
            _, stdout, stderr = self.connection.exec_command(command)
            lines = stdout.read().replace('\r', '').split('\n')

            # Mikrotik CLI is not producing stderr. Linux does.
            if not (hasstring(lines) or haslist(lines)):
                lines = stderr.read().replace('\r', '').split('\n')

        except Exception:
            _, message = getexcept()
            self.err(3, message)

        finally:
            if status == 1:
                self.disconnect()
        ##### fix the logic ^^^ \/\/\/\ of get/except/disconnect

        results = []

        if raw:
            for line in lines:
                results.append(line)

        elif lines:
            for line in lines:
                if line:
                    if line[0] != '#':
                        results.append(line.strip())

        if not haslist(results) and hasstdout:
            self.err(4, command)

        return results
