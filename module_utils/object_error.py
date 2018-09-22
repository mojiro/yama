# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Error Collector"""

import sys


class ErrorObject(object):
    """Error Collector
    """
    messages = []

    def __init__(self):
        """Init - Does nothing at the moment
        """
        pass

    def err(self, code=0, message=''):
        """The function that receives the errors

        :param code: (int) Error ID
        :param message: (str) Message
        :returns: (bool) False
        """
        getframe_expr = 'sys._getframe({}).f_code.co_name'
        self.messages.append(eval(getframe_expr.format(2)) \
                            + ':{0}:{1}'.format(code, message))
        return False

    def err0(self):
        """Empties the error list
        :returns: (bool) True
        """
        self.messages = []
        return True

    def errc(self):
        """Counts the number of errors
        :returns: (int) Number of errors
        """
        return len(self.messages)

    def errors(self):
        """Prints the errors
        :returns: (str) Concatenated string with all messages
        """
        return '\n'.join(self.messages)
