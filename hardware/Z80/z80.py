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
from hardware.cpu import (
    CPU, CPUTrapInvalidOP,
    _add_cycles,
    cpu_inc_t,
    cpu_reset,
    cpu_irq,
    cpu_nmi,
)

from tools import *
from dasm import *
from opcodes import *

__all__ = ('Z80',)

class Z80(CPU, Z80MixinBASE):
    IM0, IM1, IM0_1 = range(0, 3)
    
    def __init__(self, break_afer, mem, io=None):
        super(Z80, self).__init__(break_afer, mem, io)
        self.reset()
        
        # # shortcuts
        # self.read = self.mem.read
        # self.write = self.mem.write
        
        # initialize opcodes
        self._init_base()
        
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
        pass
        # # run until we spend all cycles
        # # TODO IRQs
        # self.T += cycles
        # 
        # while self.T >= 0:
        #     old_pc = self.pc
        #     op = self.read_op()
        #     t = CYCLES[op]
        #     
        #     try:
        #         self._op[op]()
        #     except KeyError:
        #         raise CPUTrapInvalidOP('Invalid opcode %02X: %s' % (op, self.disassemble(old_pc)))
        #     self.abs_T += t
        #     self.T -= t
    
    # =================
    # = mem I/O stuff =
    # =================
    def read16(self, adr, w1=None, w2=None):
        r = self.read # shortcut
        return r(adr, w1) + (r(adr + 1, w2) * 256)
    
    def write16(self, adr, val, w1=None, w2=None):
        w = self.write # shortcut
        w(adr, val, w1) # no need for & 0xFF, memory will do this
        w(adr + 1, val >> 8, w2)
    
    def read_op_arg16(self):
        r = self.read_op # shortcut
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
        
        # internal flags
        self.noint_once = False
        self.halt = False
        self.int_vector_req = 0
        

    # =======
    # = I/O =
    # =======
    def read_port(self, port, wait=0):
        if wait: self._wait_until(wait)
        return self.io.read(port)
    
    def write_port(self, port, value, wait=0):
        """ write port """
        if wait: self._wait_until(wait)
        self.io.write(port, value)

    # 16b regs
    # TODO see which 16b regs are more used and use them like Ix regs
    #      instead of using them as two 8b regs -- HL?
    
    # AF
    def _gAF(self):
        return self.f + (self.a * 256)
    def _sAF(self, val):
        self.f = val & 0xFF
        self.f = (val >> 8) & 0xFF
    AF = property(fget=_gAF, fset=_sAF)
    af = property(fget=_gAF, fset=_sAF)
    
    # BC
    def _gBC(self):
        return self.C + (self.B * 256)
    def _sBC(self, val):
        self.C = val & 0xFF
        self.B = (val >> 8) & 0xFF
    BC = property(fget=_gBC, fset=_sBC)
    
    # DE
    def _gDE(self):
        return self.E + (self.D * 256)
    def _sDE(self, val):
        self.E = val & 0xFF
        self.D = (val >> 8) & 0xFF
    DE = property(fget=_gDE, fset=_sDE)
    
    # HL
    def _gHL(self):
        return self.L + (self.H * 256)
    def _sHL(self, val):
        self.L = val & 0xFF
        self.H = (val >> 8) & 0xFF
    HL = property(fget=_gHL, fset=_sHL)
    
    # (HL)
    def _gHLind(self):
        return self.read(self.HL)
    def _sHLind(self, val):
        self.write(self.HL, val)
    HL_ind = property(fget=_gHLind, fset=_sHLind)
    
    # index lo/hi
    def _gIXL(self):
        return self.IX & 0xFF
    def _sIXL(self, val):
        self.IX = (self.IX & 0xFF00) + (val & 0xFF)
    IXL = property(fget=_gIXL, fset=_sIXL)
    
    def _gIXH(self):
        return (self.IX >> 8) & 0xFF
    def _sIXH(self, val):
        self.IX = ((val & 0xFF) * 256) + (self.IX & 0xFF)
    IXH = property(fget=_gIXH, fset=_sIXH)
    
    def _gIYL(self):
        return self.IY & 0xFF
    def _sIYL(self, val):
        self.IY = (self.IY & 0xFF00) + (val & 0xFF)
    IYL = property(fget=_gIYL, fset=_sIYL)
    
    def _gIYH(self):
        return (self.IY >> 8) & 0xFF
    def _sIYH(self, val):
        self.IY = ((val & 0xFF) * 256) + (self.IY & 0xFF)
    IYH = property(fget=_gIYH, fset=_sIYH)
    
    # ====================
    # = Standard opcodes =
    # ====================
    
    def nop(self):
        pass
    
    def register_opcodes(self):
        self._create_8b_load()
        # ============
        # = standard =
        # ============
        self._op[NOP] = self.nop

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
            k = k.upper()
            if k != 'F':
                setattr(self, k, v)
            else:
                self.F.byte = v
