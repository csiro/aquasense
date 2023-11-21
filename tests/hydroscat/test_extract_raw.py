"""
HydroScat raw extraction function unit tests.
"""

import pytest

from aquasense.hydroscat.extract_raw import checksum, extract_time
from aquasense.hydroscat.extract_raw import extract_from_raw_line, extract_from_data_packet
from aquasense.hydroscat.extract_raw import extract_from_H_packet

# Raw packets

D = [
     # from HydroScat user manual, section 9.2; checksum incorrect!
     "*D346A023C055613CC160615DE13232034FB24F952555555000648870042\r\n"
    ]

T = [
     # from supplied sample.dat, lines 12 and 20
     "*T636CC1C232039D033A064F07A803230323000000003333330008F5CD036A\r\n",
     "*T636CC1C632052B049A086E0A51046B04B3000000003333330008F6CD008B\r\n",
     # from HydroScat user manual, section 9.3; checksum incorrect!
     #"*T346A023C1A055613CC160615DE13232034FB24F9525555550006488700B4\r\n"
     ]

H = [
     # first H packet from supplied sample.dat, line 22
     "*H636CC1C7068145640635FF05B449C70476FF05504EB10650FF061542070613FF05C04F660676FF069C3BB10763FF0000000000000000000000000000006F6DFF4F0E\r\n"
    ]


# ** Checksum **

def test_checksum_T():
    for line in T:
        chk = checksum(line.rstrip())
        assert chk == int(line[-4:-2], 16)


# ** D packet **

def test_extract_time_from_D():
    index, Time = extract_time(packet=D[0], start=2, frac_time=False)
    assert index == 10
    assert Time == 879362620


def test_extract_D():
    packet = D[0].rstrip()
    fields = extract_from_data_packet(packet, num_channels=8)
    assert len(fields) == 21
    assert [value for value in fields.values()] == \
        [879362620, 1366, 5068, 5638, 5598, 4899, 8244,
         -1244, -1710, 5, 5, 5, 5, 5, 5, 0, 0, 1608, 135, 0, 66]


# ** T packet **

def test_extract_time_from_T():
    index, Time = extract_time(packet=T[0], start=2, frac_time=True)
    assert index == 12
    assert Time == 1668071874.5


def test_extract_T_1():
    packet = T[0].rstrip()
    fields = extract_from_data_packet(packet, num_channels=8)
    assert len(fields) == 21
    # Verified by HydroScat software save of sample.raw + sample.dec
    # Note: raw temperature (205 here) in .dec file is converted to
    # actual temperature as per 9.2.9 of HydoScat user manual
    # TODO: why do we see Error value of 3 (2**1 + 2**0 = 11: high background & signal)?
    assert [value for value in fields.values()] == \
        [1668071874.5, 925, 826, 1615, 1960, 803, 803,
         0, 0, 3, 3, 3, 3, 3, 3, 0, 0, 2293, 205, 3, 106]


def test_extract_T_2():
    packet = T[1].rstrip()
    fields = extract_from_data_packet(packet, num_channels=8)
    assert len(fields) == 21
    # Verified by HydroScat software save of sample.raw + sample.dec
    # Note: raw temperature (205 here) in .dec file is converted to
    # actual temperature as pe 9.2.9 of HydoScat user manual
    assert [value for value in fields.values()] == \
        [1668071878.5, 1323, 1178, 2158, 2641, 1131, 1203,
         0, 0, 3, 3, 3, 3, 3, 3, 0, 0, 2294, 205, 0, 139]


def test_extract_raw_with_T():
    fields = extract_from_raw_line(T[0], num_channels=8)
    assert len(fields) == 21
        

def test_extract_raw_with_T_bad_checksum():
    T_bad_checksum = "{}{}\r\n".format(T[0][:-4], "77")
    with pytest.raises(ValueError):
        extract_from_raw_line(T_bad_checksum, num_channels=8)


# ** H packet **

def test_extract_time_from_H():
    index, Time = extract_time(packet=H[0], start=2, frac_time=False)
    assert index == 10
    assert Time == 1668071879


def test_extract_raw_with_H():
    fields = extract_from_raw_line(H[0], num_channels=8)
    assert len(fields) == 38


def test_extract_H():
    packet = H[0].rstrip()
    fields = extract_from_H_packet(packet, num_channels=8)
    assert len(fields) == 38
    assert [value for value in fields.values()] == \
                     [1668071879,
                      1665, 17764, 1589, -1,
                      1460, 18887, 1142, -1,
                      1360, 20145, 1616, -1,
                      1557, 16903, 1555, -1,
                      1472, 20326, 1654, -1,
                      1692, 15281, 1891, -1,
                      0, 0, 0, 0,
                      0, 0, 0, 0,
                      0, 111, 109, -177,
                      14]
