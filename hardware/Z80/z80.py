"""
Z80 CPU core
"""

# stdlib
import random

# lib
#from pydispatch.dispatcher import send

# app
from hardware.cpu import (
    CPU, CPUTrapInvalidOP,
    _add_cycles,
    cpu_inc_t,
    cpu_reset,
    cpu_irq,
    cpu_nmi,
)
from hardware.flags import Flags

from tables import *

__all__ = ('Z80Flags', 'Z80',)

class Z80Flags(Flags):
    S  = S_FLAG # 7
    Z  = Z_FLAG # 6
    F5 = F5_FLAG # 5
    H  = H_FLAG # 4
    F3  = F3_FLAG # 3
    V  = V_FLAG # 2
    N  = N_FLAG # 1
    C  = C_FLAG # 0
    
    def __init__(self, val=None):
        self.s = False
        self.z = False
        self.f5 = False
        self.h = False
        self.f3 = False
        self.v = False
        self.n = False
        self.c = False
        
        if val is None:
            val = random.randint(0, 0xFF)
        super(Z80Flags, self).__init__(val)
    
    def mset(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def set(self, val):
        self.s = bool(val & S_FLAG)
        self.z = bool(val & Z_FLAG)
        self.f5 = bool(val & F5_FLAG)
        self.h = bool(val & H_FLAG)
        self.f3 = bool(val & F3_FLAG)
        self.v = bool(val & V_FLAG)
        self.n = bool(val & N_FLAG)
        self.c = bool(val & C_FLAG)
    
    def get(self):
        return (
            (S_FLAG if self.s else 0)
            | (Z_FLAG if self.z else 0)
            | (F5_FLAG if self.f5 else 0)
            | (H_FLAG if self.h else 0)
            | (F3_FLAG if self.f3 else 0)
            | (V_FLAG if self.v else 0)
            | (N_FLAG if self.n else 0)
            | (C_FLAG if self.c else 0)
            )
    
    byte = property(fget=get, fset=set)
    
    def __str__(self):
        ret = ['-'] * 8
        ret[7] = 'S' if self.s else '-'
        ret[6] = 'Z' if self.z else '-'
        ret[5] = '5' if self.f5 else '-'
        ret[4] = 'H' if self.h else '-'
        ret[3] = '3' if self.f3 else '-'
        ret[2] = 'V' if self.v else '-'
        ret[1] = 'N' if self.n else '-'
        ret[0] = 'C' if self.c else '-'
        ret.reverse()
        return ''.join(ret)

class Z80JumpsMixin(object):
    # ======
    # = JR =
    # ======
    def _jr(self, cond, op):
        if not cond: return
        self.T -= 5
        self.abs_T += 5
        self.PC = (self.PC + self.mem.as_signed(op)) & 0xFFFF
    
    def jr(self, adr, op):
        self.PC = (self.PC + self.mem.as_signed(op)) & 0xFFFF
    
    def jr_nz(self, adr, op):
        self._jr(not self.F.z, op)
    def jr_z(self, adr, op):
        self._jr(self.F.z, op)
    
    def jr_nc(self, adr, op):
        self._jr(not self.F.c, op)
    def jr_c(self, adr, op):
        self._jr(self.F.c, op)
    
    # ======
    # = JP =
    # ======
    def _jp(self, adr, op):
        self.PC = op
    
    def _jp(self, cond, op):
        if not cond: return
        self.PC = op
    
    def jp_nz(self, adr, op):
        self._jp(not self.F.z, op)
    def jp_z(self, adr, op):
        self._jp(self.F.z, op)
    
    def jp_nc(self, adr, op):
        self._jp(not self.F.c, op)
    def jp_c(self, adr, op):
        self._jp(self.F.c, op)
    
    # ========
    # = CALL =
    # ========
    def _call(self, cond, op):
        if not cond: return
        self.T -= 7
        self.abs_T += 7
        self.push(self.PC)
        self.PC = op
    
    def call(self, adr, op):
        self.push(self.PC)
        self.PC = op
    
    # =======
    # = RST =
    # =======
    def _rst(self, op):
        self.push(self.PC)
        self.PC = op
    
    def rst00(self, adr, op):
        self._rst(0x0000)
    def rst08(self, adr, op):
        self._rst(0x0008)
    def rst10(self, adr, op):
        self._rst(0x0010)
    def rst18(self, adr, op):
        self._rst(0x0018)
    def rst20(self, adr, op):
        self._rst(0x0020)
    def rst28(self, adr, op):
        self._rst(0x0028)
    def rst30(self, adr, op):
        self._rst(0x0030)
    def rst38(self, adr, op):
        self._rst(0x0038)
    
    
    # ========
    # = RET  =
    # ========
    def _ret(self, cond):
        if not cond: return
        self.T -= 6
        self.abs_T += 6
        self.PC = self.pop()
    
    def ret(self, adr, op):
        self.PC = self.pop()


class Z80OPTablesMixin(object):
    def add_cb_op(self, opcode, handler, adr_mode, override=False):
        self._add_op(self, self._cb_op, self._cb_cycles, opcode, handler, adr_mode, override)
    
    def _cb_cycles(self, op):
        return CYCLES_CB[op]
    
    def cb_prefix(self, adr, op):
        op = self.read_op()
        t, handler, read_op = self._cb_op[op]
        handler(*read_op())
        self.abs_T += t
        self.T -= t


# R_A = 0x07
# R_B = 0x00
# R_C = 0x01
# R_D = 0x02
# R_E = 0x03
# R_H = 0x04
# R_L = 0x05

REGS_SRC = {
    0x07: 'A',
    0x00: 'B',
    0x01: 'C',
    0x02: 'D',
    0x03: 'E',
    0x04: 'H',
    0x05: 'L',
}

REGS_DST = {
    0x07 << 3: 'A',
    0x00 << 3: 'B',
    0x01 << 3: 'C',
    0x02 << 3: 'D',
    0x03 << 3: 'E',
    0x04 << 3: 'H',
    0x05 << 3: 'L',
}

class Z80_8BitLoad(object):
    def ld_a_a(self):
        pass
    
    def ld_a_b(self):
        self.A = self.B
    
    def ld_a_c(self):
        self.A = self.C
    
    def ld_a_d(self):
        self.A = self.D

    def ld_a_e(self):
        self.A = self.E

    def ld_a_h(self):
        self.A = self.H

    def ld_a_l(self):
        self.A = self.L

    def ld_b_a(self):
        self.B = self.A

    def ld_b_b(self):
        pass

    def ld_b_c(self):
        self.B = self.C

    def ld_b_d(self):
        self.B = self.D

    def ld_b_e(self):
        self.B = self.E

    def ld_b_h(self):
        self.B = self.H

    def ld_b_l(self):
        self.B = self.L

    def ld_c_a(self):
        self.C = self.A

    def ld_c_b(self):
        self.C = self.B

    def ld_c_c(self):
        pass

    def ld_c_d(self):
        self.C = self.D

    def ld_c_e(self):
        self.C = self.E

    def ld_c_h(self):
        self.C = self.H

    def ld_c_l(self):
        self.C = self.L

    def ld_d_a(self):
        self.D = self.A

    def ld_d_b(self):
        self.D = self.B

    def ld_d_c(self):
        self.D = self.C

    def ld_d_d(self):
        pass

    def ld_d_e(self):
        self.D = self.E

    def ld_d_h(self):
        self.D = self.H

    def ld_d_l(self):
        self.D = self.L

    def ld_e_a(self):
        self.E = self.A

    def ld_e_b(self):
        self.E = self.B

    def ld_e_c(self):
        self.E = self.C

    def ld_e_d(self):
        self.E = self.D

    def ld_e_e(self):
        pass

    def ld_e_h(self):
        self.E = self.H

    def ld_e_l(self):
        self.E = self.L

    def ld_h_a(self):
        self.H = self.A

    def ld_h_b(self):
        self.H = self.B

    def ld_h_c(self):
        self.H = self.C

    def ld_h_d(self):
        self.H = self.D

    def ld_h_e(self):
        self.H = self.E

    def ld_h_h(self):
        pass

    def ld_h_l(self):
        self.H = self.L

    def ld_l_a(self):
        self.L = self.A

    def ld_l_b(self):
        self.L = self.B

    def ld_l_c(self):
        self.L = self.C

    def ld_l_d(self):
        self.L = self.D

    def ld_l_e(self):
        self.L = self.E

    def ld_l_h(self):
        self.L = self.H

    def ld_l_l(self):
        pass

    def _create_8b_load(self):
        # A
        self._op[LD_A_A] = self.ld_a_a
        self._op[LD_A_B] = self.ld_a_b
        self._op[LD_A_C] = self.ld_a_c
        self._op[LD_A_D] = self.ld_a_d
        self._op[LD_A_E] = self.ld_a_e
        self._op[LD_A_H] = self.ld_a_h
        self._op[LD_A_L] = self.ld_a_l
        # B
        self._op[LD_B_A] = self.ld_b_a
        self._op[LD_B_B] = self.ld_b_b
        self._op[LD_B_C] = self.ld_b_c
        self._op[LD_B_D] = self.ld_b_d
        self._op[LD_B_E] = self.ld_b_e
        self._op[LD_B_H] = self.ld_b_h
        self._op[LD_B_L] = self.ld_b_l
        # C
        self._op[LD_C_A] = self.ld_c_a
        self._op[LD_C_B] = self.ld_c_b
        self._op[LD_C_C] = self.ld_c_c
        self._op[LD_C_D] = self.ld_c_d
        self._op[LD_C_E] = self.ld_c_e
        self._op[LD_C_H] = self.ld_c_h
        self._op[LD_C_L] = self.ld_c_l
        # D
        self._op[LD_D_A] = self.ld_d_a
        self._op[LD_D_B] = self.ld_d_b
        self._op[LD_D_C] = self.ld_d_c
        self._op[LD_D_D] = self.ld_d_d
        self._op[LD_D_E] = self.ld_d_e
        self._op[LD_D_H] = self.ld_d_h
        self._op[LD_D_L] = self.ld_d_l
        # E
        self._op[LD_E_A] = self.ld_e_a
        self._op[LD_E_B] = self.ld_e_b
        self._op[LD_E_C] = self.ld_e_c
        self._op[LD_E_D] = self.ld_e_d
        self._op[LD_E_E] = self.ld_e_e
        self._op[LD_E_H] = self.ld_e_h
        self._op[LD_E_L] = self.ld_e_l
        # H
        self._op[LD_H_A] = self.ld_h_a
        self._op[LD_H_B] = self.ld_h_b
        self._op[LD_H_C] = self.ld_h_c
        self._op[LD_H_D] = self.ld_h_d
        self._op[LD_H_E] = self.ld_h_e
        self._op[LD_H_H] = self.ld_h_h
        self._op[LD_H_L] = self.ld_h_l
        # L
        self._op[LD_L_A] = self.ld_l_a
        self._op[LD_L_B] = self.ld_l_b
        self._op[LD_L_C] = self.ld_l_c
        self._op[LD_L_D] = self.ld_l_d
        self._op[LD_L_E] = self.ld_l_e
        self._op[LD_L_H] = self.ld_l_h
        self._op[LD_L_L] = self.ld_l_l
    


class Z80(CPU, Z80JumpsMixin, Z80_8BitLoad):
    def __init__(self, break_afer, mem, io=None):
        self.F = Z80Flags()
        
        super(Z80, self).__init__(break_afer, mem, io)
        # shortcuts
        self.read = self.mem.read
        self.write = self.mem.write
        
        # additional tables
        self._cb_op = {}
        
        # reg setup
        self.reset()
        
        # init opcodes
        self._create_8b_load()
        self.register_opcodes()
    
    # =================
    # = mem I/O stuff =
    # =================
    def read16(self, adr):
        r = self.read # shortcut
        return r(adr) + (r(adr + 1) * 256)
    
    def read16_tuple(self, adr):
        """return touple lo, hi"""
        r = self.read # shortcut
        return r(adr), (r(adr + 1) * 256)
    
    def write16(self, adr, val):
        w = self.write # shortcut
        w(adr, val & 0xFF)
        w(adr + 1, (val >> 8) & 0xFF)
    
    def write16_tuple(self, adr, lo, hi):
        """write lo/hi"""
        w = self.write # shortcut
        w(adr, lo)
        w(adr + 1, hi)
    
    def push(self, val):
        w = self.write # shortcut
        sp = self.SP # shortcut
        sp = (sp - 1) & 0xFFFF
        w(sp, (val >> 8) & 0xFF) # hi
        sp = self.SP = (sp - 1) & 0xFFFF
        w(sp, val & 0xFF) # lo
    
    def pop(self):
        r = self.read # shortcut
        sp = self.SP # shortcut
        ret = r(sp) # lo
        sp = (sp + 1) & 0xFFFF
        ret += r(sp) * 256 # hi
        self.SP = (sp + 1) & 0xFFFF
        return ret
    
    def read_op(self):
        """read opcode"""
        ret = self.read(self.PC)
        self.PC = (self.PC + 1) & 0xFFFF
        return ret
    
    def read_op16(self):
        """read opcode 16b"""
        ret = self.read16(self.PC)
        self.PC = (self.PC + 2) & 0xFFFF
        return ret
    
    def run(self, cycles=0):
        # run until we spend all cycles
        # TODO IRQs
        self.T += cycles
        while self.T >= 0:
            op = self.current_op = self.read_op()
            #print '%02X' % op
            if op == 0xCB:
                op = self.current_op = self.read_op()
                try:
                    self._cb_op[op]()
                except KeyError:
                    raise CPUTrapInvalidOP('invalid op 0x%04X: 0xCB%02X' % (self.PC, op))
            else:
                try:
                    self._op[op]()
                except KeyError:
                    raise CPUTrapInvalidOP('invalid op 0x%04X: 0x%02X' % (self.PC, op))
                t = CYCLES[op]
            self.abs_T += t
            self.T -= t
    
    def reset(self):
        # FIXME real reset values!
        self.AF = 0xFFFF
        self.BC = 0x0000
        self.DE = 0x0000
        self.HL = 0x0000
        self.IX = 0x0000
        self.IY = 0x0000
        
        self.R = 0x00
        self.IFF1 = self.IFF2 = False
        self.I = 0x00
        
        
        self.PC = 0x0000
        self.SP = 0xFFFF
        
        # alt reg set
        self.AF1 = 0x0000
        self.BC1 = 0x0000
        self.DE1 = 0x0000
        self.HL1 = 0x0000
        
        # tstates
        self.T = 0
        self.abs_T = 0
    
    # 16b regs
    # TODO see which 16b regs are more used and use them like Ix regs
    #      instead of using them as two 8b regs -- HL?
    
    # AF
    def _gAF(self):
        return self.F.byte + (self.A * 256)
    def _sAF(self, val):
        self.F.byte = val & 0xFF
        self.A = (val >> 8) & 0xFF
    AF = property(fget=_gAF, fset=_sAF)
    
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
    
    def register_opcodes(self):
        pass
