#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests"""

import unittest
import ansible.module_utils.remote_management.yama.mikrotik_helpers as \
    mikrotik_helpers


class strings_test(unittest.TestCase):
    """Declaring unittest class for testing handled below.
    """

    def test_properties_to_list(self):
        """
        """

        data_in0 = 'a,b,c d'
        data_out0 = ['a', 'b', 'c', 'd']

        self.assertEqual(mikrotik_helpers.properties_to_list(data_in0),
                         data_out0)


if __name__ == '__main__':
    unittest.main()
