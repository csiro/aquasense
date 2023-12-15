## Overview

Instrument emulators in this directory have been implemented and tested on Arduino Uno microcontrollers. The key requirement is that the Arduino can be connected via USB to a computer, appearing as a serial port to software.

The intended use of emulation in this context is to permit testing at the system level in the absence of immediate or frequent access to the real instrument, providing confidence that the code works at the `driver.py` level (see `src` sub-directories) before connecting the actual instrument.

Currently only a HOBILabs HydroScat emulator is provided, but more may be added over time. Only the necessary subset of command handling and a small amount of data is used for output to "fool" software into "thinking" that it is connected to an actual HydroScat. See also the [vendor's manual](https://www.hobilabs.com/cms/index.cfm/37/1288/1295/2831.htm).

See also the main `README.md` re: use of the `driver.py` for command-line interaction with an instrument or emulator.