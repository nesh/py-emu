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
from ld8 import *

__all__ = ('Z80Flags', 'Z80',)

class Z80(CPU, Z80_8BitLoad):
    IM0, IM1, IM0_1 = range(0, 3)
    
    def __init__(self, break_afer, mem, io=None):
        self.F = Z80Flags()
        self.last_prefix = None
        
        super(Z80, self).__init__(break_afer, mem, io)
        # shortcuts
        self.read = self.mem.read
        self.write = self.mem.write
        
        # additional tables
        self._cb_op = {}
        self._xx_op = {}
        self._xxcb_op = {}
        self._ed_op = {}
        
        # reg setup
        self.reset()
        
        # init opcodes
        self._op[0xCB] = self.cb
        self._xx_op[0xCB] = self.xxcb
        self._op[0xED] = self.ed
        self._op[0xDD] = self.dd
        self._op[0xFD] = self.fd
        # other
        self.register_opcodes()
    
    def xxcb(self, reg):
        offset = as_signed(self.read_op())
        op = self.read_op()
        t = CYCLES_XXCB[op]
        self._xxcb_op[op](reg, offset)
        self.abs_T += t
        self.T -= t
        

    def dd(self):
        op = self.read_op()
        t = CYCLES_XX[op]
        self._xx_op[op]('IX')
        self.abs_T += t
        self.T -= t

    def fd(self):
        op = self.read_op()
        t = CYCLES_XX[op]
        self._xx_op[op]('IY')
        self.abs_T += t
        self.T -= t

    def ed(self):
        op = self.read_op()
        t = CYCLES_ED[op]
        self._ed_op[op]()
        self.abs_T += t
        self.T -= t

    def cb(self):
        op = self.read_op()
        t = CYCLES_CB[op]
        self._cb_op[op]()
        self.abs_T += t
        self.T -= t

    def disassemble(self, address, instruction_count=1, dump_adr=True, dump_hex=True, bytes=1):
        ret = []
        while bytes > 0:
            s, ln = dasm(address, self.read)
            hx = []
            for o in range(ln):
                hx.append('%02X' % self.read(address + o))
            ret.append('%04X %s: %s' % (address, ''.join(hx), s))
            bytes -= ln
        return '\n'.join(ret)
    
    def run(self, cycles=0):
        # run until we spend all cycles
        # TODO IRQs
        self.T += cycles
        
        while self.T >= 0:
            old_pc = self.PC
            op = self.read_op()
            t = CYCLES[op]
            
            try:
                self._op[op]()
            except KeyError:
                raise CPUTrapInvalidOP('Invalid opcode %02X: %s' % (op, self.disassemble(old_pc)))
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
    
    def __str__(self):
        ret = []
        ret.append('PC: %04X AF: %04X BC: %04X DE: %04X HL: %04X IX: %04X IY: %04X SP: %04X' %\
                    (self.PC, self.AF, self.BC, self.DE, self.HL, self.IX, self.IY, self.SP)
                  )
        ret.append('I: %02X R: %02X IFF1: %s IFF2: %s IM: %s T: %d' % (
                    self.I, self.R, self.IFF1, self.IFF2, self.IM, self.abs_T
                  ))
        ret.append('F: %s' % self.F)
        return '\n'.join(ret)

    def reset(self):
        self.last_prefix = None
        
        self.IM = Z80.IM0
        self.HALT = False
        
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
