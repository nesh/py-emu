"""
Z80 CPU core
"""

import sys
from ctypes import cast, c_void_p, pointer

from hardware.cpu import (
    CPU, CPUTrapInvalidOP,
)
from hardware.memory import RAM
from z80core import *
from dasm import *

__all__ = ('Z80', 'Z80Mem')

class Z80Mem(RAM):
    """ we are using a C core so data is already in the required range """
    # faster than array-like access
    def read(self, adr):
        return self.mem[adr]
    
    def write(self, adr, value):
        self.mem[adr] = value

class Z80(CPU):
    def __init__(self, break_afer, mem, io=None):
        super(Z80, self).__init__(break_afer, mem, io)
        
        # shortcuts
        # self.read = self.mem.read
        self.write = self.mem.write
        self.io_read = self.io.read
        self.io_write = self.io.write
        
        self.cpu = libz80.z80ex_create(
                                        cast(z80ex_mread_cb(self.read), c_func_ptr), None,
                                        cast(z80ex_mwrite_cb(self.write), c_func_ptr), None,
                                        cast(z80ex_pread_cb(self.io_read), c_func_ptr), None,
                                        cast(z80ex_pwrite_cb(self.io_write), c_func_ptr), None,
                                        cast(z80ex_intread_cb(self.int_read), c_func_ptr), None,
                                       )
        self.reset()
    
    def __del__(self):
        libz80.z80ex_destroy(self.cpu)
    
    def read(self, addr, m1=0):
        return self.mem.read(addr)
    
    def int_read(self, ptr):
        """ read byte of interrupt vector -- called when M1 and IORQ goes active """
        return 0xFF
    
    def flags_as_str(self, val=None):
        if val is None:
            val = self.F
        ret = ['-'] * 8
        ret[7] = 'S' if val & S_FLAG else '-'
        ret[6] = 'Z' if val & Z_FLAG else '-'
        ret[5] = 'Y' if val & Y_FLAG else '-'
        ret[4] = 'H' if val & H_FLAG else '-'
        ret[3] = 'X' if val & X_FLAG else '-'
        ret[2] = 'V' if val & V_FLAG else '-'
        ret[1] = 'N' if val & N_FLAG else '-'
        ret[0] = 'C' if val & C_FLAG else '-'
        ret.reverse()
        return ''.join(ret)
    
    def reset(self):
        self.itotal = 0
        libz80.z80ex_reset(self.cpu)
    
    def run(self, cycles=1):
        if cycles < 1:
            return libz80.z80ex_step(self.cpu)
        else:
            return libz80.z80ex_run(self.cpu, cycles)
    
    def disassemble(self, address, bytes=1, dump_adr=True, dump_hex=True):
        ret = []
        idx = 0
        while bytes > 0:
            s, ln = dasm(address + idx, self.read)
            line = []
            if dump_adr:
                line.append('%04X' % (address + idx))
            if dump_hex:
                hx = []
                for o in range(ln):
                    hx.append('%02X' % self.read(address + idx + o))
                line.append('%s: %s' % (''.join(hx), s))
            elif dump_adr and not dump_hex:
                ret.append(': %s' % s)
            else:
                ret.append(s)
            bytes -= ln
            idx += ln
            ret.append(' '.join(line))
        return '\n'.join(ret)
    
    def set_state(self, state):
        for k, v in state.items():
            k = k.upper()
            setattr(self, k, v)
    
    def __str__(self):
        ret = []
        ret.append('PC: %04X AF: %04X BC: %04X DE: %04X HL: %04X IX: %04X IY: %04X SP: %04X' %\
                    (self.PC, self.AF, self.BC, self.DE, self.HL, self.IX, self.IY, self.SP)
                  )
        ret.append('I: %02X R: %02X IFF1: %s IFF2: %s IM: %s T: %d' % (
                    self.I, self.R, self.IFF1, self.IFF2, self.IM, self.itotal
                  ))
        ret.append('F: %s' % self.flags_as_str())
        return '\n'.join(ret)
    
    # ===================
    # = data access =
    # ===================
    # ======
    # = PC =
    # ======
    def _gPC(self):
        return self.cpu.contents.pc.w
    def _sPC(self, val):
        self.cpu.contents.pc.w = val
    PC = property(fget=_gPC, fset=_sPC)
    
    # ======
    # = SP =
    # ======
    def _gSP(self):
        return self.cpu.contents.sp.w
    def _sSP(self, val):
        self.cpu.contents.sp.w = val
    SP = property(fget=_gSP, fset=_sSP)
    
    # ======
    # = AF =
    # ======
    def _gAF(self):
        return self.cpu.contents.af.w
    def _sAF(self, val):
        self.cpu.contents.af.w = val
    AF = property(fget=_gAF, fset=_sAF)
    
    def _gA(self):
        return self._get_hi_reg(regAF)
    def _sA(self, val):
        self.cpu.contents.af.b.h = val
    A = property(fget=_gA, fset=_sA)
    
    def _gF(self):
        return self.cpu.contents.af.b.l
    def _sF(self, val):
        self.cpu.contents.af.b.l = val
    F = property(fget=_gF, fset=_sF)
    
    # ======
    # = BC =
    # ======
    def _gBC(self):
        return self.cpu.contents.bc.w
    def _sBC(self, val):
        self.cpu.contents.bc.w = val
    BC = property(fget=_gBC, fset=_sBC)
    
    def _gB(self):
        return self.cpu.contents.bc.b.h
    def _sB(self, val):
        self.cpu.contents.bc.b.h = val
    B = property(fget=_gB, fset=_sB)
    
    def _gC(self):
        return self.cpu.contents.bc.b.l
    def _sC(self, val):
        self.cpu.contents.bc.b.l = val
    C = property(fget=_gC, fset=_sC)
    
    # ======
    # = DE =
    # ======
    def _gDE(self):
        return self.cpu.contents.de.w
    def _sDE(self, val):
        self.cpu.contents.de.w = val
    DE = property(fget=_gDE, fset=_sDE)
    
    def _gD(self):
        return self.cpu.contents.de.b.h
    def _sD(self, val):
        self.cpu.contents.de.b.h = val
    D = property(fget=_gD, fset=_sD)
    
    def _gE(self):
        return self.cpu.contents.de.b.l
    def _sE(self, val):
        self.cpu.contents.de.b.l = val
    E = property(fget=_gE, fset=_sE)
    
    # ======
    # = HL =
    # ======
    def _gHL(self):
        return self.cpu.contents.hl.w
    def _sHL(self, val):
        self.cpu.contents.hl.w = val
    HL = property(fget=_gHL, fset=_sHL)
    
    def _gH(self):
        return self.cpu.contents.hl.b.h
    def _sH(self, val):
        self.cpu.contents.hl.b.h = val
    H = property(fget=_gH, fset=_sH)
    
    def _gL(self):
        return self.cpu.contents.hl.b.l
    def _sL(self, val):
        self.cpu.contents.hl.b.l = val
    L = property(fget=_gL, fset=_sL)
    
    # ======
    # = AF1 =
    # ======
    def _gAF1(self):
        return self.cpu.contents.af_.w
    def _sAF1(self, val):
        self.cpu.contents.af_.w = val
    AF1 = property(fget=_gAF1, fset=_sAF1)
    
    # ======
    # = BC1 =
    # ======
    def _gBC1(self):
        return self.cpu.contents.bc_.w
    def _sBC1(self, val):
        self.cpu.contents.bc_.w = val
    BC1 = property(fget=_gBC1, fset=_sBC1)
    
    # ======
    # = DE1 =
    # ======
    def _gDE1(self):
        return self.cpu.contents.de_.w
    def _sDE1(self, val):
        self.cpu.contents.de_.w = val
    DE1 = property(fget=_gDE1, fset=_sDE1)
    
    # ======
    # = HL1 =
    # ======
    def _gHL1(self):
        return self.cpu.contents.hl_.w
    def _sHL1(self, val):
        self.cpu.contents.hl_.w = val
    HL1 = property(fget=_gHL1, fset=_sHL1)
    
    # ======
    # = IX =
    # ======
    def _gIX(self):
        return self.cpu.contents.ix.w
    def _sIX(self, val):
        self.cpu.contents.ix.w = val
    IX = property(fget=_gIX, fset=_sIX)
    
    # ======
    # = IY =
    # ======
    def _gIY(self):
        return self.cpu.contents.iy.w
    def _sIY(self, val):
        self.cpu.contents.iy.w = val
    IY = property(fget=_gIY, fset=_sIY)
    
    # ======
    # = I =
    # ======
    def _gI(self):
        return self.cpu.contents.i
    def _sI(self, val):
        self.cpu.contents.i = val
    I = property(fget=_gI, fset=_sI)
    
    # ======
    # = R =
    # ======
    def _gR(self):
        return self.cpu.contents.r
    def _sR(self, val):
        self.cpu.contents.r = val
    R = property(fget=_gR, fset=_sR)
    
    # ======
    # = IFF =
    # ======
    def _gIFF1(self):
        return self.cpu.contents.iff1 !=0
    def _sIFF1(self, val):
        self.cpu.contents.iff1 = val
    IFF1 = property(fget=_gIFF1, fset=_sIFF1)
    def _gIFF2(self):
        return self.cpu.contents.iff2 !=0
    def _sIFF2(self, val):
        self.cpu.contents.iff2 = val
    IFF2 = property(fget=_gIFF2, fset=_sIFF2)
    
    # ======
    # = IM =
    # ======
    def _gIM(self):
        return self.cpu.contents.im
    def _sIM(self, val):
        self.cpu.contents.im = val
    IM = property(fget=_gIM, fset=_sIM)