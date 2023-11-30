"""
RAMSES sampling class using PyTrios library functionality.

G1 devices currently supported and tested.
"""

import datetime
import logging
import time

from aquasense.common.sensor import SensorBase

import pytrios.radman as radiometer_manager

from typing import List, TextIO, Tuple

class RAMSES(SensorBase):

    def __init__(self,
                 out: TextIO,
                 sep: str,
                 port: str,
                 integration_time: int = 0,
                 repeats: int = 1,
                 intra_sample_delay: float = 1,
                 logger: logging.Logger=None,
                 verbose: bool=False):
        
        """Initialise RAMSES object.
        
        Args:
            out: File-like object to write output to.
            sep: Output column separator.
            port: serial port name.
            integration_time: integration time for sensor data acquisition.
            repeats: number of times to repeat sample acquisition; None means forever.
            intra_sample_delay: delay between sample acquisitions.
            logger: A logger object; defaults to None.
            verbose: Verbose mode flag.
        """
        devtype = "G1"
        in_out = None # PyTrios creates communication channels
        SensorBase.__init__(self, in_out, out, sep, logger, verbose)
        self.integration_time = integration_time
        self.repeats = repeats
        self.intra_sample_delay = intra_sample_delay

        self.logger.info("Starting {} radiometry manager".format(devtype))
        self.rad_manager = radiometer_manager.TriosManager(port)


    def single_sample(self) -> Tuple[datetime.datetime, List[int], List[int], List[int]]:
        """Read and return a single sample for each connected device."""
        self.logger.info("Trigger measurement")

        trig_time, specs, sids, itimes, _, _, _ = \
            self.rad_manager.sample_all(datetime.datetime.now(),
                                        inttime=self.integration_time)

        return trig_time, specs, sids, itimes
    

    def run(self):
        """Read samples from one or more RAMSES devices."""
        if self.rad_manager.ready:
            if self.repeats is None:
                self.logger.info("Starting measurements (press CTRL-C to interrupt)")
            else:
                self.logger.info("Starting {repeats} measurements (press CTRL-C to interrupt)")

            finished = False
            while not finished:
                try:
                    trig_time, specs, sids, itimes = self.single_sample()
                    
                    for i, sid in enumerate(sids):
                        self.logger.info("Received spectrum from {sid}: {trig_time} | int-time: {itimes[i]} ms | Spectrum: {specs[i][0:3]}...{specs[i][-3::]}")
                        print("{}\t{}\t{}\t{}\n".format(sid, trig_time.isoformat(),
                                                        itimes[i],
                                                        ','.join([str(s) for s in specs[i]])),
                              file=self.out)

                    if self.repeats > 0:
                        self.repeats = self.repeats - 1
                    
                    finished = self.repeats == 0

                    time.sleep(self.intra_sample_delay)

                except KeyboardInterrupt:
                    finished = True
        else:
            self.logger.warning("Radiometry manager not ready. Exiting")

        self.logger.info("Stopping radiometry manager.")
        if self.rad_manager is not None:
            self.rad_manager.stop()
        self.logger.info("Done.")