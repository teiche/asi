from ..utils.xmlrpc import RPCAble, rpc_method

class AbstractScienceCamera(RPCAble):
    FULL = 0
    HALF = 1
    QUARTER = 2
    EIGTHT = 3
    SIXTEENTH = 4

    def __init__(self):
        self._xmlrpc_funcs = [self.get_filename, self.get_itime, self.get_emgain, self.ready,
                           self.target_in_camera, self.get_roi, self.start_continuous,
                           self.start_acquisition, self.abort, self.get_progress, 
                           self.get_kinetic_series_length, self.get_avg_well_fill,
                           self.set_kinetic_series_length, self.set_itime, self.set_gain,
                           self.set_roi]

        print self._xmlrpc_funcs
        
        super(AbstractScienceCamera, self).__init__()

    def get_filename(self):
        """
        Return the file name of the last saved FITS cube
        """
        raise NotImplementedError

    def get_itime(self):
        """
        Return the integration time in milliseconds
        """
        raise NotImplementedError

    def get_emgain(self):
        """
        Return the gain of the sensor
        If gain is not supported, this always returns -1
        """
        raise NotImplementedError

    def ready(self):
        """
        Return true if the camera is not imaging
        """
        raise NotImplementedError

    def target_in_camera(self):
        """
        Return true if there is a high probability that the target is in the science camera
        """
        raise NotImplementedError

    def get_roi(self):
        """
        Return the current region of interest size(not position), as a 2-tuple
        """
        raise NotImplementedError

    def start_continuous(self):
        """
        Start continuous acquisiton without saving any data
        This does not modify the sequence number
        """
        raise NotImplementedError

    def start_acquisition(self):
        """
        Take and save a FITS cube. This increments the sequence number.
        """
        raise NotImplementedError
        
    def abort(self):
        """
        Abort the current acquisition, be it continuous or data taking
        If this aborts an acquisition for data(start_acquisition), the sequence number
        is reverted to the previous number and no data is stored
        """
        raise NotImplementedError

    def get_progress(self):
        """
        Return a 2-tuple of (percent, frames) indicating the progress of the current
        acquisition.  In continuous mode, percent is always 100
        """
        raise NotImplementedError

    def get_kinetic_series_length(self):
        """
        Return the length of the current kinetic serieso
        """
        raise NotImplementedError

    def get_avg_well_fill(self):
        """
        Return a 2-tuple of (percent, ADU), representing the average well counts 
        for the top 10% of pixels
        """
        raise NotImplementedError

    def set_kinetic_series_length(self, klen):
        """
        Set the number of frames per FITS cube
        """
        raise NotImplementedError

    def set_itime(self, itime):
        """
        Set the integration time, in milliseconds
        """
        raise NotImplementedError

    def set_gain(self, gain):
        """
        Set the gain of the sensor.  If the camera does not support gain, this raises a
        NotImplementedError
        """
        raise NotImplementedError

    def set_roi(self, roi_enum):
        """
        Set the square ROI of the sensor.

        roi_enum has special meaning:
        0 - FULL
        1 - 512x512
        2 - 256x256
        3 - 128x128
        4 - 64x64
        
        These values are encapsulated in this.FULL, this.HALF, this.QUARTER, ...etc
        """
        raise NotImplementedError
