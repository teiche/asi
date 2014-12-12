import sys
import time
import logging
import xmlrpclib
import datetime
import math

from .. import db
from asi.db.runlog import Observation
from .. import log
from ..utils.xmlrpc import RPCAble, rpc_method
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

def periodize(ang):
    if ang < -180:
        return periodize(ang + 360)

    if ang > 180:
        return periodize(ang - 360)

    return ang

class RunManager(RPCAble):
    IDLE_GRANULARITY = .1
    
    def __init__(self, rpc_server, scheduler, telescope, slider, focuser, scicam, acquiscam, plate_solver):
        super(RunManager, self).__init__()
        self.waiting_on = []
        
        self.rpc_server = rpc_server
        self.scheduler = scheduler
        self.telescope = telescope
        self.slider = slider
        self.focuser = focuser
        self.scicam = scicam
        self.acquiscam = acquiscam
        self.plate_solver = plate_solver
        
        self.session = db.Session()

        self.auto_mode = True

        self.current_step = 'slew'
        
        self.startup()

    def _idle(self):
        """
        The idle process function

        This function gets called while RunManager is waiting for other modules to complete work
        """
        self.rpc_server.handle_request()
        
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

        '''
        # Return true if all modules are ready, false otherwise
        check_ready = lambda: all(map(lambda mod: mod.ready(), modules))
        all_ready = check_ready()

        while not all_ready:
            self._idle()

            # If it's been granularity seconds, check the readiness
            if (time.time() - last_ready_check) >= self.IDLE_GRANULARITY:
                all_ready = check_ready()
        '''
        self.waiting_on = filter(lambda mod: not mod.ready(), modules)
        while self.waiting_on:
            self._idle()

            if (time.time() - last_ready_check) >= self.IDLE_GRANULARITY:
                self.waiting_on = filter(lambda mod: not mod.ready(), modules)

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
        try:
            self._unsafe_update_running()

        except:
            print sys.exc_info()
            self.skip_target(self.target)

    @rpc_method
    def singlestep_mode(self):
        self.auto_mode = False

    @rpc_method
    def automatic_mode(self):
        self.auto_mode = True

    @rpc_method
    def step(self):
        self.single_continue = True

    @rpc_method
    def in_auto_mode(self):
        return self.auto_mode

    @rpc_method
    def ready_to_step(self):
        """
        Returns true if the only thing we are waiting on is the step input from the user
        """
        return len(self.waiting_on) == 1 and isinstance(self.waiting_on[0], RunManager)
            
    @rpc_method
    def current_target_name(self):
        return self.target.name

    @rpc_method
    def get_current_actions(self):
        """
        Return string names of the currently blocking actions
        """
        print '#'*100                
        print self.current_step
        print '#'*100
        return self.current_step
        
    def task_boundary(self, name):
        print '#'*100                
        print "TASK BOUNDARY", name
        print '#'*100
        self.current_step = name
        
        if not self.auto_mode:
            self.single_continue = False
            self._idle_while_busy(self)

        else:
            # Do at least one idle cycle so we can handle xmlrpc requests
            self._idle()

        
        
        
    def ready(self):
        """
        Return true if we're ready to move to the next step

        In auto mode this is always true
        In single step mode, this is self.single_continue
        """
        return self.auto_mode or self.single_continue
            

    def _unsafe_update_running(self):
        ########################################################################
        self.task_boundary('scheduler')
        logger.info("Requesting new target...")
        try:
            target, band, requester = self.scheduler.get_next_target()

        except xmlrpclib.Fault, e:
            # There are no observable targets
            logger.error(log.sanitize_fault(e.faultString))
            logger.error(sys.exc_info())
            self.shutdown()
            return

        self.target = target


        
        logger.info("New Target: {target}".format(target=target))

        ########################################################################
        self.task_boundary('slew')
        logger.info("Slewing to target...")
        try:
            self.telescope.slew_obs(target)
        except xmlrpclib.Fault, e:
            logger.error("Slew Failed")
            self.skip_target(target)
            return

        #self.task_boundary('slider_acq')

        self.slider.to_acquisition()
        logger.info("Slider to Acquisition Camera...")
        
        self.focuser.to_acquisition()
        logger.info("Focuser to Acquisition Camera...")
        
        self._idle_while_busy(self.telescope, self.slider, self.focuser)
        time.sleep(5) # Mount settling time
        

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
        
        ra_deg, dec_deg = self.slew_until_within_bounds(target.ra_deg, target.dec_deg)
        ########################################################################
            
        logger.info("Slewing telescope to place target in science camera")

        """
        cam_angle = math.radians(cam_angle)

        ra_offset_slew  = ((config.scicam_x * ra_deg_pix * math.cos(cam_angle)) + 
                           (config.scicam_y * dec_deg_pix * math.sin(cam_angle)))
        dec_offset_slew = ((config.scicam_x * ra_deg_pix * math.sin(cam_angle)) + 
                           (config.scicam_y * dec_deg_pix * math.cos(cam_angle)))
        """
        cam_ra, cam_dec = self.plate_solver.transform_plate_to_j2000(config.scicam_x, config.scicam_y)

        ra_offset_slew = periodize(ra_deg - cam_ra)
        dec_offset_slew = periodize(dec_deg - cam_dec)

        print "cam_ra", cam_ra, "ra_deg", ra_deg
        print "cam_dec", cam_dec, "dec_deg", dec_deg

        logger.debug("    ({ra}, {dec})".format(ra=ra_offset_slew, dec=dec_offset_slew))
        #self.telescope.slew_rel(-ra_offset_slew, -dec_offset_slew)

        solution = self.slew_until_within_bounds(ra_deg + ra_offset_slew, dec_deg + dec_offset_slew)

        if solution:
            ra_deg, dec_deg = solution

        else:
            self.scheduler.target_failed(target)

        logger.info("Acquisition camera centered at: ({0}, {1})".format(ra_deg, dec_deg))
        logger.info("   for science camera to be centered on object")

        self.task_boundary('slider_sci')
        self.focuser.to_science()
        self.slider.to_science()
        self._idle_while_busy(self.focuser, self.slider)

        # TODO: Do some speckle imaging
        # # Slew telescope by offset
        # # Make initial guess of science camera exposure parameters

        self.task_boundary('autoexpose')
        #self.scicam.autoexpose()
        print "TODO: Autoexposure"
        time.sleep(15) # TODO: check for scicam.busy, not constant time
        self._idle_while_busy(self.scicam)

        if self.scicam.target_in_camera():
            # # Set science camera exposure parameters

            self.task_boundary('takedata')
            # Give the mount/slider time to settle before imaging
            time.sleep(5)
            self.scicam.start_acquisition()

            #self.scicam.start_acquisition()
            self._idle_while_busy(self.scicam)

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

            self.scheduler.target_success()
                            
            print "Saved obsevation in run log with filename {}".format(filename)
           
        """    
        if s.lower() == 'y':
            print "Success!"
            self.scheduler.target_success()
        else:
            print "Failure"
            self.scheduler.target_failed()
        """ 

        self.task_boundary()
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
        #self.telescope.park()
        
    def skip_target(self, target):
        """
        Called when a target is skipped
        """
        logger.warning("Skipping target {target}.".format(target=target))
        self.scheduler.target_failed()

    def slew_until_within_bounds(self, ra, dec):
        """
        Using the acquisition camera and a plate solver, iteratively 
        slew and acquire a plate solution to guarantee that the telescope is
        within acceptible pointing error limits defined in config

        Returns the final location of the telescope
        """
        self.task_boundary('slew_offset')
        
        # Determine where we're pointing and slew by the difference between than and the target
        # until the target is within (ra_err, dec_err) of the center of the field
        ra_offset_slew = dec_offset_slew = 0
        
        outside_target_bounds = True        
        while outside_target_bounds:
            if ra_offset_slew or dec_offset_slew:
                logger.info("Slewing by offset ({ra_deg}, {dec_deg})".format(ra_deg=ra_offset_slew,
                                                                           dec_deg=dec_offset_slew))

                self.telescope.slew_rel(ra_offset_slew, dec_offset_slew)
                self._idle_while_busy(self.telescope)
                time.sleep(10) # Mount settling time
                
            logger.info("Calculating current actual position with acquisition camera...")
            self.task_boundary('acq')
            for x in range(0, config.plate_solve_tries):
                logger.info("Taking acquisition image...")
                self.acquiscam.take_temp_light(config.acquiscam_itime)
                self._idle_while_busy(self.acquiscam)

                imgpath = self.acquiscam.get_img_path()
                if not imgpath:
                    logger.error("Acquisition Camera could not acquire an image")
                    self.skip_target(self.target)

                self.task_boundary('plate')
                logger.info("Plate solving acquisition image...")
                #self.acquiscam.plate_solve(*self.telescope.get_pos())
                self.plate_solver.solve(imgpath)
                self._idle_while_busy(self.plate_solver)
                
                solution = self.plate_solver.plate_solution()

                if not solution:
                    logger.warning("Plate solving failed")
                else:
                    logger.info("Plate solving succeeded")            
                    break
                            
            else:
                # Plate solving failed config.plate_solve_tries times
                # Skip this target
                self.skip_target(self.target)
                return

            self.task_boundary('slew_offset')

            ra_deg, dec_deg, cam_angle, xsize, ysize = solution

            # How far the target is from our current position
            ra_offset_slew = ra - ra_deg
            dec_offset_slew = dec - dec_deg

            print "RA DEG", ra_deg
            print "DEC DEG", dec_deg

            logger.debug("Target distance: ({0}, {1})".format(ra_offset_slew, dec_offset_slew))
            
            outside_target_bounds = (abs(ra_offset_slew) > config.ra_err) or (abs(dec_offset_slew) > config.dec_err)
        return ra_deg, dec_deg
        
