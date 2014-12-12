from random import randrange

from abstract import AbstractScienceCamera

class ScienceCameraSimulator(AbstractScienceCamera):
    """Randomly generated data science camera simulator

    Only has methods relevant to the run log data"""

    def __init__(self):
        super(ScienceCameraSimulator, self).__init__()

    def get_filename(self):
        return str(randrange(0,1000000))

    def get_itime(self):
        return randrange(0,100)*.1

    def get_emgain(self):
        return randrange(0,100)*.1

    def ready(self):
        return True

    def target_in_camera(self):
        return True

    def get_roi(self):
        return (1024, 1024)

    def autoexpose(self):
        return True

    def quit(self):
        return True
