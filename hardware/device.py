try:
    from psyco.classes import __metaclass__
except ImportError:
    pass

from settings import logging

class Device(object):
    def __init__(self):
        super(Device, self).__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)
        self.reset()
    
    def reset(self):
        raise NotImplementedError('%s.reset() is not implemented' % self.__class__)
    
    def write(self, adr, value):
        raise NotImplementedError('%s.write() is not implemented' % self.__class__)
    
    def read(self, adr):
        raise NotImplementedError('%s.read() is not implemented' % self.__class__)
