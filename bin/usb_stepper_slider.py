#! /usr/bin/env python

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

import asi
from asi.utils.xmlrpc import RequestHandler
from asi.slider.usb_stepper_slider import USBStepperSlider

asi.log.init_logging("slider.log")

server = SimpleXMLRPCServer(("localhost", 7275),
                            requestHandler=RequestHandler,
                            allow_none=True,
                            logRequests=False)

server.timeout = .001

server.register_introspection_functions()

slider = USBStepperSlider()
slider.register_xmlrpc_functions(server)
    
print "USB Stepper-stick slider running..."

while 1:
    server.handle_request()
