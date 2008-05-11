# Copyright 2008 Djordjevic Nebojsa <djnesh@gmail.com>
#
# This file is part of py-emu.
#
# py-emu is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# py-emu is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with py-emu.  If not, see <http://www.gnu.org/licenses/>.

"""
Z80 CPU core
"""

# stdlib
import random

# app
from hardware.cpu import CPU, CPUTrapInvalidOP
from tools import *
from dasm import *
from opcodes import *

__all__ = ('Z80',)

class Z80(CPU, Z80MixinBASE):
    IM0, IM1, IM0_1 = range(0, 3)
    
    def __init__(self, mem, io=None):
        super(Z80, self).__init__(mem, io)
        self.reset()
        
        # shortcuts
        self.read = self.mem.read
        self.write = self.mem.write
        self.io_read = self.io.read
        self.io_write = self.io.write
        
        # initialize opcodes
        self.register_opcodes()
    
    def disassemble(self, address, bytes=1, dump_adr=True, dump_hex=True):
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
    
    def run(self, cycles=0):
        # run until we spend all cycles
        # TODO IRQs
        self.icount += cycles
        while self.icount > 0:
            op = self.read_op()
            self.r = (self.r + 1) & 0x7F # R is 7bit
            self._base[op]()
    
    # =================
    # = mem I/O stuff =
    # =================
    def read16(self, adr):
        r = self.read # shortcut
        return r(adr) + (r(adr + 1) * 256)
    
    def write16(self, adr, val):
        w = self.write # shortcut
        w(adr, val) # no need for & 0xFF, memory will do this
        w(adr + 1, val >> 8)
    
    def read_op(self):
        ret = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return ret
    read_op_arg = read_op
    
    def read_op_arg16(self):
        r = self.read_op_arg # shortcut
        return r() + (r() * 256)
    
    def flags_as_str(self, val = None):
        from flags import Z80Flags
        if val is None: val = self.f
        return str(Z80Flags(val))
    
    def __str__(self):
        ret = []
        ret.append('PC: %04X AF: %04X BC: %04X DE: %04X HL: %04X IX: %04X IY: %04X SP: %04X' %\
                    (self.pc, self.af, self.bc, self.de, self.hl, self.ix, self.iy, self.sp)
                  )
        ret.append('I: %02X R: %02X IFF1: %s IFF2: %s IM: %s T: %d' % (
                    self.i, self.r, self.iff1, self.iff2, self.im, self.itotal
                  ))
        ret.append('F: %s' % self.flags_as_str())
        return '\n'.join(ret)
    
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
    
    def register_opcodes(self):
        self._init_base()
    
    def get_state(self):
        """get cpu state
           
           return dict with current cpu state
        """
        raise NotImplementedError('%s.get_state() is not implemented' % self.__class__)
    
    def set_state(self, state):
        """set cpu state
           
           set current cpu state with state dict
        """
        for k, v in state.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise KeyError("Z80 don't have attribute %s" % k)
    
    # =============
    # = registers =
    # =============
    
    def _get_af(self):
        return (self.a << 8) | self.f
    def _set_af(self, val):
        self.a = (val & 0xFF00) >> 8
        self.f = val & 0xFF
    af = property(fset=_set_af, fget=_get_af)
    
    def _get_bc(self):
        return (self.b << 8) | self.c
    def _set_bc(self, val):
        self.b = (val & 0xFF00) >> 8
        self.c = val & 0xFF
    bc = property(fset=_set_bc, fget=_get_bc)
    
    def _get_de(self):
        return (self.d << 8) | self.e
    def _set_de(self, val):
        self.d = (val & 0xFF00) >> 8
        self.e = val & 0xFF
    de = property(fset=_set_de, fget=_get_de)
    
    # def _get_hl(self):
    #     return (self.h << 8) | self.l
    # def _set_hl(self, val):
    #     self.h = (val & 0xFF00) >> 8
    #     self.l = val & 0xFF
    # hl = property(fset=_set_hl, fget=_get_hl)
    
    def _get_h(self):
        return (self.hl & 0xFF00) >> 8
    def _set_h(self, val):
        self.hl = (self.hl & 0x00FF) | ((val & 0xFF) << 8)
    h = property(fget=_get_h, fset=_set_h)
    
    def _get_l(self):
        return self.hl & 0xFF
    def _set_l(self, val):
        self.hl = (self.hl & 0xFF00) | (val & 0xFF)
    l = property(fget=_get_l, fset=_set_l)
    
    # ==================
    # = IX/IY high/low =
    # ==================
    def _get_ixh(self):
        return (self.ix & 0xFF00) >> 8
    def _set_ixh(self, val):
        self.ix = (self.ix & 0x00FF) | ((val & 0xFF) << 8)
    ixh = property(fget=_get_ixh, fset=_set_ixh)
    
    def _get_ixl(self):
        return self.ix & 0xFF
    def _set_ixl(self, val):
        self.ix = (self.ix & 0xFF00) | (val & 0xFF)
    ixl = property(fget=_get_ixl, fset=_set_ixl)
    
    def _get_iyh(self):
        return (self.iy & 0xFF00) >> 8
    def _set_iyh(self, val):
        self.iy = (self.iy & 0x00FF) | ((val & 0xFF) << 8)
    iyh = property(fget=_get_iyh, fset=_set_iyh)
    
    def _get_iyl(self):
        return self.iy & 0xFF
    def _set_iyl(self, val):
        self.iy = (self.iy & 0xFF00) | (val & 0xFF)
    iyl = property(fget=_get_iyl, fset=_set_iyl)