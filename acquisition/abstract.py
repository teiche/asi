from ..utils.xmlrpc import RPCAble

class AbstractAcquisitionCamera(RPCAble):    
    def __init__(self):
        self._xmlrpc_funcs = [self.take_light, self.ready, self.shutdown, self.take_temp_light, self.get_img_path]

        super(AbstractAcquisitionCamera, self).__init__()

    def take_light(self, seconds):
        """
        Take a light frame with integration time seconds, returning None immediately
        """
        raise NotImplementedError

    def take_temp_light(self, seconds):
        raise NotImplementedError

    def get_img_path(self):
        raise NotImplementedError

    def ready(self):
        """
        Return true if the previously queued image has finished downloading
               false otherwise
        """
        raise NotImplementedError
    def shutdown(self):
        """
        Shut down the camera
        """
        raise NotImplementedError
