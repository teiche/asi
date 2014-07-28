import sys
import time
import logging
import xmlrpclib
import datetime
import math

from .. import db
from asi.db.runlog import Observation
from .. import log
from ..utils.xmlrpc import RPCAble
from .. import config

logger = logging.getLogger(__name__)

"""
This is the main run manager for the automated speckle system

As per the flow chart, the order of operations is:

Operations on the same line in () are executed in parallel

-- Request New Target
-- (Slew to Target) (Move Slider to Acquisition Camera)
-- Focus Acquisition Camera
-- Take Acquisition Image
-- Locate Target in Plate and Calculate Offset
-- (Move Slider to Science Camera) (Slew by Offset) (Make Initial Guess of Exposure Parameters)
-- Apply Focus Offset for Science Camera
-- Is Target in Science Camera?
YES -- Set Science Camera Parameters
    -- Take FITS Cube
    -- (Log Success) (Store FITS Cube) (Enter in Run Log DB)
    -- Report Success to Target Selector
NO  -- Log Failure
    -- Is this the Nth failure?
    YES -- Safe Shut Down
    NO  -- Report Failure to Target Selector
"""

class RunManager(RPCAble):
    IDLE_GRANULARITY = .1
    
    def __init__(self, scheduler, telescope, slider, focuser, scicam, acquiscam):
        self.scheduler = scheduler
        self.telescope = telescope
        self.slider = slider
        self.focuser = focuser
        self.scicam = scicam
        self.acquiscam = acquiscam
        
        self.session = db.Session()

        self.startup()

    def _idle(self):
        """
        The idle process function

        This function gets called while RunManager is waiting for other modules to complete work
        """
        pass
        
    def _idle_while_busy(self, *modules):
        """
        modules is a variadic argument of RPC instances accessing other speckle modules.  These modules all expose a "ready" method, which returns true when the module is ready to accept more input.

        For example, the telescope mount will return False while slewing, and True otherwise.

        This function calls self._idle() until all modules listed in modules are ready

        granularity is a value in seconds that determines how often the ready methods are checked.
        self._idle() is called continously, but the ready methods are only called every 
        granularity seconds to cut down on unecessary TCP traffic
        """         
        logger.debug("Entering Idle State...")
        logger.debug("Waiting For:")
        for mod in modules:
            logger.debug("    * {name}".format(name=mod.name()))
            
        # Guarantee _idle() is called at least once
        self._idle()

        last_ready_check = time.time()

        # Return true if all modules are ready, false otherwise
        check_ready = lambda: all(map(lambda mod: mod.ready(), modules))
        all_ready = check_ready()

        while not all_ready:
            self._idle()

            # If it's been granularity seconds, check the readiness
            if (time.time() - last_ready_check) >= self.IDLE_GRANULARITY:
                all_ready = check_ready()

        logger.debug("Exiting Idle State...")

    def update_idle(self):
        """
        The main loop, while the telescope is shut down(during the day, usually)
        """
        pass

    def update_running(self):
        """
        The main loop, while the telescope is running(not shut down)
        """
        ########################################################################
        logger.info("Requesting new target...")
        try:
            target, band, requester = self.scheduler.get_next_target()

        except xmlrpclib.Fault, e:
            # There are no observable targets
            logger.error(log.sanitize_fault(e.faultString))
            logger.error(sys.exc_info())
            self.shutdown()
            return

        logger.info("New Target: {target}".format(target=target))

        ########################################################################
        logger.info("Slewing to target...")
        try:
            self.telescope.slew_obs(target)
        except xmlrpclib.Fault, e:
            logger.error("Slew Failed")
            self.skip_target(target)
            return


        self.slider.to_acquisition()
        logger.info("Slider to Acquisition Camera...")
        
        self.focuser.to_acquisition()
        logger.info("Focuser to Acquisition Camera...")
        
        self._idle_while_busy(self.telescope, self.slider, self.focuser)

        ########################################################################
        '''
        logger.info("Focusing Acquisition Camera...")
        try:
            self.focuser.focus()

        except Exception, e:
            logger.error(str(e))
            self.skip_target(target)
            return
        '''
        ########################################################################
        
        # Determine where we're pointing and slew by the difference between than and the target
        # until the target is within (ra_err, dec_err) of the center of the field
        ra_offset_slew = dec_offset_slew = 0
        
        outside_target_bounds = True        
        while outside_target_bounds:
            if ra_offset_slew or dec_offset_slew:
                logger.info("Slewing by offset ({ra_deg}, {dec_deg})".format(ra_deg=ra_offset_slew,
                                                                           dec_deg=dec_offset_slew))

                self.telescope.slew_rel(ra_offset_slew, dec_offset_slew)
            
            logger.info("Calculating current actual position with acquisition camera...")
            for x in range(0, config.plate_solve_tries):
                logger.info("Taking acquisition image...")
                self.acquiscam.take_light(config.acquiscam_itime)
                self._idle_while_busy(self.acquiscam)
                
                logger.info("Plate solving acquisition image...")
                self.acquiscam.plate_solve(*self.telescope.get_pos())
                self._idle_while_busy(self.acquiscam.plate_solve)
                
                if not self.acquiscam.plate_solution():
                    logger.warning("Plate solving failed")
                else:
                    logger.info("Plate solving succeeded")            
                    break
                            
            else:
                # Plate solving failed config.plate_solve_tries times
                # Skip this target
                self.skip_target(target)
                return

            ra_deg, dec_deg, cam_angle, ra_deg_pix, dec_deg_pix = self.acquiscam.plate_solution()

            # How far the target is from our current position
            ra_offset_slew = target.ra_deg - ra_deg
            dec_offset_slew = target.dec_deg - dec_deg

            logger.debug("Target distance: ({0}, {1})".format(ra_offset_slew, dec_offset_slew))
            
            outside_target_bounds = (abs(ra_offset_slew) > config.ra_err) or (abs(dec_offset_slew) > config.dec_err)

        ########################################################################
            
        logger.info("Slewing telescope to place target in science camera")

        cam_angle = math.radians(cam_angle)
        
        ra_offset_slew  = ((config.scicam_x * ra_deg_pix * math.cos(cam_angle)) + 
                           (config.scicam_y * dec_deg_pix * math.sin(cam_angle)))
        dec_offset_slew = ((config.scicam_x * ra_deg_pix * math.sin(cam_angle)) + 
                           (config.scicam_y * dec_deg_pix * math.cos(cam_angle)))

        logger.debug("    ({ra}, {dec})".format(ra=ra_offset_slew, dec=dec_offset_slew))
        self.telescope.slew_rel(ra_offset_slew, dec_offset_slew)
        
        self.focuser.to_science()
        self.slider.to_science()
        self._idle_while_busy(self.focuser, self.slider)

        # TODO: Do some speckle imaging
        # # Slew telescope by offset
        # # Make initial guess of science camera exposure parameters

        if self.scicam.target_in_camera(): #placeholder
            # # Set science camera exposure parameters

            filename = self.scicam.get_filename()
            itime = self.scicam.get_itime()
            emgain = self.scicam.get_emgain()
            roi_height, roi_width = self.scicam.get_roi()
            ra_deg, dec_deg = self.telescope.get_pos()
            
            if isinstance(target, db.catalog.DoubleStar):
                obs = Observation(
                     filename = filename,
                    star_id = target.id,
                    datetime = datetime.datetime.now(),
                    emgain = emgain,
                    itime = itime,
                    requester = requester,
                    roi_width = roi_width,
                    roi_height = roi_height,
                    ra_deg = ra_deg,
                    dec_deg = dec_deg,
                    band = band
                    )

                self.session.add(obs)
                self.session.commit()

                del obs
                            
            print """Saved obsevation in run log with filename {}""".format(filename)

            
            self.scheduler.target_success()

        

        self.focuser.to_acquisition()
        self._idle_while_busy(self.focuser)

    def startup(self):
        """
        Start observing
        This is the opposite of self.shutdown()
        """        
        logger.info("Starting up.")
        self.update = self.update_running
        self.telescope.unpark()

    def shutdown(self):
        """
        Shut down the automated speckle system.  This method must leave the system in a state
        that can be recovered from by software, as this is the method used to shut the system
        down each morning.  self.startup() must be able to recover from a self.shutdown().
        """
        logger.info("Shutting down.")
        self.update = self.update_idle
        self.telescope.park()
        
    def skip_target(self, target):
        """
        Called when a target is skipped
        """
        logger.warning("Skipping target {target}.".format(target=target))
        self.scheduler.target_failed()

    
        
