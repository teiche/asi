#!/usr/bin/env python

from asi.utils.xmlrpc import RPCAble, rpc_method

class SimPlateSolve3(RPCAble):
    def __init__(self):
        self._xmlrpc_funcs = [self.solve, self.ready, self.plate_solution, self.transform_plate_to_j2000]
        super(SimPlateSolve3, self).__init__()
        
    def ready(self):
        return True

    def plate_solution(self):
        return (0, 0, 0, 1, 1)

    def solve(self, fname, xsize=0, ysize=0, ra=100, dec=100):
        pass

    def transform_plate_to_j2000(self, x, y):
        return (0, 0)

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

import asi
from asi.utils.xmlrpc import RequestHandler
from asi.slider.simulator import SliderSimulator

asi.log.init_logging("slider.log")

server = SimpleXMLRPCServer(("localhost", 7278),
                            requestHandler=RequestHandler,
                            allow_none=True,
                            logRequests=False)

server.timeout = .001

server.register_introspection_functions()

slider = SimPlateSolve3()
slider.register_xmlrpc_functions(server)
    
print "Slider Simulator Running..."

while 1:
    server.handle_request()


