#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests"""

import unittest
import ansible.module_utils.remote_management.yama.valid as valid


class valid_test(unittest.TestCase):
    """Declaring unittest class for testing handled below.
    """

    def test_hasstring(self):
        """Test if input is string.
        """

        none0 = None
        int0 = 0
        int1 = 1
        int2 = -1
        str0 = ''
        str1 = 'abcd'
        list0 = []
        list1 = ['ab', 'cd']
        dict0 = {}
        dict1 = {'ab': 'cd'}
        set0 = set()
        set1 = set(['a', 'b', 1, 2])
        tuple0 = ()
        tuple1 = ('a', 'b', 1, 2)

        self.assertFalse(valid.hasstring(none0))
        self.assertFalse(valid.hasstring(int0))
        self.assertFalse(valid.hasstring(int1))
        self.assertFalse(valid.hasstring(int2))
        self.assertFalse(valid.hasstring(str0))
        self.assertTrue(valid.hasstring(str1))  # assertTrue
        self.assertFalse(valid.hasstring(list0))
        self.assertFalse(valid.hasstring(list1))
        self.assertFalse(valid.hasstring(dict0))
        self.assertFalse(valid.hasstring(dict1))
        self.assertFalse(valid.hasstring(set0))
        self.assertFalse(valid.hasstring(set1))
        self.assertFalse(valid.hasstring(tuple0))
        self.assertFalse(valid.hasstring(tuple1))

    def test_haslist(self):
        """Test if input is list.
        """

        none0 = None
        int0 = 0
        int1 = 1
        int2 = -1
        str0 = ''
        str1 = 'abcd'
        list0 = []
        list1 = ['ab', 'cd']
        dict0 = {}
        dict1 = {'ab': 'cd'}
        set0 = set()
        set1 = set(['a', 'b', 1, 2])
        tuple0 = ()
        tuple1 = ('a', 'b', 1, 2)

        self.assertFalse(valid.haslist(none0))
        self.assertFalse(valid.haslist(int0))
        self.assertFalse(valid.haslist(int1))
        self.assertFalse(valid.haslist(int2))
        self.assertFalse(valid.haslist(str0))
        self.assertFalse(valid.haslist(str1))
        self.assertFalse(valid.haslist(list0))
        self.assertTrue(valid.haslist(list1))  # assertTrue
        self.assertFalse(valid.haslist(dict0))
        self.assertFalse(valid.haslist(dict1))
        self.assertFalse(valid.haslist(set0))
        self.assertFalse(valid.haslist(set1))
        self.assertFalse(valid.haslist(tuple0))
        self.assertFalse(valid.haslist(tuple1))

    def test_hasdict(self):
        """Test if input is dictionary.
        """

        none0 = None
        int0 = 0
        int1 = 1
        int2 = -1
        str0 = ''
        str1 = 'abcd'
        list0 = []
        list1 = ['ab', 'cd']
        dict0 = {}
        dict1 = {'ab': 'cd'}
        set0 = set()
        set1 = set(['a', 'b', 1, 2])
        tuple0 = ()
        tuple1 = ('a', 'b', 1, 2)

        self.assertFalse(valid.hasdict(none0))
        self.assertFalse(valid.hasdict(int0))
        self.assertFalse(valid.hasdict(int1))
        self.assertFalse(valid.hasdict(int2))
        self.assertFalse(valid.hasdict(str0))
        self.assertFalse(valid.hasdict(str1))
        self.assertFalse(valid.hasdict(list0))
        self.assertFalse(valid.hasdict(list1))
        self.assertFalse(valid.hasdict(dict0))
        self.assertTrue(valid.hasdict(dict1))  # assertTrue
        self.assertFalse(valid.hasdict(set0))
        self.assertFalse(valid.hasdict(set1))
        self.assertFalse(valid.hasdict(tuple0))
        self.assertFalse(valid.hasdict(tuple1))

    def test_haskey(self):
        """Test if key exists in dictionary.
        """

        none0 = None
        int0 = 0
        int1 = 1
        int2 = -1
        str0 = ''
        str1 = 'abcd'
        list0 = []
        list1 = ['ab', 'cd']
        dict0 = {}
        dict1 = {'ab': 'cd'}
        set0 = set()
        set1 = set(['a', 'b', 1, 2])
        tuple0 = ()
        tuple1 = ('a', 'b', 1, 2)

        self.assertFalse(valid.haskey(none0, none0))
        self.assertFalse(valid.haskey(dict1, none0))
        self.assertFalse(valid.haskey(dict1, int0))
        self.assertFalse(valid.haskey(dict1, int1))
        self.assertFalse(valid.haskey(dict1, int2))
        self.assertFalse(valid.haskey(dict1, str0))
        self.assertFalse(valid.haskey(dict1, str1))
        self.assertFalse(valid.haskey(dict1, list0))
        self.assertFalse(valid.haskey(dict1, list1))
        self.assertFalse(valid.haskey(dict1, dict0))
        self.assertFalse(valid.haskey(dict1, dict1))
        self.assertFalse(valid.haskey(dict1, set0))
        self.assertFalse(valid.haskey(dict1, set1))
        self.assertFalse(valid.haskey(dict1, tuple0))
        self.assertFalse(valid.haskey(dict1, tuple1))

        key0 = 'ab'
        self.assertTrue(valid.haskey(dict1, key0, str))  # assertTrue
        self.assertFalse(valid.haskey(dict1, key0, list))  # assertFalse

    def test_haskeys(self):
        """Test if keys exist in dictionary.
        """

        none0 = None
        int0 = 0
        int1 = 1
        int2 = -1
        str0 = ''
        str1 = 'abcd'
        list0 = []
        list1 = ['ab', 'cd']
        dict0 = {}
        dict1 = {'ab': 'cd'}
        set0 = set()
        set1 = set(['a', 'b', 1, 2])
        tuple0 = ()
        tuple1 = ('a', 'b', 1, 2)

        self.assertFalse(valid.haskeys(none0, none0))
        self.assertFalse(valid.haskeys(dict1, none0))
        self.assertFalse(valid.haskeys(dict1, int0))
        self.assertFalse(valid.haskeys(dict1, int1))
        self.assertFalse(valid.haskeys(dict1, int2))
        self.assertFalse(valid.haskeys(dict1, str0))
        self.assertFalse(valid.haskeys(dict1, str1))
        self.assertFalse(valid.haskeys(dict1, list0))
        self.assertFalse(valid.haskeys(dict1, list1))
        self.assertFalse(valid.haskeys(dict1, dict0))
        self.assertFalse(valid.haskeys(dict1, dict1))
        self.assertFalse(valid.haskeys(dict1, set0))
        self.assertFalse(valid.haskeys(dict1, set1))
        self.assertFalse(valid.haskeys(dict1, tuple0))
        self.assertFalse(valid.haskeys(dict1, tuple1))

        keys0 = ['ab']
        self.assertTrue(valid.haskeys(dict1, keys0))  # assertTrue

    def test_isdir(self):
        """Test if input is directory.
        """

        none0 = None
        int0 = 0
        int1 = 1
        int2 = -1
        str0 = ''
        str1 = 'abcd'
        list0 = []
        list1 = ['ab', 'cd']
        dict0 = {}
        dict1 = {'ab': 'cd'}
        set0 = set()
        set1 = set(['a', 'b', 1, 2])
        tuple0 = ()
        tuple1 = ('a', 'b', 1, 2)

        self.assertFalse(valid.isdir(none0))
        self.assertFalse(valid.isdir(int0))
        self.assertFalse(valid.isdir(int1))
        self.assertFalse(valid.isdir(int2))
        self.assertFalse(valid.isdir(str0))
        self.assertFalse(valid.isdir(str1))
        self.assertFalse(valid.isdir(list0))
        self.assertFalse(valid.isdir(list1))
        self.assertFalse(valid.isdir(dict0))
        self.assertFalse(valid.isdir(dict1))
        self.assertFalse(valid.isdir(set0))
        self.assertFalse(valid.isdir(set1))
        self.assertFalse(valid.isdir(tuple0))
        self.assertFalse(valid.isdir(tuple1))

        directory0 = '/'
        directory1 = '/abcd'

        self.assertTrue(valid.isdir(directory0))  # assertTrue
        self.assertFalse(valid.isdir(directory1))

    def test_isfile(self):
        """Test if input is directory.
        """

        none0 = None
        int0 = 0
        int1 = 1
        int2 = -1
        str0 = ''
        str1 = 'abcd'
        list0 = []
        list1 = ['ab', 'cd']
        dict0 = {}
        dict1 = {'ab': 'cd'}
        set0 = set()
        set1 = set(['a', 'b', 1, 2])
        tuple0 = ()
        tuple1 = ('a', 'b', 1, 2)

        self.assertFalse(valid.isfile(none0))
        self.assertFalse(valid.isfile(int0))
        self.assertFalse(valid.isfile(int1))
        self.assertFalse(valid.isfile(int2))
        self.assertFalse(valid.isfile(str0))
        self.assertFalse(valid.isfile(str1))
        self.assertFalse(valid.isfile(list0))
        self.assertFalse(valid.isfile(list1))
        self.assertFalse(valid.isfile(dict0))
        self.assertFalse(valid.isfile(dict1))
        self.assertFalse(valid.isfile(set0))
        self.assertFalse(valid.isfile(set1))
        self.assertFalse(valid.isfile(tuple0))
        self.assertFalse(valid.isfile(tuple1))

        filename0 = 'valid_test.py'

        self.assertTrue(valid.isfile(filename0))  # assertTrue

    def test_ismacaddress(self):
        """Test if input is MAC Address.
        """

        none0 = None
        int0 = 0
        int1 = 1
        int2 = -1
        str0 = ''
        str1 = 'abcd'
        list0 = []
        list1 = ['ab', 'cd']
        dict0 = {}
        dict1 = {'ab': 'cd'}
        set0 = set()
        set1 = set(['a', 'b', 1, 2])
        tuple0 = ()
        tuple1 = ('a', 'b', 1, 2)

        self.assertFalse(valid.ismacaddress(none0))
        self.assertFalse(valid.ismacaddress(int0))
        self.assertFalse(valid.ismacaddress(int1))
        self.assertFalse(valid.ismacaddress(int2))
        self.assertFalse(valid.ismacaddress(str0))
        self.assertFalse(valid.ismacaddress(str1))
        self.assertFalse(valid.ismacaddress(list0))
        self.assertFalse(valid.ismacaddress(list1))
        self.assertFalse(valid.ismacaddress(dict0))
        self.assertFalse(valid.ismacaddress(dict1))
        self.assertFalse(valid.ismacaddress(set0))
        self.assertFalse(valid.ismacaddress(set1))
        self.assertFalse(valid.ismacaddress(tuple0))
        self.assertFalse(valid.ismacaddress(tuple1))

        mac0 = '12:34:56:78:90:AB'
        mac1 = '12'
        mac2 = '12:34:56:78:90:A'
        mac3 = '12:34:56:78:90:AQ'
        mac4 = '12:34:56:78:90:AB:'
        mac5 = '12:34:56:78:90:AB:C'
        mac6 = '12:34:56:78:90:AB:CD'

        self.assertTrue(valid.ismacaddress(mac0))  # assertTrue
        self.assertFalse(valid.ismacaddress(mac1))
        self.assertFalse(valid.ismacaddress(mac2))
        self.assertFalse(valid.ismacaddress(mac3))
        self.assertFalse(valid.ismacaddress(mac4))
        self.assertFalse(valid.ismacaddress(mac5))
        self.assertFalse(valid.ismacaddress(mac6))

    def test_isipv4(self):
        """Test if input is IPv4 Address.
        """

        none0 = None
        int0 = 0
        int1 = 1
        int2 = -1
        str0 = ''
        str1 = 'abcd'
        list0 = []
        list1 = ['ab', 'cd']
        dict0 = {}
        dict1 = {'ab': 'cd'}
        set0 = set()
        set1 = set(['a', 'b', 1, 2])
        tuple0 = ()
        tuple1 = ('a', 'b', 1, 2)

        self.assertFalse(valid.isipv4(none0))
        self.assertFalse(valid.isipv4(int0))
        self.assertFalse(valid.isipv4(int1))
        self.assertFalse(valid.isipv4(int2))
        self.assertFalse(valid.isipv4(str0))
        self.assertFalse(valid.isipv4(str1))
        self.assertFalse(valid.isipv4(list0))
        self.assertFalse(valid.isipv4(list1))
        self.assertFalse(valid.isipv4(dict0))
        self.assertFalse(valid.isipv4(dict1))
        self.assertFalse(valid.isipv4(set0))
        self.assertFalse(valid.isipv4(set1))
        self.assertFalse(valid.isipv4(tuple0))
        self.assertFalse(valid.isipv4(tuple1))

        ip0 = '192.168.0.1'
        ip1 = '192'
        ip2 = '192.168.0'
        ip3 = '192.168.0.'
        ip4 = '192.168.0.1.'
        ip5 = '192.168.0.1.1'
        ip6 = '292.168.0.1'
        ip7 = 'A.168.0.1'

        self.assertTrue(valid.isipv4(ip0))  # assertTrue
        self.assertFalse(valid.isipv4(ip1))
        self.assertFalse(valid.isipv4(ip2))
        self.assertFalse(valid.isipv4(ip3))
        self.assertFalse(valid.isipv4(ip4))
        self.assertFalse(valid.isipv4(ip5))
        self.assertFalse(valid.isipv4(ip6))
        self.assertFalse(valid.isipv4(ip7))

    def test_isipv6(self):
        """Test if input is IPv6 Address.
        """

        none0 = None
        int0 = 0
        int1 = 1
        int2 = -1
        str0 = ''
        str1 = 'abcd'
        list0 = []
        list1 = ['ab', 'cd']
        dict0 = {}
        dict1 = {'ab': 'cd'}
        set0 = set()
        set1 = set(['a', 'b', 1, 2])
        tuple0 = ()
        tuple1 = ('a', 'b', 1, 2)

        self.assertFalse(valid.isipv6(none0))
        self.assertFalse(valid.isipv6(int0))
        self.assertFalse(valid.isipv6(int1))
        self.assertFalse(valid.isipv6(int2))
        self.assertFalse(valid.isipv6(str0))
        self.assertFalse(valid.isipv6(str1))
        self.assertFalse(valid.isipv6(list0))
        self.assertFalse(valid.isipv6(list1))
        self.assertFalse(valid.isipv6(dict0))
        self.assertFalse(valid.isipv6(dict1))
        self.assertFalse(valid.isipv6(set0))
        self.assertFalse(valid.isipv6(set1))
        self.assertFalse(valid.isipv6(tuple0))
        self.assertFalse(valid.isipv6(tuple1))

        ip0 = '2001:0db8:85a3:0000:0000:8a2e:0370:7334'
        ip1 = '2001'
        ip2 = '2001:0db8:85a3:0000:0000:8a2e:0370:7334:'
        ip3 = '2001:0db8:85a3:0000:0000:8a2e:0370:7334:1234'
        ip4 = '2001:0db8:85a3:0000:0000:8a2q:0370:7334'

        self.assertTrue(valid.isipv6(ip0))  # assertTrue
        self.assertFalse(valid.isipv6(ip1))
        self.assertFalse(valid.isipv6(ip2))
        self.assertFalse(valid.isipv6(ip3))
        self.assertFalse(valid.isipv6(ip4))

    def test_ishostname(self):
        """Test if input is hostname.
        """

        none0 = None
        int0 = 0
        int1 = 1
        int2 = -1
        str0 = ''
        str1 = 'abcd'
        list0 = []
        list1 = ['ab', 'cd']
        dict0 = {}
        dict1 = {'ab': 'cd'}
        set0 = set()
        set1 = set(['a', 'b', 1, 2])
        tuple0 = ()
        tuple1 = ('a', 'b', 1, 2)

        self.assertFalse(valid.ishostname(none0))
        self.assertFalse(valid.ishostname(int0))
        self.assertFalse(valid.ishostname(int1))
        self.assertFalse(valid.ishostname(int2))
        self.assertFalse(valid.ishostname(str0))
        self.assertTrue(valid.ishostname(str1))  # assertTrue
        self.assertFalse(valid.ishostname(list0))
        self.assertFalse(valid.ishostname(list1))
        self.assertFalse(valid.ishostname(dict0))
        self.assertFalse(valid.ishostname(dict1))
        self.assertFalse(valid.ishostname(set0))
        self.assertFalse(valid.ishostname(set1))
        self.assertFalse(valid.ishostname(tuple0))
        self.assertFalse(valid.ishostname(tuple1))

        host0 = 'example.com'
        host1 = 'example'
        host2 = 'example.com.'
        host3 = 'example.com#'

        self.assertTrue(valid.ishostname(host0))  # assertTrue
        self.assertTrue(valid.ishostname(host1))  # assertTrue
        self.assertTrue(valid.ishostname(host2))  # assertTrue
        self.assertFalse(valid.ishostname(host3))


if __name__ == '__main__':
    unittest.main()
