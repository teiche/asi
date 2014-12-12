import os
import sys
import logging

import pywintypes
import win32com.client

import abstract

from .. import config

logger = logging.getLogger(__name__)

class MaximDLAcquisitionCamera(abstract.AbstractAcquisitionCamera):
    def __init__(self):
        super(MaximDLAcquisitionCamera, self).__init__()

        self.ccd = win32com.client.Dispatch("MaxIm.CCDCamera")
        self.ccd.LinkEnabled = True

        self.app = win32com.client.Dispatch("MaxIm.Application")

        if not self.ccd.LinkEnabled:
            logger.error("Could not establish COM link to MaximDL")
            print 'dying'
            sys.exit()

        self.seqnum = 0

    def take_light(self, seconds, fname):
        """
        Take and save an image to fname
        """
        self.ccd.BinX = 2
        self.ccd.Expose(seconds, 1, 0)
        self.fname = fname
        
    def take_temp_light(self, seconds):
        """
        Take a light frame and save it to the temp directory defined in config
        """
        tfile = os.path.join(config.acquiscam_tempdir, config.acquiscam_tempfile + str(self.seqnum) + '.fit')

        logger.info("Writing temporary image file to " + tfile)
        self.take_light(seconds, tfile)

    def get_img_path(self):
        """
        If successful, return the path of the most recently acquired image
        If unsuccessful, return none

        if get_img_path is called before ready() is true, get_img_path will block
        until the camera is one
        """
        while not self.ready():
            pass

        try:
            if self.ccd.SaveImage(self.fname):
                return self.fname

        except pywintypes.com_error as e:
            logger.error("MaximDL could not save the image!")
            logger.error(str(e))
            return None
            

        return None

    def ready(self):
        return self.ccd.ImageReady

    '''
    def plate_solve(self, ra, dec):
        self.doc = self.app.CurrentDocument
        self.doc.PinPointSolve(ra, dec)
        #self.doc.PinPointSolve()
        print 'howdy'

    def plate_solve_ready(self):
        return self.doc.PinPointStatus != 3

    def plate_solution(self):
        if self.doc.PinPointStatus == 2:
            return self.doc.CenterRA, self.doc.CenterDec, self.doc.PositionAngle, self.doc.ImageScale, self.doc.ImageScale
            
        return None
    '''

    def shutdown(self):
        pass

def test():
    from asi import log
    log.init_logging('maximdl')

    import time
    print "Running MaximDL COM Tests!"

    x = MaximDLAcquisitionCamera()
    #x.take_light(10)
    print x.take_temp_light(10)

    i = 0
    while not x.ready():
        i += 1
        time.sleep(1)
        print i, " ", 

    print "Exposure done!"
    print x.get_img_path()
    
    #print "Exposure done!"
    #x.plate_solve(13.5, 47)

    #time.sleep(1)

    #while not x.plate_solve_ready():
    #    pass

    #print x.plate_solution()
