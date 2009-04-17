from pyemu.hardware.cpu import CPU
from op_gen import JP_BASE

def Property(func):
    """ small property helper """
    return property(**func())

class Z80(CPU):
    IM0, IM1, IM0_1 = range(0, 3)
    
    def __init__(self, mem, io=None):
        super(Z80, self).__init__(mem, io)
        self.reset()
        
        # shortcuts
        self.read = self.mem.read
        self.write = self.mem.write
        self.io_read = self.io.read
        self.io_write = self.io.write

    def read_op(self):
        ret = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return ret
    read_op_arg = read_op

    def reset(self):
        super(Z80, self).reset()
        
        self.af = 0xFFFF
        self.bc = 0xFFFF
        self.de = 0xFFFF
        self.hl = 0xFFFF
        self.ix = 0xFFFF
        self.iy = 0xFFFF
        
        self.r = 0x00
        self.iff1 = False
        self.iff2 = False
        self.i = 0x00
        self.im = Z80.IM0
        
        self.pc = 0x0000
        self.sp = 0xFFFF
        
        # alt reg set
        self.af1 = 0xFFFF
        self.bc1 = 0xFFFF
        self.de1 = 0xFFFF
        self.hl1 = 0xFFFF
        
        # cpu (internal) flags
        self.in_halt = False
        self.prefix = 0
        self.no_irq_once = False
        self.memptr = 0

    def run(self, cycles=0):
        # run until we spend all cycles
        # TODO IRQs
        self.icount += cycles
        while self.icount > 0:
            op = self.read_op()
            self._r += 1
            JP_BASE[op](self)

    def set_state(self, state):
        """set cpu state
           
           set current cpu state with state dict
        """
        for k, v in state.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise KeyError("Z80 don't have attribute %s" % k)

    def flags_as_str(self, val = 0):
        from tables import (CF, NF, PF, VF, XF, F3, HF, YF, F5, ZF, SF)
        ret = [' '] * 8
        ret[7] = 'S' if val & SF else '-'
        ret[6] = 'Z' if val & ZF else '-'
        ret[5] = 'Y' if val & YF else '-'
        ret[4] = 'H' if val & HF else '-'
        ret[3] = 'X' if val & XF else '-'
        ret[2] = 'P/V' if val & PF else '-'
        ret[1] = 'N' if val & NF else '-'
        ret[0] = 'C' if val & CF else '-'
        ret.reverse()
        return ''.join(ret)

    def disassemble(self, address, bytes=1, dump_adr=True, dump_hex=True):
        from dasm import dasm
        ret = []
        while bytes > 0:
            s, ln = dasm(address, self.read)
            line = []
            if dump_adr:
                line.append('%04X' % address)
            if dump_hex:
                hx = []
                for o in range(ln):
                    hx.append('%02X' % self.read(address + o))
                line.append('%s: %s' % (''.join(hx), s))
            elif dump_adr and not dump_hex:
                ret.append(': %s' % s)
            else:
                ret.append(s)
            bytes -= ln
            ret.append(' '.join(line))
        return '\n'.join(ret)

    def __str__(self):
        ret = []
        ret.append('PC: %04X AF: %04X BC: %04X DE: %04X HL: %04X IX: %04X IY: %04X SP: %04X' %\
                    (self.pc, self.af, self.bc, self.de, self.hl, self.ix, self.iy, self.sp)
                  )
        ret.append('I: %02X R: %02X IFF1: %s IFF2: %s IM: %s T: %d' % (
                    self.i, self.r, self.iff1, self.iff2, self.im, self.itotal
                  ))
        ret.append('F: %s' % self.flags_as_str(self.f))
        return '\n'.join(ret)

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
            return (self.a * 256) | self.f
        def fset(self, val):
            self.a = (val & 0xFF00) / 256
            self.f = val & 0xFF
        return locals()
    
    @Property
    def bc():
        def fget(self):
            return (self.b * 256) | self.c
        def fset(self, val):
            self.b = (val & 0xFF00) / 256
            self.c = val & 0xFF
        return locals()
    
    @Property
    def de():
        def fget(self):
            return (self.d * 256) | self.e
        def fset(self, val):
            self.d = (val & 0xFF00) / 256
            self.e = val & 0xFF
        return locals()
    
    @Property
    def h():
        def fget(self):
            return (self.hl & 0xFF00) / 256
        def fset(self, val):
            self.hl = (self.hl & 0x00FF) | ((val & 0xFF) * 256)
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
            self.ix = (self.ix & 0x00FF) | ((val & 0xFF) * 256)
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
            self.iy = (self.iy & 0x00FF) | ((val & 0xFF) * 256)
        return locals()
    
    @Property
    def iyl():
        def fget(self):
            return self.iy & 0xFF
        def fset(self, val):
            self.iy = (self.iy & 0xFF00) | (val & 0xFF)
        return locals()

    @Property
    def pch():
        def fget(self):
            return (self.pc & 0xFF00) / 256
        def fset(self, val):
            self.pc = (self.pc & 0x00FF) | ((val & 0xFF) * 256)
        return locals()
    
    @Property
    def pcl():
        def fget(self):
            return self.pc & 0xFF
        def fset(self, val):
            self.pc = (self.pc & 0xFF00) | (val & 0xFF)
        return locals()

    @Property
    def memptr_h():
        def fget(self):
            return (self.memptr & 0xFF00) / 256
        def fset(self, val):
            self.memptr = (self.memptr & 0x00FF) | ((val & 0xFF) * 256)
        return locals()
    
    @Property
    def memptr_l():
        def fget(self):
            return self.memptr & 0xFF
        def fset(self, val):
            self.memptr = (self.memptr & 0xFF00) | (val & 0xFF)
        return locals()
