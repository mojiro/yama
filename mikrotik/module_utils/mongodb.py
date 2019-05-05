# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""   """

from pymongo import MongoClient
from ansible.module_utils.yama.object_error import ErrorObject
from ansible.module_utils.yama.exception import getexcept
from ansible.module_utils.yama.valid import hasstring, hasdict, ishost, \
    isport, isusername
from ansible.module_utils.yama.strings import readjson


class Database(ErrorObject):
    """
    """
    connection = None
    cmdb = None
    host = '127.0.0.1'
    port = 27017
    username = None
    password = None
    name = 'ansible'
    status = -1 # -1 - Not ready, 0 - Disconnected/Ready, 1 - Connected

    def __init__(self, conffile='config/mongodb.json'):
        """
        """
        super(Database, self).__init__()

        contents = readjson(conffile)

        if hasdict(contents):
            if 'host' in contents:
                if ishost(contents['host']):
                    self.host = contents['host']
                else:
                    self.err(1, contents['host'])

            if 'port' in contents:
                if isport(contents['port']):
                    self.port = contents['port']
                else:
                    self.err(2, contents['port'])

            if 'username' in contents:
                if isusername(contents['username']):
                    self.username = contents['username']
                else:
                    self.err(3, contents['username'])

            if 'password' in contents:
                if hasstring(contents['password']):
                    self.password = contents['password']
                else:
                    self.err(4, contents['password'])

            if 'name' in contents:
                if hasstring(contents['name']):
                    self.name = contents['name']
                else:
                    self.err(5, contents['name'])

        if self.errc() == 0:
            self.status = 0

    def __del__(self):
        """
        """
        self.disconnect()

    def checkconnection(self):
        """
        """
        if not self.cmdb:
            return False

        try:
            self.cmdb.admin.command('ismaster')
            self.status = 1
            return True

        except EOFError:
            self.status = 0
            return False

    def connect(self):
        """
        """
        if self.status < 0:
            return self.err(1, self.status)

        if self.status == 1:
            if self.checkconnection():
                return True

        try:
            self.connection = MongoClient(self.host, self.port)
            self.cmdb = self.connection[self.name]
            self.status = 1
            return True

        except Exception:
            _, message = getexcept()
            return self.err(2, message)

    def disconnect(self):
        """
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

    def find(self, collection, find=None):
        """
        """
        results = None

        if self.status < 1:
            self.err(1, self.status)
            return None

        if not hasstring(collection):
            self.err(2)
            return None

        try:
            if find:
                results = self.cmdb[collection].find(find)
            else:
                results = self.cmdb[collection].find()

        except Exception:
            _, message = getexcept()
            self.err(4, message)

        return results

    def find_one(self, collection, find=None):
        """
        """
        results = None

        if self.status < 1:
            self.err(1, self.status)
            return None

        if not hasstring(collection):
            self.err(2)
            return None

        if not find:
            self.err(3)
            return None

        try:
            results = self.cmdb[collection].find_one(find)

        except Exception:
            _, message = getexcept()
            self.err(4, message)

        return results

    def insert_one(self, collection, data=None):
        """
        """
        if self.status < 1:
            return self.err(1, self.status)

        if not hasstring(collection):
            return self.err(2)

        if not data:
            return self.err(3)

        try:
            self.cmdb[collection].insert_one(data)
            return True

        except Exception:
            _, message = getexcept()
            return self.err(4, message)

    def update(self, collection, find=None, key='', data=None):
        """
        """
        if self.status < 1:
            return self.err(1, self.status)

        if not hasstring(collection):
            return self.err(2)

        if not find:
            return self.err(3)

        if not hasstring(key):
            return self.err(4)

        if not data:
            return self.err(5)

        try:
            document = self.cmdb[collection].find_one(find)

            if not document:
                return self.err(6)

            if key in document:
                document[key].update(data)

            else:
                document[key] = data

            self.cmdb[collection].update_one(find,
                                             {'$set': {key: document[key]}})
            return True

        except Exception:
            _, message = getexcept()
            return self.err(7, message)

    def getlist(self, connect=True):
        """
        """
        results = {}
        status = 0

        if self.status < 1 and connect:
            if self.connect():
                status = 1

        if self.status < 1:
            self.err(1)
            return {}

        hosts = self.find('hosts')

        if not hosts:
            self.err(2)
            return {}

        for host in hosts:
            for group in host['groups']:
                group = group.encode('utf-8')

                if group not in results.keys():
                    results[group] = {'hosts': []}

                results[group]['hosts'].append(host['host'].encode('utf-8'))

        if status == 1:
            self.disconnect()

        return results

    def gethost(self, host, connect=True):
        """
        """
        results = {}
        status = 0

        if not ishost(host):
            self.err(1)
            return {}

        if self.status < 1 and connect:
            if self.connect():
                status = 1

        if self.status < 1:
            self.err(2)
            return {}

        host = self.find_one('hosts', {'host': host})

        if not host:
            self.err(3)
            return {}

        for var in host['vars']:
            results[var.encode('utf-8')] = host['vars'][var].encode('utf-8')

        if status == 1:
            self.disconnect()

        return results

    def addhost(self, host, connect=True):
        """
        """
        results = False
        status = 0

        if not ishost(host):
            return self.err(1)

        if self.status < 1 and connect:
            if self.connect():
                status = 1

        if self.status < 1:
            return self.err(2)

        result = self.find_one('hosts', {'host': host})

        if not result:
            return False

        data = {'host': host, 'groups': [], 'facts': {}, 'vars': {}}
        results = self.insert_one('hosts', data)

        if status == 1:
            self.disconnect()

        return results
