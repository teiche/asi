import logging

from ..utils.xmlrpc import RPCAble, rpc_method

logger = logging.getLogger(__name__)

class AbstractSlider(RPCAble):
    MOVING      = 0
    ACQUISITION = 1
    SCIENCE     = 2

    def __init__(self):
        self._xmlrpc_funcs = [self.to_acquisition, self.to_science, self.get_pos, self.ready]

        super(AbstractSlider, self).__init__()

    def to_acquisition(self):
        raise NotImplementedError

    def to_science(self):
        raise NotImplementedError

    def get_pos(self):
        raise NotImplementedError

    def ready(self):
        raise NotImplementedError
    


