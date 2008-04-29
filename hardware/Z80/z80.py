"""
Z80 CPU core
"""

import sys
from ctypes import cast, c_void_p, pointer

from hardware.cpu import (
    CPU, CPUTrapInvalidOP,
    _add_cycles,
    cpu_inc_t,
    cpu_reset,
    cpu_irq,
    cpu_nmi,
)
from z80core import *
from z80core import _Z80
from dasm import *

__all__ = ('Z80',)

class Z80(CPU):
    def __init__(self, break_afer, mem, io=None):
        self._cpu = Z80State()
        super(Z80, self).__init__(break_afer, mem, io)
        
        self.read = self.mem.read
        self.write = self.mem.write
        
        self.io_read = self.io.read
        self.io_write = self.io.write

        self._cpu.read = cast(READ(self.read), c_void_p)
        self._cpu.read_op = cast(READ(self.read), c_void_p)
        self._cpu.write = cast(WRITE(self.write), c_void_p)
        
        self._cpu.io_read = cast(READ(self.io_read), c_void_p)
        self._cpu.io_write = cast(WRITE(self.io_write), c_void_p)

    def flags_as_str(self, val=None):
        if val is None:
            val = self.F
        ret = ['-'] * 8
        ret[7] = 'S' if val & S_FLAG else '-'
        ret[6] = 'Z' if val & Z_FLAG else '-'
        ret[5] = '5' if val & F5_FLAG else '-'
        ret[4] = 'H' if val & H_FLAG else '-'
        ret[3] = '3' if val & F3_FLAG else '-'
        ret[2] = 'V' if val & V_FLAG else '-'
        ret[1] = 'N' if val & N_FLAG else '-'
        ret[0] = 'C' if val & C_FLAG else '-'
        ret.reverse()
        return ''.join(ret)
        
    def reset(self):
        self._cpu.Trap = 0
        _Z80.ResetZ80(self._cpu)
    
    def run(self, cycles=0):
        left = _Z80.ExecZ80(self._cpu, cycles)

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
                    self.I, self.R, self.IFF1, self.IFF2, self.IM, self.abs_T
                  ))
        ret.append('F: %s' % self.flags_as_str())
        return '\n'.join(ret)

    # ===================
    # = data access =
    # ===================

    # ==========
    # = icount =
    # ==========
    def _gIC(self):
        return self._cpu.ITotal
    icount = property(fget=_gIC)

    # ======
    # = PC =
    # ======
    def _gPC(self):
        return self._cpu.PC.W
    def _sPC(self, val):
        self._cpu.PC.W = val
    PC = property(fget=_gPC, fset=_sPC)

    # ======
    # = SP =
    # ======
    def _gSP(self):
        return self._cpu.SP.W
    def _sSP(self, val):
        self._cpu.SP.W = val
    SP = property(fget=_gSP, fset=_sSP)

    # ======
    # = AF =
    # ======
    def _gAF(self):
        return self._cpu.AF.W
    def _sAF(self, val):
        self._cpu.AF.W = val
    AF = property(fget=_gAF, fset=_sAF)
    def _gA(self):
        return self._cpu.AF.B.h
    def _sA(self, val):
        self._cpu.AF.B.h = val
    A = property(fget=_gA, fset=_sA)
    def _gF(self):
        return self._cpu.AF.B.l
    def _sF(self, val):
        self._cpu.AF.B.h = val
    F = property(fget=_gF, fset=_sF)
    
    # ======
    # = BC =
    # ======
    def _gBC(self):
        return self._cpu.BC.W
    def _sBC(self, val):
        self._cpu.BC.W = val
    BC = property(fget=_gBC, fset=_sBC)
    def _gB(self):
        return self._cpu.BC.B.h
    def _sB(self, val):
        self._cpu.BC.B.h = val
    B = property(fget=_gB, fset=_sB)
    def _gC(self):
        return self._cpu.BC.B.l
    def _sC(self, val):
        self._cpu.BC.B.h = val
    C = property(fget=_gC, fset=_sC)

    # ======
    # = DE =
    # ======
    def _gDE(self):
        return self._cpu.DE.W
    def _sDE(self, val):
        self._cpu.DE.W = val
    DE = property(fget=_gDE, fset=_sDE)
    def _gD(self):
        return self._cpu.DE.B.h
    def _sD(self, val):
        self._cpu.DE.B.h = val
    D = property(fget=_gD, fset=_sD)
    def _gE(self):
        return self._cpu.DE.B.l
    def _sE(self, val):
        self._cpu.DE.B.h = val
    E = property(fget=_gE, fset=_sE)

    # ======
    # = HL =
    # ======
    def _gHL(self):
        return self._cpu.HL.W
    def _sHL(self, val):
        self._cpu.HL.W = val
    HL = property(fget=_gHL, fset=_sHL)
    def _gH(self):
        return self._cpu.HL.B.h
    def _sH(self, val):
        self._cpu.HL.B.h = val
    H = property(fget=_gH, fset=_sH)
    def _gL(self):
        return self._cpu.HL.B.l
    def _sL(self, val):
        self._cpu.HL.B.h = val
    L = property(fget=_gL, fset=_sL)

    # ======
    # = AF1 =
    # ======
    def _gAF1(self):
        return self._cpu.AF1.W
    def _sAF1(self, val):
        self._cpu.AF1.W = val
    AF1 = property(fget=_gAF1, fset=_sAF1)
    
    # ======
    # = BC1 =
    # ======
    def _gBC1(self):
        return self._cpu.BC1.W
    def _sBC1(self, val):
        self._cpu.BC1.W = val
    BC1 = property(fget=_gBC1, fset=_sBC1)

    # ======
    # = DE1 =
    # ======
    def _gDE1(self):
        return self._cpu.DE1.W
    def _sDE1(self, val):
        self._cpu.DE1.W = val
    DE1 = property(fget=_gDE1, fset=_sDE1)

    # ======
    # = HL1 =
    # ======
    def _gHL1(self):
        return self._cpu.HL1.W
    def _sHL1(self, val):
        self._cpu.HL1.W = val
    HL1 = property(fget=_gHL1, fset=_sHL1)

    # ======
    # = IX =
    # ======
    def _gIX(self):
        return self._cpu.IX.W
    def _sIX(self, val):
        self._cpu.IX.W = val
    IX = property(fget=_gIX, fset=_sIX)

    # ======
    # = IY =
    # ======
    def _gIY(self):
        return self._cpu.IY.W
    def _sIY(self, val):
        self._cpu.IY.W = val
    IY = property(fget=_gIY, fset=_sIY)

    # ======
    # = I =
    # ======
    def _gI(self):
        return self._cpu.I
    def _sI(self, val):
        self._cpu.I = val
    I = property(fget=_gI, fset=_sI)

    # ======
    # = R =
    # ======
    def _gR(self):
        return self._cpu.R
    def _sR(self, val):
        self._cpu.R = val
    R = property(fget=_gR, fset=_sR)

    # ======
    # = IFF =
    # ======
    def _gIFF(self):
        return self._cpu.IFF
    def _sIFF(self, val):
        self._cpu.IFF = val
    IFF1 = property(fget=_gIFF, fset=_sIFF)
    IFF2 = property(fget=_gIFF, fset=_sIFF)

    # ======
    # = IM =
    # ======
    # TODO CHECK!!!!
    def _gIM(self):
        return self._cpu.I
    def _sIM(self, val):
        self._cpu.I = val
    IM = property(fget=_gR, fset=_sR)