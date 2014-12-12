import time

from abstract import AbstractFocuser
import errors

class SimulatorFocuser(AbstractFocuser):
    FOCUS_DELAY = 2

    def __init__(self):
        super(SimulatorFocuser, self).__init__()
        
        # The time at which we become in focus
        self.in_focus = 0
    
    def focus(self):
        print "Focusing"
        self.in_focus = time.time() + self.FOCUS_DELAY

    def ready(self):
        return time.time() > self.in_focus

    def relative_move(self, dist):
        print "Relative Move:", dist
        
