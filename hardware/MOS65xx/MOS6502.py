"""
CPU core based on source from http://stella.sourceforge.net
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

__all__ = ('MOS6502Flags', 'MOS6502',)

BCD_TAB = (
    tuple([(((t >> 4) * 10) + (t & 0x0f)) & 0xFFFF for t in range(0x100)]),
    tuple([((((t % 100) / 10) << 4) | (t % 10)) & 0xFFFF \
           for t in range(0x100)])
)

def as_signed(val):
    """ convert value to the signed one """
    if val & 0x80:
        return -(256 - val)
    else:
        return val

SVZ_TAB = None
SZ_TAB = None

def init_tabs():
    global SVZ_TAB, SZ_TAB

    SVZ_TAB = [None] * 0x100
    SZ_TAB = [None] * 0x100

    for n in range(0x100):
        s = as_signed(n)

        SVZ_TAB[n] = {
            's': bool(n & 0x80),
            'v': (s > 127) or (s < -128),
            'z': not n
        }

        SZ_TAB[n] = {
            's': bool(n & 0x80),
            'z': not n
        }

    SVZ_TAB = tuple(SVZ_TAB)
    SZ_TAB = tuple(SZ_TAB)
init_tabs()
del init_tabs # cleanup

CYCLES = (
#   0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
    7, 6, 2, 8, 3, 3, 5, 5, 3, 2, 2, 2, 4, 4, 6, 6,  # 0
    2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 7, 7,  # 1
    6, 6, 2, 8, 3, 3, 5, 5, 4, 2, 2, 2, 4, 4, 6, 6,  # 2
    2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 7, 7,  # 3
    6, 6, 2, 8, 3, 3, 5, 5, 3, 2, 2, 2, 3, 4, 6, 6,  # 4
    2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 7, 7,  # 5
    6, 6, 2, 8, 3, 3, 5, 5, 4, 2, 2, 2, 5, 4, 6, 6,  # 6
    2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 7, 7,  # 7
    2, 6, 2, 6, 3, 3, 3, 3, 2, 2, 2, 2, 4, 4, 4, 4,  # 8
    2, 6, 2, 6, 4, 4, 4, 4, 2, 5, 2, 5, 5, 5, 5, 5,  # 9
    2, 6, 2, 6, 3, 3, 3, 4, 2, 2, 2, 2, 4, 4, 4, 4,  # a
    2, 5, 2, 5, 4, 4, 4, 4, 2, 4, 2, 4, 4, 4, 4, 4,  # b
    2, 6, 2, 8, 3, 3, 5, 5, 2, 2, 2, 2, 4, 4, 6, 6,  # c
    2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 7, 7,  # d
    2, 6, 2, 8, 3, 3, 5, 5, 2, 2, 2, 2, 4, 4, 6, 6,  # e
    2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 7, 7   # f
)

MNEMONICS = (
    "BRK",  "ORA",  "n/a",  "slo",  "nop",  "ORA",  "ASL",  "slo",    # 0x0?
    "PHP",  "ORA",  "ASLA", "anc",  "nop",  "ORA",  "ASL",  "slo",

    "BPL",  "ORA",  "n/a",  "slo",  "nop",  "ORA",  "ASL",  "slo",    # 0x1?
    "CLC",  "ORA",  "nop",  "slo",  "nop",  "ORA",  "ASL",  "slo",

    "JSR",  "AND",  "n/a",  "rla",  "BIT",  "AND",  "ROL",  "rla",    # 0x2?
    "PLP",  "AND",  "ROLA", "anc",  "BIT",  "AND",  "ROL",  "rla",

    "BMI",  "AND",  "n/a",  "rla",  "nop",  "AND",  "ROL",  "rla",    # 0x3?
    "SEC",  "AND",  "nop",  "rla",  "nop",  "AND",  "ROL",  "rla",

    "RTI",  "EOR",  "n/a",  "sre",  "nop",  "EOR",  "LSR",  "sre",    # 0x4?
    "PHA",  "EOR",  "LSRA", "asr",  "JMP",  "EOR",  "LSR",  "sre",

    "BVC",  "EOR",  "n/a",  "sre",  "nop",  "EOR",  "LSR",  "sre",    # 0x5?
    "CLI",  "EOR",  "nop",  "sre",  "nop",  "EOR",  "LSR",  "sre",

    "RTS",  "ADC",  "n/a",  "rra",  "nop",  "ADC",  "ROR",  "rra",    # 0x6?
    "PLA",  "ADC",  "RORA", "arr",  "JMP",  "ADC",  "ROR",  "rra",

    "BVS",  "ADC",  "n/a",  "rra",  "nop",  "ADC",  "ROR",  "rra",    # 0x7?
    "SEI",  "ADC",  "nop",  "rra",  "nop",  "ADC",  "ROR",  "rra",

    "nop",  "STA",  "nop",  "sax",  "STY",  "STA",  "STX",  "sax",    # 0x8?
    "DEY",  "nop",  "TXA",  "ane",  "STY",  "STA",  "STX",  "sax",

    "BCC",  "STA",  "n/a",  "sha",  "STY",  "STA",  "STX",  "sax",    # 0x9?
    "TYA",  "STA",  "TXS",  "shs",  "shy",  "STA",  "shx",  "sha",

    "LDY",  "LDA",  "LDX",  "lax",  "LDY",  "LDA",  "LDX",  "lax",    # 0xA?
    "TAY",  "LDA",  "TAX",  "lxa",  "LDY",  "LDA",  "LDX",  "lax",

    "BCS",  "LDA",  "n/a",  "lax",  "LDY",  "LDA",  "LDX",  "lax",    # 0xB?
    "CLV",  "LDA",  "TSX",  "las",  "LDY",  "LDA",  "LDX",  "lax",

    "CPY",  "CMP",  "nop",  "dcp",  "CPY",  "CMP",  "DEC",  "dcp",    # 0xC?
    "INY",  "CMP",  "DEX",  "sbx",  "CPY",  "CMP",  "DEC",  "dcp",

    "BNE",  "CMP",  "n/a",  "dcp",  "nop",  "CMP",  "DEC",  "dcp",    # 0xD?
    "CLD",  "CMP",  "nop",  "dcp",  "nop",  "CMP",  "DEC",  "dcp",

    "CPX",  "SBC",  "nop",  "isb",  "CPX",  "SBC",  "INC",  "isb",    # 0xE?
    "INX",  "SBC",  "NOP",  "sbc",  "CPX",  "SBC",  "INC",  "isb",

    "BEQ",  "SBC",  "n/a",  "isb",  "nop",  "SBC",  "INC",  "isb",    # 0xF?
    "SED",  "SBC",  "nop",  "isb",  "nop",  "SBC",  "INC",  "isb"
)


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
    byte = get # alias

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


class LowMOS6502MemMixin(object):
    """ low compatibility mem r/w mixin"""

    def read_word(self, adr):
        return self.mem.read(adr) + (self.mem.read(adr + 1) * 256)

    def read_word_lo_hi(self, adr):
        return self.mem.read(adr), (self.mem.read(adr + 1) * 256)

    def write_word(self, adr, val):
        self.mem.write(adr, val & 0xFF)
        self.mem.write(adr + 1, (val >> 8) & 0xFF)

    def write_word_lo_hi(self, adr, lo, hi):
        self.mem.write(adr, lo)
        self.mem.write(adr + 1, hi)

    # addr modes

    def implied(self):
        return None, None

    def immediate_read(self):
        adr = self.PC
        self.PC = (self.PC + 1) & 0xFFFF
        return adr, self.mem.read(adr)

    def absolute_read(self):
        adr = self.mem.read(self.PC) + (self.mem.read(self.PC + 1) * 256)
        self.PC = (self.PC + 2) & 0xFFFF
        return adr, self.mem.read(adr)

    def absolute_write(self):
        adr = self.mem.read(self.PC) + (self.mem.read(self.PC + 1) * 256)
        self.PC = (self.PC + 2) & 0xFFFF
        return adr, None

    absolute_read_modify_write = absolute_read

    def absolute_x_read(self):
        adr = self.mem.read(self.PC) + (self.mem.read(self.PC + 1) * 256)
        self.PC = (self.PC + 2) & 0xFFFF
        # See if we need to add one cycle for indexing across a page boundary
        if (adr ^ (adr + self.X)) & 0xff00:
            self.T -= 1
            self.abs_T += 1
        adr += self.X
        return adr, self.mem.read(adr)

    def absolute_x_write(self):
        adr = self.mem.read(self.PC) + (self.mem.read(self.PC + 1) * 256)
        self.PC = (self.PC + 2) & 0xFFFF
        return adr + self.X, None

    def absolute_x_read_modify_write(self):
        adr = self.mem.read(self.PC) + (self.mem.read(self.PC + 1) * 256)
        self.PC = (self.PC + 2) & 0xFFFF
        adr += self.X
        return adr, self.mem.read(adr)

    def absolute_y_read(self):
        adr = self.mem.read(self.PC) + (self.mem.read(self.PC + 1) * 256)
        self.PC = (self.PC + 2) & 0xFFFF
        # See if we need to add one cycle for indexing across a page boundary
        if (adr ^ (adr + self.Y)) & 0xff00:
            self.T -= 1
            self.abs_T += 1
        adr += self.Y
        return adr, self.mem.read(adr)

    def absolute_y_write(self):
        adr = self.mem.read(self.PC) + (self.mem.read(self.PC + 1) * 256)
        self.PC = (self.PC + 2) & 0xFFFF
        return adr + self.Y, None

    def absolute_y_read_modify_write(self):
        adr = self.mem.read(self.PC) + (self.mem.read(self.PC + 1) * 256)
        self.PC = (self.PC + 2) & 0xFFFF
        adr += self.Y
        return adr, self.mem.read(adr)

    def zero_read(self):
        adr = self.mem.read(self.PC)
        self.PC = (self.PC + 1) & 0xFFFF
        return adr, self.mem.read(adr)

    def zero_write(self):
        adr = self.PC
        self.PC = (self.PC + 1) & 0xFFFF
        return adr, None

    zero_read_modify_write = zero_read

    def zero_x_read(self):
        adr = (self.mem.read(self.PC) + self.X) & 0xFF
        self.PC = (self.PC + 1) & 0xFFFF
        return adr, self.mem.read(adr)

    def zero_x_write(self):
        adr = (self.mem.read(self.PC) + self.X) & 0xFF
        self.PC = (self.PC + 1) & 0xFFFF
        return adr, None

    zero_x_read_modify_write = zero_x_read

    def zero_y_read(self):
        adr = (self.mem.read(self.PC) + self.Y) & 0xFF
        self.PC = (self.PC + 1) & 0xFFFF
        return adr, self.mem.read(adr)

    def zero_y_write(self):
        adr = (self.mem.read(self.PC) + self.Y) & 0xFF
        self.PC = (self.PC + 1) & 0xFFFF
        return adr, None

    zero_y_read_modify_write = zero_y_read

    def indirect(self):
        adr = self.mem.read(self.PC) + (self.mem.read(self.PC + 1) * 256)
        self.PC = (self.PC + 2) & 0xFFFF
        # Simulate the error in the indirect addressing mode!
        if (adr ^ (adr + 1)) & 0xFF00:
            return self.mem.read(adr) + (self.mem.read(adr & 0xFF00) * 256), None
        else:
            return self.mem.read(adr) + (self.mem.read(adr + 1) * 256), None

    def indirect_x_read(self):
        ptr = (self.mem.read(self.PC) + self.X) & 0xFF
        self.PC = (self.PC + 1) & 0xFFFF
        adr = self.mem.read(ptr) + (self.mem.read(ptr + 1) * 256)
        return adr, self.mem.read(adr)

    def indirect_x_write(self):
        ptr = (self.mem.read(self.PC) + self.X) & 0xFF
        self.PC = (self.PC + 1) & 0xFFFF
        return self.mem.read(ptr) + (self.mem.read(ptr + 1) * 256), None

    indirect_x_read_modify_write = indirect_x_read

    def indirect_y_read(self):
        ptr = self.mem.read(self.PC)
        adr = self.mem.read(ptr) + (self.mem.read(ptr + 1) * 256)
        self.PC = (self.PC + 1) & 0xFFFF
        # See if we need to add one cycle for indexing across a page boundary
        if (adr ^ (adr + self.Y)) & 0xff00:
            self.T -= 1
            self.abs_T += 1
        adr = (adr + self.Y) & 0xFFFF
        return adr, self.mem.read(adr)

    def indirect_y_write(self):
        ptr = self.mem.read(self.PC)
        adr = self.mem.read(ptr) + (self.mem.read(ptr + 1) * 256)
        self.PC = (self.PC + 1) & 0xFFFF
        return (adr + self.Y) & 0xFFFF, None

    def indirect_y_read_modify_write(self):
        ptr = self.mem.read(self.PC)
        adr = self.mem.read(ptr) + (self.mem.read(ptr + 1) * 256)
        self.PC = (self.PC + 1) & 0xFFFF
        adr = (adr + self.Y) & 0xFFFF
        return adr, self.mem.read(adr)


class LowMOS6502BxxMixin(object):
    """ low compatibility Bxx instructions mixin"""

    def _bxx(self, op, cond):
        if not cond: return
        adr = self.PC + self.mem.as_signed(op)
        # See if we need to add one cycle for indexing across a page boundary
        if (self.PC ^ adr) & 0xFF00:
            self.T -= 2
            self.abs_T += 2
        else:
            self.T -= 1
            self.abs_T += 1
        self.PC = adr

    def bcc(self, adr, op):
        self._bxx(op, not self.P.c)

    def bcs(self, adr, op):
        self._bxx(op, self.P.c)

    def beq(self, adr, op):
        self._bxx(op, self.P.z)

    def bne(self, adr, op):
        self._bxx(op, not self.P.z)

    def bmi(self, adr, op):
        self._bxx(op, self.P.s)

    def bpl(self, adr, op):
        self._bxx(op, not self.P.s)

    def bvc(self, adr, op):
        self._bxx(op, not self.P.v)

    def bvs(self, adr, op):
        self._bxx(op, self.P.v)

class MOS6502(CPU, LowMOS6502MemMixin, LowMOS6502BxxMixin):
    RESET_VECTOR = 0xFFFC
    BRK_VECTOR = 0xFFFE

    # adr modes
    IMPLIED = 0
    IMMEDIATE_READ = 1
    ABSOLUTE_READ = 2
    ABSOLUTE_WRITE = 3
    ABSOLUTE_READMODIFYWRITE = 4
    ABSOLUTEX_READ = 5
    ABSOLUTEX_WRITE = 6
    ABSOLUTEX_READMODIFYWRITE = 7
    ABSOLUTEY_READ = 8
    ABSOLUTEY_WRITE = 9
    ABSOLUTEY_READMODIFYWRITE = 10
    ZERO_READ = 11
    ZERO_WRITE = 12
    ZERO_READMODIFYWRITE = 13
    ZEROX_READ = 14
    ZEROX_WRITE = 15
    ZEROX_READMODIFYWRITE = 16
    ZEROY_READ = 17
    ZEROY_WRITE = 18
    ZEROY_READMODIFYWRITE = 19
    INDIRECT = 20
    INDIRECTX_READ = 21
    INDIRECTX_WRITE = 22
    INDIRECTX_READMODIFYWRITE = 23
    INDIRECTY_READ = 24
    INDIRECTY_WRITE = 25
    INDIRECTY_READMODIFYWRITE = 26

    def __init__(self, break_afer, mem, io=None):
        self.A = random.randint(0, 0xFF)
        self.X = random.randint(0, 0xFF)
        self.Y = random.randint(0, 0xFF)

        self.S = random.randint(0, 0xFF)
        self.P = MOS6502Flags()

        self.PC = random.randint(0, 0xFFFF)
        self._halt = False

        super(MOS6502, self).__init__(break_afer, mem, io)

        # init adrmode tab

        self.adr_modes[MOS6502.IMPLIED] = (self.implied, '')

        self.adr_modes[MOS6502.IMMEDIATE_READ] = (self.immediate_read, '#%02X')

        self.adr_modes[MOS6502.ABSOLUTE_READ] = (self.absolute_read, '%04X')
        self.adr_modes[MOS6502.ABSOLUTE_WRITE] = (self.absolute_write, '%04X')
        self.adr_modes[MOS6502.ABSOLUTE_READMODIFYWRITE] = (self.absolute_read_modify_write, '%04X')

        self.adr_modes[MOS6502.ABSOLUTEX_READ] = (self.absolute_x_read, '%04X, X')
        self.adr_modes[MOS6502.ABSOLUTEX_WRITE] = (self.absolute_x_write, '%04X, X')
        self.adr_modes[MOS6502.ABSOLUTEX_READMODIFYWRITE] = (self.absolute_x_read_modify_write, '%04X, X')

        self.adr_modes[MOS6502.ABSOLUTEY_READ] = (self.absolute_y_read, '%04X, Y')
        self.adr_modes[MOS6502.ABSOLUTEY_WRITE] = (self.absolute_y_write, '%04X, Y')
        self.adr_modes[MOS6502.ABSOLUTEY_READMODIFYWRITE] = (self.absolute_y_read_modify_write, '%04X, Y')

        self.adr_modes[MOS6502.ZERO_READ] = (self.zero_read, '%02X')
        self.adr_modes[MOS6502.ZERO_WRITE] = (self.zero_write, '%02X')
        self.adr_modes[MOS6502.ZERO_READMODIFYWRITE] = (self.zero_read_modify_write, '%02X')

        self.adr_modes[MOS6502.ZEROX_READ] = (self.zero_x_read, '%02X, X')
        self.adr_modes[MOS6502.ZEROX_WRITE] = (self.zero_x_write, '%02X, X')
        self.adr_modes[MOS6502.ZEROX_READMODIFYWRITE] = (self.zero_x_read_modify_write, '%02X, X')

        self.adr_modes[MOS6502.ZEROY_READ] = (self.zero_y_read, '%02X, Y')
        self.adr_modes[MOS6502.ZEROY_WRITE] = (self.zero_y_write, '%02X, Y')
        self.adr_modes[MOS6502.ZEROY_READMODIFYWRITE] = (self.zero_y_read_modify_write, '%02X, Y')

        self.adr_modes[MOS6502.INDIRECT] = (self.indirect, '(%04X)')

        self.adr_modes[MOS6502.INDIRECTX_READ] = (self.indirect_x_read, '(%02X, X)')
        self.adr_modes[MOS6502.INDIRECTX_WRITE] = (self.indirect_x_write, '(%02X, X)')
        self.adr_modes[MOS6502.INDIRECTX_READMODIFYWRITE] = (self.indirect_x_read_modify_write, '(%02X, X)')

        self.adr_modes[MOS6502.INDIRECTY_READ] = (self.indirect_y_read, '(%02X), Y')
        self.adr_modes[MOS6502.INDIRECTY_WRITE] = (self.indirect_y_write, '(%02X), Y')
        self.adr_modes[MOS6502.INDIRECTY_READMODIFYWRITE] = (self.indirect_y_read_modify_write, '(%02X), Y')

        # init opcodes
        self.register_opcodes()

    def _cycles(self, op):
        return CYCLES[op]

    def _mnemonic(self, op):
        return MNEMONICS[op]

    def __str__(self):
        return 'PC: %04X A: %02X X: %02X Y: %02X S: %02X P: %s' % \
                (self.PC, self.A, self.X, self.Y, self.S, self.P)

    def read_op(self):
        ret = self.mem.read(self.PC)
        self.PC = (self.PC + 1) & 0xFFFF
        return ret

    def push(self, val):
        self.mem.write(0x100 + self.S, val)
        self.S = (self.S - 1) & 0xFF

    def push_word(self, val):
        self.mem.write(0x100 + self.S, val >> 8)
        self.S = (self.S - 1) & 0xFF

        self.mem.write(0x100 + self.S, val & 0x00FF)
        self.S = (self.S - 1) & 0xFF

    def pop(self):
        self.mem.read(0x100 + self.S)
        self.S = (self.S + 1) & 0xFF
        return self.mem.read(0x100 + self.S)

    def pop_word(self):
        lo = self.mem.read(0x100 + self.S)
        self.S = (self.S + 1) & 0xFF
        hi = self.mem.read(0x100 + self.S)
        self.S = (self.S + 1) & 0xFF
        return lo | (hi << 8)

    def reset(self):
        self.A = 0x00
        self.X = 0x00
        self.Y = 0x00
        self.halt = False

        self.S = 0xFF
        self.P.set(MOS6502Flags.F5)

        self.PC = self.read_word(MOS6502.RESET_VECTOR)

        # tstates
        self.T = 0
        self.abs_T = 0

    # OPCODES

    def hlt(self, adr, val):
        """ HALT """
        self._halt = True
        raise CPUTrapInvalidOP('CPU halted')

    def adc(self, adr, val):
        """
          uInt8 oldA = A;

          if(!D)
          {
            Int16 sum = (Int16)((Int8)A) + (Int16)((Int8)operand) + (C ? 1 : 0);
            V = ((sum > 127) || (sum < -128));

            sum = (Int16)A + (Int16)operand + (C ? 1 : 0);
            A = sum;
            C = (sum > 0xff);
            notZ = A;
            N = A & 0x80;
          }
          else
          {
            Int16 sum = ourBCDTable[0][A] + ourBCDTable[0][operand] + (C ? 1 : 0);

            C = (sum > 99);
            A = ourBCDTable[1][sum & 0xff];
            notZ = A;
            N = A & 0x80;
            V = ((oldA ^ A) & 0x80) && ((A ^ operand) & 0x80);
          }
        """

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

    def anc(self, adr, op):
        """
          A &= operand;
          notZ = A;
          N = A & 0x80;
          C = N;
        """

        self.A &= op
        self.P.mset(**SZ_TAB[self.A])
        self.P.c = self.P.s

    def and_(self, adr, op):
        """
          A &= operand;
          notZ = A;
          N = A & 0x80;
        """

        self.A &= op
        self.P.mset(**SZ_TAB[self.A])

    def ane(self, adr, op):
        """
          // NOTE: The implementation of this instruction is based on
          // information from the 64doc.txt file.  This instruction is
          // reported to be unstable!
          A = (A | 0xee) & X & operand;
          notZ = A;
          N = A & 0x80;
        """

        self.A = (self.A | 0xEE) & self.X & op
        self.P.mset(**SZ_TAB[self.A])

    def arr(self, adr, op):
        """
          // NOTE: The implementation of this instruction is based on
          // information from the 64doc.txt file.  There are mixed
          // reports on its operation!
          if(!D)
          {
            A &= operand;
            A = ((A >> 1) & 0x7f) | (C ? 0x80 : 0x00);

            C = A & 0x40;
            V = (A & 0x40) ^ ((A & 0x20) << 1);

            notZ = A;
            N = A & 0x80;
          }
          else
          {
            uInt8 value = A & operand;

            A = ((value >> 1) & 0x7f) | (C ? 0x80 : 0x00);
            N = C;
            notZ = A;
            V = (value ^ A) & 0x40;

            if(((value & 0x0f) + (value & 0x01)) > 0x05)
            {
              A = (A & 0xf0) | ((A + 0x06) & 0x0f);
            }

            if(((value & 0xf0) + (value & 0x10)) > 0x50)
            {
              A = (A + 0x60) & 0xff;
              C = 1;
            }
            else
            {
              C = 0;
            }
          }
        """

        if self.P.d:
            val = self.A & op
            self.A = ((val >> 1) & 0x7F) | (0x80 if self.P.c else 0x00)
            self.P.s = self.P.c
            self.P.z = not self.A
            self.P.v = bool((val ^ self.A) & 0x40)
            if ((val & 0x0F) + (val & 0x01)) > 0x05:
                self.A = (self.A & 0xF0) | ((self.A + 0x06) & 0x0f)
            if ((val & 0xF0) + (val & 0x10)) > 0x50:
                self.A = (self.A + 0x60) & 0xFF
                self.P.c = True
            else:
                self.P.c = False
        else:
            self.A &= op;
            self.A = ((self.A >> 1) & 0x7F) | (0x80 if self.P.c else 0x00)
            self.P.c = self.A & 0x40
            self.P.v = (self.A & 0x40) ^ ((self.A & 0x20) << 1)
            self.P.mset(**SZ_TAB[self.A])

    def asl(self, adr, op):
        """
          // Set carry flag according to the left-most bit in value
          C = operand & 0x80;

          operand <<= 1;
          poke(operandAddress, operand);

          notZ = operand;
          N = operand & 0x80;
        """

        self.P.c = bool(op & 0x80)
        op = (op << 1) & 0xFF
        self.mem.write(adr, op)
        self.P.mset(**SZ_TAB[op])

    def asla(self, adr, op):
        """
          // Set carry flag according to the left-most bit in A
          C = A & 0x80;

          A <<= 1;

          notZ = A;
          N = A & 0x80;
        """

        self.P.c = bool(self.A & 0x80)
        self.A = (self.A << 1) & 0xFF
        self.P.mset(**SZ_TAB[self.A])

    def asr(self, adr, op):
        """
          A &= operand;

          // Set carry flag according to the right-most bit
          C = A & 0x01;

          A = (A >> 1) & 0x7f;

          notZ = A;
          N = A & 0x80;
        """

        self.A &= op
        self.P.c = bool(self.A & 0x01)
        self.A = (self.A >> 1) & 0x7F
        self.P.mset(**SZ_TAB[self.A])

    def bit(self, adr, op):
        """
          notZ = (A & operand);
          N = operand & 0x80;
          V = operand & 0x40;
        """

        self.P.z = not (self.A & op)
        self.P.s = bool(op & 0x80)
        self.P.v = bool(op & 0x40)

    def brk(self, adr, op):
        """
          peek(PC++);

          B = true;

          poke(0x0100 + SP--, PC >> 8);
          poke(0x0100 + SP--, PC & 0x00ff);
          poke(0x0100 + SP--, PS());

          I = true;

          PC = peek(0xfffe);
          PC |= ((uInt16)peek(0xffff) << 8);
        """

        self.read_op()
        self.P.b = True

        self.push_word(self.PC)
        self.push(self.P.byte())

        self.P.i = True
        self.PC = self.read_word(MOS6502.BRK_VECTOR)

    def clc(self, adr, op):
        """
            C = false;
        """

        self.P.c = False

    def cld(self, adr, op):
        """
            D = false;
        """

        self.P.d = False

    def cli(self, adr, op):
        """
            I = false;
        """

        self.P.i = False

    def clv(self, adr, op):
        """
            V = false;
        """

        self.P.v = False

    def _cp(self, op1, op2):
        val = op1 - op2
        self.P.mset(**SZ_TAB[val & 0xFF])
        self.P.c = not (val & 0x0100)

    def cmp(self, adr, op):
        """
          uInt16 value = (uInt16)A - (uInt16)operand;

          notZ = value;
          N = value & 0x0080;
          C = !(value & 0x0100);
        """

        self._cp(self.A, op)

    def cpx(self, adr, op):
        """
          uInt16 value = (uInt16)X - (uInt16)operand;

          notZ = value;
          N = value & 0x0080;
          C = !(value & 0x0100);
        """

        self._cp(self.X, op)

    def cpy(self, adr, op):
        """
          uInt16 value = (uInt16)Y - (uInt16)operand;

          notZ = value;
          N = value & 0x0080;
          C = !(value & 0x0100);
        """

        self._cp(self.Y, op)

    def dcp(self, adr, op):
        """
          uInt8 value = operand - 1;
          poke(operandAddress, value);

          uInt16 value2 = (uInt16)A - (uInt16)value;
          notZ = value2;
          N = value2 & 0x0080;
          C = !(value2 & 0x0100);
        """

        val = (op - 1) & 0xFF
        self.mem.write(adr, val)
        self._cp(self.A, val)

    def dec(self, adr, op):
        """
          uInt8 value = operand - 1;
          poke(operandAddress, value);

          notZ = value;
          N = value & 0x80;
        """

        val = (op - 1) & 0xFF
        self.mem.write(adr, val)
        self.P.mset(**SZ_TAB[val])

    def dex(self, adr, op):
        """
          X--;

          notZ = X;
          N = X & 0x80;
        """

        self.X = (self.X - 1) & 0xFF
        self.P.mset(**SZ_TAB[self.X])

    def dey(self, adr, op):
        """
          Y--;

          notZ = Y;
          N = Y & 0x80;
        """
        self.Y = (self.Y - 1) & 0xFF
        self.P.mset(**SZ_TAB[self.Y])

    def eor(self, adr, op):
        """
              A ^= operand;
              notZ = A;
              N = A & 0x80;
        """

        self.A ^= op
        self.P.mset(**SZ_TAB[self.A])

    def inc(self, adr, op):
        """
          uInt8 value = operand + 1;
          poke(operandAddress, value);

          notZ = value;
          N = value & 0x80;
        """

        val = (op + 1) & 0xFF
        self.mem.write(adr, val)
        self.P.mset(**SZ_TAB[val])

    def inx(self, adr, op):
        """
          X++;
          notZ = X;
          N = X & 0x80;
        """

        self.X = (self.X + 1) & 0xFF
        self.P.mset(**SZ_TAB[self.X])

    def iny(self, adr, op):
        """
          Y++;
          notZ = Y;
          N = Y & 0x80;
        """

        self.Y = (self.Y + 1) & 0xFF
        self.P.mset(**SZ_TAB[self.Y])

    def isb(self, adr, op):
        """
          operand = operand + 1;
          poke(operandAddress, operand);

          uInt8 oldA = A;

          if(!D)
          {
            operand = ~operand;
            Int16 difference = (Int16)((Int8)A) + (Int16)((Int8)operand) + (C ? 1 : 0);
            V = ((difference > 127) || (difference < -128));

            difference = ((Int16)A) + ((Int16)operand) + (C ? 1 : 0);
            A = difference;
            C = (difference > 0xff);
            notZ = A;
            N = A & 0x80;
          }
          else
          {
            Int16 difference = ourBCDTable[0][A] - ourBCDTable[0][operand]
                - (C ? 0 : 1);

            if(difference < 0)
              difference += 100;

            A = ourBCDTable[1][difference];
            notZ = A;
            N = A & 0x80;

            C = (oldA >= (operand + (C ? 0 : 1)));
            V = ((oldA ^ A) & 0x80) && ((A ^ operand) & 0x80);
          }
        """

        op = (op + 1) & 0xFF
        self.mem.write(adr, op)
        olda = self.A
        if not self.P.d:
            op = ~op
            diff = self.mem.as_signed(self.A) + self.mem.as_signed(op) + (1 if self.P.c else 0) & 0xFFFF
            self.P.v = (diff > 127) or (diff < -128)
            self.A = diff & 0xFF
            self.P.c = diff > 0xFF
            self.P.mset(**SZ_TAB[self.A])
        else:
            diff = BCD_TAB[0][self.A] - BCD_TAB[0][op] - (0 if self.P.c else 1)
            if diff < 0: diff += 100
            self.A = BCD_TAB[1][diff & 0xFF]
            self.P.mset(**SZ_TAB[self.A])
            self.P.c = (olda >= (op + (0 if self.P.c else 1)))
            self.P.v = ((olda ^ self.A) & 0x80) and ((self.A ^ op) & 0x80)

    def jmp(self, adr, op):
        """
            PC = operandAddress;
        """

        self.PC = adr

    def jsr(self, adr, op):
        """
          uInt8 low = peek(PC++);
          peek(0x0100 + SP);

          // It seems that the 650x does not push the address of the next instruction
          // on the stack it actually pushes the address of the next instruction
          // minus one.  This is compensated for in the RTS instruction
          poke(0x0100 + SP--, PC >> 8);
          poke(0x0100 + SP--, PC & 0xff);

          PC = low | ((uInt16)peek(PC++) << 8);
        """

        low = self.read_op()
        self.mem.read(0x100 + self.S)
        self.push_word(self.PC)
        self.PC = low | (self.mem.read_op() << 8)

    def las(self, adr, op):
        """
          A = X = SP = SP & operand;
          notZ = A;
          N = A & 0x80;
        """

        self.A = self.X = self.S = self.S & op
        self.P.mset(**SZ_TAB[self.A])

    def lax(self, adr, op):
        """
          A = operand;
          X = operand;
          notZ = A;
          N = A & 0x80;
        """

        self.A = self.X = op
        self.P.mset(**SZ_TAB[op])

    def lda(self, adr, op):
        """
          A = operand;
          notZ = A;
          N = A & 0x80;
        """

        self.A = op
        self.P.mset(**SZ_TAB[op])

    def ldx(self, adr, op):
        """
          X = operand;
          notZ = X;
          N = X & 0x80;
        """

        self.X = op
        self.P.mset(**SZ_TAB[op])

    def ldy(self, adr, op):
        """
          Y = operand;
          notZ = Y;
          N = Y & 0x80;
        """

        self.Y = op
        self.P.mset(**SZ_TAB[op])

    def lsr(self, adr, op):
        """
          // Set carry flag according to the right-most bit in value
          C = operand & 0x01;

          operand = (operand >> 1) & 0x7f;
          poke(operandAddress, operand);

          notZ = operand;
          N = operand & 0x80;
        """

        self.P.c = bool(op & 0x01)
        op = (op >> 1) & 0x7F
        self.mem.write(adr, op)
        self.P.mset(**SZ_TAB[op])

    def lsra(self, adr, op):
        """
          // Set carry flag according to the right-most bit
          C = A & 0x01;

          A = (A >> 1) & 0x7f;

          notZ = A;
          N = A & 0x80;
        """

        self.P.c = bool(self.A & 0x01)
        self.A = (self.A >> 1) & 0x7F
        self.P.mset(**SZ_TAB[self.A])

    def lxa(self, adr, op):
        """
          // NOTE: The implementation of this instruction is based on
          // information from the 64doc.txt file.  This instruction is
          // reported to be very unstable!
          A = X = (A | 0xee) & operand;
          notZ = A;
          N = A & 0x80;
        """

        self.A = self.X = (self.A | 0xEE) & op
        self.P.mset(**SZ_TAB[self.A])

    def nop(self, adr, op):
        pass

    def ora(self, adr, op):
        """
          A |= operand;
          notZ = A;
          N = A & 0x80;
        """

        self.A |= op
        self.P.mset(**SZ_TAB[self.A])

    def pha(self, adr, op):
        """
            poke(0x0100 + SP--, A);
        """

        self.push(self.A)

    def php(self, adr, op):
        """
            poke(0x0100 + SP--, PS());
        """

        self.push(self.P.byte())

    def pla(self, adr, op):
        """
          peek(0x0100 + SP++);
          A = peek(0x0100 + SP);
          notZ = A;
          N = A & 0x80;
        """

        self.A = self.pop()
        self.P.mset(**SZ_TAB[self.A])

    def plp(self, adr, op):
        """
          peek(0x0100 + SP++);
          PS(peek(0x0100 + SP));
        """

        self.P.set(self.pop())

    def rla(self, adr, op):
        """
          uInt8 value = (operand << 1) | (C ? 1 : 0);
          poke(operandAddress, value);

          A &= value;
          C = operand & 0x80;
          notZ = A;
          N = A & 0x80;
        """

        val = ((op << 1) | (1 if self.P.c else 0)) & 0xFF
        self.mem.write(adr, val)
        self.A &= val
        self.P.mset(**SZ_TAB[self.A])
        self.P.c = bool(op & 0x80)

    def rol(self, adr, op):
        """
          bool oldC = C;

          // Set carry flag according to the left-most bit in operand
          C = operand & 0x80;

          operand = (operand << 1) | (oldC ? 1 : 0);
          poke(operandAddress, operand);

          notZ = operand;
          N = operand & 0x80;
        """

        oldc = self.P.c
        self.P.c = bool(op & 0x80)
        op = ((op << 1) | (1 if oldc else 0)) & 0xFF
        self.mem.write(adr, op)
        self.P.mset(**SZ_TAB[op])

    def rola(self, adr, op):
        """
          bool oldC = C;

          // Set carry flag according to the left-most bit
          C = A & 0x80;

          A = (A << 1) | (oldC ? 1 : 0);

          notZ = A;
          N = A & 0x80;
        """

        oldc = self.P.c
        self.P.c = bool(self.A & 0x80)
        self.A = ((self.A << 1) | (1 if oldc else 0)) & 0xFF
        self.P.mset(**SZ_TAB[self.A])

    def ror(self, adr, op):
        """
          bool oldC = C;

          // Set carry flag according to the right-most bit
          C = operand & 0x01;

          operand = ((operand >> 1) & 0x7f) | (oldC ? 0x80 : 0x00);
          poke(operandAddress, operand);

          notZ = operand;
          N = operand & 0x80;
        """

        oldc = self.P.c
        self.P.c = bool(op & 0x01)
        op = ((op >> 1) | (0x80 if oldc else 0)) & 0xFF
        self.mem.write(adr, op)
        self.P.mset(**SZ_TAB[op])

    def rora(self, adr, op):
        """
          bool oldC = C;

          // Set carry flag according to the right-most bit
          C = A & 0x01;

          A = ((A >> 1) & 0x7f) | (oldC ? 0x80 : 0x00);

          notZ = A;
          N = A & 0x80;
        """

        oldc = self.P.c
        self.P.c = bool(self.A & 0x01)
        self.A = ((self.A >> 1) | (0x80 if oldc else 0)) & 0xFF
        self.P.mset(**SZ_TAB[self.A])

    def rra(self, adr, op):
        """
          uInt8 oldA = A;
          bool oldC = C;

          // Set carry flag according to the right-most bit
          C = operand & 0x01;

          operand = ((operand >> 1) & 0x7f) | (oldC ? 0x80 : 0x00);
          poke(operandAddress, operand);

          if(!D)
          {
            Int16 sum = (Int16)((Int8)A) + (Int16)((Int8)operand) + (C ? 1 : 0);
            V = ((sum > 127) || (sum < -128));

            sum = (Int16)A + (Int16)operand + (C ? 1 : 0);
            A = sum;
            C = (sum > 0xff);
            notZ = A;
            N = A & 0x80;
          }
          else
          {
            Int16 sum = ourBCDTable[0][A] + ourBCDTable[0][operand] + (C ? 1 : 0);

            C = (sum > 99);
            A = ourBCDTable[1][sum & 0xff];
            notZ = A;
            N = A & 0x80;
            V = ((oldA ^ A) & 0x80) && ((A ^ operand) & 0x80);
          }
        """

        olda = self.A
        oldc = self.P.c
        self.P.c = bool(op & 0x01)
        op = (((op >> 1) & 0x7F) | (0x80 if oldc else 0)) & 0xFF
        self.mem.write(adr, op)

        if not self.P.d:
            sum = self.mem.as_signed(self.A) + self.mem.as_signed(op) + (1 if self.P.c else 0)
            self.P.v = (sum > 127) or (sum < -128)
            self.A = sum & 0xFF
            self.P.c = sum > 0xFF
            self.P.mset(**SZ_TAB[self.A])
        else:
            sum = BCD_TAB[0][self.A] + BCD_TAB[0][op] + (1 if self.P.c else 0)
            self.P.c = sum > 99
            self.A = BCD_TAB[1][sum & 0xFF]
            self.P.mset(**SZ_TAB[self.A])
            self.P.v = ((olda ^ self.A) & 0x80) and ((self.A ^ op) & 0x80)

    def rti(self, adr, op):
        """
          peek(0x0100 + SP++);
          PS(peek(0x0100 + SP++));
          PC = peek(0x0100 + SP++);
          PC |= ((uInt16)peek(0x0100 + SP) << 8);
        """
        self.P.set(self.pop())
        self.PC = self.pop_word()

    def rts(self, adr, op):
        """
          peek(0x0100 + SP++);
          PC = peek(0x0100 + SP++);
          PC |= ((uInt16)peek(0x0100 + SP) << 8);
          peek(PC++);
        """
        self.P.set(self.pop())
        self.PC = self.pop_word()
        self.read_op()

    def sax(self, adr, op):
        """
            poke(operandAddress, A & X);
        """
        self.mem.write(adr, self.A & self.X)


    def sbc(self, adr, op):
        """
          uInt8 oldA = A;

          if(!D)
          {
            operand = ~operand;
            Int16 difference = (Int16)((Int8)A) + (Int16)((Int8)operand) + (C ? 1 : 0);
            V = ((difference > 127) || (difference < -128));

            difference = ((Int16)A) + ((Int16)operand) + (C ? 1 : 0);
            A = difference;
            C = (difference > 0xff);
            notZ = A;
            N = A & 0x80;
          }
          else
          {
            Int16 difference = ourBCDTable[0][A] - ourBCDTable[0][operand]
                - (C ? 0 : 1);

            if(difference < 0)
              difference += 100;

            A = ourBCDTable[1][difference];
            notZ = A;
            N = A & 0x80;

            C = (oldA >= (operand + (C ? 0 : 1)));
            V = ((oldA ^ A) & 0x80) && ((A ^ operand) & 0x80);
          }
        """

        olda = self.A
        if not self.P.d:
            op = ~op
            diff = self.mem.as_signed(self.A) + self.mem.as_signed(op) + (1 if self.P.c else 0)
            self.P.v = (diff > 127) or (diff < -128)
            self.A = diff & 0xFF
            self.P.c = diff > 0xFF
            self.P.mset(**SZ_TAB[self.A])
        else:
            diff = BCD_TAB[0][self.A] - BCD_TAB[0][op] - (0 if self.P.c else 1)
            if diff < 0: diff += 100
            self.A = BCD_TAB[1][diff & 0xFF]
            self.P.mset(**SZ_TAB[self.A])
            self.P.c = olda >= (op + (0 if self.P.c else 1))
            self.P.v = ((olda ^ self.A) & 0x80) and ((self.A ^ op) & 0x80)

    def sbx(self, adr, op):
        """
          uInt16 value = (uInt16)(X & A) - (uInt16)operand;
          X = (value & 0xff);

          notZ = X;
          N = X & 0x80;
          C = !(value & 0x0100);
        """

        val = (self.X & self.A) - op
        self.X = val & 0xFF
        self.P.mset(**SZ_TAB[self.X])
        self.P.c = not (val & 0x0100)

    def sec(self, adr, op):
        """
            C = true;
        """

        self.P.c = True

    def sed(self, adr, op):
        """
            D = true;
        """

        self.P.d = True

    def sei(self, adr, op):
        """
            I = true;
        """

        self.P.i = True

    def sha(self, adr, op):
        """
          // NOTE: There are mixed reports on the actual operation
          // of this instruction!
          poke(operandAddress, A & X & (((operandAddress >> 8) & 0xff) + 1));
        """

        self.mem.write(adr, self.A & self.X and (((adr >> 8) & 0xFF) + 1))

    def shs(self, adr, op):
        """
          // NOTE: There are mixed reports on the actual operation
          // of this instruction!
          SP = A & X;
          poke(operandAddress, A & X & (((operandAddress >> 8) & 0xff) + 1));
        """

        self.S = self.A & self.X
        self.mem.write(adr, self.A & self.X & (((op >> 8) & 0xFF) + 1))

    def shx(self, adr, op):
        """
          // NOTE: There are mixed reports on the actual operation
          // of this instruction!
          poke(operandAddress, X & (((operandAddress >> 8) & 0xff) + 1));
        """

        self.mem.write(adr, self.X & (((op >> 8) & 0xFF) + 1))

    def shy(self, adr, op):
        """
          // NOTE: There are mixed reports on the actual operation
          // of this instruction!
          poke(operandAddress, Y & (((operandAddress >> 8) & 0xff) + 1));
        """

        self.mem.write(adr, self.Y & (((op >> 8) & 0xFF) + 1))

    def slo(self, adr, op):
        """
          // Set carry flag according to the left-most bit in value
          C = operand & 0x80;

          operand <<= 1;
          poke(operandAddress, operand);

          A |= operand;
          notZ = A;
          N = A & 0x80;
        """

        self.P.c = bool(op & 0x80)
        op = (op << 1) & 0xFF
        self.mem.write(adr, op)
        self.A |= op
        self.P.mset(**SZ_TAB[self.A])

    def sre(self, adr, op):
        """
          // Set carry flag according to the right-most bit in value
          C = operand & 0x01;

          operand = (operand >> 1) & 0x7f;
          poke(operandAddress, operand);

          A ^= operand;
          notZ = A;
          N = A & 0x80;
        """

        self.P.c = bool(op & 0x01)
        op = (op >> 1) & 0x7F
        self.mem.write(adr, op)
        self.A ^= op
        self.P.mset(**SZ_TAB[self.A])

    def sta(self, adr, op):
        """
        poke(operandAddress, A);
        """

        self.mem.write(adr, self.A)

    def stx(self, adr, op):
        """
        poke(operandAddress, X);
        """

        self.mem.write(adr, self.X)

    def sty(self, adr, op):
        """
        poke(operandAddress, Y);
        """

        self.mem.write(adr, self.Y)

    def tax(self, adr, op):
        """
          X = A;
          notZ = X;
          N = X & 0x80;
        """

        self.X = self.A
        self.P.mset(**SZ_TAB[self.X])

    def tay(self, adr, op):
        """
          Y = A;
          notZ = Y;
          N = Y & 0x80;
        """

        self.Y = self.A
        self.P.mset(**SZ_TAB[self.Y])

    def tsx(self, adr, op):
        """
          X = SP;
          notZ = X;
          N = X & 0x80;
        """

        self.X = self.S
        self.P.mset(**SZ_TAB[self.X])

    def txa(self, adr, op):
        """
          A = X;
          notZ = A;
          N = A & 0x80;
        """

        self.A = self.X
        self.P.mset(**SZ_TAB[self.A])

    def txs(self, adr, op):
        """ SP = X; """
        self.S = self.X

    def tya(self, adr, op):
        """
          A = Y;
          notZ = A;
          N = A & 0x80;
        """

        self.A = self.Y
        self.P.mset(**SZ_TAB[self.A])

    # opcode dispatcher!
    def register_opcodes(self):
        # register instructions
        #           op    handler   addr mode

        # ADC
        self.add_op(0x69, self.adc, MOS6502.IMMEDIATE_READ)
        self.add_op(0x65, self.adc, MOS6502.ZERO_READ)
        self.add_op(0x75, self.adc, MOS6502.ZEROX_READ)
        self.add_op(0x6D, self.adc, MOS6502.ABSOLUTE_READ)
        self.add_op(0x7D, self.adc, MOS6502.ABSOLUTEX_READ)
        self.add_op(0x79, self.adc, MOS6502.ABSOLUTEY_READ)
        self.add_op(0x61, self.adc, MOS6502.INDIRECTX_READ)
        self.add_op(0x71, self.adc, MOS6502.INDIRECTY_READ)

        # ASR
        self.add_op(0x4B, self.asr, MOS6502.IMMEDIATE_READ)

        # ANC
        self.add_op(0x0B, self.anc, MOS6502.IMMEDIATE_READ)
        self.add_op(0x2B, self.anc, MOS6502.IMMEDIATE_READ)

        # AND
        self.add_op(0x29, self.and_, MOS6502.IMMEDIATE_READ)
        self.add_op(0x25, self.and_, MOS6502.ZERO_READ)
        self.add_op(0x35, self.and_, MOS6502.ZEROX_READ)
        self.add_op(0x2D, self.and_, MOS6502.ABSOLUTE_READ)
        self.add_op(0x3D, self.and_, MOS6502.ABSOLUTEX_READ)
        self.add_op(0x39, self.and_, MOS6502.ABSOLUTEY_READ)
        self.add_op(0x21, self.and_, MOS6502.INDIRECTX_READ)
        self.add_op(0x31, self.and_, MOS6502.INDIRECTY_READ)

        # ANE
        self.add_op(0x8B, self.ane, MOS6502.IMMEDIATE_READ)

        # ARR
        self.add_op(0x6B, self.arr, MOS6502.IMMEDIATE_READ)

        # ASLA
        self.add_op(0x0A, self.asla, MOS6502.IMPLIED)

        # ASL
        self.add_op(0x06, self.asl, MOS6502.ZERO_READMODIFYWRITE)
        self.add_op(0x16, self.asl, MOS6502.ZEROX_READMODIFYWRITE)
        self.add_op(0x0E, self.asl, MOS6502.ABSOLUTE_READMODIFYWRITE)
        self.add_op(0x1E, self.asl, MOS6502.ABSOLUTEX_READMODIFYWRITE)

        # Bxx
        self.add_op(0x90, self.bcc, MOS6502.IMMEDIATE_READ)
        self.add_op(0xB0, self.bcs, MOS6502.IMMEDIATE_READ)
        self.add_op(0xF0, self.beq, MOS6502.IMMEDIATE_READ)
        self.add_op(0x30, self.bmi, MOS6502.IMMEDIATE_READ)
        self.add_op(0xD0, self.bne, MOS6502.IMMEDIATE_READ)
        self.add_op(0x10, self.bpl, MOS6502.IMMEDIATE_READ)
        self.add_op(0x50, self.bvc, MOS6502.IMMEDIATE_READ)
        self.add_op(0x70, self.bvs, MOS6502.IMMEDIATE_READ)

        # BIT
        self.add_op(0x24, self.bit, MOS6502.ZERO_READ)
        self.add_op(0x2C, self.bit, MOS6502.ABSOLUTE_READ)

        # BRK
        self.add_op(0x00, self.brk, MOS6502.IMPLIED)

        # CLx
        self.add_op(0x18, self.clc, MOS6502.IMPLIED)
        self.add_op(0xD8, self.cld, MOS6502.IMPLIED)
        self.add_op(0x58, self.cli, MOS6502.IMPLIED)
        self.add_op(0xB8, self.clv, MOS6502.IMPLIED)

        # CMP
        self.add_op(0xC9, self.cmp, MOS6502.IMMEDIATE_READ)
        self.add_op(0xC5, self.cmp, MOS6502.ZERO_READ)
        self.add_op(0xD5, self.cmp, MOS6502.ZEROX_READ)
        self.add_op(0xCD, self.cmp, MOS6502.ABSOLUTE_READ)
        self.add_op(0xDD, self.cmp, MOS6502.ABSOLUTEX_READ)
        self.add_op(0xD9, self.cmp, MOS6502.ABSOLUTEY_READ)
        self.add_op(0xC1, self.cmp, MOS6502.INDIRECTX_READ)
        self.add_op(0xD1, self.cmp, MOS6502.INDIRECTY_READ)

        # CPX
        self.add_op(0xE0, self.cpx, MOS6502.IMMEDIATE_READ)
        self.add_op(0xE4, self.cpx, MOS6502.ZERO_READ)
        self.add_op(0xEC, self.cpx, MOS6502.ABSOLUTE_READ)

        # CPY
        self.add_op(0xC0, self.cpy, MOS6502.IMMEDIATE_READ)
        self.add_op(0xC4, self.cpy, MOS6502.ZERO_READ)
        self.add_op(0xCC, self.cpy, MOS6502.ABSOLUTE_READ)

        # DCP
        self.add_op(0xCF, self.dcp, MOS6502.ABSOLUTE_READMODIFYWRITE)
        self.add_op(0xDF, self.dcp, MOS6502.ABSOLUTEX_READMODIFYWRITE)
        self.add_op(0xDB, self.dcp, MOS6502.ABSOLUTEY_READMODIFYWRITE)
        self.add_op(0xC7, self.dcp, MOS6502.ZERO_READMODIFYWRITE)
        self.add_op(0xD7, self.dcp, MOS6502.ZEROX_READMODIFYWRITE)
        self.add_op(0xC3, self.dcp, MOS6502.INDIRECTX_READMODIFYWRITE)
        self.add_op(0xD3, self.dcp, MOS6502.INDIRECTY_READMODIFYWRITE)

        # DEC
        self.add_op(0xC6, self.dec, MOS6502.ZERO_READMODIFYWRITE)
        self.add_op(0xD6, self.dec, MOS6502.ZEROX_READMODIFYWRITE)
        self.add_op(0xCE, self.dec, MOS6502.ABSOLUTE_READMODIFYWRITE)
        self.add_op(0xDE, self.dec, MOS6502.ABSOLUTEX_READMODIFYWRITE)

        # DEX
        self.add_op(0xCA, self.dex, MOS6502.IMPLIED)

        # DEY
        self.add_op(0x88, self.dey, MOS6502.IMPLIED)

        # EOR
        self.add_op(0x49, self.eor, MOS6502.IMMEDIATE_READ)
        self.add_op(0x45, self.eor, MOS6502.ZERO_READ)
        self.add_op(0x55, self.eor, MOS6502.ZEROX_READ)
        self.add_op(0x4D, self.eor, MOS6502.ABSOLUTE_READ)
        self.add_op(0x5D, self.eor, MOS6502.ABSOLUTEX_READ)
        self.add_op(0x59, self.eor, MOS6502.ABSOLUTEY_READ)
        self.add_op(0x41, self.eor, MOS6502.INDIRECTX_READ)
        self.add_op(0x51, self.eor, MOS6502.INDIRECTY_READ)

        # INC
        self.add_op(0xE6, self.inc, MOS6502.ZERO_READMODIFYWRITE)
        self.add_op(0xF6, self.inc, MOS6502.ZEROX_READMODIFYWRITE)
        self.add_op(0xEE, self.inc, MOS6502.ABSOLUTE_READMODIFYWRITE)
        self.add_op(0xFE, self.inc, MOS6502.ABSOLUTEX_READMODIFYWRITE)

        # INX
        self.add_op(0xE8, self.inx, MOS6502.IMPLIED)

        # INY
        self.add_op(0xC8, self.iny, MOS6502.IMPLIED)

        # ISB
        self.add_op(0xEF, self.isb, MOS6502.ABSOLUTE_READMODIFYWRITE)
        self.add_op(0xFF, self.isb, MOS6502.ABSOLUTEX_READMODIFYWRITE)
        self.add_op(0xFB, self.isb, MOS6502.ABSOLUTEY_READMODIFYWRITE)
        self.add_op(0xE7, self.isb, MOS6502.ZERO_READMODIFYWRITE)
        self.add_op(0xF7, self.isb, MOS6502.ZEROX_READMODIFYWRITE)
        self.add_op(0xE3, self.isb, MOS6502.INDIRECTX_READMODIFYWRITE)
        self.add_op(0xF3, self.isb, MOS6502.INDIRECTY_READMODIFYWRITE)

        # JMP
        self.add_op(0x4C, self.jmp, MOS6502.ABSOLUTE_WRITE)
        self.add_op(0x6C, self.jmp, MOS6502.INDIRECT)

        # JSR
        self.add_op(0x20, self.jsr, MOS6502.IMPLIED)

        # LAS
        self.add_op(0xBB, self.las, MOS6502.ABSOLUTEY_READ)

        # LAX
        self.add_op(0xAF, self.lax, MOS6502.ABSOLUTE_READ)
        self.add_op(0xBF, self.lax, MOS6502.ABSOLUTEY_READ)
        self.add_op(0xA7, self.lax, MOS6502.ZERO_READ)
        self.add_op(0xB7, self.lax, MOS6502.ZEROY_READ)
        self.add_op(0xA3, self.lax, MOS6502.INDIRECTX_READ)
        self.add_op(0xB3, self.lax, MOS6502.INDIRECTY_READ)

        # LDA
        self.add_op(0xA9, self.lda, MOS6502.IMMEDIATE_READ)
        self.add_op(0xA5, self.lda, MOS6502.ZERO_READ)
        self.add_op(0xB5, self.lda, MOS6502.ZEROX_READ)
        self.add_op(0xAD, self.lda, MOS6502.ABSOLUTE_READ)
        self.add_op(0xBD, self.lda, MOS6502.ABSOLUTEX_READ)
        self.add_op(0xB9, self.lda, MOS6502.ABSOLUTEY_READ)
        self.add_op(0xA1, self.lda, MOS6502.INDIRECTX_READ)
        self.add_op(0xB1, self.lda, MOS6502.INDIRECTY_READ)

        # LDX
        self.add_op(0xA2, self.ldx, MOS6502.IMMEDIATE_READ)
        self.add_op(0xA6, self.ldx, MOS6502.ZERO_READ)
        self.add_op(0xB6, self.ldx, MOS6502.ZEROY_READ)
        self.add_op(0xAE, self.ldx, MOS6502.ABSOLUTE_READ)
        self.add_op(0xBE, self.ldx, MOS6502.ABSOLUTEY_READ)

        # LDY
        self.add_op(0xA0, self.ldy, MOS6502.IMMEDIATE_READ)
        self.add_op(0xA4, self.ldy, MOS6502.ZERO_READ)
        self.add_op(0xB4, self.ldy, MOS6502.ZEROX_READ)
        self.add_op(0xAC, self.ldy, MOS6502.ABSOLUTE_READ)
        self.add_op(0xBC, self.ldy, MOS6502.ABSOLUTEX_READ)

        # LSRA
        self.add_op(0x4A, self.lsra, MOS6502.IMPLIED)

        # LSR
        self.add_op(0x46, self.lsr, MOS6502.ZERO_READMODIFYWRITE)
        self.add_op(0x56, self.lsr, MOS6502.ZEROX_READMODIFYWRITE)
        self.add_op(0x4E, self.lsr, MOS6502.ABSOLUTE_READMODIFYWRITE)
        self.add_op(0x5E, self.lsr, MOS6502.ABSOLUTEX_READMODIFYWRITE)

        # LXA
        self.add_op(0xAB, self.lxa, MOS6502.IMMEDIATE_READ)

        # NOP
        self.add_op(0x1A, self.nop, MOS6502.IMPLIED)
        self.add_op(0x3A, self.nop, MOS6502.IMPLIED)
        self.add_op(0x5A, self.nop, MOS6502.IMPLIED)
        self.add_op(0x7A, self.nop, MOS6502.IMPLIED)
        self.add_op(0xDA, self.nop, MOS6502.IMPLIED)
        self.add_op(0xEA, self.nop, MOS6502.IMPLIED)
        self.add_op(0xFA, self.nop, MOS6502.IMPLIED)
        self.add_op(0x80, self.nop, MOS6502.IMMEDIATE_READ)
        self.add_op(0x82, self.nop, MOS6502.IMMEDIATE_READ)
        self.add_op(0x89, self.nop, MOS6502.IMMEDIATE_READ)
        self.add_op(0xC2, self.nop, MOS6502.IMMEDIATE_READ)
        self.add_op(0xE2, self.nop, MOS6502.IMMEDIATE_READ)
        self.add_op(0x04, self.nop, MOS6502.ZERO_READ)
        self.add_op(0x44, self.nop, MOS6502.ZERO_READ)
        self.add_op(0x64, self.nop, MOS6502.ZERO_READ)
        self.add_op(0x14, self.nop, MOS6502.ZEROX_READ)
        self.add_op(0x34, self.nop, MOS6502.ZEROX_READ)
        self.add_op(0x54, self.nop, MOS6502.ZEROX_READ)
        self.add_op(0x74, self.nop, MOS6502.ZEROX_READ)
        self.add_op(0xD4, self.nop, MOS6502.ZEROX_READ)
        self.add_op(0xF4, self.nop, MOS6502.ZEROX_READ)
        self.add_op(0x0C, self.nop, MOS6502.ABSOLUTE_READ)
        self.add_op(0x1C, self.nop, MOS6502.ABSOLUTEX_READ)
        self.add_op(0x3C, self.nop, MOS6502.ABSOLUTEX_READ)
        self.add_op(0x5C, self.nop, MOS6502.ABSOLUTEX_READ)
        self.add_op(0x7C, self.nop, MOS6502.ABSOLUTEX_READ)
        self.add_op(0xDC, self.nop, MOS6502.ABSOLUTEX_READ)
        self.add_op(0xFC, self.nop, MOS6502.ABSOLUTEX_READ)

        # ORA
        self.add_op(0x09, self.ora, MOS6502.IMMEDIATE_READ)
        self.add_op(0x05, self.ora, MOS6502.ZERO_READ)
        self.add_op(0x15, self.ora, MOS6502.ZEROX_READ)
        self.add_op(0x0D, self.ora, MOS6502.ABSOLUTE_READ)
        self.add_op(0x1D, self.ora, MOS6502.ABSOLUTEX_READ)
        self.add_op(0x19, self.ora, MOS6502.ABSOLUTEY_READ)
        self.add_op(0x01, self.ora, MOS6502.INDIRECTX_READ)
        self.add_op(0x11, self.ora, MOS6502.INDIRECTY_READ)

        # Pxx
        self.add_op(0x48, self.pha, MOS6502.IMPLIED)
        self.add_op(0x08, self.php, MOS6502.IMPLIED)
        self.add_op(0x68, self.pla, MOS6502.IMPLIED)
        self.add_op(0x28, self.plp, MOS6502.IMPLIED)

        # RLA
        self.add_op(0x2F, self.rla, MOS6502.ABSOLUTE_READMODIFYWRITE)
        self.add_op(0x3F, self.rla, MOS6502.ABSOLUTEX_READMODIFYWRITE)
        self.add_op(0x3B, self.rla, MOS6502.ABSOLUTEY_READMODIFYWRITE)
        self.add_op(0x27, self.rla, MOS6502.ZERO_READMODIFYWRITE)
        self.add_op(0x37, self.rla, MOS6502.ZEROX_READMODIFYWRITE)
        self.add_op(0x23, self.rla, MOS6502.INDIRECTX_READMODIFYWRITE)
        self.add_op(0x33, self.rla, MOS6502.INDIRECTY_READMODIFYWRITE)

        # ROLA
        self.add_op(0x2A, self.rola, MOS6502.IMPLIED)

        # ROL
        self.add_op(0x26, self.rol, MOS6502.ZERO_READMODIFYWRITE)
        self.add_op(0x36, self.rol, MOS6502.ZEROX_READMODIFYWRITE)
        self.add_op(0x2E, self.rol, MOS6502.ABSOLUTE_READMODIFYWRITE)
        self.add_op(0x3E, self.rol, MOS6502.ABSOLUTEX_READMODIFYWRITE)

        # RORA
        self.add_op(0x6A, self.rora, MOS6502.IMPLIED)

        # ROR
        self.add_op(0x66, self.ror, MOS6502.ZERO_READMODIFYWRITE)
        self.add_op(0x76, self.ror, MOS6502.ZEROX_READMODIFYWRITE)
        self.add_op(0x6E, self.ror, MOS6502.ABSOLUTE_READMODIFYWRITE)
        self.add_op(0x7E, self.ror, MOS6502.ABSOLUTEX_READMODIFYWRITE)

        # RRA
        self.add_op(0x6F, self.rra, MOS6502.ABSOLUTE_READMODIFYWRITE)
        self.add_op(0x7F, self.rra, MOS6502.ABSOLUTEX_READMODIFYWRITE)
        self.add_op(0x7B, self.rra, MOS6502.ABSOLUTEY_READMODIFYWRITE)
        self.add_op(0x67, self.rra, MOS6502.ZERO_READMODIFYWRITE)
        self.add_op(0x77, self.rra, MOS6502.ZEROX_READMODIFYWRITE)
        self.add_op(0x63, self.rra, MOS6502.INDIRECTX_READMODIFYWRITE)
        self.add_op(0x73, self.rra, MOS6502.INDIRECTY_READMODIFYWRITE)

        # RTI
        self.add_op(0x40, self.rti, MOS6502.IMPLIED)

        # RTS
        self.add_op(0x60, self.rts, MOS6502.IMPLIED)

        # SAX
        self.add_op(0x8F, self.sax, MOS6502.ABSOLUTE_WRITE)
        self.add_op(0x87, self.sax, MOS6502.ZERO_WRITE)
        self.add_op(0x97, self.sax, MOS6502.ZEROY_WRITE)
        self.add_op(0x83, self.sax, MOS6502.INDIRECTX_WRITE)

        # SBC
        self.add_op(0xE9, self.sbc, MOS6502.IMMEDIATE_READ)
        self.add_op(0xEB, self.sbc, MOS6502.IMMEDIATE_READ)
        self.add_op(0xE5, self.sbc, MOS6502.ZERO_READ)
        self.add_op(0xF5, self.sbc, MOS6502.ZEROX_READ)
        self.add_op(0xED, self.sbc, MOS6502.ABSOLUTE_READ)
        self.add_op(0xFD, self.sbc, MOS6502.ABSOLUTEX_READ)
        self.add_op(0xF9, self.sbc, MOS6502.ABSOLUTEY_READ)
        self.add_op(0xE1, self.sbc, MOS6502.INDIRECTX_READ)
        self.add_op(0xF1, self.sbc, MOS6502.INDIRECTY_READ)

        # SBX
        self.add_op(0xCB, self.sbx, MOS6502.IMMEDIATE_READ)

        # SEx
        self.add_op(0x38, self.sec, MOS6502.IMPLIED)
        self.add_op(0xF8, self.sed, MOS6502.IMPLIED)
        self.add_op(0x78, self.sei, MOS6502.IMPLIED)

        # SHA
        self.add_op(0x9F, self.sha, MOS6502.ABSOLUTEY_WRITE)
        self.add_op(0x93, self.sha, MOS6502.INDIRECTY_WRITE)

        # SHS
        self.add_op(0x9B, self.shs, MOS6502.ABSOLUTEY_WRITE)

        # SHX
        self.add_op(0x9E, self.shx, MOS6502.ABSOLUTEY_WRITE)

        # SHY
        self.add_op(0x9C, self.shy, MOS6502.ABSOLUTEX_WRITE)

        # SLO
        self.add_op(0x0F, self.slo, MOS6502.ABSOLUTE_READMODIFYWRITE)
        self.add_op(0x1F, self.slo, MOS6502.ABSOLUTEX_READMODIFYWRITE)
        self.add_op(0x1B, self.slo, MOS6502.ABSOLUTEY_READMODIFYWRITE)
        self.add_op(0x07, self.slo, MOS6502.ZERO_READMODIFYWRITE)
        self.add_op(0x17, self.slo, MOS6502.ZEROX_READMODIFYWRITE)
        self.add_op(0x03, self.slo, MOS6502.INDIRECTX_READMODIFYWRITE)
        self.add_op(0x13, self.slo, MOS6502.INDIRECTY_READMODIFYWRITE)

        # SRE
        self.add_op(0x4F, self.sre, MOS6502.ABSOLUTE_READMODIFYWRITE)
        self.add_op(0x5F, self.sre, MOS6502.ABSOLUTEX_READMODIFYWRITE)
        self.add_op(0x5B, self.sre, MOS6502.ABSOLUTEY_READMODIFYWRITE)
        self.add_op(0x47, self.sre, MOS6502.ZERO_READMODIFYWRITE)
        self.add_op(0x57, self.sre, MOS6502.ZEROX_READMODIFYWRITE)
        self.add_op(0x43, self.sre, MOS6502.INDIRECTX_READMODIFYWRITE)
        self.add_op(0x53, self.sre, MOS6502.INDIRECTY_READMODIFYWRITE)

        # STA
        self.add_op(0x85, self.sta, MOS6502.ZERO_WRITE)
        self.add_op(0x95, self.sta, MOS6502.ZEROX_WRITE)
        self.add_op(0x8D, self.sta, MOS6502.ABSOLUTE_WRITE)
        self.add_op(0x9D, self.sta, MOS6502.ABSOLUTEX_WRITE)
        self.add_op(0x99, self.sta, MOS6502.ABSOLUTEY_WRITE)
        self.add_op(0x81, self.sta, MOS6502.INDIRECTX_WRITE)
        self.add_op(0x91, self.sta, MOS6502.INDIRECTY_WRITE)

        # STX
        self.add_op(0x86, self.stx, MOS6502.ZERO_WRITE)
        self.add_op(0x96, self.stx, MOS6502.ZEROY_WRITE)
        self.add_op(0x8E, self.stx, MOS6502.ABSOLUTE_WRITE)

        # STY
        self.add_op(0x84, self.sty, MOS6502.ZERO_WRITE)
        self.add_op(0x94, self.sty, MOS6502.ZEROX_WRITE)
        self.add_op(0x8C, self.sty, MOS6502.ABSOLUTE_WRITE)

        # Txx
        self.add_op(0xAA, self.tax, MOS6502.IMPLIED)
        self.add_op(0xA8, self.tay, MOS6502.IMPLIED)
        self.add_op(0xBA, self.tsx, MOS6502.IMPLIED)
        self.add_op(0x8A, self.txa, MOS6502.IMPLIED)
        self.add_op(0x9A, self.txs, MOS6502.IMPLIED)
        self.add_op(0x98, self.tya, MOS6502.IMPLIED)

        # Invalid (HALT) ops
        # 02, 12, 22, 32, 42, 52, 62, 72, 92, B2, D2, F2.
        self.add_op(0x02, self.hlt, MOS6502.IMPLIED)
        self.add_op(0x12, self.hlt, MOS6502.IMPLIED)
        self.add_op(0x22, self.hlt, MOS6502.IMPLIED)
        self.add_op(0x32, self.hlt, MOS6502.IMPLIED)
        self.add_op(0x42, self.hlt, MOS6502.IMPLIED)
        self.add_op(0x52, self.hlt, MOS6502.IMPLIED)
        self.add_op(0x62, self.hlt, MOS6502.IMPLIED)
        self.add_op(0x72, self.hlt, MOS6502.IMPLIED)
        self.add_op(0x92, self.hlt, MOS6502.IMPLIED)
        self.add_op(0xB2, self.hlt, MOS6502.IMPLIED)
        self.add_op(0xD2, self.hlt, MOS6502.IMPLIED)
        self.add_op(0xF2, self.hlt, MOS6502.IMPLIED)
