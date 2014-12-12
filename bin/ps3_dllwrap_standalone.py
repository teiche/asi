import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler    


def rpc_method(func):
    """
    Mark the function as one to be registered to the XMLRPC server.  This attribute is used
    during the __new__ method of an RPCAble to add the function to RPCAble._xmlrpc_funcs
    """
    setattr(func, 'rpc_method', True)

    return func



# An object with methods that can be RPCed
# This enforces a tuple of the RPC methods(_xmlrpc_funcs)
# and the function register_xmlrpc_functions,
# which takes an xmlrpc server and registers all functions in the tuple _xmlrpc_funcs
class RPCAble(object):
    def __init__(self):
        if not hasattr(self, '_xmlrpc_funcs'):
            # If the subclass didn't make an _xmlrpc_funcs, make one and populate it
            # with decorated functions
            self._xmlrpc_funcs = []

        else:
            self._xmlrpc_funcs = list(self._xmlrpc_funcs)
            
        for thing in dir(self):
            obj = getattr(self, thing)
            if hasattr(obj, 'rpc_method'):
                self._xmlrpc_funcs.append(obj)

                #return super(RPCAble, self).__new__(self)
                                
    @rpc_method
    def name(self):
        return self.__class__.__name__
    
    def register_xmlrpc_functions(self, server):
        """
        Take a SimpleXMLRPCServer and register all functions in self._xmlrpc_funcs with it
        """        
        for func in self._xmlrpc_funcs:
            server.register_function(func)


import sys
from math import degrees


if 'IronPython' not in sys.version:
    print("PlateSolve3 objects rely on the Microsoft CLR, and thus can only be used from within IronPython")
    sys.exit()

import clr
#clr.AddReferenceToFileAndPath(r'C:\Users\alex\Desktop\PS3DLLExample\PS3DLLExample\bin\Debug\SRSLib.dll')
clr.AddReferenceToFileAndPath(r'C:\Users\Russ\asi\PlateSolve3SRS\SRSLib.dll')

import SRSLib

def rad2sec(rad):
    return degrees(rad) * 3600.

class PlateSolve3(RPCAble):
    def __init__(self):
        self._xmlrpc_funcs = [self.solve, self.ready, self.plate_solution, self.transform_plate_to_j2000]
        super(PlateSolve3, self).__init__()

        #SRSLib.MatchLib.SetCatalogLocation(r'C:\Users\Alex\Desktop\PlateSolve3Catalogs')
        SRSLib.MatchLib.SetCatalogLocation(r'C:\Users\Russ\Documents\PS3\PS3Cats')
        #SRSLib.MatchLib.SetCatalogLocation(config.platesolve_catalogs)

        if not SRSLib.MatchLib.VerifyCatalog():
            print("PlateSolve3 Catalogs did not verify correctly.")
            sys.exit()

        #TODO: Nondefault parameters
        SRSLib.MatchLib.SetParms(500, 10, 2, 3, 60, 65000, 2014.5, 0.0)

        self.solution = False
        
    def ready(self):
        return True

    def plate_solution(self):
        return self.solution

    def solve(self, fname, xsize=0, ysize=0, ra=100, dec=100):
        plate = SRSLib.MatchLib.PlateListType()

        success, xsize, ysize, ra, dec, rot, plate = SRSLib.MatchLib.PlateSolveFilePlateList(fname, 0, 0, 100, 100, 0, plate)

        print 'xsize', xsize
        print 'ysize', ysize
        print 'ra', ra
        print 'dec', dec
        print 'rot', rot

        if success:
            self.plate = plate
            self.solution = degrees(ra), degrees(dec), degrees(rot), rad2sec(xsize), rad2sec(ysize)

        else:
            self.solution = False

    def transform_plate_to_j2000(self, x, y):
        ra, dec = SRSLib.MatchLib.TransformPlateToJ2000(self.plate.Xform, x, y, 0, 0)

        return degrees(ra), degrees(dec)


            
import os
import sys
#TODO: Remove this
#sys.path.append(r'C:\\Users\\alex\\Desktop\\')
sys.path.extend(os.environ['PYTHONPATH'].split(';'))

for i in sys.path:
    print i

# Default request handler for the XML-RPC server
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2')


server = SimpleXMLRPCServer(("localhost", 7278),
                            requestHandler=RequestHandler,
                            logRequests=False,
                            allow_none=True)
server.timeout = .001
server.register_introspection_functions()

ps3 = PlateSolve3()
ps3.register_xmlrpc_functions(server)

while 1:
    server.handle_request()
