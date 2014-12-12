from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

import asi
from asi.scheduler import InOrderScheduler, WeightedSingleScheduler
from asi.utils.xmlrpc import RequestHandler

asi.log.init_logging("scheduler.log")

server = SimpleXMLRPCServer(("localhost", 7273),
                            requestHandler=RequestHandler,
                            logRequests=False,
                            allow_none=True)
server.timeout = .001
server.register_introspection_functions()

rs = InOrderScheduler()
#rs = WeightedSingleScheduler(asi.client.Telescope())
rs.register_xmlrpc_functions(server)

while 1:
    rs.update()
    server.handle_request()
