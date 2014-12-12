import time
import atexit
import logging
import subprocess
import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

from asi.utils.xmlrpc import RequestHandler
from asi.scicam.andor import AndorScienceCamera

logger = logging.getLogger(__name__)
logger.info("Starting AndorControl.exe")

#child = subprocess.Popen('AndorControl')
#child = subprocess.Popen([r'C:\Users\alex\Documents\Visual Studio 2012\Projects\AndorControl\Debug\AndorControl.exe'])

if not '-n' in sys.argv: 
    print "Spawning ANDORControlAutomatic.exe"
    child = subprocess.Popen([r'C:\Users\Russ\asi\AndorControl\Release\AndorControlAutomatic.exe'])


logger.info("Waiting for AndorControl to start")
time.sleep(30)

server = SimpleXMLRPCServer(("localhost", 7276),
                            requestHandler=RequestHandler,
                            logRequests=False,  
                            allow_none=True)

server.timeout = .001

server.register_introspection_functions()

science_camera = AndorScienceCamera("127.0.0.1", 7077)
science_camera.register_xmlrpc_functions(server)

logger.info("Connected to AndorControl")

while 1:
    server.handle_request()
