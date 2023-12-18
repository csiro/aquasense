"""
HydroScat packet I/O, extraction, calibration class.

See sections 9.5, 9.2.8, and 9.2.9 of User's Manual, Revision J.
"""

import configparser

from aquasense.common.sensor import SensorBase
from aquasense.hydroscat.calibrate import seconds_since_posix_epoch_to_excel_days
from aquasense.hydroscat.calibrate import temperature, depth, voltage, beta
from aquasense.hydroscat.extract_raw import extract_from_raw_line

from collections import OrderedDict

from datetime import datetime

import logging

from typing import Dict, List, TextIO, Tuple, Union

class HydroScat(SensorBase):

    def __init__(self,
                 cal_path: str,
                 in_out: TextIO,
                 out: TextIO,
                 sep: str,
                 serial_mode: bool,
                 burst_mode: bool,
                 sleep_on_memory_full: bool,
                 fluorescence_control: int,
                 start_delay: float,
                 warmup_time: float,
                 burst_duration: float,
                 burst_cycle: float,
                 total_duration: float,
                 log_period: float,
                 output_cal_header: bool=False,
                 logger: logging.Logger=None,
                 verbose: bool=False):
        """Configure initial HydroScat state.
        
        Args:
            cal_path: Path to a HydroScat calibration file.
            in_out: File-like object which is raw packet in_out and command destination.
            out: File-like object to write output to.
            sep: Output column separator.
            serial_mode: Is the in_out a serial port?
            burst_mode: Enable burst mode?
            sleep_on_memory_full: If the HydroScat's memory is full, should it go to sleep?
            fluorescence_control: As per section 8.3.12 of HydroScat user manual.
            start_delay: Start delay (seconds) in sending data.
            warmup_time: Warm-up time in seconds.
            burst_duration: Burst duration in seconds.
            burst_cycle: Burst cycle in minutes.
            total_duration: Total logging duration in minutes.
            log_period: Logging period in seconds.
            output_cal_header: Output header with information from calibration file?
            logger: A logger object; defaults to None.
            verbose: Verbose mode flag.
        """
        SensorBase.__init__(self, in_out, out, sep, logger, verbose)

        self.serial_mode = serial_mode
        self.burst_mode = burst_mode
        self.sleep_on_memory_full = sleep_on_memory_full
        self.fluorescence_control = fluorescence_control
        self.start_delay = start_delay
        self.warmup_time = warmup_time
        self.burst_duration = burst_duration
        self.burst_cycle = burst_cycle
        self.total_duration = total_duration
        self.log_period = log_period
        self.output_cal_header = output_cal_header

        self.aux_data = {"Time":None, "Depth":None, "Voltage":0, "Temperature":None}

        self.config = configparser.ConfigParser()
        self.config.read(cal_path)

        self.num_channels = len(self.channel_names())

        if serial_mode:
            self.init_serial()
            self.exit_str = None
        else:
            self.exit_str = "'End of cast"


    def channel_names(self) -> List[str]:
        """Return a list of channel names for this device."""
        names = []

        if len(self.config) != 0:
            channel_num = 1
            finished = False
            while not finished:
                channel_name = "Channel {}".format(channel_num)
                if channel_name in self.config:
                    names.append(self.config[channel_name]["Name"])
                    channel_num += 1
                else:
                    finished = True

        return names
    
    
    def run(self):
        """Read as many lines of data as the in_out offers
        after issuing the start command."""
        if self.serial_mode:
            self.start_command()

        line, dataline = self.next()

        print("\n".join(self.header_lines()), file=self.out)

        while True:
            if dataline is not None:
                print("{}".format(dataline), file=self.out)
            line, dataline = self.next()
            if line is not None and self.exit_str is not None and \
                line.startswith(self.exit_str):
                break

        self.out.close()
        self.in_out.close()


    def init_serial(self):
        """Issue serial initialisation commands."""
        self.consume_available(self.in_out)
        self.date_command()


    def date_command(self):
        """Issue DATE command"""
        date_time = datetime.strftime(datetime.now(), format="%m/%d/%Y %H:%M:%S")
        self.command_response("DATE,{}".format(date_time),
                              response_patterns=None)


    def flourescence_command(self):
        """Issue FL command"""
        self.command_response("FL,{}".format(self.fluorescence_control),
                              response_patterns=None)


    def burst_command(self):
        """Issue BURST command"""
        burst_mode = 1 if self.burst_mode else 0
        sleep_on_memory_full = 1 if self.sleep_on_memory_full else 0
        auto_start = 0

        self.command_response("BURST,{},{},{},{},{},{},{},{},{}".\
                              format(burst_mode,
                                     self.warmup_time, self.burst_duration,
                                     self.burst_cycle, self.total_duration,
                                     self.log_period, self.start_delay,
                                     auto_start, sleep_on_memory_full),
                               response_patterns=None)


    def start_command(self):
        """Issue START command"""
        return self.command_response("START,{}".format(self.start_delay),
                            response_patterns=["'Sampling starts in 1 second",
                                               r"HS\d"])


    def stop_command(self):
        """Issue STOP command"""
        return self.command_response("STOP",
                                     response_patterns=["'Sampling stopped."])
    

    def header_lines(self):
        """Returns the header lines."""
        header_lines = []

        if self.output_cal_header:
            for section in self.config:
                if "default" not in section.lower() and "end"  not in section.lower():
                    header_lines.append("[{}]".format(section))
                    for param in self.config[section]:
                        val = self.config[section][param]
                        if "//" in val:
                            val = val[0:val.find("//")]
                        if "(" in val:
                            val = val[0:val.find("(")]
                        header_lines.append("{}={}".format(param, val))

        header_lines.append("[ColumnHeadings]")
        names = ["Time", "Depth"]
        for index in range(1, self.num_channels+1):
            channel_config = self.config["Channel {}".format(index)]
            channel_name = channel_config["Name"]
            if channel_name[0:2] in ["bb", "fl"]:
                channel_name = "beta{}".format(channel_name)
            names.append(channel_name)
        header_lines.append(",".join(names))
        header_lines.append("[Data]")

        return header_lines
        

    def next(self) -> Tuple[str,str]:
        """Returns the next data line from the source."""
        rawline = self.in_out.readline()

        dataline = None

        if rawline is not None:
            rawline = rawline.rstrip()
            dataline = self.rawline2dataline(rawline)

        return rawline, dataline


    def rawline2dataline(self, line: str) -> str:
        """Given a line containing a raw packet, return a line of
        calibrated output data.

        Args:
            line: A line corresponding to a raw format packet, ending in CRLF.

        Returns:
            A line of data.

        Throws:
            ValueError if packet checksum field not same as computed checksum value.
        """
        data_dict = self.rawline2datadict(line)
        
        if data_dict is not None:
            dataline = self.sep.join([str(data_dict[key]) for key in data_dict])
        else:
            dataline = None

        return dataline
    

    def rawline2datadict(self, line: str) -> Dict[str,Union[int,float]]:
        """Given a line containing a raw packet, return a dictionary of calibrated
        data or housekeeping packet fields. Also updates auxillary data dictionary.

        Args:
            line: A line corresponding to a raw format packet, ending in CRLF.

        Returns:
            An ordered dictionary of named calibrated data values.

        Throws:
            ValueError if packet checksum field not same as computed checksum value.
        """
        raw_values_dict = extract_from_raw_line(line, self.num_channels)

        if raw_values_dict is None:
            data_dict = None
        elif len(raw_values_dict) <= 21:
            # from data packet
            data_dict = self.raw2datadict(raw_values_dict)
        else:
            # from housekeeping packet
            data_dict = {key: raw_values_dict[key]
                         for key in raw_values_dict if key != "Checksum"}
            # as per section 9.4.5 of user manual, HydroScat manual Rev J,
            # HydroScat only draws power from supply with highest voltage,
            # so find maximum
            VsupA = data_dict["VsupA"]
            VsupB = data_dict["VsupB"]
            Vback = data_dict["Vback"]
            self.aux_data["Voltage"] = voltage(max(VsupA, VsupB, Vback))

        return data_dict


    def raw2datadict(self, raw_values: Dict[str,Union[int,float]]) -> Dict[str,Union[int,float]]:
        """Given a dictionary of raw data packet fields, return a dictionary of calibrated
        data packet fields. Also updates auxillary data dictionary.

        Args:
            raw_values: An ordered dictionary of the numeric fields extracted from the packet.

        Returns:
            An ordered dictionary of named calibrated data values.

        Throws:
            ValueError if packet checksum field not same as computed checksum value.
        """
        data_dict = OrderedDict()

        self.aux_data["Time"] = raw_values["Time"]
        data_dict["Time"] = seconds_since_posix_epoch_to_excel_days(raw_values["Time"])
        
        data_dict["Depth"] = depth(raw_values["RawDepth"],
                                   self.config["General"].getfloat("DepthCal"),
                                   self.config["General"].getfloat("DepthOff"))
        self.aux_data["Depth"] = data_dict["Depth"]

        instr_temperature = temperature(raw_values["TempRaw"])
        self.aux_data["Temperature"] = instr_temperature

        calibration_temperature = self.config["General"].getfloat("CalTemp")

        for index in range(1, self.num_channels+1):
            s_norm = raw_values["Snorm{}".format(index)]
            gain_status = raw_values["GainStatus{}".format(index)]
            gain_index = gain_status & 3 # gain is lower two bits
            status = (gain_status & 4) >> 2 # status is upper bit 2
            channel_config = self.config["Channel {}".format(index)]
            if gain_index != 0:
                beta_value = \
                    beta(s_norm=s_norm, mu=channel_config.getfloat("Mu"),
                         temp_coeff=channel_config.getfloat("TempCoeff"),
                         instr_temp=instr_temperature,
                         cal_temp=calibration_temperature,
                         gain_ratio=channel_config.getfloat("Gain{}".format(gain_index)),
                         r_nom=channel_config.getfloat("RNominal"))
            else:
                beta_value = 0

            data_dict[channel_config["Name"]] = beta_value

        return data_dict
