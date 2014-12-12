import logging
from ctypes import *
import sys

from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, CurrentChangeEventArgs, StepperPositionChangeEventArgs, VelocityChangeEventArgs
from Phidgets.Devices.Stepper import Stepper

from asi import config

from abstract import AbstractSlider

logger = logging.getLogger(__name__)

class PhidgetStepperSlider(AbstractSlider):
    def __init__(self):
        super(PhidgetStepperSlider, self).__init__()

        logger.info("Connecting to Phidget stepper driver...")
        try:
            self.stepper = Stepper()
        except RuntimeError as e:
            logger.error("Could not connect to Phidgets stepper driver: {s}".format(s=e.details))
            sys.exit(1)

        logger.info("Opening Phidget stepper driver...")

        try:
            self.stepper.openPhidget()
        except PhidgetException as e:
            logger.error("Could not open Phidget stepper driver: {e}".format(e=e.details))
            sys.exit(1)

        logger.info("Waiting for Phidget to attach...")
        try:
            self.stepper.waitForAttach(1000)
        except PhidgetException as e:
            logger.error("Could not wait for Phidget to attach: {e}".format(e=e.details))
            sys.exit(1)

        logger.info("Successfully connected to Phidget stepper driver.")
        logger.info("    Device Name: " + self.stepper.getDeviceName())
        logger.info("    Serial Number: " + str(self.stepper.getSerialNum()))
        logger.info("    Device Version: " + str(self.stepper.getDeviceVersion()))
                
        # Assume the slider is currently at the acquisition camera
        self.stepper.setCurrentPosition(config.slider_motor_id, config.slider_acquis_pos)

    def _set_target(self, target):
        self.target = target
        self.stepper.setTargetPosition(config.slider_motor_id, target)
        
    def to_acquisition(self):
        logger.info("Slider to acquisition camera")
        
        self.stepper.setEngaged(config.slider_motor_id, True)
        self._set_target(config.slider_acquis_pos)

    def to_science(self):
        logger.info("Slider to science camera")

        self.stepper.setEngaged(config.slider_motor_id, True)
        self._set_target(config.slider_sci_pos)

    def get_pos(self):
        pos = self.stepper.getCurrentPosition(0)
        
        if pos == config.slider_acquis_pos:
            return self.ACQUISITOIN

        elif pos == config.slider_sci_pos:
            return self.SLIDER

        else:
            return self.MOVING

    def ready(self):
        return self.target == self.stepper.getCurrentPosition(0)
        
    

