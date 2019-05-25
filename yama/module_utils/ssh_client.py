# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""YAMA: Module for SSH connections <module_utils.ssh_client>"""

import socket
import paramiko
from ansible.module_utils.yama.object_error import ErrorObject
from ansible.module_utils.yama.exception import getexcept
from ansible.module_utils.yama.valid import hasstring, haslist, isfile, \
    isport, ishost, isusername


class SSHClient(ErrorObject):
    """A class that will handle all SSH operations.
    """
    connection = None
    pkey = None
    host = None
    port = 22
    username = 'root'
    password = None
    pkey_file = None
    status = -1 # -1 - Not ready, 0 - Disconnected/Ready, 1 - Connected

    def __init__(self, host, port=22, username='root', password='',
                 pkey_file=''):
        """Initializes a SSHClient object.

        :param host: (str) Remote host. It can be IPv4, IPv6 or hostname.
        :param port: (int) SSH Port.
        :param username: (str) Username.
        :param password: (str) Password.
        :param pkey_file: (file) Private Key Path.
        :return: (obj) SSH Client.
        """
        super(SSHClient, self).__init__()

        if ishost(host):
            self.host = host
        else:
            self.err(1, host)

        if isport(port):
            self.port = int(port)
        else:
            self.err(2, port)

        if isusername(username):
            self.username = username
        else:
            self.err(3, username)

        # There is no need to validate the existence of (password OR pkey_file)
        # because the router might have empty password and no public key set.

        if pkey_file:
            if not isfile(pkey_file):
                self.err(4, pkey_file)

        self.password = password
        self.pkey_file = pkey_file

        if self.errc() == 0:
            self.status = 0

    def __del__(self):
        """Closes open connections.
        """
        self.disconnect()

    def checkconnection(self):
        """Sends a single null command to check the connectivity.

        :return: (bool) True on success, False on failure.
        """
        try:
            transport = self.connection.get_transport()
            transport.send_ignore()
            self.status = 1
            return True

        except EOFError:
            self.status = 0
            return False

        except AttributeError:
            _, message = getexcept()
            return self.err(1, message)

    def connect(self, timeout=30):
        """Connects to remote host via SSH

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
            if self.pkey_file:
                self.pkey = paramiko.RSAKey.from_private_key_file(
                    self.pkey_file)

            self.connection = paramiko.SSHClient()
            self.connection.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())

            if self.pkey:
                self.connection.connect(hostname=self.host, port=self.port,
                                        username=self.username, pkey=self.pkey,
                                        timeout=timeout)
            else:
                self.connection.connect(hostname=self.host, port=self.port,
                                        username=self.username,
                                        password=self.password,
                                        timeout=timeout, allow_agent=False,
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

    def disconnect(self):
        """Disconnects from current host, unless it is already disconnected.

        :return: (bool) True on success, False on failure.
        """
        if not self.checkconnection():
            return True

        try:
            self.connection.close()
            self.status = 0
            return True

        except Exception:
            _, message = getexcept()
            return self.err(1, message)

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

        if not hasstring(command):
            self.err(1)
            return None

        if self.status < 1 and connect:
            if self.connect():
                status = 1

        if self.status < 1:
            self.err(2, self.status)
            return None

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
