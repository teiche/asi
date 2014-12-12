import sys

import win32com.client

from abstract import AbstractFocuser
import errors

class FocusMaxFocuser(AbstractFocuser):
    def __init__(self):
        self.com = win32com.client.Dispatch("FocusMax.FocusControl")

        super(FocusMaxFocuser, self).__init__()
        
    def focus(self):
        """
        Block until FocusMax is focused
        
        This call has to be blocking, because there is no other good way to determine if
        there was a focusing error.  The blocking focus call will raise an exception, but the
        asynchronous call is silent.
        """
        #TODO: Error handling
        try:
            self.com.Focus()

        except:
            raise errors.FocusMaxInternalError("FocusMax Internal Error: " + 
                                               sys.exc_info()[1][2][2])

    def ready(self):
        return not self.com.IsBusy

    def relative_move(self, dist):
        """
        Move the focuser dist units relative to its current position
        """
        self.com.Move(dist + self.com.Position)


