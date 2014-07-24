from ..utils.xmlrpc import RPCAble

class AbstractAcquisitionCamera(RPCAble):
    def take_light(self, seconds):
        """
        Take a light frame with integration time seconds, returning None immediately
        """
        raise NotImplementedError

    def ready(self):
        """
        Return true if the previously queued image has finished downloading
               false otherwise
        """
        raise NotImplementedError

    def plate_solve(self):
        """
        Return the RA and Dec of the previously acquired image
        """
        raise NotImplementedError

    def shutdown(self):
        """
        Shut down the camera
        """
        raise NotImplementedError
