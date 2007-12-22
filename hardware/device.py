# future stuff
from __future__ import absolute_import

import ctypes

from .settings import logging

try:
    from psyco import compact
    from psyco.classes import __metaclass__
except ImportError:
    import sys
    print >>sys.stderr, 'No psyco'
    class compact(object):
        pass

class Device(compact):
    # width: (unsigned, signed)
    WIDTH_MAP = {
        8: (ctypes.c_ubyte, ctypes.c_byte),
        16: (ctypes.c_ushort, ctypes.c_short),
        32: (ctypes.c_ulong, ctypes.c_long),
        64: (ctypes.c_ulonglong, ctypes.c_longlong),
    }
    
    def __init__(self):
        super(Device, self).__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)
        self.reset()
    
    @staticmethod
    def _width_to_ctype(width):
        # big bad switch
        if width not in Device.WIDTH_MAP:
            raise ValueError('invalid bit width %d', width)
        return Device.WIDTH_MAP[width]
    
    @staticmethod
    def signed_type(width):
        return Device._width_to_ctype(width)[1]
    
    @staticmethod
    def unsigned_type(width):
        return Device._width_to_ctype(width)[0]
    
    def reset(self):
        raise NotImplementedError('%s.reset() is not implemented' % self.__class__)
    
    def write(self, adr, value):
        raise NotImplementedError('%s.write() is not implemented' % self.__class__)
    
    def read(self, adr):
        raise NotImplementedError('%s.read() is not implemented' % self.__class__)
