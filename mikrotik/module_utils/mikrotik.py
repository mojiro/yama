# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""YAMA: Module for mikrotik connections <module_utils.mikrotik>"""

import re
import csv
from ansible.module_utils.yama.ssh_client import SSHClient
from ansible.module_utils.yama.valid import hasstring, haslist, hasdict, haskey
from ansible.module_utils.yama.strings import readjson
import ansible.module_utils.network.mikrotik.mongodb as mongodb
from ansible.module_utils.network.mikrotik.mikrotik_helpers import branchfix, \
    properties_to_list, propvals_to_dict, propvals_diff_getvalues


class Router(SSHClient):
    """A class that will handle all router operations.
    """
    branch = None
    inventory = None

    # List of Mikrotik errors.
    #
    # Example:
    # [admin@host] > ls -la
    # bad command name ls (line 1 column 1)
    message_errors = [
        'bad command name',
        'expected end of command',
        'failure:',
        'input does not match any value of',
        'invalid value',
        'no such item',
        'Script Error:',
        'syntax error'
    ]

    # List of Mikrotik messages with positive meaning.
    #
    # Example:
    # [admin@host] > /user add name=ftp password=ftp group=ftp
    # failure: user with the same name already exisits
    #
    # Lines with 'exisi?ts' are valid because of known typo in Mikrotik.
    message_regexes = [
        re.compile(r'failure: \S+ with the same \S+ already exisi?ts'),
        re.compile(r'failure: \S+ already exisi?ts'),
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
        self.branch = readjson(branchfile)
        if not self.branch:
            self.err(5, branchfile)

        self.inventory = mongodb.Database(db_conffile)
        if self.inventory.status < 0:
            self.err(6, self.inventory.errors())

        super(Router, self).__init__(host, port, username, password, pkeyfile)

    def __del__(self):
        """Closes open connections.
        """
        self.inventory.disconnect()
        super(Router, self).__del__()

    def checkline(self, data=''):
        """Checks the input against a list of common errors.

        :param data: (str) Data to be checked.
        :return: (bool) True on success, False on failure.
        """
        if not hasstring(data):
            return True

        data = data.strip()
        for index, error in enumerate(self.message_errors):
            if data.find(error) == 0:
                if error == 'failure:':
                    return self.checkline_falsepos(data)
                return self.err(index, data)

        return True

    def checkline_falsepos(self, data=''):
        """Checks false-positives. For error messages that begin with the word
        'failure'.

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
        return self.err(1, 'Host is not Mikrotik')

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
        """Executes the <command> on the remote host and returns the results.

        :param command: (str) The command that has to be executed.
        :param raw: (bool) Returns all results without filtering lines that
            start with #.
        :param connect: (bool) Connects to host, if it is not connected already.
        :param hasstdout: (bool) Is it expected the command to give output?
        :return: (list) The execution result.
        """
        results = super(Router, self).command(command, raw, connect, hasstdout)

        if not self.checkline(results[0]):
            self.err(5, command)

        return results

    def commands(self, commands, raw=False, connect=True):
        """Executes a list of command on the remote host using the
        self.command() method.

        :param commands: (list) The list of commands to be executed.
        :param raw: (bool) Returns all results without filtering lines that
            start with #.
        :param connect: (bool) Connects to host, if it is not connected already.
        :return: (list) The execution result.
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
                return self.err(2, 'commands[{}]: {}'.format(index, command))

        if status == 1:
            self.disconnect()

        return results

    def getvalues(self, branch, properties, find='', csvout=False, iid=False):
        """Retrieves requested values from remote host.

        :param branch: (str) Branch of commands.
        :param properties: (str / list) List or Comma / Space separated
            properties.
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
