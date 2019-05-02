# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""YAMA: Module for mikrotik connections <module_utils.mikrotik>"""

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
    hasdict, haskey, isdir, isfile, isport, ishost, isusername
from ansible.module_utils.network.mikrotik.strings import readjson
from ansible.module_utils.network.mikrotik.mikrotik_helpers import branchfix, \
    properties_to_list, propvals_to_dict, propvals_diff_getvalues


class Router(ErrorObject):
    """A class that will handle all router operations.
    """

    branch = None
    transport = None
    connection = None
    pkey = None
    host = None
    port = 22
    username = 'admin'
    password = None
    pkeyfile = None
    status = -1 # -1 - Not ready, 0 - Disconnected/Ready, 1 - Connected

    inventory = None

    # List of errors.
    #
    # Example:
    # [admin@host] > ls -la
    # bad command name ls (line 1 column 1)
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

    # List of messages with positive meaning.
    #
    # Example:
    # [admin@host] > /user add name=ftp password=ftp group=ftp
    # failure: user with the same name already exisits
    #
    # Lines with 'exisits' are valid because of known typo in Mikrotik.
    message_regexes = [
        re.compile(r'failure: \S+ with the same \S+ already exisits'),
        re.compile(r'failure: \S+ with the same \S+ already exists'),
        re.compile(r'failure: \S+ already exisits'),
        re.compile(r'failure: \S+ already exists'),
        re.compile(r'failure: already have such \S+')
    ]

    def __init__(self, host, port=22, username='admin', password='',
                 pkeyfile='', branchfile='config/branch.json',
                 db_conffile='config/mongodb.json'):
        """Initializes a Router object.

        :param host: (str) Router's host. It can be IPv4, IPv6 or hostname.
        :param port: (int) SSH Port.
        :param username: (str) Username.
        :param password: (str) Password.
        :param pkeyfile: (file) Private Key Path.
        :param branchfile: (file) Path of branch.json. Directory of Mikrotik
            commands.
        :param db_conffile: (file) Path of MongoDB Connection file.
        :return: (obj) Router.
        """
        super(Router, self).__init__()

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

        # There is no need to validate the existence of (password OR pkeyfile)
        # because the router might have empty password and no public key set.

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
        """Closes open connections.
        """
        self.disconnect()
        self.inventory.disconnect()

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

    def checkline(self, data=''):
        """Checks the input against a list of common errors.

        :param data: (str) Data to be checked.
        :return: (bool) True on success, False on failure.
        """
        if not hasstring(data):
            return True

        data = data.strip()
        for index, error in enumerate(self.errors):
            if data.find(error) == 0:
                return self.err(index, data)

        return True

    def checkline_falsepos(self, data=''):
        """Checks false-positives.

        :param data: (str) Data to be checked.
        :return: (bool) True on success, False on failure.
        """
        if not hasstring(data):
            return self.err(1)

        for regex in self.message_regexes:
            if regex.match(data):
                return True

        return False

    def checkmikrotik(self):
        """Executes a Mikrotik-only command to determine if host is a Mikrotik
        device.
        """
        results = self.command('/system resource print')

        for line in results:
            if line == 'platform: MikroTik':
                return True

        self.disconnect()
        self.err(1, 'Host is not Mikrotik')

        return False

    def connect(self, protocol='ssh', timeout=30):
        """Connects to remote host using specified protocol.

        :param ssh: (str) Protocol. Valid options: ssh, sftp.
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
            # There are four combinations:
            # 1) SSH with password
            # 2) SSH with private key
            # 3) SFTP with password
            # 4) SFTP with private key

            if self.pkeyfile:
                self.pkey = paramiko.RSAKey.from_private_key_file(self.pkeyfile)

            if protocol == 'sftp':
                self.transport = paramiko.Transport((self.host, self.port))

                if self.pkey:
                    self.transport.connect(username=self.username,
                                           pkey=self.pkey)
                else:
                    self.transport.connect(username=self.username,
                                           password=self.password,
                                           allow_agent=False,
                                           look_for_keys=False)

                self.connection = paramiko.SFTPClient.from_transport(
                    self.transport)
                self.status = 1
                return True

            else:
                self.connection = paramiko.SSHClient()
                self.connection.set_missing_host_key_policy(
                    paramiko.AutoAddPolicy())

                if self.pkey:
                    self.connection.connect(hostname=self.host,
                                            port=self.port,
                                            username=self.username,
                                            pkey=self.pkey,
                                            timeout=timeout)
                else:
                    self.connection.connect(hostname=self.host,
                                            port=self.port,
                                            username=self.username,
                                            password=self.password,
                                            timeout=timeout,
                                            allow_agent=False,
                                            look_for_keys=False)

                self.status = 1
                return checkmikrotik()

            return False

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
        """Disconnects from current host, unless it is already disconnected.

        :return: (bool) True on success, False on failure.
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
        """Stores information from <propvals> about current router to MongoDB.

        :param branch: (str) Branch of commands.
        :param propvals: (dict) Dictionary of Variables=Values.
        :return: (bool): True on success, False on failure.
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

        if not self.inventory.update('hosts', {'host': self.host}, 'facts',
                                     {branch: propvals}):
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

            # Mikrotik CLI is not producing stderr. Linux does.
            if not (hasstring(lines) or haslist(lines)):
                lines = stderr.read().replace('\r', '').split('\n')

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

                return self.err(2, 'commands[{}]: {}'.format(index, command))

        if status == 1:
            self.disconnect()

        return results

    def getvalues(self, branch, properties, find='', csvout=False, iid=False):
        """Retrieves requested values from remote host.

        :param branch: (str) Branch of commands.
        :param properties: (str / list) List or Comma/Space seperated properties.
        :param find: (str) Mikrotik CLI filter.
        :param csvout: (bool) Output in CSV File.
        :param iid: (bool) Adds $id to output.
        :return: (dict) Variables-Values dictionary.

        Example output if <csvout=False>:
            [
                "variable1": "value1",
                ...
            ]

        Example output if <csvout=True>:
            Return of <self.command>

            [
                "value1,value2,value3,...",
                "value1,value2,value3,...",
                ...
            ]
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
                commands.append('[{} get {} {}]'.format(branch, find, prop))

            command = ':put ({})'.format('.",".'.join(commands))

        elif self.branch[branch]['class'] == 'list':
            if iid:
                commands.append('$i')

            for prop in properties:
                commands.append('[{} get $i {}]'.format(branch, prop))

            command = (':foreach i in=[' + branch + ' find ' + find + '] '
                       'do={:put (' + '.",".'.join(commands) + ')}')

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
        """Sets requested values to remote host. That method compares the
        configuration before and after command execution to detect changes and
        form the bool result.

        :param branch: (str) Branch of commands.
        :param propvals: (dict) Dictionary of Variables=Values.
        :param find: (str) Mikrotik CLI filter.
        :return: (bool) True when <propvals> have changed the configuration. If
            for some reason, configuration remains unchanged False will be
            returned, but the <self.errc> will be zero. It will also return
            False in case of error.
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
                    find_command = '[find {}] '.format(find)
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
        command = '{} set {}{}'.format(branch, find_command, propvals)
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
        """Adds new entries to remote host. That method compares the
        configuration before and after command execution to detect changes and
        form the bool result.

        :param branch: (str) Branch of commands
        :param propvals: (str) Space seperated pairs of Variable=Value
        :return: (bool) True when <propvals> have changed the configuration. If
            for some reason, configuration remains unchanged False will be
            returned, but the <self.errc> will be zero. It will also return
            False in case of error.
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
        command = ':put [:len [{} find]]'.format(branch)
        entries_c0 = self.command(command)
        if not entries_c0:
            return self.err(4)

        # Check if such an entry exists
        if self.branch[branch]['id']:
            propvals_d = propvals_to_dict(propvals)
            prop = self.branch[branch]['id'][0]

            if haskey(propvals_d, prop):
                command = ':put [:len [{} find {}={}]]'.format(branch, prop,
                                                               propvals_d[prop])
                result = self.command(command)

                if result[0] != '0':
                    return False

        # Add Command
        command = '{} add {}'.format(branch, propvals)
        results = self.command(command, hasstdout=False)
        if results:
            if self.checkline_falsepos(results[0]):
                self.err0()
                return False  # Not changed != Failed
            self.err(5, command)
            return self.err(6, results)

        # Count entries after add command
        command = ':put [:len [{} find]]'.format(branch)
        entries_c1 = self.command(command)
        if not entries_c1:
            return self.err(7)

        # Compare Before and After add command
        if entries_c0 != entries_c1:
            return True  # Changed
        return False  # Not changed != Failed

    def removeentry(self, branch, find=''):
        """Removes entries from remote host based onto <find>. If <find> is
        note set, it will remove everything under that <branch>. That method
        compares the configuration before and after command execution to detect
        changes and form the bool result.

        :param branch: (str) Branch of commands.
        :param find: (str) Mikrotik CLI filter.
        :return: (bool) True when <propvals> have changed the configuration. If
            for some reason, configuration remains unchanged False will be
            returned, but the <self.errc> will be zero. It will also return
            False in case of error.
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

        if not hasstring(find):
            find = ''

        # Count entries before remove command
        command = ':put [:len [{} find]]'.format(branch)
        entries_c0 = self.command(command)
        if not entries_c0:
            return self.err(3)

        # Remove command
        command = '{} remove [find {}]'.format(branch, find)
        results = self.command(command, hasstdout=False)
        if results:
            return self.err(4, results)

        # Count entries after remove command
        command = ':put [:len [{} find]]'.format(branch)
        entries_c1 = self.command(command)
        if not entries_c1:
            return self.err(5)

        # Compare Before and After remove command
        if entries_c0 != entries_c1:
            return True  # Changed
        return False  # Not changed != Failed

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

        try:
            for index in range(0, path_c):
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
