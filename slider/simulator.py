import time
import logging

from ..utils.xmlrpc import RPCAble, rpc_method

logger = logging.getLogger(__name__)

class SliderSimulator(RPCAble):
    # Seconds per slider port switch
    SPEED = 2

    MOVING      = 0
    ACQUISITION = 1
    SCIENCE     = 2
    
    def __init__(self):
        super(SliderSimulator, self).__init__()
        
        self.position = self.ACQUISITION

        # The time at which slider movement will be done
        self._slider_done = 0

    @rpc_method
    def to_acquisition(self):
        logger.info("To Acquisition Camera")
        if self.position != self.ACQUISITION:
            self._slider_done = time.time() + self.SPEED
            self.position = self.ACQUISITION

    @rpc_method
    def to_science(self):
        logger.info("To Science Camera")
        if self.position != self.SCIENCE:
            self._slider_done = time.time() + self.SPEED
            self.position = self.SCIENCE

    @rpc_method
    def get_pos(self):
        if time.time() < self._slider_done:
            return self.MOVING

        return self.position
        
    @rpc_method
    def ready(self):
        return self.get_pos() != self.MOVING
        


    
