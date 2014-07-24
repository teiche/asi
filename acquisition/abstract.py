from ..utils.xmlrpc import RPCAble

class AbstractAcquisitionCamera(RPCAble):
    def __init__(self):
        """
        This inner function is an interesting trick

        The acquisition camera has two blocking operations, take an image and 
        plate solve an image.  Both have very different end conditions, so I want
        different objects to pass into _idle_while_busy.  This lets me call
        _idle_while_busy(self.acquisition) to wait for an image to finish exposing, 
        and _idle_while_busy(self.acquisition.plate_solve) to wait for a plate to
        finish solving

        This does require a small workaround in client.py to work over XMLRPC
        """
        self.plate_solve.__func__.ready = self.plate_solve_ready
        
        self._xmlrpc_funcs = [self.take_light, self.ready, self.plate_solve, self.plate_solution, self.shutdown, self.plate_solve_ready]

        super(AbstractAcquisitionCamera, self).__init__()

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
