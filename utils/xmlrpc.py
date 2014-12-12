import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

# Default request handler for the XML-RPC server
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2')

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
                        
class RPCClientOverloadWrapper(object):
    """
    RPCClientOverloadWrapper exposes all methods of an RPC connection as if they were direct
    members of RPCClientOverloadWrapper, while also allowing new/overloaded/compound methods
    to be built on top of it

    It is used when client-side functionality needs to be added to an RPC relationship
    An example of this is in client.Scheduler
    """
    def __init__(self, hostname):
        self._rpc = xmlrpclib.ServerProxy(hostname)

        self.system = self._rpc.system
        
        # Load RPC methods
        for method_name in self._rpc.system.listMethods():
            # If a method by the name already exists, don't load it
            # That method has been overridden, and accesses the name through self._rpc
            if not hasattr(self, method_name):
                setattr(self, method_name, getattr(self._rpc, method_name))            

