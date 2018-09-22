# -*- coding: utf-8 -*-

# Copyright (c) 2018 Michail Topaloudis
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Easy exception handling"""

import linecache
import sys


def getexcept(stderr=True):
    """Parses the latest exception. By default, it prints the error message to
    stdout.

    :param stderr: If it is True, will print the error message
    :returns: False, error message
    """

    _, exc_obj, exc_tb = sys.exc_info()
    frame = exc_tb.tb_frame
    lineno = exc_tb.tb_lineno
    filename = frame.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, frame.f_globals)
    message = 'Exception in {}:{}\n  {}\n    ^ {}'.format(
        filename, lineno, line.strip(), exc_obj)

    if stderr:
        print message

    return False, message
