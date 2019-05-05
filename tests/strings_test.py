#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests"""

import unittest

import ansible.module_utils.yama.strings as strings


class strings_test(unittest.TestCase):
    """Declaring unittest class for testing handled below.
    """

    def test_ifnull(self):
        """Test if data has content.
        """

        data_in0 = None
        data_out0 = 'a'

        data_in1 = 'b'
        data_out1 = 'b'

        self.assertEqual(strings.ifnull(data_in0, data_out0), data_out0)
        self.assertEqual(strings.ifnull(data_in1, data_out1), data_out1)

    def test_wtrim(self):
        """Test if input can get trimmed by whitespace.
        """

        data_in0 = None
        data_out0 = ''

        data_in1 = '   a     b c              d  '
        data_out1 = 'a b c d'

        self.assertEqual(strings.wtrim(data_in0), data_out0)
        self.assertEqual(strings.wtrim(data_in1), data_out1)

    def test_csv_parse(self):
        """Test if input can be converted to CSV.
        """

        data_in0 = 'ab,cd,ef\ngh,ij,kl'
        data_out0 = [
            ['ab', 'cd', 'ef'],
            ['gh', 'ij', 'kl']
        ]

        data_in1 = None
        data_in2 = ''
        data_in3 = 5
        data_out1 = None

        self.assertEqual(strings.csv_parse(data_in0), data_out0)
        self.assertEqual(strings.csv_parse(data_in1), data_out1)
        self.assertEqual(strings.csv_parse(data_in2), data_out1)
        self.assertEqual(strings.csv_parse(data_in3), data_out1)


if __name__ == '__main__':
    unittest.main()
