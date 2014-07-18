import functools
import logging

logger = logging.getLogger(__name__)

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

from .. import db
from ..db.catalog import DoubleStar, ReferenceStar
from ..db.targetlist import Target

from ..utils.xmlrpc import RPCAble, rpc_method
from ..utils import astro

import errors

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
        self.double_queue = []

        # Once a double is observed, if the observation is successful it is moved from the 
        # double_queue to this list.  If it was unsuccessful, it is forgotten entirely.
        # This list is so the best single star can be recalculated if self.single can't be found
        # This list is only used after double_queue is exhausted AND self.single fails
        self.successful_doubles = []

        # The single to observe for the doubles in self.double_queue
        self.single = None

        # This is the star we are currently observing
        self.current = None

        #self._xmlrpc_funcs = (self.get_next_target, self.target_failed, self.target_success)

    def _get_next_target(self):
        """
        Fetch and return the next target to observe, as a Django ORM object
        """
        if self.double_queue: # If there are still doubles in the queue
            self.current = self.double_queue.pop(0)

        elif self.single and self.successful_doubles: 
            # If we have a single ready to go, and we observed at least one double
            self.current = self.single
            self.single = None

        else: # We're out of singles and doubles
            self._load_next_group()
            return self._get_next_target()

        return self.current

    @rpc_method
    def get_next_target(self):
        """
        Return the next target to observe as an RPC-serializable string, to be converted into
        an SQLAlchemy ORM object at the client side
        """
        t = self._get_next_target()

        db = t.__class__.__name__
        i = t.id
        
        return (db, i)
        
    @rpc_method
    def target_failed(self):
        """
        The current target was a failure

        This method is how the run controller tells the scheduler that the target could not be found, or failed for some other reason

        In the case of a double, it is simply skipped
        In the case of a single, a new single is found
        """
        if isinstance(self.current, ReferenceStar):
            self.single = self.get_next_single_star(self.successful_doubles)

    @rpc_method
    def target_success(self):
        """
        The current target was a success
        """
        if isinstance(self.current, DoubleStar):
            self.successful_doubles.append(self.current)

    def _load_next_group(self):
        """
        Load the next group of doubles into the queue, then select a single star for them
        """
        self.successful_doubles = []
        self.double_queue = self.get_next_double_group()
        self.single = self.get_next_single_star(self.double_queue)

    def _get_next_target_group(self):
        """
        Return a list of targets to observe.  They are observed in that order.

        This is to be overloaded by a child class
        """
        raise NotImplemented
        
    def get_next_double_group(self):
        """
        Call _get_next_target_group, extract all DoubleStars from the Target objects, 
        and return a new list, preserving order
        """
        return [x.star for x in self._get_next_target_group()]

    def update(self):
        """
        """
        pass

    def get_next_single_star(self, doubles, ra_dist=0, dec_dist=0):
        if len(doubles) != 1:
            logger.critical("Finding a single star for a non-1 set of doubles is not currently supported.")
            raise NotImplementedError

        if ra_dist == 0:
            ra_dist = self.MAX_SINGLE_DIST_RA

        if dec_dist == 0:
            dec_dist = self.MAX_SINGLE_DIST_DEC

        print 'double', doubles
        dbl = doubles[0]
        ra_range = (dbl.ra_deg - ra_dist, dbl.ra_deg + ra_dist)
        dec_range = (dbl.dec_deg - dec_dist, dbl.dec_deg + dec_dist)

        # Get all singles that are close enough to the double to be a reference
        singles = self.session.query(ReferenceStar).filter(
            ReferenceStar.ra_deg >= ra_range[0],
            ReferenceStar.ra_deg <= ra_range[1],
            ReferenceStar.dec_deg >= dec_range[0],
            ReferenceStar.dec_deg <= dec_range[1]).all()

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
