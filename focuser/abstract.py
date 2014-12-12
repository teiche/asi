# The focuser configuration for the Automatic Speckle System is a little nontraditional:
# There is one focuser with two instruments and a slider, the focuser moves all three(slider + two instruments)
# Focusing is done by normal means(FocusMAX and MaximDL) using the acquisition camera, then a calibrated and known ahead-of-time offset is applied to the focuser to place the science camera in focus.
# The focus() method here assumes that the slider is already in the acquisition camera position

import logging
logger = logging.getLogger(__name__)

from ..utils.xmlrpc import RPCAble, rpc_method
from .. import config

import errors

class AbstractFocuser(RPCAble):
    def __init__(self):
        # Has the science camera offset been applied since we focused?
        self.applied_science_offset = False

        self._xmlrpc_funcs = [self.focus, self.ready]

    def focus(self):
        """
        Focus the acquisition camera using normal means(FocusMax and MaximDL)
        This assumes that the slider is in the acquisition camera position
        """
        self.applied_science_offset = False
        logger.info("Starting autofocus routine")

    def relative_move(self, dist):
        """
        Move the focuser dist units relative to its current position, regardless of whether
        or not the focuser is absolute or relative
        """
        logger.info("Focuser moving {dist} units".format(dist=dist))


    def ready(self):
        """
        Returns true if we are currently not in the middle of an autofocus routine
        """
        raise NotImplemented

    def to_science(self):
        """
        Offset the focuser to put the science camera in focus
        For this method to do work, the focuser must be focused on the acquisition camera
        If this method is called more than once consecutively, it will only offset the focuser
        once
        """
        if not self.applied_science_offset:
            logger.info("Applying science camera offset")
            self.applied_science_offset = True
            self.relative_move(config.science_focus_offset)
            
    def to_acquisition(self):
        """
        Offset the focuser to put the acquisition camera in focus
        The focuser must have applied the science camera offset for this to once
        Multiple consecutive calls of this function will only result in one focus offset
        being applied
        """
        if self.applied_science_offset:
            logger.info("Applying acquisition camera offset")
            self.applied_science_offset = False
            self.relative_move(-1 * config.science_focus_offset)

    # TODO: Science camera focusing with offsets
        
