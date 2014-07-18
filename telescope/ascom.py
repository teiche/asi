import sys

import win32com.client

from abstract import AbstractTelescope

import errors

class ASCOMTelescope(AbstractTelescope):
    def __init__(self, ascom_id):
        self.com = win32com.client.Dispatch(ascom_id)
        #self.com.SetupDialog()
        self.com.Connected = True

        super(ASCOMTelescope, self).__init__()

    def slew_rel(self, ra, dec):
        """
        Slew relative to the current position
        RA and Dec are both in degrees, positive dec is North facing
        """
        cur_ra = self.com.RightAscension
        cur_dec = self.com.Declination
        
        # Convert ra back to degrees for slew_abs
        self.slew_abs((ra * 15.0) + cur_ra, dec + cur_dec)

        super(ASCOMTelescope, self).slew_rel(ra, dec)

    def slew_abs(self, ra, dec):
        """
        Slew to the absolute position (ra, dec), both measured in degrees
        Positive dec is North facing
        """
        # Convert RA to hours for ASCOM
        try:
            self.com.SlewToCoordinatesAsync((ra / 15.0), dec)

        except:
            e = sys.exc_info()[0]
            raise errors.SlewFailed()
            

        super(ASCOMTelescope, self).slew_abs(ra, dec)

    def ready(self):
        return not self.com.Slewing
        
    def get_pos(self):
        return (self.com.RightAscension * 15.0, self.com.Declination)

    def park(self):
        super(ASCOMTelescope, self).park()
        self.com.Park()

    def unpark(self):
        super(ASCOMTelescope, self).unpark()
        self.com.Unpark()

def SiTechTelescope():
    return ASCOMTelescope("ASCOM.SiTechDll.Telescope")
