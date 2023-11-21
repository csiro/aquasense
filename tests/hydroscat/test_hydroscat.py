"""
HydroScat class unit tests.
"""

import io
import os

from collections import OrderedDict

from aquasense.hydroscat.extract_raw import extract_from_raw_line
from aquasense.hydroscat import HydroScat


CAL_FILE = "HS080339-2021-10-16.cal"

T = "*T636CC1C232039D033A064F07A803230323000000003333330008F5CD036A\r\n"
H = "*H636CC1C7068145640635FF05B449C70476FF05504EB10650FF061542070613FF05C04F660676FF069C3BB10763FF0000000000000000000000000000006F6DFF4F0E\r\n"


def test_channel_names():
    hydroscat = hydroscat_instance()

    assert hydroscat.channel_names() == ["bb420", "bb550", "bb442", "bb676",
                                         "bb488", "bb852", "fl550", "fl676"]


def test_raw2datadict():
    hydroscat = hydroscat_instance()

    raw_values = extract_from_raw_line(T, num_channels=8)
    data = hydroscat.raw2datadict(raw_values)

    assert data == \
        OrderedDict([('Time', 44875.38743634259),
                     ('Depth', 0.7031400000000012),
                     ('bb420', 0.025754903765375356),
                     ('bb550', 0.030739601946873866),
                     ('bb442', 0.029715078878937973),
                     ('bb676', 0.029120465467088703),
                     ('bb488', 0.02967847321685616),
                     ('bb852', 0.022862791961543512),
                     ('fl550', 0), ('fl676', 0)])


def test_rawline2datadict_with_T():
    hydroscat = hydroscat_instance()

    data = hydroscat.rawline2datadict(T)

    assert data == \
        OrderedDict([('Time', 44875.38743634259),
                     ('Depth', 0.7031400000000012),
                     ('bb420', 0.025754903765375356),
                     ('bb550', 0.030739601946873866),
                     ('bb442', 0.029715078878937973),
                     ('bb676', 0.029120465467088703),
                     ('bb488', 0.02967847321685616),
                     ('bb852', 0.022862791961543512),
                     ('fl550', 0), ('fl676', 0)])


def test_rawline2datadict_with_H():
    hydroscat = hydroscat_instance()

    data = hydroscat.rawline2datadict(H)

    assert data == \
        OrderedDict([('Time', 1668071879), ('SigOff1', 1665), ('Ref1', 17764),
                     ('RefOff1', 1589), ('Back1', -1), ('SigOff2', 1460), ('Ref2', 18887),
                     ('RefOff2', 1142), ('Back2', -1), ('SigOff3', 1360), ('Ref3', 20145),
                     ('RefOff3', 1616), ('Back3', -1), ('SigOff4', 1557), ('Ref4', 16903),
                     ('RefOff4', 1555), ('Back4', -1), ('SigOff5', 1472), ('Ref5', 20326),
                     ('RefOff5', 1654), ('Back5', -1), ('SigOff6', 1692), ('Ref6', 15281),
                     ('RefOff6', 1891), ('Back6', -1), ('SigOff7', 0), ('Ref7', 0),
                     ('RefOff7', 0), ('Back7', 0), ('SigOff8', 0), ('Ref8', 0),
                     ('RefOff8', 0),
                     ('Back8', 0), ('VsupA', 0), ('VsupB', 111), ('Vback', 109), ('VAux', -177)])
    

def test_raw2dataline():
    hydroscat = hydroscat_instance()

    dataline = hydroscat.rawline2dataline(T)

    assert dataline == \
        "44875.38743634259,0.7031400000000012,0.025754903765375356," + \
        "0.030739601946873866,0.029715078878937973,0.029120465467088703," + \
        "0.02967847321685616,0.022862791961543512,0,0"


def test_dataline_generator():
    line_str = "*T636CC1C232039D033A064F07A803230323000000003333330008F5CD036A\r\n" + \
               "*T636CC1C300050E048208380A0E045C049F000000003333330008FECD008C\r\n" + \
               "*T636CC1C3320508047308480A15045E0497000000003333330008EFCD0069\r\n"
    
    raw_source = io.StringIO(initial_value=line_str)

    hydroscat = hydroscat_instance(raw_source)
    
    datalines = []
    rawline, dataline = hydroscat.next()
    while dataline is not None:
        datalines.append(dataline)
        rawline, dataline = hydroscat.next()

    assert len(datalines) == 3
    assert datalines[0] == \
        "44875.38743634259,0.7031400000000012,0.025754903765375356," + \
        "0.030739601946873866,0.029715078878937973,0.029120465467088703," + \
        "0.02967847321685616,0.022862791961543512,0,0"
    assert datalines[1] == \
        "44875.387442129635,0.8199600000000018,0.036029022132319684," + \
        "0.04294612669091095,0.03871239997602817,0.03824289699606445," + \
        "0.04124679465754854,0.03368204594085426,0,0"
    assert datalines[2] == \
        "44875.38744791667,0.6252600000000008,0.03586196329708482," + \
        "0.04238790147395803,0.03900679085037059,0.038346898658446905," + \
        "0.04132071364439002,0.033454272172868775,0,0"


def test_header_lines():
    hydroscat = hydroscat_instance()
    hydroscat.output_cal_header = True
    header_lines = hydroscat.header_lines()
    assert len(header_lines) != 0


def test_date_command():
    hydroscat = hydroscat_instance(io.StringIO())
    # considered a pass if no exception
    hydroscat.date_command()


def test_flourescence_command():
    hydroscat = hydroscat_instance(io.StringIO())
    # considered a pass if no exception
    hydroscat.flourescence_command()


def test_burst_command():
    hydroscat = hydroscat_instance(io.StringIO())
    # considered a pass if no exception
    hydroscat.burst_command()


def test_start_command():
    response = "'Sampling starts in 1 second"
    hydroscat = hydroscat_instance(MockIOChannel(response_line=response),
                                   serial_mode=True)
    # considered a pass if no exception and reads response
    hydroscat.start_command()


def test_stop_command():
    response = "'Sampling stopped."
    hydroscat = hydroscat_instance(in_out=MockIOChannel(response_line=response),
                                   serial_mode=True)
    # considered a pass if no exception and reads response
    hydroscat.stop_command()


# Helpers

class MockIOChannel:
    # Mock I/O channel class tailored for usage in this context
    def __init__(self, consumable_lines=["\n"], response_line=None):
        self.consumable_lines= consumable_lines
        self.response_data = response_line

    def write(self, data):
        pass

    def flush(self):
        pass

    def readline(self):
        return self.response_data
    
    def readlines(self):
        if len(self.consumable_lines) != 0:
            self.consumable_lines.pop()
        return self.consumable_lines


def hydroscat_instance(in_out=None, serial_mode=False):
    cal_path = full_path_from_filename(CAL_FILE)
    assert cal_path is not None

    return HydroScat(cal_path=cal_path, in_out=in_out, out=None,
                     sep=",", serial_mode=serial_mode,
                     burst_mode=1, sleep_on_memory_full=0,
                     fluorescence_control=1, start_delay=1,
                     warmup_time=0, burst_duration=0, burst_cycle=0.7,
                     total_duration=0.4, log_period=0.6, logger=None, verbose=True)


def full_path_from_filename(filename: str) -> str:
    path = None
    for root, dir, files in os.walk("."):
        if filename in files:
            path = os.path.join(root, filename)
    return path