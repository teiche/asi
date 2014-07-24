class AbstractAcquistionCamera(RPCAble):
    def take_light(seconds):
        """
        Take a light frame with integration time seconds, returning None immediately
        """
        raise NotImplementedError

    def ready():
        """
        Return true if the previously queued image has finished downloading
               false otherwise
        """
        raise NotImplementedError

    def plate_solve():
        """
        Return the RA and Dec of the previously acquired image
        """
        raise NotImplementedError

    def shutdown():
        """
        Shut down the camera
        """
        raise NotImplementedError
