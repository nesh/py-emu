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

from tables import *
from dasm import *
from flags import *

__all__ = ('Z80Flags', 'Z80',)

class Z80(CPU, DasmMixin):
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
        #self._create_8b_load()
        #self.register_opcodes()
    
    def disassemble(self, address, instruction_count=1, dump_adr=True, dump_hex=True):
        s, ln = self.dasm(address)
        hx = []
        for o in range(ln):
            hx.append('%02X' % self.read(address + o))
        return '%04X %s: %s' % (address, ''.join(hx), s)
    
    def run_one(self):
        rdop = self.read_op # shortcut
        
        old_pc = self.PC
        byte = rdop()

        t = CYCLES[byte]
        self.abs_T += t
        self.T -= t
        
        # shortcuts
        rd = self.read
        wr = self.write
        x, y, z, p, q = break_opcode(byte)

        if x == 0:
            if z == 6:
                n = rdop()
                setattr(self, OP_R_A[y], n)
                return
        if x == 1:
            if (z == 6) and (y == 6):
                pass
                # ret.append('HALT') # special case, replaces LD (HL), (HL)
            else:
                setattr(self, OP_R_A[y], getattr(self, OP_R_A[z]))
                return

        raise CPUTrapInvalidOP('Invalid opcode %02X: %s' % (byte, self.disassemble(old_pc)))
        
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
    
    def register_opcodes(self):
        pass
