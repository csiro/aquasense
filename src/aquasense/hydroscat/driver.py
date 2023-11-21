"""
HydroScat I/O driver for integration testing.
"""

import argparse
import io
import os
import serial
import sys

from aquasense.common.arghelp import less_than_zero_check, usage
from aquasense.hydroscat.hydroscat import HydroScat


def create_arg_parser() -> argparse.ArgumentParser:
    """
    Create and return the command-line parser.
    """
    parser = argparse.ArgumentParser(
            description="Read HydroScat data from a file or serial port.")

    parser.add_argument("--source", "-s",
                        dest="source",
                        type=str,
                        default="reference/data files/HydroScat-6/sample.raw",
                        help="Raw lines source (file path or serial port name)")

    parser.add_argument("--cal-path", "-c",
                        dest="cal_path",
                        type=str,
                        default="reference/Device files/HydroScat/HS080339 2021-10-16.cal",
                        help="Calibration file path")
    
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
    
    parser.add_argument("--baud-rate", "-b",
                        dest="baud_rate",
                        type=int,
                        default=9600,
                        help="Serial port baud rate (default: 9600)")

    parser.add_argument("--serial-timeout", "-t",
                        dest="timeout",
                        type=int,
                        default=1,
                        help="Serial port read timeout (default: 1 second)")

    parser.add_argument("--burst-mode", "-e",
                        dest="burst_mode",
                        default=False,
                        action="store_true",
                        help="Enable burst mode?")
    
    parser.add_argument("--sleep-on-memory-full", "-z",
                        dest="sleep_on_memory_full",
                        default=False,
                        action="store_true",
                        help="Enable burst mode?")
    
    parser.add_argument("--fluorescence-control", "-f",
                        dest="fluorescence_control",
                        type=int,
                        default=1,
                        help="Fluorescence channel setting (0, 1, 2) as "
                             "per section 8.3.12 of HydroScat user manual "
                             "(default: 1)")

    parser.add_argument("--start-delay", "-r",
                        dest="start_delay",
                        type=float,
                        default=1,
                        help="Start delay in seconds (default: 1)")

    parser.add_argument("--warmup-time", "-w",
                        dest="warmup_time",
                        type=float,
                        default=0,
                        help="Start delay in seconds (default: 0)")

    parser.add_argument("--burst-duration", "-u",
                        dest="burst_duration",
                        type=float,
                        default=0,
                        help="Burst duration in seconds (default: 0)")
    
    parser.add_argument("--burst-cycle", "-y",
                        dest="burst_cycle",
                        type=float,
                        default=0.7,
                        help="Burst cycle in minutes (default: 0.7)")

    parser.add_argument("--total-duration", "-a",
                        dest="total_duration",
                        type=float,
                        default=0.4,
                        help="Total duration in minutes (default: 0.4)")

    parser.add_argument("--log-period", "-i",
                        dest="log_period",
                        type=float,
                        default=0.6,
                        help="Log period in seconds (default: 0.6)")

    parser.add_argument("--output-cal-header", "-l",
                        dest="output_cal_header",
                        default=False,
                        action="store_true",
                        help="Output calibration header")
    
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

    if not os.path.exists(args.cal_path):
        msgs.append("calibration file does not exist")

    if args.source.startswith("COM") or args.source.startswith("/dev/tty"):
        serial_mode = True
        if args.baud_rate <= 0:
            msgs.append("baud rate must be a positive integer (e.g. 9600, 19200)")
    else:
        serial_mode = False
        if not os.path.exists(args.source):
            msgs.append("raw packet lines source does not exist")

    if args.out_path is not None and \
        not os.path.exists(os.path.dirname(args.out_path)):
        msgs.append("output file directory does not exist")

    if args.fluorescence_control not in [0,1,2]:
        msgs.append("fluorescence control value must be 0, 1, or 2")

    less_than_zero_check(args.start_delay, "start delay", msgs)
    less_than_zero_check(args.warmup_time, "warm-up time", msgs)
    less_than_zero_check(args.burst_duration, "burst duration", msgs)
    less_than_zero_check(args.burst_cycle, "burst cycle", msgs)
    less_than_zero_check(args.total_duration, "total duration", msgs)
    less_than_zero_check(args.log_period, "log_period", msgs)

    if len(msgs) != 0:
        usage(parser, msgs)

    return serial_mode


def main():
    try:
        parser = create_arg_parser()
        args = parser.parse_args()

        serial_mode = check_args(parser, args)

        if serial_mode: 
            ser = serial.Serial(port=args.source,
                                baudrate=args.baud_rate,
                                timeout=args.timeout)
            in_out = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
        else:
            in_out = open(args.source)

        if args.out_path is None:
            out = sys.stdout
        else:
            out = open(args.out_path, "w")

        hydroscat = HydroScat(cal_path=args.cal_path,
                              in_out=in_out,
                              out=out,
                              sep=args.output_field_delimiter,
                              serial_mode=serial_mode,
                              burst_mode=args.burst_mode,
                              sleep_on_memory_full=args.sleep_on_memory_full,
                              fluorescence_control=args.fluorescence_control,
                              start_delay=args.start_delay,
                              warmup_time=args.warmup_time,
                              burst_duration=args.burst_duration,
                              burst_cycle=args.burst_cycle,
                              total_duration=args.total_duration,
                              log_period=args.log_period,
                              output_cal_header=args.output_cal_header,
                              logger=None,
                              verbose=args.verbose)

        if serial_mode:
            hydroscat.flourescence_command()
            hydroscat.burst_command()

        hydroscat.run()

    except KeyboardInterrupt:
        print("** keyboard interrupt", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("** exiting with error: {}".format(str(e)), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
