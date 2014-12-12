import functools
import logging
import datetime
import math

logger = logging.getLogger(__name__)

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

import ephem

from .. import db
from ..db.catalog import DoubleStar, ReferenceStar
from ..db.runlog import Observation
from ..db.targetlist import Target

from ..utils.xmlrpc import RPCAble, rpc_method
from ..utils import astro

import errors

moon = ephem.Moon()
site = ephem.Observer()
site.lon = "120:39:00"
site.lat = "35:18:03"

class AbstractScheduler(RPCAble):
    """
    An abstract scheduler for the automated speckle interferometry system

    This provides the infrastructure for database access and XMLRPC communication

    Subclasses of this are responsible for selecting targets and grouping them
    """
    # The maximum distance a single may be from its double in degrees
    MAX_SINGLE_DIST_RA = 2.0
    MAX_SINGLE_DIST_DEC = 2.0
    
    def __init__(self):
        super(AbstractScheduler, self).__init__()

        print db
        self.session = db.Session()
        
        # The list of doubles that are currently scheduled
        # They are observed in the order contained in this list
        # After this list is exhausted, if any doubles were successfully observed then 
        # self.single is observed
        # Each item in this list is a tuple of (double, band)
        self.double_queue = []

        # Once a double is observed, if the observation is successful it is moved from the 
        # double_queue to this list.  If it was unsuccessful, it is forgotten entirely.
        # This list is so the best single star can be recalculated if self.single can't be found
        # This list is only used after double_queue is exhausted AND self.single fails
        # Each item in this list is also a tuple of (double, band)
        self.successful_doubles = []

        # The single to observe for the doubles in self.double_queue
        # (single, band)
        self.single = None

        # This is the star we are currently observing
        self.current = None

        # Singles that have failed
        self.blacklisted_singles = []

        #self._xmlrpc_funcs = (self.get_next_target, self.target_failed, self.target_success)

        # List of run log database ids of successful observations
        # This will be used after all doubles in a group are observed to
        # update their run log entries with the correct reference star
        # filename and reference star id.
        self.successful_observations = []

        # Run log database id of successful reference star observation, to be
        # used to get the filename of the FITS cube for that observation, and
        # the reference star id. 
        self.successful_single_observation = None

    def _get_next_target(self):
        """
        Fetch and return the next target to observe, as a (SQLAlchemy ORM object,
        band) tuple
        """
        if self.double_queue: # If there are still doubles in the queue
            self.current = self.double_queue.pop(0)

        elif self.single and self.successful_doubles: 
            # If we have a single ready to go, and we observed at least one double
            self.current = self.single, None, None # None = placeholders for band, requester
            self.single = None

        else: # We're out of singles and doubles
            self._load_next_group()
            return self._get_next_target()

        return self.current

    @rpc_method
    def get_next_target(self):
        """
        Return the next target to observe and the band as an RPC-serializable string, to be converted into
        an SQLAlchemy ORM object at the client side
        """
        double, band, requester = self._get_next_target()
        
        db = double.__class__.__name__
        i = double.id
        
        return (db, i, band, requester)
        
    @rpc_method
    def target_failed(self):
        """
        The current target was a failure

        This method is how the run controller tells the scheduler that the target could not be found, or failed for some other reason

        In the case of a double, it is simply skipped
        In the case of a single, a new single is found
        """
        if isinstance(self.current[0], ReferenceStar):
            self.blacklisted_singles.append(self.current[0])
            self.single = self.get_next_single_star(self.successful_doubles)

    @rpc_method
    def target_success(self):
        """
        The current target was a success

        Takes a list of run log database ids of successful observations that
        it will add to self.sucessful_observations
        """
        if isinstance(self.current[0], DoubleStar):
            self.successful_doubles.append(self.current)
            #self.successful_observations.extend(observation_ids)

        '''
        elif isinstance(self.current[0], ReferenceStar):
            print observation_ids
            assert len(observation_ids) == 1, "There should only be one observation of the single star"
            self.successful_single_obs = observation_ids[0]
        '''

    def _load_next_group(self):
        """
        Load the next group of doubles into the queue, then select a single star for them

        Also update all the successful observations for the group we have just
        observed to include the reference observation filename and reference
        star id.
        """
        # TODO Move this updating stuff to a more reasonably named function
        # i.e. split this one in two
        '''
        single_id = self.single.id
        single_obs = self.session.query(Observation).filter(Observation.id == self.successful_single_obs).one()
        
        single_obs_filename = single_obs.ref_filename 

        for observation_id in self.successful_observations:
            obs = self.session.query(Observation).filter(Observation.id == observation_id).one()
            obs.ref_id = single_id
            obs.ref_filename = single_obs_filename
            session.commit()
        '''
    
        self.successful_observations = []
        self.successful_single_obs = None
        self.successful_doubles = []
        self.double_queue = self.get_next_double_group()
        self.single = self.get_next_single_star(self.double_queue)

    def _get_next_target_group(self):
        """
        Return a list of targets to observe.  They are observed in that order.

        This is to be overloaded by a child class
        """
        raise NotImplemented

    def update(self):
        """
        """
        pass
        
    def get_next_double_group(self):
        """
        Call _get_next_target_group, extract all DoubleStars, the band to
        observe them in, and the requester from the Target objects, 
        and return a new list, preserving order

        # We do this to avoid using Target objects outside this class
        # We avoid doing that because it gets complicated when ReferenceStars don't have
        # corresponding target objects
        """
        return [(x.star, x.band, x.requester) for x in self._get_next_target_group()]
        
    def get_next_single_star(self, doubles, ra_dist=0, dec_dist=0):
        if len(doubles) != 1:
            logger.critical("Finding a single star for a non-1 set of doubles is not currently supported.")
            raise NotImplementedError

        if ra_dist == 0:
            ra_dist = self.MAX_SINGLE_DIST_RA

        if dec_dist == 0:
            dec_dist = self.MAX_SINGLE_DIST_DEC

        dbl, band, _ = doubles[0]
        ra_range = (dbl.ra_deg - ra_dist, dbl.ra_deg + ra_dist)
        dec_range = (dbl.dec_deg - dec_dist, dbl.dec_deg + dec_dist)

        # Get all singles that are close enough to the double to be a reference
        singles = self.session.query(ReferenceStar).filter(
            ReferenceStar.ra_deg >= ra_range[0],
            ReferenceStar.ra_deg <= ra_range[1],
            ReferenceStar.dec_deg >= dec_range[0],
            ReferenceStar.dec_deg <= dec_range[1]).all()

        # Remove all blacklisted singles
        singles = filter(lambda s: s not in self.blacklisted_singles, singles)

        if len(singles) == 0:
            # If we couldn't find any single stars close enough, widen the search
            logger.warning("No single stars were found within {ra} degrees RA and {dec} degrees Dec of double star {dbl}.".format(
                ra=ra_dist,
                dec=dec_dist,
                dbl=dbl.name))

            ra_dist = 2 * ra_dist
            dec_dist = 2 * dec_dist
            
            logger.warning("The search is being widened to {ra} degrees RA and {dec} degrees Dec."
                           .format(
                               ra=ra_dist,
                               dec=dec_dist))

            return self.get_next_single_star(doubles, ra_dist, dec_dist)

        # Now that we have some singles to pick from, pick the one with the most similar spectral
        # type

        # Find the minimum spectral type difference between the double and a single
        spec_diff =  min(abs(astro.stype_to_number(dbl.stype) - astro.stype_to_number(s.stype))
                     for s in singles)

        # Find all single stars with that minimum spectral type difference
        singles = filter(lambda s: abs(astro.stype_to_number(dbl.stype) - astro.stype_to_number(s.stype)) == spec_diff, singles)

        # Then find the single among those of the most similar spectral 
        # type that is closest to the double
        single = min(singles, key=functools.partial(astro.dist, dbl))

        return single
        # TODO: In what band do we observe the single?

    @rpc_method
    def reset(self):
        """
        Reset the internal state of the scheduler
        This is identical to restarting the scheduler process
        This does not modify the database in any way
        """
        logger.info("Resetting...")
        
#### SPLIT FILE HERE
        
import random
        
class RandomScheduler(AbstractScheduler):
    """
    This scheduler randomly groups doubles, then assigns a random single.  It is ONLY for testing.
    """
    MIN_GROUP_SIZE = 1
    MAX_GROUP_SIZE = 10
    
    def _get_next_target_group(self):
        doubles = []
        
        for x in range(0, random.randrange(RandomScheduler.MIN_GROUP_SIZE, RandomScheduler.MAX_GROUP_SIZE)):
            doubles.append(random.choice(self.session.query(DoubleStar).all()))
                
        return doubles

    def get_next_single_star(self, doubles):
        singles = self.session.query(ReferenceStar).all()
        
        return singles[random.randrange(0, 100000)]

#### SPLIT FILE HERE

class InOrderScheduler(AbstractScheduler):
    """
    This scheduler observes one single star per double star, in the order the doubles appear in
    the target list, starting with a double star.
    """
    def __init__(self):
        super(InOrderScheduler, self).__init__()

        self.targets = self.session.query(Target).all()
        print 'targets', self.targets
        
    def _get_next_target_group(self):
        if self.targets:
            return [self.targets.pop(0)]

        raise errors.NoObservableTargetsError("There are no observable targets.")

    @rpc_method
    def reset(self):
        self.targets = self.session.query(Target).all()
        super(InOrderScheduler, self).reset()

class WeightedSingleScheduler(AbstractScheduler):
    HOUR_ANGLE_WEIGHT = 1
    DISTANCE_WEIGHT = 10
    MOON_DIST_WEIGHT = 2
    TIME_DELTA_WEIGHT = 15

    CLOSEST_MOON_DIST = 5 #degrees
    
    def __init__(self, telescope):
        super(WeightedSingleScheduler, self).__init__()        

        self.targets = self.session.query(Target).all()

        print self.targets

        self.telescope = telescope

        # XMLRPC is quite slow on windows, so only get this data once per
        # set of cost calculations
        self.tele_ra, self.tele_dec = self.telescope.get_pos()
        #self.tele_ra = self.tele_dec = 0

        # Maps targets to the last time they were scheduled, regardless of whether or not
        # they were observed
        # { target : datetime }
        self.scheduled_time = {}

    def _get_next_target_group(self):
        self.tele_ra, self.tele_dec = self.telescope.get_pos()
    
        target = min(self.targets, key=self.cost)

        self.scheduled_time[target] = datetime.datetime.now()
        
        return [target]

    @rpc_method
    def reset(self):
        self.scheduled_time = {}

    def cost(self, target):
        """
        Calculate the cost of a target
        The target with the lowest cost within horizon limits is chosen
        """
        # Set this to a very high number to make a target excluded
        # e.g. below horizon or too close to moon
        adjust = 0
        
        # Hour-angle
        ha = abs(target.star.ra_deg - ephem.degrees(site.sidereal_time()))        

        # Distance from current position

        tele_dist = math.sqrt(((target.star.ra_deg - self.tele_ra) ** 2) + (target.star.dec_deg - self.tele_dec) ** 2)

        # Time since last observation
        last_obs_time = self.scheduled_time.get(target, None)
        if not last_obs_time:
            #last_obs_time =  self.session.query(Observation).filter_by(star_id=target.star_id).order_by("datetime").all()
            last_obs_time = []

            if last_obs_time:
                last_obs_time = last_obs_time[0].datetime
                
        if last_obs_time:
            hours = 2000. / (((datetime.datetime.now() - last_obs_time).total_seconds()))

        else:
            hours = 0
        
        # Distance from moon
        moon.compute()
        moon_dist = math.sqrt(((target.star.ra_deg - ephem.degrees(moon.a_ra)) ** 2) + \
                               (target.star.dec_deg - moon.a_dec) ** 2)

        print "dist", tele_dist
        print "hours", hours
        print 'ha', ha
        print 'moon_dist', moon_dist
        print
                               
        if moon_dist < self.CLOSEST_MOON_DIST:
            adjust = 2**32

        
        cost = (tele_dist * self.DISTANCE_WEIGHT) + \
               (hours     * self.TIME_DELTA_WEIGHT) + \
               (moon_dist * self.MOON_DIST_WEIGHT) + \
               (ha        * self.HOUR_ANGLE_WEIGHT)

        return cost
