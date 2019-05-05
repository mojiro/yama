# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""YAMA: Module for SFTP connections <module_utils.sftp_client>"""

import stat
import os
import socket
import paramiko
from ansible.module_utils.yama.ssh_client import SSHClient
from ansible.module_utils.yama.exception import getexcept
from ansible.module_utils.yama.valid import hasstring, isdir, isfile


class SFTPClient(SSHClient):
    """A class that will handle all SFTP operations.
    """
    transport = None

    def connect(self, timeout=30):
        """Connects to remote host via SFTP.

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

        # Check this approach (timeout is not being used):
        # https://stackoverflow.com/questions/9758432/timeout-in-paramiko-python
        _ = timeout
        # After changing it, in the password connect, add:
        # allow_agent=False, look_for_keys=False

        try:
            if self.pkeyfile:
                self.pkey = paramiko.RSAKey.from_private_key_file(
                    self.pkeyfile)

            self.transport = paramiko.Transport((self.host, self.port))

            if self.pkey:
                self.transport.connect(username=self.username, pkey=self.pkey)
            else:
                self.transport.connect(username=self.username,
                                       password=self.password)

            self.connection = paramiko.SFTPClient.from_transport(
                self.transport)
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
        """Does nothing. Eliminates accidental call of the parent.command().
        """
        return None

    def mkdir_remote(self, data):
        """Creates remote directories.

        :param data: (str) Path.
        :return: (bool) True on success, False on failure.
        """
        if not hasstring(data):
            return False

        if data[-1] == '/':
            data = data[:-1]

        path = data.split('/')
        path_c = len(path)
        index = 1

        for index in range(0, path_c):
            try:
                if stat.S_ISREG(
                        self.connection.stat(
                            '/'.join(path[0:index + 1])).st_mode):
                    return False
            except IOError:
                index -= 1
                break

        if index < path_c - 1:
            try:
                for index in range(index + 1, path_c):
                    self.connection.mkdir('/'.join(path[0:index + 1]))
            except IOError:
                _, message = getexcept()
                return self.err(1, message)

        return True

    def isdir_remote(self, data, makedirs=False):
        """Checks if remote directory exists.

        :param data: (str) Path.
        :param makedirs: (bool) If True, creates the whole path. Equilevant to
            <mkdir -p>.
        :return: (bool) True on success, False on failure.
        """
        if not hasstring(data):
            return False

        try:
            return stat.S_ISDIR(self.connection.stat(data).st_mode)

        except IOError:
            if makedirs:
                return self.mkdir_remote(data)

    def isfile_remote(self, data):
        """Checks if remote file exists.

        :param data: (str) Path.
        :return: (bool) True on success, False on failure.
        """
        if not hasstring(data):
            return False

        try:
            return stat.S_ISREG(self.connection.stat(data).st_mode)

        except IOError:
            return False

    def walk_remote(self, data):
        """Kindof a stripped down version of <os.walk>, implemented for SFTP.
        Tried running it flat without the yields, but it really chokes on big
        directories.

        Source: https://gist.github.com/johnfink8/2190472#file-ssh-py-L92

        :param data: (str) Path.
        :return: (str) Path.
        """
        path = data
        files = []
        folders = []

        for attr in self.connection.listdir_attr(data):
            if stat.S_ISDIR(attr.st_mode):
                folders.append(attr.filename)
            else:
                files.append(attr.filename)

        yield path, folders, files

        for folder in folders:
            new_path = os.path.join(data, folder)

            for x in self.walk_remote(new_path):
                yield x

    def upload(self, local, remote):
        """Uploads local files or directories to remote host.

        :param local: (str) Local path.
        :param remote: (str) Remote path.
        :return: (bool) True on success, False on failure.
        """
        if not hasstring(remote):
            return self.err(1)

        if isfile(local):
            return self.upload_file(local, remote)

        if isdir(local):
            return self.upload_dir(local, remote)

        return False

    def upload_dir(self, local, remote):
        """Uploads local directories to remote host.

        Source: https://www.tutorialspoint.com/python/os_walk.htm

        :param local: (str) Local path.
        :param remote: (str) Remote path.
        :return: (bool) True on success, False on failure.
        """
        if not isdir(local):
            return self.err(1, local)

        if self.isfile_remote(remote):
            return self.err(2, remote)

        if not self.isdir_remote(remote, True):
            return self.err(3, remote)

        if local[-1] == '/':
            local = local[:-1]

        if remote[-1] == '/':
            remote = remote[:-1]

        local_c = len(local)

        for root, dirs, files in os.walk(local, topdown=False):
            remote_root = remote + root[local_c:]

            if not self.mkdir_remote(remote_root):
                return self.err(4, remote_root)

            for name in dirs:
                remote_dir = remote_root + '/' + name

                if not self.mkdir_remote(remote_dir):
                    return self.err(5, remote_dir)

            try:
                for name in files:
                    remote_file = remote_root + '/' + name
                    self.connection.put(root + '/' + name, remote_file)
            except Exception:
                _, message = getexcept()
                self.err(6, remote_file)
                return self.err(7, message)

        return True

    def upload_file(self, local, remote):
        """Uploads local files to remote host.

        :param local: (str) Local path.
        :param remote: (str) Remote path.
        :return: (bool) True on success, False on failure.
        """
        if not isfile(local):
            return self.err(1, local)

        if not hasstring(remote):
            return self.err(2, remote)

        if self.isdir_remote(remote) and remote[-1] != '/':
            remote += '/'

        if remote[-1] == '/':
            remote += local.split('/')[-1]

        if not self.isdir_remote('/'.join(remote.split('/')[:-1]), True):
            return self.err(3, remote)

        try:
            self.connection.put(local, remote)
            return True

        except Exception:
            _, message = getexcept()
            return self.err(4, message)

    def download(self, remote, local):
        """Downloads remote files or directories to local path.

        :param remote: (str) Remote path.
        :param local: (str) Local path.
        :return: (bool) True on success, False on failure.
        """
        if self.isdir_remote(remote):
            return self.download_dir(remote, local)

        if self.isfile_remote(remote):
            return self.download_file(remote, local)

        return False

    def download_dir(self, remote, local):
        """Downloads remote directories to local path.

        :param remote: (str) Remote path.
        :param local: (str) Local path.
        :return: (bool) True on success, False on failure.
        """
        if not self.isdir_remote(remote):
            return self.err(1, remote)

        if isfile(local):
            return self.err(2, local)

        if not isdir(local, True):
            return self.err(3, local)

        if remote[-1] == '/':
            remote = remote[:-1]

        if local[-1] == '/':
            local = local[:-1]

        remote_c = len(remote)

        for root, dirs, files in self.walk_remote(remote):
            local_root = local + root[remote_c:]

            if not isdir(local_root, True):
                return self.err(4, local_root)

            for name in dirs:
                local_dir = local_root + '/' + name

                if not isdir(local_dir, True):
                    return self.err(5, local_dir)

            try:
                for name in files:
                    local_file = local_root + '/' + name
                    self.connection.get(root + '/' + name, local_file)
            except Exception:
                _, message = getexcept()
                self.err(6, local_file)
                return self.err(7, message)

        return True

    def download_file(self, remote, local):
        """Downloads remote files to local path.

        :param remote: (str) Remote path.
        :param local: (str) Local path.
        :return: (bool) True on success, False on failure.
        """
        if not self.isfile_remote(remote):
            return self.err(1, remote)

        if not hasstring(local):
            return self.err(2, local)

        if isdir(local) and local[-1] != '/':
            local += '/'

        if local[-1] == '/':
            local += remote.split('/')[:-1]

        if not isdir('/'.join(local.split('/')[:-1]), True):
            return self.err(3, local)

        try:
            self.connection.get(remote, local)
            return True

        except Exception:
            _, message = getexcept()
            return self.err(4, message)
