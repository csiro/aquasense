"""
HydroScat calibration function unit tests.
"""

import pytest

from aquasense.hydroscat.calibrate import seconds_since_posix_epoch_to_excel_days
from aquasense.hydroscat.calibrate import temperature, depth, voltage, beta


def test_seconds_since_epoch_to_decimal_days():
    # - time in seconds taken from 1st row of data in sample.dec
    # - verified result from sampledat_updated.dat file
    assert seconds_since_posix_epoch_to_excel_days(1668071874.5) == \
        pytest.approx(44875.38744)
    # - time in seconds taken from 10th row of data in sample.dec
    # - verified result from sampledat_updated.dat file
    assert seconds_since_posix_epoch_to_excel_days(1668071878.5) == \
        pytest.approx(44875.38749)


def test_temperature():
    # raw temperature value taken from
    # test_extract_raw.py:test_extract_T_1()
    raw_temperature = 205

    # verified result from sample.dec file
    assert temperature(raw_temperature) == 31.0


def test_depth():
    # raw depth value taken from
    # test_extract_raw.py:test_extract_T_1()
    depth_raw = 2293

    # depth cal and off values taken from HS080339 2021-10-16.cal
    depth_cal = .01298
    depth_off = 29.06

    # verified result from sampledat_updated.dat file
    # (manual calculation gives 0.70314vs 0.7031408)
    assert depth(depth_raw, depth_cal, depth_off) == \
        pytest.approx(0.70314)


def test_voltage():
    assert voltage(raw_voltage=119) == 11.9


# test_beta*():
# - raw Snorm1 and Gain/Status values taken from
#   test_extract_raw.py:test_extract_T_1()
#   (extracted raw packet value 3 = Gain3)
# - instrument temperature taken from test_temperature()
# - mu, temp coefficient & calibration, and nominal reference
#   values taken from HS080339 2021-10-16.cal
#   (Channel N [bbxyz] and General sections)
# - verified result from sampledat_updated.dat file


def test_betabb420():
    assert beta(s_norm=925, mu=21.23, temp_coeff=-.000806,
                            instr_temp=31.0, cal_temp=22.4,
                            gain_ratio=95.976, r_nom=8000) == \
            pytest.approx(0.0257549)


def test_betabb550():
    assert beta(s_norm=826, mu=28.3, temp_coeff=.000235,
                            instr_temp=31.0, cal_temp=22.4,
                            gain_ratio=94.864, r_nom=8000) == \
            pytest.approx(0.0307396)


def test_betabb442():
    assert beta(s_norm=1615, mu=13.99, temp_coeff=-.000236,
                            instr_temp=31.0, cal_temp=22.4,
                            gain_ratio=95.237, r_nom=8000) == \
            pytest.approx(2.971508E-02)


def test_betabb676():
    assert beta(s_norm=1960, mu=11.03, temp_coeff=-.003349,
                            instr_temp=31.0, cal_temp=22.4,
                            gain_ratio=95.551, r_nom=8000) == \
            pytest.approx(2.912047E-02)
    

def test_betabb488():
    assert beta(s_norm=803, mu=28.23, temp_coeff=-.000147,
                            instr_temp=31.0, cal_temp=22.4,
                            gain_ratio=95.597, r_nom=8000) == \
            pytest.approx(2.967847E-02)
    

def test_betabb852():
    assert beta(s_norm=803, mu=22.81, temp_coeff=.005131,
                            instr_temp=31.0, cal_temp=22.4,
                            gain_ratio=95.911, r_nom=8000) == \
            pytest.approx(2.286279E-02)
    

# beta() should never be called if the raw gain/status value
# is zero; a value of zero should be used instead for the value of the
# corresponding channel; invoking beta() when raw gain/status
# for the channel is therefore undefined, e.g. see fl550, fl676 in sample data