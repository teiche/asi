from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

import asi
from asi.utils.xmlrpc import RequestHandler
from asi.slider.simulator import SliderSimulator

asi.log.init_logging("slider.log")

server = SimpleXMLRPCServer(("localhost", 7275),
                            requestHandler=RequestHandler,
                            allow_none=True,
                            logRequests=False)

server.timeout = .001

server.register_introspection_functions()

slider = SliderSimulator()
slider.register_xmlrpc_functions(server)
    
print "Slider Simulator Running..."

while 1:
    server.handle_request()
