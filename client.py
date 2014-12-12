import xmlrpclib

from utils.xmlrpc import RPCClientOverloadWrapper
from db.catalog import ReferenceStar, DoubleStar
import db
import config

TABLE_NAME_MAP = {
    'ReferenceStar' : ReferenceStar,
    'DoubleStar' : DoubleStar,
    }
    
SCHEDULER_DEFAULT_ADDR  = config.scheduler_addr
TELESCOPE_DEFAULT_ADDR  = config.telescope_addr
SLIDER_DEFAULT_ADDR     = config.slider_addr
SCICAM_DEFAULT_ADDR     = config.scicam_addr
ACQUISCAM_DEFAULT_ADDR  = config.acquiscam_addr
PLATESOLVE_DEFAULT_ADDR = config.platesolve_addr
RUNMAN_DEFAULT_ADDR     = config.runman_addr


"""
Scheduler needs some client side helper code:
XMLRPC can't send arbitrary Python objects, so to get a Star object into the RunManager thread
the scheduler returns a database name and primary key, which gets looked up using the Django ORM
here and returned
"""
class Scheduler(RPCClientOverloadWrapper):
    def __init__(self, hostname=SCHEDULER_DEFAULT_ADDR):
        super(Scheduler, self).__init__(hostname)

    def get_next_target(self):
        table, i, band, requester = self._rpc.get_next_target()

        session = db.Session()
        star = session.query(TABLE_NAME_MAP[table]).filter_by(id=i).first()

        return star, band, requester

class Telescope(RPCClientOverloadWrapper):
    def __init__(self, hostname=TELESCOPE_DEFAULT_ADDR):
        super(Telescope, self).__init__(hostname)
    
    def slew_obs(self, star):
        assert hasattr(star, 'ra_deg') and hasattr(star, 'dec_deg')

        self.slew_abs(star.ra_deg, star.dec_deg)

'''
class AcquisitionCamera(RPCClientOverloadWrapper):
    def __init__(self, hostname=ACQUISCAM_DEFAULT_ADDR):
        super(AcquisitionCamera, self).__init__(hostname)

        # These are so _idle_while_busy(acquiscam.plate_solve) waits for a plate solve to complete
        self.plate_solve.__func__.ready = lambda: self._rpc.plate_solve_ready()
        self.plate_solve.__func__.name = lambda: self._rpc.name() + '-PlateSolver'
        
    def plate_solve(self, ra, dec):
        self._rpc.plate_solve(ra, dec)
'''     
# The rest are vanilla XMLRPC instance, so configure them in a sane manner then pass off it on
def _make_xmlrpc_connection(addr):
    return xmlrpclib.ServerProxy(addr, allow_none=True)

'''
def Telescope(addr=TELESCOPE_DEFAULT_ADDR):
    return _make_xmlrpc_connection(addr)
'''

def Slider(addr=SLIDER_DEFAULT_ADDR):
    return _make_xmlrpc_connection(addr)

def ScienceCamera(addr=SCICAM_DEFAULT_ADDR):
    return _make_xmlrpc_connection(addr)

def AcquisitionCamera(addr=ACQUISCAM_DEFAULT_ADDR):
    return _make_xmlrpc_connection(addr)

def PlateSolve(addr=PLATESOLVE_DEFAULT_ADDR):
    return _make_xmlrpc_connection(addr)


def RunManager(addr=RUNMAN_DEFAULT_ADDR):
    return _make_xmlrpc_connection(addr)
