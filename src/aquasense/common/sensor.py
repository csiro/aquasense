"""
Module for common sensor code.
"""

from typing import List, TextIO

import logging
import re

class SensorBase(object):
    """
    A base class for sensors.

    Args:
        in_out: File-like object for I/O (e.g. serial)
        out: File-like object to write output to.
        sep: Output column separator; defaults to comma.
        logger: A logger object; defaults to None.
        verbose: Verbose mode flag.
    """
    def __init__(self,
                 in_out: TextIO,
                 out: TextIO,
                 sep: str,
                 logger: logging.Logger=None,
                 verbose: bool=False):
        self.in_out = in_out
        self.out = out
        self.sep = sep
        if logger is None:
            logging.basicConfig()
            self.logger = logging.getLogger(self.__class__.__name__)
        else:
            self.logger = logger
        self.verbose = verbose
        if self.verbose:
            self.logger.setLevel(logging.INFO)
    

    def run(self):
        """Read samples forever or until some some
           implementation specific end state
        """
        raise NotImplementedError
    

    def command_response(self, command: str,
                         response_patterns: List[str]=None,
                         eoln_out: str="\r\n") -> List[str]:
        """Write a command to I/O channel, wait for one of a number of possible expected
        response regular expressions, return any matched groups.
        
        Args:
            in_out: I/O channel (e.g. serial)
            command: The command string to be sent.
            response_patterns: Optional expected response regular expression list.
            eoln_out: The end of line sequence to be added to commands.

        Returns:
            Values matched from response pattern.

        Raises:
            IOError: If an I/O error occurs or the expected responses are not received.
        """
        if self.verbose:
            self.logger.info(">> {}".format(command))

        self.in_out.write("{}{}".format(command, eoln_out))
        self.in_out.flush()

        matched_values = None

        if response_patterns is None or len(response_patterns) == 0:
            self.consume_available(self.in_out)
        else:
            if self.verbose:
                self.logger.info("?? {}".format(response_patterns))
            finished = False
            patterns = [re.compile(resp_patt) for resp_patt in response_patterns]
            while not finished:
                response = self.in_out.readline()
                if self.verbose and response.strip() != "":
                    self.logger.info("<< {}".format(response))
                for pattern in patterns:
                    matcher = pattern.search(response.rstrip())
                    if matcher is not None:
                        finished = True
                        matched_values = matcher.groups()
                        break

        return matched_values


    def consume_available(self, in_out: TextIO):
        """Consume any incoming bytes waiting on serial port
        before beginning.

        Args:
            in_out: I/O channel (file, serial port)
        """
        while len(in_out.readlines()) > 0:
            pass