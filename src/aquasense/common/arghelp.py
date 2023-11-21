"""
Command-line helper functions
"""

import argparse
import os
import sys

from typing import List, Union


def less_than_zero_check(val: Union[int,float], name: str, msgs: List[str]):
    """
    Checks whether a named numeric value is less than zero,
    and if so, adds to a message list.

    Args:
        val: The numeric value to check.
        name: The name of the argument associated with the value.
        msgs: Message collector along with usage.
    """
    if val < 0:
        msgs.append("{} must be zero or more".format(name))


def usage(parser: argparse.ArgumentParser, msgs: List[str]=None):
    """
    Print usage message and exit.

    Args:
        parser: The command-line parser whose help we seek.
        msgs: Optional messages to print along with usage.
    """
    if msgs is not None:
        for msg in msgs:
            print("{0}{1}".format(os.linesep, msg), file=sys.stderr)
    print(os.linesep)

    parser.print_help()

    sys.exit(1)