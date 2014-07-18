from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

import asi
from asi.utils.xmlrpc import RequestHandler
from asi.telescope.ascom import SiTechTelescope

asi.log.init_logging("telescope.log")

server = SimpleXMLRPCServer(("localhost", 7274),
                            requestHandler=RequestHandler,
                            logRequests=False,  
                            allow_none=True)

server.timeout = .001

server.register_introspection_functions()

telescope = SiTechTelescope()
telescope.register_xmlrpc_functions(server)
    
print "Telescope Simulator Running..."

while 1:
    telescope.update()
    server.handle_request()