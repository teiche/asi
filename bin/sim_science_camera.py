from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

from asi.utils.xmlrpc import RequestHandler

from asi.scicam.simulator import ScienceCameraSimulator

server = SimpleXMLRPCServer(("localhost", 7276),
                            requestHandler=RequestHandler,
                            logRequests=False,  
                            allow_none=True)

server.timeout = .001

server.register_introspection_functions()

science_camera = ScienceCameraSimulator()
science_camera.register_xmlrpc_functions(server)
    
print "Science Camera Simulator Running..."

while 1:
    server.handle_request()
