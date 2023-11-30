"""
RAMSES I/O driver for integration testing.
"""

import argparse
import os
import sys

from aquasense.common.arghelp import less_than_zero_check, usage
from aquasense.ramses.ramses import RAMSES


INTEGRATION_TIMES = [2**i for i in range(3, 14)]


def create_arg_parser() -> argparse.ArgumentParser:
    """
    Create and return the command-line parser.
    """
    parser = argparse.ArgumentParser(
            description="Read RAMSES data from a serial port.")

    parser.add_argument("--port", "-p",
                        dest="port",
                        type=str,
                        default=None,
                        help="Serial port name")
    
    parser.add_argument("--output-path", "-o",
                    dest="out_path",
                    type=str,
                    default=None,
                    help="Output file path")

    parser.add_argument("--output-field-delimiter", "-d",
                        dest="output_field_delimiter",
                        type=str,
                        default=",",
                        help="Delimiter for fields in output rows (default: ,)")
    
    parser.add_argument("--integration-time", "-i",
                        dest="integration_time",
                        type=int,
                        default=0,
                        help="Integration time in ms (default: 0 [auto]); can be one of "
                             "{}".format(", ".join([str(n) for n in INTEGRATION_TIMES])))
    
    parser.add_argument("--repeats", "-r",
                        dest="repeats",
                        type=int,
                        default=1,
                        help="Number of sampling repeats (default: 1)")
    
    parser.add_argument("--intra-sample-delay", "-s",
                        dest="intra_sample_delay",
                        type=int,
                        default=1,
                        help="Delay between sampling in secs (default: 1)")
    
    parser.add_argument("--verbose", "-v",
                    dest="verbose",
                    default=False,
                    action="store_true",
                    help="Verbose output mode")
    

    return parser


def check_args(parser: argparse.ArgumentParser, args: argparse.Namespace):
    """
    Check args and exit if any problem is found.

    Args:
        parser: Command-line parser
        args: Command-line options
    
    Returns:
        Whether or not the source is serial.
    """
    msgs = []

    if args.port is None:
        msgs.append("serial port name required")

    if args.out_path is not None and \
        not os.path.exists(os.path.dirname(args.out_path)):
        msgs.append("output file directory does not exist")

    if args.integration_time not in INTEGRATION_TIMES:
        msgs.append("integration time must be one of {}".\
                    format(", ".join([str(n) for n in INTEGRATION_TIMES])))

    less_than_zero_check(args.repeats, "repeats", msgs)
    less_than_zero_check(args.intra_sample_delay, "intra sample delay", msgs)

    if len(msgs) != 0:
        usage(parser, msgs)


def main():
    try:
        parser = create_arg_parser()
        args = parser.parse_args()

        check_args(parser, args)

        if args.out_path is None:
            out = sys.stdout
        else:
            out = open(args.out_path, "w")

        ramses = RAMSES(out=out,
                        sep=args.output_field_delimiter,
                        port=args.port,
                        integration_time=args.integration_time,
                        repeats=args.repeats,
                        intra_sample_delay=args.intra_sample_delay,
                        logger=None,
                        verbose=args.verbose)
        
        ramses.run()

    except KeyboardInterrupt:
        print("** keyboard interrupt", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("** exiting with error: {}".format(str(e)), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()