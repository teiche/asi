import logging
import time
import random

from ..utils.xmlrpc import RPCAble

logger = logigng.getLogger(__name__)

class AcquisitionCameraSimulator(RPCAble):
    """
    """

    def __init__(self):
        logger.info("Acquisition Camera Simulator Running...")

        self.done_imaging_at = 0
        self.done_solving_at = 0
        
    def take_light(seconds):
        logger.info("Taking {seconds} second exposure".format(seconds=seconds))
        self.done_imaging_at = time.time() + seconds

    def ready():
        return time.time() > self.done_imaging_at

    def plate_solve(ra, dec):
        """
        Start plate solving, and return immediately
        The results are available through plate_solution() once plate_solve.ready() return True
        """
        
        """
        This inner function is an interesting trick

        The acquisition camera has two blocking operations, take an image and 
        plate solve an image.  Both have very different end conditions, so I want
        different objects to pass into _idle_while_busy.  This lets me call
        _idle_while_busy(self.acquisition) to wait for an image to finish exposing, 
        and _idle_while_busy(self.acquisition.plate_solve) to wait for a plate to
        finish solving
        """
        def ready():
            """
            Return true if the plate is solved
            """
            return time.time() > self.done_solving_at

        logger.info("Plate Solving...")
        self.done_solving_at = time.time() + (random.random() * 5)

        rand_err = lambda: (random.random() - .5) * 2
        self.plate_solution = (ra + rand_err(), dec + rand_err())

    def plate_solution():
        """
        return the RA and Dec(in degrees) for the center of the image, 
        as well as the camera angle pixel scale(RA and Dec) in degrees per pixel
        plate_solve -> (ra_deg, dec_deg, plate_angle, ra_deg_per_pix, dec_deg_per_pix)

        This returns False if the plate solve failed
        """      
        if random.random() < .9:  
            return tuple(self.plate_solution, random.random() * 360, 0.000763, 0.000763)

        else:
            # Fail 10% of the time
            return False
        
    def shutdown():
        logger.info("Acquisition Camera Simulator Shutting Down...")
