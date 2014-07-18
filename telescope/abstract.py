import logging

logger = logging.getLogger(__name__)

from ..utils.xmlrpc import RPCAble, rpc_method

class AbstractTelescope(RPCAble):
    def __init__(self):
        self._xmlrpc_funcs = [self.slew_rel, self.slew_abs, self.ready, self.get_pos, 
                              self.park, self.unpark]

        super(AbstractTelescope, self).__init__()

    def slew_rel(self, ra, dec):
        """
        Slew by RA and Dec, relative to the current position
        RA and Dec are both in degrees
        """
        logger.info("Slewing (Relative) by ({ra}, {dec})".format(ra=ra, dec=dec))
        
    def slew_abs(self, ra, dec):
        """
        Slew to the coordinates RA, Dec
        RA and Dec are both in degrees
        """
        logger.info("Slewing (Absolute) to ({ra}, {dec})".format(ra=ra, dec=dec))
        
    def ready(self):
        """
        Return true if the telescope is ready to move, false otherwise
        This is generally synonymous to "not slewing"
        """
        pass
        
    def get_pos(self):
        """
        Return the current pointing position as a 2-tuple (ra, dec)
        RA and Dec are both measured in degrees
        """
        pass
        
    def park(self):
        """
        Park the telescope
        """
        logger.info("Parking the telescope")

    def unpark(self):
        """
        Unpark the telescope
        """
        logger.info("Unparking the telescope.")

    def update(self):
        """
        This method is not required, but can take care of any bookkeeping is a semi asynchronous manner.
        It gets called between each check for RPC calls
        """
        pass
