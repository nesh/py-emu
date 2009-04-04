from op_gen import JP_BASE

def Property(func):
    """ small property helper """
    return property(**func())

class Z80(object):
    IM0, IM1, IM0_1 = range(0, 3)
    
    def __init__(self, mem, io=None):
        super(Z80, self).__init__(mem, io)
        self.reset()
        
        # shortcuts
        self.read = self.mem.read
        self.write = self.mem.write
        self.io_read = self.io.read
        self.io_write = self.io.write
        self.read_op = self.mem.read_op

    def run(self, cycles=0):
        # run until we spend all cycles
        # TODO IRQs
        self.icount += cycles
        while self.icount > 0:
            op = self.read_op()
            self._r += 1
            JP_BASE[op](self)

    # register access
    @Property
    def r():
        def fget(self):
            return (self._r & 0x7F) | (self._r7 & 0x80)
        def fset(self, val):
            self._r = self._r7 = val & 0xFF
        return locals()

    @Property
    def af():
        def fget(self):
            return (self.a / 256) | self.f
        def fset(self, val):
            self.a = (val & 0xFF00) / 256
            self.f = val & 0xFF
        return locals()
    
    @Property
    def bc():
        def fget(self):
            return (self.b / 256) | self.c
        def fset(self, val):
            self.b = (val & 0xFF00) / 256
            self.c = val & 0xFF
        return locals()
    
    @Property
    def de():
        def fget(self):
            return (self.d / 256) | self.e
        def fset(self, val):
            self.d = (val & 0xFF00) / 256
            self.e = val & 0xFF
        return locals()
    
    @Property
    def h():
        def fget(self):
            return (self.hl & 0xFF00) / 256
        def fset(self, val):
            self.hl = (self.hl & 0x00FF) | ((val & 0xFF) / 256)
        return locals()
    
    @Property
    def l():
        def fget(self):
            return self.hl & 0xFF
        def fset(self, val):
            self.hl = (self.hl & 0xFF00) | (val & 0xFF)
        return locals()
    
    @Property
    def ixh():
        def fget(self):
            return (self.ix & 0xFF00) / 256
        def fset(self, val):
            self.ix = (self.ix & 0x00FF) | ((val & 0xFF) / 256)
        return locals()
    
    @Property
    def ixl():
        def fget(self):
            return self.ix & 0xFF
        def fset(self, val):
            self.ix = (self.ix & 0xFF00) | (val & 0xFF)
        return locals()
    
    @Property
    def iyh():
        def fget(self):
            return (self.iy & 0xFF00) / 256
        def fset(self, val):
            self.iy = (self.iy & 0x00FF) | ((val & 0xFF) / 256)
        return locals()
    
    @Property
    def iyl():
        def fget(self):
            return self.iy & 0xFF
        def fset(self, val):
            self.iy = (self.iy & 0xFF00) | (val & 0xFF)
        return locals()
