"""
HydroScat calibration functions.
"""

def seconds_since_posix_epoch_to_excel_days(seconds: float) -> float:
    """Convert seconds since January 1 1970 (POSIX epoch)
       to days since January 1 1900 (Excel epoch).

    Args:
        seconds: seconds since POSIX epoch

    Returns:
        The decimal days since Excel epoch.
    """
    #from datetime import datetime
    #hydroscat_epoch = datetime(1900, 1, 1)
    #posix_epoch = datetime(1970, 1, 1)
    #delta = posix_epoch - hydroscat_epoch
    #seconds_since_posix_epoch = datetime.fromtimestamp(seconds)
    seconds_per_day = 86400
    days_since_1970 = seconds/seconds_per_day
    excel_day_1970_01_01 = 25569
    return days_since_1970 + excel_day_1970_01_01


def temperature(raw_temperature: int) -> float:
    """Convert the raw temperature to temperature in degrees C.
       See section 9.2.9 of HydroScat manual Rev J, TempRaw

    Args:
        raw_temperature: raw integer temperature from a D or T packet

    Returns:
        The converted, actual temperature.
    """
    return raw_temperature / 5.0 - 10


def depth(raw_depth: int, depth_cal: float, depth_off: float) -> float:
    """Convert the raw depth to depth in metres.
       See section 9.2.8 of HydroScat manual Rev J, DepthRaw

    Args:
        raw_depth: raw integer depth from a D or T packet.
        depth_cal: depth calibration value.
        depth_off: depth offset calibration value

    Returns:
        The converted, actual depth.
    """
    return raw_depth * depth_cal - depth_off


def voltage(raw_voltage: int) -> float:
    """Convert the raw voltage to a decimal voltage value.
       See section 9.4.5 of HydroScat manual Rev J, VsupA, VsupB, Vback

    Args:
        raw_voltage: raw integer voltage value from a H packet.

    Returns:
        The decimal voltage value.
    """
    return raw_voltage / 10


def beta(s_norm: int, mu: float,
         temp_coeff: float, instr_temp: float, cal_temp: float,
         gain_ratio: float, r_nom: float) -> float:
    """Convert the raw signal to the value of the volume scattering function.
       See section 9.5 of HydroScat manual Rev J, Calculating beta and bb

    Args:
        s_norm: raw normalized backscatter value from HydroScat
        mu: mu value from .cal file
        temp_coeff: temperature coefficient (TempCoeff) in .cal file
        instr_temp: instrument temperature from temperature function
        cal_temp: temperature calibration value (CalTemp) in .cal file
        gain_ratio: gain ratio for gain_g (Gain1 - Gain5) in .cal file
        r_nom: nominal reference value (Rnom) in .cal file

    Returns:
        value of the volume scattering function, beta(140 degrees)
    """
    return s_norm * mu / \
        ((1.0 + temp_coeff*(instr_temp - cal_temp)) * gain_ratio * r_nom)