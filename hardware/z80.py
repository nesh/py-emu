import random, ctypes, sys
from cpu import CPU, CPUReset
from register import CRegister16_8, CRegister16, CRegister8
from pydispatch.dispatcher import send


class _Z80Flags(ctypes.Structure):
    _fields_ = (
        ('C', ctypes.c_uint8, 1),  # 0
        ('N', ctypes.c_uint8, 1),  # 1
        ('V', ctypes.c_uint8, 1),  # 2
        ('F3', ctypes.c_uint8, 1), # 3
        ('H', ctypes.c_uint8, 1),  # 4
        ('F5', ctypes.c_uint8, 1), # 5
        ('Z', ctypes.c_uint8, 1),  # 6
        ('S', ctypes.c_uint8, 1),  # 7
    )

class Z80Flags(ctypes.Union):
    _fields_ = (
        ('flag', _Z80Flags),
        ('byte', ctypes.c_uint8)
    )

if sys.byteorder == "little":
    class _AF(ctypes.Structure):
        """Structure with little endian byte order"""
        _fields_ = (
            ('lo', Z80Flags), # low
            ('hi', ctypes.c_uint8), # high
        )
elif sys.byteorder == "big":
    class _AF(ctypes.Structure):
        """Structure with big endian byte order"""
        _fields_ = (
            ('hi', ctypes.c_uint8), # high
            ('lo', Z80Flags), # low
        )
else:
    raise RuntimeError("Invalid byteorder")

class AF(ctypes.Union):
    _fields_ = (
        ('word', ctypes.c_uint16),
        ('byte', _AF)
    )

class Z80R(ctypes.Structure):
    _fields_ = (
        ('byte', ctypes.c_uint8, 7),  # 0
    )


# Parity table for 256 bytes (True = even parity, False = odd parity)
P_TABLE = (
    True, False, False, True, False, True, True, False, False, True, True, False, True, False, False, True,
    False, True, True, False, True, False, False, True, True, False, False, True, False, True, True, False,
    False, True, True, False, True, False, False, True, True, False, False, True, False, True, True, False,
    True, False, False, True, False, True, True, False, False, True, True, False, True, False, False, True,
    False, True, True, False, True, False, False, True, True, False, False, True, False, True, True, False,
    True, False, False, True, False, True, True, False, False, True, True, False, True, False, False, True,
    True, False, False, True, False, True, True, False, False, True, True, False, True, False, False, True,
    False, True, True, False, True, False, False, True, True, False, False, True, False, True, True, False,
    False, True, True, False, True, False, False, True, True, False, False, True, False, True, True, False,
    True, False, False, True, False, True, True, False, False, True, True, False, True, False, False, True,
    True, False, False, True, False, True, True, False, False, True, True, False, True, False, False, True,
    False, True, True, False, True, False, False, True, True, False, False, True, False, True, True, False,
    True, False, False, True, False, True, True, False, False, True, True, False, True, False, False, True,
    False, True, True, False, True, False, False, True, True, False, False, True, False, True, True, False,
    False, True, True, False, True, False, False, True, True, False, False, True, False, True, True, False,
    True, False, False, True, False, True, True, False, False, True, True, False, True, False, False, True,
)

# Half carry table (addition)
ADD_H_TABLE = (False, False, True, False, True, False, True, True)

# Half carry table (subtraction).
SUB_H_TABLE = (False, True, True, True, False, False, False, True)

# Overflow table (addition).
ADD_V_TABLE = (False, True, False, False, False, False, True, False)

# Overflow table (subtraction)
SUB_V_TABLE  = (False, False, False, True, True, False, False, False)

class Z80(CPU):
    RESET_VECTOR = 0x0000
    S  = 0x80 # 7
    Z  = 0x40 # 6
    F5 = 0x20 # 5
    H  = 0x10 # 4
    F3 = 0x08 # 3
    V  = 0x04 # 2
    N  = 0x02 # 1
    C  = 0x01 # 0

    IM0, IM1, IM2 = range(3)

    BIT_16 = (
        'AF', 'BC', 'DE', 'HL',
        'AF1', 'BC1', 'DE1', 'HL1',
        'IX', 'IY',
        'SP', 'PC',
    )
    BIT_8 = ('R', 'I', 'IM')
    BIT_1 = ('IFF1', 'IFF2', 'HALT')
    
    def __init__(self, break_afer, mem, io=None):
        self.AF = AF(random.randint(0, 0xFFFF))
        self.F = self.AF.byte.lo # shortcut

        self.BC = CRegister16_8(random.randint(0, 0xFFFF))
        self.DE = CRegister16_8(random.randint(0, 0xFFFF))
        self.HL = CRegister16_8(random.randint(0, 0xFFFF))
        self.AF1 = CRegister16_8(random.randint(0, 0xFFFF))
        self.BC1 = CRegister16_8(random.randint(0, 0xFFFF))
        self.DE1 = CRegister16_8(random.randint(0, 0xFFFF))
        self.HL1 = CRegister16_8(random.randint(0, 0xFFFF))
        
        self.IX = CRegister16_8(random.randint(0, 0xFFFF))
        self.IY = CRegister16_8(random.randint(0, 0xFFFF))
        self.PC = CRegister16(random.randint(0, 0xFFFF))
        self.SP = CRegister16(random.randint(0, 0xFFFF))
        self.R = Z80R(random.randint(0, 0xFF))
        self.I = CRegister8(random.randint(0, 0xFF))
        self.IM = random.randint(0, 2)
        
        self.IFF1 = random.randint(0, 1)
        self.IFF2 = random.randint(0, 1)
        self.HALT = random.randint(0, 1)
        
        super(Z80, self).__init__(break_afer, mem, io)
        
    def reset(self):
        # according to http://www.z80.info/interrup.htm

        self.AF.word = 0xFFFF
        self.SP.word = 0xFFFF
        self.PC.word = Z80.RESET_VECTOR

        self.I.byte = 0x00
        self.R.byte = 0x00
        
        self.IFF1 = False
        self.IFF2 = False
        self.HALT = False

        self.IM = Z80.IM0

        self.T = 0
        self.abs_T = 0
        
    def _read_op(self):
        ret = self.mem.read(self.PC.word)
        self.PC.word += 1
        self.R.byte += 1
        return ret

    def read_word(self, adr):
        return self.mem.read(adr) + (self.mem.read(adr + 1) * 256)

    def _read_param(self):
        ret = int(self.mem.read(self.PC.word))
        self.PC.word += 1
        return ret
        
    def _read_param_word(self):
        ret = self.mem.read(self.PC.word) + (self.mem.read(self.PC.word + 1) * 256)
        self.PC.word += 2
        return ret
    
    def run(self, cycles=None):
        if not cycles:
            cycles = self.break_after
        self.T = cycles

        while self.T > 0:
            opcode = self._read_op()
            cycles_used, ln, handler, addr, mnemo = self._op[opcode]
            handler(addr)
            self.T -= cycles_used
            self.abs_T += cycles_used
            
    def set_state(self, state):
        """set cpu state

           set current cpu state
        """
        for reg, val in state.items():
            reg = reg.upper()
            r = getattr(self, reg)
            if reg in Z80.BIT_16:
                r.word = val
                print '%s\t=\t$%04X' % (reg, r.word)
            elif reg in Z80.BIT_8:
                r.byte = val
                print '%s\t=\t$%02X' % (reg, r.byte)
            elif reg in Z80.BIT_1:
                r = not not val
                print '%s\t=\t%s' % (reg, r)

    # dissasembler

    def _dis_instr(self, opcode, address, mnemo, prefix='$'):
        """
            # - word
        """
        ret = mnemo[:] # copy
        if '^' in ret:
            ret = ret.replace('^', '%s%02X' % (prefix, self.mem.read(address)))
            address += 1
        if '*' in ret:
            ret = ret.replace('*', '%s%02X' % (prefix, self.mem.read(address)))
            address += 1
        if '#' in ret:
            ret = ret.replace('#', '%s%04X' % (prefix, self.read_word(address)))
            address += 2

        return ret

    def disassemble(self, address, instruction_count=1, dump_adr=True, dump_hex=True):
        ret = []
        
        for i in range(0, instruction_count):
            line = []
            if i > 1:
                ret.append('\n')
            if dump_adr:
                line.append('%04X:' % address)
            opcode = self.mem.read(address)
            cycles_used, ln, handler, addr, mnemo = self._op[opcode]
            address += 1

            if dump_hex:
                h = ['%02X' % opcode]
                for n in range(0, ln - 1):
                    h.append('%02X' % self.mem.read(address + n))
                if len(h):
                    line.append(' '.join(h))
            line.append(self._dis_instr(opcode, address, mnemo))
            ret.append(' '.join(line))
            
        return ''.join(ret)

    # helpers
    def inc8_flags(self, work8):
        self.F.flag.S = not not (work8 & 0x80)
        self.F.flag.Z = not work8
        self.F.flag.H = not (work8 & 0x0f)
        self.F.flag.PV = work8 == 0x80
        self.F.flag.N = False
        self.F.flag.F3 = not not (work8 & Z80.F3)
        self.F.flag.F5 = not not (work8 & Z80.F5)
        
    def dec8_flags(self, work8):
        self.F.flag.S = not not (work8 & 0x80)
        self.F.flag.Z = work8 == 0
        self.F.flag.H = (work8 & 0x0f) == 0x0f
        self.F.flag.PV = work8 == 0x7f
        self.F.flag.N = True
        self.F.flag.F3 = not not (work8 & Z80.F3)
        self.F.flag.F5 = not not(work8 & Z80.F5)

    def add_hl(self, val16):
        hl = self.HL.word
        work32 = hl + val16
        idx = ((hl & 0x800) >> 9) | ((val16 & 0x800) >> 10) | ((work32 & 0x800) >> 11)
        self.HL.word = work32
        self.F.flag.H = ADD_H_TABLE[idx]
        self.F.flag.N = False
        self.F.flag.C = not not (work32 & 0x10000)
        self.F.flag.F5 = not not (((work32 >> 8) & 0xFF) & Z80.F5)
        self.F.flag.F3 = not not (((work32 >> 8) & 0xFF) & Z80.F3)

    def _bc_ind(self):
        return int(self.mem.read(self.BC.word))

    # OPCODES
    def _opcodes(self):
        """
            0 cycles
            1 len
            2 handler
            3 address handler
            4 mnemo
        """
        
        # main table
        ret = []
        for x in range(0x100):
            ret.append((0, 1, self._invalid_op, x, 'INVALID OP $%02X' % x))

        # Real instructions
        ret[0x00] = (4, 1, self.nop, None, 'nop')
        ret[0x01] = (10, 3, self.ld_bc, self._read_param_word, 'ld bc,#')
        ret[0x02] = (7, 1, self.ld_bc_a, None, 'ld (bc),a')
        ret[0x03] = (6, 1, self.inc_bc, None, 'inc bc')
        ret[0x04] = (4, 1, self.inc_b, None, 'inc b')
        ret[0x05] = (4, 1, self.dec_b, None, 'dec b')
        ret[0x06] = (7, 2, self.ld_b_n, self._read_param, 'ld b,*')
        ret[0x07] = (4, 1, self.rlca, None, 'rlca')
        ret[0x08] = (4, 1, self.ex_af_af1, None, "ex af,af'")
        ret[0x09] = (11, 1, self.add_hl_bc, None, "add hl, bc'")
        ret[0x0A] = (7, 1, self.ld_a, self._bc_ind, "ld a,(bc)'")
        ret[0x0B] = (6, 1, self.dec_bc, None, "dec bc'")
        
        return ret

    def nop(self, adr_handler):
        pass
        
    def ld_bc(self, adr_handler):
        self.BC.word = adr_handler()
        
    def ld_bc_a(self, adr_handler):
        self.mem.write(self.BC.word, self.AF.byte.hi)
        
    def inc_bc(self, adr_handler):
        self.BC.word += 1
        
    def inc_b(self, adr_handler):
        self.BC.byte.hi += 1
        self.inc8_flags(self.BC.byte.hi)
        
    def dec_b(self, adr_handler):
        self.BC.byte.hi -= 1
        self.dec8_flags(self.BC.byte.hi)
        
    def ld_b_n(self, adr_handler):
        self.BC.byte.hi = adr_handler()

    def rlca(self, adr_handler):
        self.F.flag.C = not not (self.AF.byte.hi & 0x80)
        self.AF.byte.hi = (self.AF.byte.hi << 1) | self.F.flag.C
        self.F.flag.H = False
        self.F.flag.N = False

    def ex_af_af1(self, adr_handler):
        self.AF.word, self.AF1.word = self.AF1.word, self.AF.word
        
    def add_hl_bc(self, adr_handler):
        self.add_hl(self.BC.word)
        
    def ld_a(self, adr_handler):
        self.AF.byte.hi = adr_handler()
        
    def dec_bc(self, adr_handler):
        self.BC.word -= 1
