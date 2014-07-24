import logging
import time
import random

from abstract import AbstractAcquisitionCamera

logger = logging.getLogger(__name__)

class AcquisitionCameraSimulator(AbstractAcquisitionCamera):
    """
    """

    def __init__(self):
        super(AcquisitionCameraSimulator, self).__init__()
        
        logger.info("Acquisition Camera Simulator Running...")

        self.done_imaging_at = 0
        self.done_solving_at = 0
        self.plate_info = ()
        
    def take_light(self, seconds):
        logger.info("Taking {seconds} second exposure".format(seconds=seconds))
        self.done_imaging_at = time.time() + seconds

    def ready(self):
        return time.time() > self.done_imaging_at

    def plate_solve(self, ra, dec):
        """
        Start plate solving, and return immediately
        The results are available through plate_solution() once plate_solve.ready() return True
        """
        
        logger.info("Plate Solving...")
        self.done_solving_at = time.time() + (random.random() * 5)

        rand_err = lambda: (random.random() - .5) * 2
        self.plate_info = (ra + rand_err(), dec + rand_err())

    def plate_solve_ready(self):
        """
        Return true if the plate is solved
        """
        return time.time() > self.done_solving_at

    def plate_solution(self):
        """
        return the RA and Dec(in degrees) for the center of the image, 
        as well as the camera angle pixel scale(RA and Dec) in degrees per pixel
        plate_solve -> (ra_deg, dec_deg, plate_angle, ra_deg_per_pix, dec_deg_per_pix)

        This returns False if the plate solve failed
        """      
        if random.random() < .9:  
            return self.plate_info + (random.random() * 360, 0.000763, 0.000763)

        else:
            # Fail 10% of the time
            return False
        
    def shutdown(self):
        logger.info("Acquisition Camera Simulator Shutting Down...")
