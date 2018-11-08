# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""YAMA: Module for mikrotik connections"""

import re
import stat
import os
import socket
import csv
import paramiko

from ansible.module_utils.network.mikrotik.object_error import ErrorObject
import ansible.module_utils.network.mikrotik.mongodb as mongodb
from ansible.module_utils.network.mikrotik.exception import getexcept
from ansible.module_utils.network.mikrotik.valid import hasstring, haslist, \
    hasdict, haskey, isdir, isfile, isport, ishostname, isusername
from ansible.module_utils.network.mikrotik.strings import readjson
from ansible.module_utils.network.mikrotik.mikrotik_helpers import branchfix, \
    properties_to_list, propvals_to_dict, propvals_diff_getvalues

class Router(ErrorObject):
    """
    """

    branch = None
    transport = None
    connection = None
    pkey = None
    hostname = None
    port = 22
    username = 'admin'
    password = None
    pkeyfile = None
    status = -1 # -1 - Not ready, 0 - Disconnected/Ready, 1 - Connected

    inventory = None

    def __init__(self, hostname, port=22, username='admin', password='',
                 pkeyfile='', branchfile='config/branch.json',
                 db_conffile='config/mongodb.json'):
        """
        """
        super(Router, self).__init__()

        if ishostname(hostname):
            self.hostname = hostname
        else:
            self.err(1, hostname)

        if isport(port):
            self.port = int(port)
        else:
            self.err(2, port)

        if isusername(username):
            self.username = username
        else:
            self.err(3, username)

        if pkeyfile:
            if not isfile(pkeyfile):
                self.err(4, pkeyfile)

        self.password = password
        self.pkeyfile = pkeyfile

        self.branch = readjson(branchfile)
        if not self.branch:
            self.err(5, branchfile)

        self.inventory = mongodb.Database(db_conffile)
        if self.inventory.status < 0:
            self.err(6, self.inventory.errors())

        if self.errc() == 0:
            self.status = 0

    def __del__(self):
        """
        """
        self.disconnect()
        self.inventory.disconnect()

    def checkconnection(self):
        """
        """
        try:
            transport = self.connection.get_transport()
            transport.send_ignore()
            self.status = 1
            return True

        except EOFError:
            self.status = 0
            return False

    def checkline(self, data=''):
        """
        """
        if not hasstring(data):
            return True

        data = data.strip()
        errors = [
            'bad command name',
            'expected end of command',
            'failure:',
            'input does not match any value of',
            'invalid value',
            'no such item',
            'Script Error:',
            'syntax error'
        ]

        for index, error in enumerate(errors):
            if data.find(error) == 0:
                return self.err(index, data)

        return True

    def checkline_falsepos(self, data=''):
        """
        """
        if not hasstring(data):
            return self.err(1)

        regexes = [
            re.compile(r'failure: \S+ with the same \S+ already exisits'),
            re.compile(r'failure: \S+ with the same \S+ already exists'),
            re.compile(r'failure: \S+ already exisits'),
            re.compile(r'failure: \S+ already exists'),
            re.compile(r'failure: already have such \S+')
        ]

        for regex in regexes:
            if regex.match(data):
                return True

        return False

    def connect(self, protocol='ssh', timeout=10):
        """
        """
        if not isinstance(timeout, int) or timeout < 0:
            timeout = 10

        if self.status < 0:
            return self.err(1, self.status)

        if self.status == 1:
            if self.checkconnection():
                return True

        try:
            if self.pkeyfile:
                self.pkey = paramiko.RSAKey.from_private_key_file(self.pkeyfile)

            if protocol == 'sftp':
                self.transport = paramiko.Transport((self.hostname, self.port))

                if self.pkey:
                    self.transport.connect(username=self.username,
                                           pkey=self.pkey)
                else:
                    self.transport.connect(username=self.username,
                                           password=self.password)

                self.connection = paramiko.SFTPClient.from_transport(self.transport)

            else:
                self.connection = paramiko.SSHClient()
                self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                if self.pkey:
                    self.connection.connect(hostname=self.hostname,
                                            port=self.port,
                                            username=self.username,
                                            pkey=self.pkey,
                                            timeout=timeout)
                else:
                    self.connection.connect(hostname=self.hostname,
                                            port=self.port,
                                            username=self.username,
                                            password=self.password,
                                            timeout=timeout)

            self.status = 1
            return True

        except socket.error:
            _, message = getexcept()
            return self.err(2, message)

        except paramiko.AuthenticationException:
            _, message = getexcept()
            return self.err(3, message)

        except paramiko.BadHostKeyException:
            _, message = getexcept()
            return self.err(4, message)

        except paramiko.SSHException:
            _, message = getexcept()
            return self.err(5, message)

        except Exception:
            _, message = getexcept()
            return self.err(6, message)

    def disconnect(self):
        """
        """
        if not self.checkconnection:
            return True

        try:
            self.connection.close()
            self.status = 0
            return True

        except Exception:
            _, message = getexcept()
            return self.err(1, message)

    def store(self, branch, propvals=None):
        """
        """
        if not hasstring(branch):
            return self.err(1)

        branch = branchfix(branch)

        if not haskey(self.branch, branch, dict):
            return self.err(2, branch)

        if not haslist(propvals):
            return self.err(3)

        if not self.inventory.connect():
            return self.err(4, self.inventory.errors())

        if not self.inventory.update('hosts', {'host': self.hostname},
                                     'facts', {branch: propvals}):
            return self.err(5, self.inventory.errors())

        self.inventory.disconnect()

        return True

    def command(self, command, raw=False, connect=True, hasstdout=True):
        """
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
            stdin, stdout, stderr = self.connection.exec_command(command)
            lines = stdout.read().replace('\r', '').split('\n')

            if not self.checkline(lines[0]):
                self.err(3, command)

        except Exception:
            _, message = getexcept()
            self.err(4, message)

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
            self.err(5, command)

        return results

    def commands(self, commands, raw=False, connect=True):
        """
        """
        status = 0

        if hasstring(commands):
            commands = [commands]
            # maybe if it is only one command, exec it and skip to end
        elif not haslist(commands):
            self.err(1)
            return None

        if self.status < 1 and connect:
            if self.connect():
                status = 1

        if self.status < 1:
            self.err(2, self.status)
            return None

        results = []

        for index, command in enumerate(commands):
            if not command:
                continue

            result = self.command(command, raw, hasstdout=False)
            results.append(result)

            if self.errc():
                if haslist(result):
                    # move the following check to self.command
                    if self.checkline_falsepos(result[0]):
                        self.err0()
                        continue

                return self.err(2, 'commands[' + str(index) + ']: ' + command)

        if status == 1:
            self.disconnect()

        return True

    def getvalues(self, branch, properties, find='', csvout=False, iid=False):
        """
        """
        results = []

        if not hasstring(branch):
            self.err(1)
            return None

        branch = branchfix(branch)

        if not haskey(self.branch, branch, dict):
            self.err(2, branch)
            return None

        properties = properties_to_list(properties)

        if not haslist(properties):
            self.err(3)
            return None

        command = ''
        commands = []

        if (self.branch[branch]['class'] == 'settings' or
                (self.branch[branch]['class'] == 'list' and
                 find and find.find('=') < 1)):
            for prop in properties:
                commands.append('[' + branch + ' get ' + find + ' ' + prop + ']')

            command = ':put (' + '.",".'.join(commands) + ')'

        elif self.branch[branch]['class'] == 'list':
            if iid:
                commands.append('$i')

            for prop in properties:
                commands.append('[' + branch + ' get $i ' + prop + ']')

            command = ':foreach i in=[' + branch + ' find ' + find + ']' \
                      + ' do={:put (' + '.",".'.join(commands) + ')}'

        else:
            self.err(4, branch)
            return None

        lines = self.command(command)

        if not lines:
            return None

        if csvout:
            results = lines

        else:
            properties_c = len(properties)
            reader = csv.reader(lines, delimiter=',', quotechar='"')

            if self.branch[branch]['class'] == 'list' and iid:
                for values in reader:
                    result = {'.id': values[0]}

                    for i in range(0, properties_c):
                        result[properties[i]] = values[i + 1].replace(';', ',')

                    results.append(result)

            else:
                for values in reader:
                    result = {}

                    for i in range(0, properties_c):
                        result[properties[i]] = values[i].replace(';', ',')

                    results.append(result)

        return results

    def setvalues(self, branch, propvals='', find=''):
        """
        """
        if not hasstring(branch):
            return self.err(1)

        branch = branchfix(branch)

        if not haskey(self.branch, branch, dict):
            return self.err(2, branch)

        if self.branch[branch]['readonly']:
            return False

        if not hasstring(propvals):
            return self.err(3)

        # Parse propvals to properties
        propvals_d = propvals_to_dict(propvals)
        if not hasdict(propvals_d):
            return self.err(4)
        properties = []
        for prop in propvals_d:
            properties.append(prop)

        # Create the find command, if find exists
        find_command = ''
        iid = True
        if self.branch[branch]['class'] == 'list':
            if hasstring(find):
                if find.find('=') > 1:
                    find_command = '[find ' + find + '] '
                else:
                    iid = False
                    find_command = find + ' '

        # Get values before updates
        getvalues0 = self.getvalues(branch, properties, find, False, iid)
        if not getvalues0:
            return self.err(5)

        # Exit if Get is same as update
        if not propvals_diff_getvalues(propvals_d, getvalues0):
            return False   # There are no changes to apply

        # Update command
        command = branch + ' set ' + find_command + propvals
        results = self.command(command, hasstdout=False)
        if results:
            self.err(6, command)
            return self.err(7, results)

        # Get values after update
        getvalues1 = self.getvalues(branch, properties, find, False, iid)
        if not getvalues1:
            return self.err(8)

        # Compare Before and After update command
        if getvalues0 != getvalues1:
            return True  # Changed
        return False  # Not changed != Failed

    def addentry(self, branch, propvals=''):
        """
        """
        if not hasstring(branch):
            return self.err(1)

        branch = branchfix(branch)

        if not haskey(self.branch, branch, dict):
            return self.err(2, branch)

        if self.branch[branch]['class'] != 'list':
            return False

        if self.branch[branch]['readonly']:
            return False

        if not hasstring(propvals):
            return self.err(3)

        # Count entries before add command
        command = ':put [:len [' + branch + ' find]]'
        entries_c0 = self.command(command)
        if not entries_c0:
            return self.err(4)

        # Check if such an entry exists
        if self.branch[branch]['id']:
            propvals_d = propvals_to_dict(propvals)
            prop = self.branch[branch]['id'][0]

            if haskey(propvals_d, prop):
                command = ':put [:len [' + branch + ' find ' + prop + '=' \
                          + propvals_d[prop] + ']]'
                result = self.command(command)

                if result[0] != '0':
                    return False

        # Add Command
        command = branch + ' add ' + propvals
        results = self.command(command, hasstdout=False)
        if results:
            if self.checkline_falsepos(results[0]):
                self.err0()
                return False  # Not changed != Failed
            self.err(5, command)
            return self.err(6, results)

        # Count entries after add command
        command = ':put [:len [' + branch + ' find]]'
        entries_c1 = self.command(command)
        if not entries_c1:
            return self.err(7)

        # Compare Before and After add command
        if entries_c0 != entries_c1:
            return True  # Changed
        return False  # Not changed != Failed

    def removeentry(self, branch, find):
        """
        """
        if not hasstring(branch):
            return self.err(1)

        branch = branchfix(branch)

        if not haskey(self.branch, branch, dict):
            return self.err(2, branch)

        if self.branch[branch]['class'] != 'list':
            return False

        if self.branch[branch]['readonly']:
            return False

        # Count entries before remove command
        command = ':put [:len [' + branch + ' find]]'
        entries_c0 = self.command(command)
        if not entries_c0:
            return self.err(3)

        # Remove command
        command = branch + ' remove [find ' + find + ']'
        results = self.command(command, hasstdout=False)
        if results:
            return self.err(4, results)

        # Count entries after remove command
        command = ':put [:len [' + branch + ' find]]'
        entries_c1 = self.command(command)
        if not entries_c1:
            return self.err(5)

        # Compare Before and After remove command
        if entries_c0 != entries_c1:
            return True  # Changed
        return False  # Not changed != Failed

    def mkdir_remote(self, data):
        """
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
            for index in range(index + 1, path_c):
                try:
                    self.connection.mkdir('/'.join(path[0:index + 1]))
                except IOError:
                    _, message = getexcept()
                    return self.err(1, message)

        return True

    def isdir_remote(self, data, makedirs=False):
        """
        """
        if not hasstring(data):
            return False

        try:
            return stat.S_ISDIR(self.connection.stat(data).st_mode)

        except IOError:
            if makedirs:
                return self.mkdir_remote(data)

    def isfile_remote(self, data):
        """
        """
        if not hasstring(data):
            return False

        try:
            return stat.S_ISREG(self.connection.stat(data).st_mode)

        except IOError:
            return False

    def walk_remote(self, data):
        """Kindof a stripped down version of os.walk, implemented for sftp.
        Tried running it flat without the yields, but it really chokes on big
        directories.
        Source: https://gist.github.com/johnfink8/2190472#file-ssh-py-L92
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
        """
        """
        if not hasstring(remote):
            return self.err(1)

        if isfile(local):
            return self.upload_file(local, remote)

        if isdir(local):
            return self.upload_dir(local, remote)

        return False

    def upload_dir(self, local, remote):
        """
        Source: https://www.tutorialspoint.com/python/os_walk.htm
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

            for name in files:
                remote_file = remote_root + '/' + name

                try:
                    self.connection.put(root + '/' + name, remote_file)
                except Exception:
                    _, message = getexcept()
                    self.err(6, remote_file)
                    return self.err(7, message)

        return True

    def upload_file(self, local, remote):
        """
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
        """
        """
        if self.isdir_remote(remote):
            return self.download_dir(remote, local)

        if self.isfile_remote(remote):
            return self.download_file(remote, local)

        return False

    def download_dir(self, remote, local):
        """
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

            for name in files:
                local_file = local_root + '/' + name

                try:
                    self.connection.get(root + '/' + name, local_file)
                except Exception:
                    _, message = getexcept()
                    self.err(6, local_file)
                    return self.err(7, message)

        return True

    def download_file(self, remote, local):
        """
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
