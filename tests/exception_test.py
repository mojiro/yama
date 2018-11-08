#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests"""

import unittest
import ansible.module_utils.network.mikrotik.exception as exception


class exception_test(unittest.TestCase):
    """Declaring unittest class for testing handled below
    """

    def test_exception(self):
        """Division by 0 to cause exception
        """

        try_result = None

        int0 = 0
        message = ''
        message_empty = ''

        try:
            try_result = True
            int0 = 0 / 0
        except ZeroDivisionError:
            try_result, message = exception.getexcept(False)
        finally:
            self.assertFalse(try_result)
            self.assertNotEqual(message, message_empty)


if __name__ == '__main__':
    unittest.main()
