"""
HydroScat raw data extraction functions.

D, T, and H packets are handled.

See HydroScat-6P Spectral Backscattering Sensor & Fluorometer
    User's Manual, Revision J, Raw Data Formats section.
"""

from typing import Dict, List, Tuple, Union
import numpy as np

# TODO
# - improve signed/unsigned function efficiency

def extract_from_raw_line(line: str, num_channels: int) -> List[Union[int,float]]:
    """Extract the numeric fields from the packet in a line.

    Args:
        line: A line corresponding to a raw format packet, ending in CRLF.
        num_channels: The number of HydroScat channels.

    Returns:
        A list of the numeric fields extracted from the packet.

    Raises:
        ValueError if packet checksum field not same as computed checksum value.
    """
    packet_handlers = {
        "*D":extract_from_data_packet,
        "*T":extract_from_data_packet,
        "*H":extract_from_H_packet
    }

    fields = None

    if len(line) > 2:
        line = line.rstrip()
        packet_prefix = line[0:2]

        if packet_prefix in packet_handlers:
            fields = packet_handlers[packet_prefix](line, num_channels=8)
        
            if fields["Checksum"] != checksum(line):
                raise ValueError()

    return fields


def extract_time(packet: str, start: int, frac_time: bool) -> Tuple[int,
                                                                    Union[int,float]]:
    """Extract the time from the packet.

    Args:
        packet: A raw D, T or H format packet.
        start: The start index in the packet string.
        frac_time: Include fractional time (T packet)?

    Returns:
        A tuple containing the next packet string index and
        the integer or decimal time.
    """
    # Extract integer time and, optionally fractional time
    #
    # Note: packet tables in user manual say signed 32 bit
    # but that is not validated by detailed description, which
    # indicates time starts from zero, so assuming unsigned 32 bit
    Time = packet[start:start+8] # 8 signed bytes
    decimalTime = unsigned32(Time)

    if frac_time:
        FractionalTime = packet[start+8:start+10] # 2 unsigned bytes
        decimalTime += unsigned8(FractionalTime)/100
        next_byte = start+10
    else:
        next_byte = start+8

    return next_byte, decimalTime


def extract_from_data_packet(packet: str, num_channels: int) -> Dict[str,Union[int,float]]:
    """Extract the numeric fields from the raw data packet.
    
    Args:
        packet: A raw D or T format packet.
        num_channels: The number of HydroScat channels.

    Returns:
        An ordered dictionary of the numeric fields extracted from the data packet.
        Note that a gain/status value of zero implies that the corresponding
        channel is disabled and its data should be ignored (see section 9.2.7
        in HydroScat manual Rev J, Gain/Status).
    """
    fields = {}

    start, Time = extract_time(packet, 2, packet[1] == "T")
    fields["Time"] = Time

    # Snorm1..N (16 bits each)
    for i in range(0, num_channels):
        Snorm = packet[start:start+4]
        fields["Snorm{}".format(i+1)] = signed16(Snorm)
        start += 4

    # Gain/Status1..N (1 nibble each)
    for i in range(0, num_channels):
        GainStatus = packet[start]
        fields["GainStatus{}".format(i+1)] = int(GainStatus, 16)
        start += 1

    # Raw depth/temperature, error, checksum

    RawDepth = packet[start:start+4]
    fields["RawDepth"] = signed16(RawDepth)
    start += 4

    TempRaw = packet[start:start+2]
    fields["TempRaw"] = unsigned8(TempRaw)
    start += 2

    # 1 byte
    Error = packet[start:start+2]
    fields["Error"] = int(Error, 16)
    start += 2

    # 1 byte
    Checksum = packet[start:start+2]
    fields["Checksum"] = int(Checksum, 16)
    start += 2

    return fields


def extract_from_H_packet(packet: str, num_channels: int) -> Dict[str,int]:
    """Extract the numeric fields from the raw H packet.

    Args:
        packet: A raw H format packet without the 2 byte packet prefix.
        num_channels: The number of HydroScat channels.

    Returns:
        An ordered dictionary of the numeric fields extracted from the H packet.
    """
    fields = {}

    start, Time = extract_time(packet, 2, packet[1] == "T")
    fields["Time"] = Time

    # SigOff1..N (16 bits), Ref1..N (16 bits), RefOff1..N (16 bits), Back1..N (16 bits)

    for i in range(0, num_channels):
        SigOff = packet[start:start+4]
        fields["SigOff{}".format(i+1)] = signed16(SigOff)
        start += 4

        Ref = packet[start:start+4]
        fields["Ref{}".format(i+1)] = signed16(Ref)
        start += 4

        RefOff = packet[start:start+4]
        fields["RefOff{}".format(i+1)] = signed16(RefOff)
        start += 4
        
        Back = packet[start:start+2]
        fields["Back{}".format(i+1)] = signed8(Back)
        start += 2

    VsupA = packet[start:start+2]
    fields["VsupA"] = unsigned8(VsupA)
    start += 2

    VsupB = packet[start:start+2]
    fields["VsupB"] = unsigned8(VsupB)
    start += 2

    Vback = packet[start:start+2]
    fields["Vback"] = unsigned8(Vback)
    start += 2

    VAux = packet[start:start+4]
    fields["VAux"] = signed16(VAux)
    start += 4

    # 1 byte
    Checksum = packet[start:start+2]
    fields["Checksum"] = int(Checksum, 16)

    return fields


def checksum(line: str) -> int:
    """Sum all bytes except the packet flag, preceding the checksum byte,
       returning the value of the least significant byte of the sum.

    Args:
        line: A line corresponding to a raw format packet, NOT ending in CRLF.

    Returns:
        Integer value of the least significant byte of the unsigned sum.
    """
    return sum([ord(byte) for byte in line[1:-2]]) & 0xFF
    

# Helpers

# These functions should be used where we have an explicit need
# for signed/unsigned values vs char, byte, nibble

def signed8(num_str: str, base=16) -> int:
    return int(np.int8(int(num_str, base)))


def unsigned8(num_str: str, base=16) -> int:
    return int(np.uint8(int(num_str, base)))


def signed16(num_str: str, base=16) -> int:
    return int(np.int16(int(num_str, base)))


def unsigned16(num_str: str, base=16) -> int:
    return int(np.uint16(int(num_str, base)))


def signed32(num_str: str, base=16) -> int:
    return int(np.int32(int(num_str, base)))


def unsigned32(num_str: str, base=16) -> int:
    return int(np.uint32(int(num_str, base)))