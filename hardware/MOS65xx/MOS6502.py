# stdlib
import random

# lib
from pydispatch.dispatcher import send

# app
from hardware.cpu import (
    CPU,
    cpu_inc_t,
    cpu_reset,
    cpu_irq,
    cpu_nmi,
)
from hardware.flags import Flags

__all__ = ('MOS6502Flags', 'MOS6502',)

class MOS6502Flags(Flags):
    S  = 0x80 # 7
    V  = 0x40 # 6
    F5 = 0x20 # 5
    B  = 0x10 # 4
    D  = 0x08 # 3
    I  = 0x04 # 2
    Z  = 0x02 # 1
    C  = 0x01 # 0
    
    def __init__(self, val = None):
        self.s  = False
        self.v  = False
        self.f5 = False
        self.b  = False
        self.d  = False
        self.i  = False
        self.z  = False
        self.c  = False
        
        if val is None:
            super(MOS6502Flags, self).__init__(random.randint(0, 0xFF))
        else:
            super(MOS6502Flags, self).__init__(val)
    
    def set(self, val):
        """ set flags """
        
        self.s  = bool(val & MOS6502Flags.S)
        self.v  = bool(val & MOS6502Flags.V)
        self.f5 = bool(val & MOS6502Flags.F5)
        self.b  = bool(val & MOS6502Flags.B)
        self.d  = bool(val & MOS6502Flags.D)
        self.i  = bool(val & MOS6502Flags.I)
        self.z  = bool(val & MOS6502Flags.Z)
        self.c  = bool(val & MOS6502Flags.C)
    
    def mset(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def get(self):
        return (
              (MOS6502Flags.S if self.s else 0)
            | (MOS6502Flags.V if self.v else 0)
            | (MOS6502Flags.F5 if self.f5 else 0)
            | (MOS6502Flags.B if self.b else 0)
            | (MOS6502Flags.D if self.d else 0)
            | (MOS6502Flags.I if self.i else 0)
            | (MOS6502Flags.Z if self.z else 0)
            | (MOS6502Flags.C if self.c else 0)
        )
    
    def __str__(self):
        ret = ['-'] * 8
        ret[7] = 'S' if self.s else '-'
        ret[6] = 'V' if self.v else '-'
        ret[5] = 'U' if self.f5 else '-'
        ret[4] = 'B' if self.b else '-'
        ret[3] = 'D' if self.d else '-'
        ret[2] = 'I' if self.i else '-'
        ret[1] = 'Z' if self.z else '-'
        ret[0] = 'C' if self.c else '-'
        ret.reverse()
        return ''.join(ret)

BCD_TAB = (
    tuple([(((t >> 4) * 10) + (t & 0x0f)) & 0xFFFF for t in range(0x100)]),
    tuple([((((t % 100) / 10) << 4) | (t % 10)) & 0xFFFF for t in range(0x100)])
)

SVZ_TAB = SZ_TAB = None

class MOS6502(CPU):
    RESET_VECTOR = 0xFFFC
    
    def __init__(self, break_afer, mem, io=None):
        self.A = random.randint(0, 0xFF)
        self.X = random.randint(0, 0xFF)
        self.Y = random.randint(0, 0xFF)
        
        self.S = random.randint(0, 0xFF)
        self.P = MOS6502Flags()
        
        self.PC = random.randint(0, 0xFFFF)
        
        super(MOS6502, self).__init__(break_afer, mem, io)
        
        if SVZ_TAB is None or SZ_TAB is None:
            self.init_tabs()
    
    def init_tabs(self):
        global SVZ_TAB, SZ_TAB
        
        SVZ_TAB = [None] * 0x100
        SZ_TAB = [None] * 0x100
        
        for n in range(0x100):
            s = self.mem.as_signed(n)
            
            SVZ_TAB[n] = {
                's': n & 0x80,
                'v': (s > 127) or (s < -128),
                'z': not n
            }
            
            SZ_TAB[n] = {
                's': n & 0x80,
                'z': not n
            }
        
        SVZ_TAB = tuple(SVZ_TAB)
        SZ_TAB = tuple(SZ_TAB)
    
    def __str__(self):
        return 'CPU MOS 6502 (PC: %04X A: %02X X: %02X Y: %02X S: %02X P: %s)' % \
                            (self.PC, self.A, self.X, self.Y, self.S, self.P)
    
    def _read_op(self):
        ret = self.mem.read(self.PC)
        self.PC = (self.PC + 1) & 0xFFFF
        return ret
    
    _read_immediate = _read_op
    
    def read_word(self, adr):
        return self.mem.read(adr) + (self.mem.read(adr + 1) * 256)
    
    def write_word(self, adr, val):
        self.mem.write(adr, val & 0xFF)
        self.mem.write(adr + 1, (val >> 8) & 0xFF)
    
    def _read_param(self):
        ret = self.mem.read(self.PC)
        self.PC = (self.PC + 1) & 0xFFFF
        return ret
    
    def _read_absolute(self):
        adr = self.read_word(self.PC)
        self.PC = (self.PC + 2) & 0xFFFF
        return self.mem.read(adr)
    
    def _read_zero_page(self):
        adr = self.mem.read(self.PC)
        self.PC = (self.PC + 1) & 0xFFFF
        return self.mem.read(adr)
    
    def not_same_page(self, adr1, adr2):
        return ((adr1) ^ (adr2)) & 0xff00
    
    def _inc_adr(self, adr, inc):
        """ add inc to addr and check if page boundary is crossed and dispatch cpu_inc_t 1 if true """
        if ((adr & 0xFF) + inc) > 0xFF:
            send(signal=cpu_inc_t, sender=self.__class__, instance=self, num=1)
        return adr + inc

    def _read_indexed_x(self):
        adr = self._inc_adr(self.read_word(self.PC), self.X)
        self.PC = (self.PC + 2) & 0xFFFF
        return self.mem.read(adr)

    def _read_indexed_y(self):
        adr = self._inc_adr(self.read_word(self.PC), self.Y)
        self.PC = (self.PC + 2) & 0xFFFF
        return self.mem.read(adr)

    def _read_zero_page_indexed_x(self):
        """ shortcut == _read_zero_page_indexed """
        adr = self.mem.read(self.PC + self.X)
        self.PC = (self.PC + 1) & 0xFFFF
        return self.mem.read(adr)

    def _read_zero_page_indexed_y(self):
        """ shortcut == _read_zero_page_indexed """
        adr = self.mem.read(self.PC + self.Y)
        self.PC = (self.PC + 1) & 0xFFFF
        return self.mem.read(adr)

    def _read_indirect(self):
        adr = self.read_word(self.PC)
        self.PC = (self.PC + 2) & 0xFFFF
        return self.read_word(adr)
    
    def _read_pre_indirect(self):
        adr = self.mem.read(self.PC)
        self.PC = (self.PC + 1) & 0xFFFF
        adr2 = self.read_word((adr + self.X) & 0xFF)
        return self.mem.read(adr2)
    
    def _read_post_indirect(self):
        adr = self.mem.read(self.PC)
        self.PC = (self.PC + 1) & 0xFFFF
        adr2 = self.read_word(adr) + self.Y
        return self.mem.read(adr2)
    
    def _read_relative(self):
        off = self.mem.as_signed(self.mem.read(self.PC))
        self.PC = (self.PC + 1) & 0xFFFF
        return (self.PC + off) & 0xFFFF
    
    def reset(self):
        self.A = 0x00
        self.X = 0x00
        self.Y = 0x00
        
        self.S = 0xFF
        self.P.set(MOS6502Flags.F5)
        
        self.PC = self.read_word(MOS6502.RESET_VECTOR)
        
        # tstates
        self.T = 0
        self.abs_T = 0
    
    # OPCODES
    def _opcodes(self):
        """
            0 cycles
            1 len
            2 handler
            3 address handler
            4 mnemo
        """
        ret = super(MOS6502, self)._opcodes()
        
        # register instructions
        ret[0x60] = (4, 3, self.adc, self._read_absolute, 'ADC %04X')
        ret[0x65] = (3, 2, self.adc, self._read_zero_page, 'ADC %02X')
        ret[0x69] = (2, 2, self.adc, self._read_immediate, 'ADC #%02X')
        ret[0x70] = (4, 3, self.adc, self._read_indexed_x, 'ADC %04X,X')
        ret[0x75] = (4, 2, self.adc, self._read_zero_page_indexed_x, 'ADC %02X,X')
        ret[0x79] = (4, 3, self.adc, self._read_indexed_y, 'ADC %04X,Y')
        
        return tuple(ret)
    
    def adc(self, read):
        val = read()
        olda = self.A
        if self.P.d:
            # decimal mode
            s = BCD_TAB[0][self.A] + BCD_TAB[0][val] + (1 if self.P.c else 0)
            self.P.c = s > 99
            self.A = BCD_TAB[1][s & 0xff]
            self.P.mset(**SZ_TAB[self.A])
            self.P.v = ((olda ^ self.A) & 0x80) and ((self.A ^ val) & 0x80)
        else:
            self.A += val + (1 if self.P.c else 0)
            self.P.c = self.A > 0xFF
            self.A &= 0xFF
            self.P.mset(**SVZ_TAB[self.A])