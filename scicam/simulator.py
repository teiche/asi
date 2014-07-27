from ..utils.xmlrpc import RPCAble, rpc_method
from random import randrange

class ScienceCameraSimulator(RPCAble):
    """Randomly generated data science camera simulator

    Only has methods relevant to the run log data"""

    def __init__(self):
        super(ScienceCameraSimulator, self).__init__()

    @rpc_method
    def get_filename(self):
        return str(randrange(0,1000000))

    @rpc_method
    def get_itime(self):
        return randrange(0,100)*.1

    @rpc_method
    def get_emgain(self):
        return randrange(0,100)*.1

    @rpc_method
    def ready(self):
        return True

    @rpc_method
    def target_in_camera(self):
        return True

    def get_roi(self):
        return (1024, 1024)
