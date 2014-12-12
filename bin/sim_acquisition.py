from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

import asi
from asi.utils.xmlrpc import RequestHandler
from asi.acquisition.simulator import AcquisitionCameraSimulator

asi.log.init_logging("acquisition.log")

server = SimpleXMLRPCServer(("localhost", 7277),
                            requestHandler=RequestHandler,
                            allow_none=True,
                            logRequests=False)

server.timeout = .001
server.register_introspection_functions()

acquiscam = AcquisitionCameraSimulator()
acquiscam.register_xmlrpc_functions(server)

while 1:
    server.handle_request()
