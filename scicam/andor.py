import socket

import abstract

START_CONTINUOUS = 'c'
START_ACQUISITION = 'x'
ABORT = 's'
GET_IMAGING = 'X'
GET_PROGRESS = 'P'
GET_KINETIC_SERIES_LENGTH = 'K'
GET_INTEGRATION_TIME = 'I'
GET_GAIN = 'G'
GET_ROI = 'R'
GET_AVG_WELL_FILL = 'W'
SET_KINETIC_SERIES_LENGTH = 'k'
SET_INTEGRATION_TIME = 'i'
SET_GAIN = 'g'
SET_ROI = 'r'

ROI_SIZE = {
    1 : (512, 512),
    2 : (256, 256),
    3 : (128, 128),
    4 : (64, 64)
}

def word2int(word):
    """
    Convert a little-endian 4-byte python string to an integer
    """
    return sum(byte << (8 * n) for n, byte in enumerate(map(ord, word)))

def int2word(i):
    """
    Convert an integer to a 4-byte little endian python string
    """
    a = i & 0xFF
    b = (i >> 8) & 0xFF
    c = (i >> 16) & 0xFF
    d = (i >> 24) & 0xFF

    return ''.join(map(chr, (d, c, b, a)))

class AndorScienceCamera(abstract.AbstractScienceCamera):
    FULL = 0
    HALF = 1
    QUARTER = 2
    EIGTHT = 3
    SIXTEENTH = 4

    def __init__(self, addr, port):
        super(AndorScienceCamera, self).__init__()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((addr, port))

    def _cmd(self, cmd):
        self.sock.send(cmd)
        return self.sock.recv(4)

    def get_filename(self):
        """
        Return the file name of the last saved FITS cube
        """
        raise NotImplementedError

    def get_itime(self):
        """
        Return the integration time in milliseconds
        """
        msg = self._cmd(GET_INTEGRATION_TIME)

        return word2int(msg)

    def get_emgain(self):
        """
        Return the gain of the sensor
        If gain is not supported, this always returns -1
        """
        msg = self._cmd(GET_GAIN)

        return word2int(msg)

    def ready(self):
        """
        Return true if the camera is not imaging
        """
        msg = self._cmd(GET_IMAGING)
        return not ord(msg[0])

    def target_in_camera(self):
        """
        Return true if there is a high probability that the target is in the science camera
        """
        print "INFO: Placeholder target_in_camera() -> True"
        return True

    def get_roi(self):
        """
        Return the current region of interest size(not position), as a 2-tuple
        """
        roi = ord(self._cmd(GET_ROI)[0])

        try:
            return ROI_SIZE[roi]

        except KeyError:
            print "INFO: Place holder, get_roi() -> Full Frame = (-1, -1)"
            return (-1, -1)

    def start_continuous(self):
        """
        Start continuous acquisiton without saving any data
        This does not modify the sequence number
        """
        self._cmd(START_CONTINUOUS)

    def start_acquisition(self):
        """
        Take and save a FITS cube. This increments the sequence number.
        """
        self._cmd(START_ACQUISITION)
        
    def abort(self):
        """
        Abort the current acquisition, be it continuous or data taking
        If this aborts an acquisition for data(start_acquisition), the sequence number
        is reverted to the previous number and no data is stored
        """
        self._cmd(ABORT)

    def get_progress(self):
        """
        Return a 2-tuple of (percent, frames) indicating the progress of the current
        acquisition.  In continuous mode, percent is always 100
        """
        msg = self._cmd(GET_PROGRESS)
        perc = ord(msg[0])
        frames = msg[1:3]
        
        return perc, word2int(frames)

    def get_kinetic_series_length(self):
        """
        Return the length of the current kinetic series
        """
        return word2int(self._cmd(GET_KINETIC_SERIES_LENGTH))

    def get_avg_well_fill(self):
        """
        Return a 2-tuple of (percent, ADU), representing the average well counts 
        for the top 10% of pixels
        """
        msg = self._cmd(GET_AVG_WELL_FILL)
        perc = ord(msg[0])
        frames = msg[1:3]
        
        return perc, word2int(frames)

    def set_kinetic_series_length(self, klen):
        """
        Set the number of frames per FITS cube
        """
        self.sock.send(SET_KINETIC_SERIES_LENGTH + int2word(klen))
        self.sock.recv(4)

    def set_itime(self, itime):
        """
        Set the integration time, in milliseconds
        """
        self.sock.send(SET_INTEGRATION_TIME + int2word(itime))
        self.sock.recv(4)

    def set_gain(self, gain):
        """
        Set the gain of the sensor.  If the camera does not support gain, this raises a
        NotImplementedError
        """
        self.sock.send(SET_GAIN + int2word(gain)[2:4])
        self.sock.recv(4)

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
        self.sock.send(SET_ROI + chr(roi_enum))
        self.sock.recv(4)

"""
if __name__ == '__main__':
    print map(ord, int2word(10))
    print map(ord, int2word(72))
    print map(ord, int2word(100))
    print map(ord, int2word(500))

    #import sys
    #sys.exit()

    x = AndorScienceCamera('127.0.0.1', 7077)

    import time

    time.sleep(1)
    x.set_kinetic_series_length(500)
    x.set_itime(20)
    x.set_gain(150)
    x.set_roi(2)

    time.sleep(1)

    #x.start_acquisition()

    print x.get_kinetic_series_length()
    time.sleep(1)

    time.sleep(100)

    while 1:
        print x.get_avg_well_fill()
"""
