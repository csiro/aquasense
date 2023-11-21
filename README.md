## Overview

Python 3.7 or higher.

### Installation

    pip install .

### Unit Tests 

Pytest requires `pip install pytest`

Coverage requires `pip install pytest-cov`

    cd Sensors
    pytest
    pytest -v
    pytest --cov
    pytest --cov --cov-report=html:covrep
    pytest --cov --cov-branch --cov-report=html:covrep

Add `--disable-warnings` if necessary, depending upon Python version.

### Example Runs
#### HydroScat

    # Decode data from a sample raw file using specified calibration file
    python src/aquasense/hydroscat/driver.py --source tests/data/sample.raw --cal-path tests/data/HS080339-2021-10-16.cal --verbose

    # Decode data via a serial port connection using specified calibration file
    python src/aquasense/hydroscat/driver.py -s COM9 -c tests/data/HS080339-2021-10-16.cal -b 9600 --burst-mode -v

    usage: driver.py [-h] [--source SOURCE] [--cal-path CAL_PATH]
                 [--output-path OUT_PATH]
                 [--output-field-delimiter OUTPUT_FIELD_DELIMITER]
                 [--baud-rate BAUD_RATE] [--serial-timeout TIMEOUT]
                 [--num-channels NUM_CHANNELS] [--burst-mode]
                 [--sleep-on-memory-full]
                 [--fluorescence-control FLUORESCENCE_CONTROL]
                 [--start-delay START_DELAY] [--warmup-time WARMUP_TIME]
                 [--burst-duration BURST_DURATION] [--burst-cycle BURST_CYCLE]
                 [--total-duration TOTAL_DURATION] [--log-period LOG_PERIOD]
                 [--output-cal-header] [--verbose]

    Read HydroScat data from a file or serial port.

    optional arguments:
    -h, --help            show this help message and exit
    --source SOURCE, -s SOURCE
                            Raw lines source (file path or serial port name)
    --cal-path CAL_PATH, -c CAL_PATH
                            Calibration file path
    --output-path OUT_PATH, -o OUT_PATH
                            Output file path
    --output-field-delimiter OUTPUT_FIELD_DELIMITER, -d OUTPUT_FIELD_DELIMITER
                            Delimiter for fields in output rows (default: ,)
    --baud-rate BAUD_RATE, -b BAUD_RATE
                            Serial port baud rate (default: 9600)
    --serial-timeout TIMEOUT, -t TIMEOUT
                            Serial port read timeout (default: 1 second)
    --num-channels NUM_CHANNELS, -n NUM_CHANNELS
                            Number of HydroScat channels (default: 8)
    --burst-mode, -e      Enable burst mode?
    --sleep-on-memory-full, -z
                            Enable burst mode?
    --fluorescence-control FLUORESCENCE_CONTROL, -f FLUORESCENCE_CONTROL
                            Fluorescence channel setting (0, 1, 2) as per section
                            8.3.12 of HydroScat user manual (default: 1)
    --start-delay START_DELAY, -r START_DELAY
                            Start delay in seconds (default: 1)
    --warmup-time WARMUP_TIME, -w WARMUP_TIME
                            Start delay in seconds (default: 0)
    --burst-duration BURST_DURATION, -u BURST_DURATION
                            Burst duration in seconds (default: 0)
    --burst-cycle BURST_CYCLE, -y BURST_CYCLE
                            Burst cycle in minutes (default: 0.7)
    --total-duration TOTAL_DURATION, -a TOTAL_DURATION
                            Total duration in minutes (default: 0.4)
    --log-period LOG_PERIOD, -i LOG_PERIOD
                            Log period in seconds (default: 0.6)
    --output-cal-header, -l
                            Output calibration header
    --verbose, -v         Verbose output mode