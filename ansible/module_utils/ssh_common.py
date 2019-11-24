# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Yama: Module for SSH connections.
<ansible.module_utils.remote_management.yama.ssh_common>"""

from ansible.module_utils.remote_management.yama.object_error import \
    ErrorObject
from ansible.module_utils.remote_management.yama.exception import getexcept
from ansible.module_utils.remote_management.yama.valid import hasstring, \
    isfile, isport, ishost, ispkey


class SSHCommon(ErrorObject):
    """A class that will handle all SSH operations.
    """
    connection = None
    pkey = None
    ssh_auth = 0 # 0 - Unknown, 1 - Password, 2 - Private Key
    status = -1 # -1 - Not ready, 0 - Disconnected/Ready, 1 - Connected
    host = None
    port = 22
    username = 'root'
    password = None
    pkey_file = None

    def __init__(self, host, port=22, username='root', password='',
                 pkey_string='', pkey_file=''):
        """Initializes a SSHCommon object.

        :param host: (str) Remote host. It can be IPv4, IPv6 or hostname.
        :param port: (int) SSH Port.
        :param username: (str) Username.
        :param password: (str) Password.
        :param pkey_string: (file) Private Key.
        :param pkey_file: (file) Private Key Path.
        :return: (obj) SSH Client.
        """
        super(SSHCommon, self).__init__()

        if ishost(host):
            self.host = host
        else:
            self.err(1, host)

        if isport(port):
            self.port = int(port)
        else:
            self.err(2, port)

        if hasstring(username):
            self.username = username
        else:
            self.err(3, username)

        # There is no need to validate the existence of (password OR pkey_file)
        # because the router might have empty password and no public key set.

        if pkey_file:
            if not isfile(pkey_file):
                self.err(4, pkey_file)

        if pkey_string:
            if not ispkey(pkey_string):
                self.err(5)

        self.password = password
        self.pkey_string = pkey_string
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

        except (EOFError, AttributeError):
            self.status = 0
            return False

        except Exception:
            _, message = getexcept()
            return self.err(1, message)

    def connect(self, timeout=30):
        """An empty method that returns False and should be overriden.

        :param timeout: (int) Connection timeout.
        :return: (bool) Connection status.
        """
        _ = timeout
        self.status = -1
        return False

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

    def getauth(self):
        """Returns the authentication way that got used.

        :return: (int) The contents of <self.ssh_auth>.
        """
        return self.ssh_auth
