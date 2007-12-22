try:
    from psyco.classes import __metaclass__
except ImportError:
    import sys
    print >>sys.stderr, 'No psyco'

class Flags(object):
    def __init__(self, val=0):
        self.set(val)
    
    def set(self, val):
        raise NotImplementedError('%s.set()s not implemented' % self.__class__)
        
    def mset(self, **kwargs):
        raise NotImplementedError('%s.mset()s not implemented' % self.__class__)
    
    def get(self):
        raise NotImplementedError('%s.get()s not implemented' % self.__class__)
    
    def __int__(self):
        """ slower than get!! """
        return self.get()

    def __str__(self):
        raise NotImplementedError('%s.__str__()s not implemented' % self.__class__)
    
    def __hex__(self):
        return hex(self.get())