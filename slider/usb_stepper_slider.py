import logging
from ctypes import *
import sys
import time

import serial

from asi import config

from abstract import AbstractSlider

logger = logging.getLogger(__name__)

SLIDER_SLEW_TIME = 5 #seconds

class USBStepperSlider(AbstractSlider):
    def __init__(self):
        super(USBStepperSlider, self).__init__()

        logger.info("Opening USB stepper-stick USB port...")
        try:
            self.stepper = serial.Serial("COM5", 9600, timeout=1)
        except:
            logger.error("Could not open USB stepper stick serial port...")
            sys.exit(1)

        self.to_acquisition()

        self.finish_time = 0
        self.pos = self.ACQUISITION
        
    def to_acquisition(self):
        logger.info("Slider to acquisition camera")
        
        self.finish_time = time.time() + SLIDER_SLEW_TIME
        self.stepper.write("/1A15000R\r\n")

    def to_science(self):
        logger.info("Slider to science camera")

        self.finish_time = time.time() + SLIDER_SLEW_TIME
        self.stepper.write("/1A0R\r\n")

    def get_pos(self):
        if time.time() > self.finish_time:
            return self.pos

        return self.MOVING

    def ready(self):
        return self.get_pos() != self.MOVING
        
    

