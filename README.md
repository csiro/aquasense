[![Unit Tests](https://github.com/csiro/aquasense/actions/workflows/unit-test.yml/badge.svg)](https://github.com/csiro/aquasense/actions/workflows/unit-test.yml)

## Overview

Aquasense is a Python library for communicating with aquatic 
sensors with simpler drivers for standalone use or for 
integration with tools such as data loggers.

Support for HOBILabs HydroScat and Trios RAMSES currently exists.

Python 3.7 or higher is required.

### Installation
#### Aquasense

    pip install .

#### PyTrios library used by `aquasense` (optional, only required if `ramses` used)
    git clone https://github.com/StefanSimis/PyTrios.git
    cd PyTrios
    pip install .

### Unit Tests 

Pytest requires `pip install pytest`

    pytest
    pytest -v

Pytest coverage requires `pip install pytest-cov`

    pytest --cov
    pytest --cov --cov-report=html:covrep
    pytest --cov --cov-branch --cov-report=html:covrep

Add `--disable-warnings` to `pytest` commands if necessary,
depending upon Python version.

### Example Runs

#### HydroScat

##### With a raw input file
    # Decode data from a sample raw file using the specified calibration file
    python src/aquasense/hydroscat/driver.py --source tests/hydroscat/data/sample.raw --cal-path tests/hydroscat/data/HS080339-2021-10-16.cal --verbose

##### Output
    [ColumnHeadings]
    Time,Depth,betabb420,betabb550,betabb442,betabb676,betabb488,betabb852,betafl550,betafl676
    [Data]
    44875.38743634259,0.7031400000000012,0.025754903765375356,0.030739601946873866,0.029715078878937973,0.029120465467088703,0.02967847321685616,0.022862791961543512,0,0
    44875.387442129635,0.8199600000000018,0.036029022132319684,0.04294612669091095,0.03871239997602817,0.03824289699606445,0.04124679465754854,0.03368204594085426,0,0
    44875.38744791667,0.6252600000000008,0.03586196329708482,0.04238790147395803,0.03900679085037059,0.038346898658446905,0.04132071364439002,0.033454272172868775,0,0
    44875.387453703705,0.7420800000000014,0.03588980643629063,0.04279726663305684,0.039025190280017,0.03845090032082937,0.04143159212465225,0.033539687335863336,0,0
    44875.38745949074,0.7161200000000001,0.03616823782834874,0.043020556719838,0.039632371458348234,0.039030338154103075,0.04187510604570116,0.033653574219856076,0,0
    44875.387465277774,0.6901600000000023,0.03611255154993712,0.0432810618210827,0.039043589709663394,0.03854004460287148,0.041727268072018195,0.033881347987841565,0,0
    44875.387471064816,0.6122800000000019,0.03542222298827248,0.04234870008505326,0.039211039101470516,0.0386707160376383,0.04165457527984523,0.03379119351302306,0,0
    ...

##### From a serial port connected instrument or emulator
    # Decode data via a serial port connection using the specified calibration file
    # Running the emulator in emulation/hydroscat on an Arduino microcontroller will # allow this command to be tested independent of a real HydroScat instrument. The
    # serial port name may differ from this particular example.
    python src/aquasense/hydroscat/driver.py -s COM9 -c tests/hydroscat/data/HS080339-2021-10-16.cal -b 9600 --burst-mode -v

#### Output
    INFO:HydroScat:>> DATE,12/15/2023 15:01:47
    INFO:HydroScat:>> FL,1
    INFO:HydroScat:>> BURST,1,0,0,0.7,0.4,0.6,1,0,0
    INFO:HydroScat:>> START,1
    INFO:HydroScat:?? ["'Sampling starts in 1 second", 'HS\\d']
    INFO:HydroScat:<< 'Sampling starts in 1 seconds.

    [ColumnHeadings]
    Time,Depth,betabb420,betabb550,betabb442,betabb676,betabb488,betabb852,betafl550,betafl676
    [Data]
    44875.38743634259,0.7031400000000012,0.025754903765375356,0.030739601946873866,0.029715078878937973,0.029120465467088703,0.02967847321685616,0.022862791961543512,0,0
    44875.387442129635,0.8199600000000018,0.036029022132319684,0.04294612669091095,0.03871239997602817,0.03824289699606445,0.04124679465754854,0.03368204594085426,0,0
    44875.38744791667,0.6252600000000008,0.03586196329708482,0.04238790147395803,0.03900679085037059,0.038346898658446905,0.04132071364439002,0.033454272172868775,0,0
    44875.387453703705,0.7420800000000014,0.03588980643629063,0.04279726663305684,0.039025190280017,0.03845090032082937,0.04143159212465225,0.033539687335863336,0,0
    44875.38745949074,0.7161200000000001,0.03616823782834874,0.043020556719838,0.039632371458348234,0.039030338154103075,0.04187510604570116,0.033653574219856076,0,0
    44875.387465277774,0.6901600000000023,0.03611255154993712,0.0432810618210827,0.039043589709663394,0.03854004460287148,0.041727268072018195,0.033881347987841565,0,0
    44875.387471064816,0.6122800000000019,0.03542222298827248,0.04234870008505326,0.039211039101470516,0.0386707160376383,0.04165457527984523,0.03379119351302306,0,0
    ...

##### From a serial port connected instrument or emulator with calibration header
    # As per last example, but also output the calibration header.
    python src/aquasense/hydroscat/driver.py -s COM10 -c tests/hydroscat/data/HS080339-2021-10-16.cal -b 9600 --burst-mode --output-cal-header -v

##### Output
    INFO:HydroScat:>> DATE,12/15/2023 15:05:11
    INFO:HydroScat:>> FL,1
    INFO:HydroScat:>> BURST,1,0,0,0.7,0.4,0.6,1,0,0
    INFO:HydroScat:>> START,1
    INFO:HydroScat:?? ["'Sampling starts in 1 second", 'HS\\d']
    INFO:HydroScat:<< 'Sampling starts in 1 seconds.

    [General]
    devicetype=HydroScat-6
    serial=HS080339
    label=CSIRO-2
    config=F1B2
    maxdepth=330
    caltime=1634395533
    depthcal=.01298
    depthoff=29.06
    caltemp=22.4
    [Channel 1]
    name=bb420
    gain1=1
    gain2=9.7006
    ...
    mu=21.23
    sigma1=.999
    sigma2=0
    ...
    sigmaexp=.143
    rnominal=8000
    beta2bb=6.79
    murho=1.1
    tempcoeff=-.000806
    offset1=2
    offset2=2
    ...
    nomoffset1=1639
    nomoffset2=1639
    ...
    floffset1=0
    floffset2=0
    ...
    [Channel 2]
    name=bb550
    ...
    [ColumnHeadings]
    Time,Depth,betabb420,betabb550,betabb442,betabb676,betabb488,betabb852,betafl550,betafl676
    [Data]
    44875.38743634259,0.7031400000000012,0.025754903765375356,0.030739601946873866,0.029715078878937973,0.029120465467088703,0.02967847321685616,0.022862791961543512,0,0
    44875.387442129635,0.8199600000000018,0.036029022132319684,0.04294612669091095,0.03871239997602817,0.03824289699606445,0.04124679465754854,0.03368204594085426,0,0
    ...

##### Usage
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

#### RAMSES

##### From a serial port connection, here via an IPS box with two RAMSES instruments 
    python src/aquasense/ramses/driver.py -p COM4 -i 0 -o testing.txt
    Start listening thread on COM4
    Closing ports
    Finished closing ports
    INFO:rad:Connecting: Starting listening threads
    Start listening thread on COM4
    INFO:rad:found SAM modules: [('020080', '5039'), ('040000', '8035')]
    INFO:rad:       2 spectra received, triggered at 2023-11-30 14:47:45.241151 (5.758781 s)
    Closing ports
    Finished closing ports
    Closing ports
    Finished closing ports

##### `testing.txt` output
    5039	2023-11-30T14:47:45.241151	4096	2827,2599,2589,2594,2605,2605,2610,2602,2612,2610,2598,2601,2598,2598,2607,2611,2601,2608,2614,2617,2612,2611,2616,2626,2627,2616,2628,2633,2633,2658,2668,2677,2698,2703,2733,2762,2761,2770,2781,2823,2860,2873,2903,2925,2958,2961,2958,2971,2960,2965,2962,2960,2980,2985,2980,2999,2995,3003,3009,3007,3035,3057,3070,3090,3097,3140,3180,3205,3248,3282,3313,3340,3339,3369,3389,3390,3390,3383,3392,3386,3367,3374,3362,3364,3347,3318,3291,3278,3291,3301,3280,3283,3271,3273,3272,3260,3264,3265,3246,3236,3238,3231,3207,3181,3165,3150,3169,3170,3192,3194,3197,3183,3182,3168,3144,3096,3080,3092,3104,3106,3127,3138,3119,3106,3056,3037,3023,3040,3074,3118,3154,3178,3203,3214,3219,3181,3096,3006,2997,3068,3133,3176,3181,3164,3157,3122,3093,3085,3054,3037,3026,2996,2977,2906,2892,2872,2865,2868,2867,2873,2856,2869,2876,2855,2830,2837,2808,2820,2806,2788,2793,2771,2766,2762,2751,2762,2743,2720,2714,2693,2674,2656,2665,2678,2648,2669,2667,2666,2648,2637,2632,2630,2610,2625,2609,2616,2630,2621,2628,2625,2622,2625,2613,2643,2633,2628,2636,2630,2640,2627,2619,2636,2640,2623,2632,2612,2619,2618,2620,2622,2611,2612,2612,2620,2602,2610,2605,2608,2606,2611,2602,2596,2606,2599,2612,2616,2601,2598,2593,2592,2600,2613,2600,2604,2609,2598,2603,2598,2605,2594,2597,2604,2600,2596,2603,2716

    8035	2023-11-30T14:47:45.241151	4096	2315,2269,2268,2258,2259,2268,2272,2269,2263,2275,2289,2272,2286,2293,2296,2306,2318,2299,2332,2334,2347,2330,2349,2332,2340,2326,2341,2342,2355,2369,2391,2408,2413,2434,2462,2463,2471,2485,2489,2499,2516,2540,2538,2544,2560,2574,2571,2556,2554,2539,2542,2521,2538,2525,2514,2518,2513,2510,2530,2542,2526,2522,2537,2530,2548,2553,2573,2576,2566,2572,2582,2564,2593,2583,2595,2584,2603,2593,2610,2631,2630,2674,2702,2796,2865,2920,2984,3067,3161,3245,3308,3366,3372,3369,3368,3347,3320,3288,3250,3263,3237,3226,3192,3127,3087,3054,3065,3071,3077,3070,3070,3066,3049,3031,2981,2940,2896,2880,2888,2892,2908,2905,2910,2869,2797,2757,2749,2739,2781,2831,2868,2892,2912,2910,2906,2841,2753,2648,2609,2655,2721,2757,2748,2741,2722,2705,2662,2657,2628,2595,2587,2577,2533,2499,2478,2458,2457,2464,2459,2447,2484,2476,2462,2453,2442,2440,2450,2424,2422,2401,2398,2391,2399,2394,2371,2388,2361,2365,2336,2318,2313,2316,2315,2300,2294,2302,2310,2301,2294,2267,2290,2284,2275,2268,2284,2267,2281,2273,2285,2274,2285,2275,2279,2267,2289,2296,2289,2268,2288,2280,2294,2285,2278,2287,2288,2271,2282,2278,2278,2265,2273,2264,2266,2266,2282,2274,2267,2268,2264,2284,2268,2272,2277,2260,2262,2272,2260,2262,2261,2260,2265,2259,2258,2264,2254,2256,2280,2268,2262,2258,2272,2261,2252,2260,2272,2308

##### Usage
    python src\aquasense\ramses\driver.py --help
    usage: driver.py [-h] [--port PORT] [--output-path OUT_PATH]
                    [--output-field-delimiter OUTPUT_FIELD_DELIMITER]
                    [--integration-time INTEGRATION_TIME] [--repeats REPEATS]
                    [--intra-sample-delay INTRA_SAMPLE_DELAY] [--verbose]

    Read RAMSES data from a serial port.

    optional arguments:
    -h, --help            show this help message and exit
    --port PORT, -p PORT  Serial port name
    --output-path OUT_PATH, -o OUT_PATH
                            Output file path
    --output-field-delimiter OUTPUT_FIELD_DELIMITER, -d OUTPUT_FIELD_DELIMITER
                            Delimiter for fields in output rows (default: ,)
    --integration-time INTEGRATION_TIME, -i INTEGRATION_TIME
                            Integration time in ms (default: 0 [auto]); can be one
                            of 0, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096,
                            8192
    --repeats REPEATS, -r REPEATS
                            Number of sampling repeats (default: 1)
    --intra-sample-delay INTRA_SAMPLE_DELAY, -s INTRA_SAMPLE_DELAY
                            Delay between sampling in secs (default: 1)
    --verbose, -v         Verbose output mode
