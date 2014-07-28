import time
import logging

from abstract import AbstractSlider

logger = logging.getLogger(__name__)

class SliderSimulator(AbstractSlider):
    # Seconds per slider port switch
    SPEED = 2

    def __init__(self):
        super(SliderSimulator, self).__init__()
        
        self.position = self.ACQUISITION

        # The time at which slider movement will be done
        self._slider_done = 0

    def to_acquisition(self):
        logger.info("To Acquisition Camera")
        if self.position != self.ACQUISITION:
            self._slider_done = time.time() + self.SPEED
            self.position = self.ACQUISITION

    def to_science(self):
        logger.info("To Science Camera")
        if self.position != self.SCIENCE:
            self._slider_done = time.time() + self.SPEED
            self.position = self.SCIENCE

    def get_pos(self):
        if time.time() < self._slider_done:
            return self.MOVING

        return self.position
        
    def ready(self):
        return self.get_pos() != self.MOVING
        


    
