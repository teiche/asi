import random

from ..utils.xmlrpc import RPCAble, rpc_method

class TelescopeSimulator(RPCAble):
    # Degrees per update
    RA_SPEED = .1
    DEC_SPEED = .1
    
    def __init__(self):
        super(TelescopeSimulator, self).__init__()
        
        self.cur_ra = 0
        self.cur_dec = 0

        self.target_ra = 0
        self.target_dec = 0        

    @rpc_method
    def slew_rel(self, ra, dec):
        print "slew_rel to ({ra}, {dec})...".format(ra=ra, dec=dec)
        
        self.target_ra = self.cur_ra + ra
        self.target_dec = self.cur_dec + dec

    @rpc_method
    def slew_abs(self, ra, dec):
        print "slew_abs to ({ra}, {dec})...".format(ra=ra, dec=dec)

        self.target_ra = ra + (random.random() - 0.5) * 10
        self.target_dec = dec + (random.random() - 0.5) * 10

    @rpc_method        
    def slewing(self):
        return not all([abs(self.cur_ra - self.target_ra) < (2*self.RA_SPEED), 
                        abs(self.cur_dec - self.target_dec) < (2*self.DEC_SPEED)])

    @rpc_method
    def ready(self):
        return not self.slewing()

    @rpc_method
    def get_pos(self):
        return self.cur_ra, self.cur_dec

    @rpc_method
    def park(self):
        print "Parking"
        
    @rpc_method
    def unpark(self):
        print "Unparking"

    def update(self):
        if self.cur_ra < self.target_ra:
            self.cur_ra += self.RA_SPEED

        elif self.cur_ra > self.target_ra:
            self.cur_ra -= self.RA_SPEED
            
        if self.cur_dec < self.target_dec:
            self.cur_dec += self.DEC_SPEED

        elif self.cur_dec > self.target_dec:
            self.cur_dec -= self.DEC_SPEED

        if self.slewing():
            print "SLEWING! Current Position: ({0}, {1})".format(self.cur_ra, self.cur_dec)

#if __name__ == '__main__':
'''
def __main__():
    server = SimpleXMLRPCServer(("localhost", 7272),
                                requestHandler=RequestHandler)

    server.register_introspection_functions()

    telescope = TelescopeSimulator()
    telescope.register_xmlrpc_functions(server)
    
    print "Telescope Simulator Running..."

    while 1:
        telescope.update()
        server.handle_request()
'''
