#!/usr/bin/env python
# -*- coding:utf-8

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from hardware.Z80.z80 import Z80, Z80Flags, REGS_SRC
from hardware.memory import RAM

class BaseZ80Test(unittest.TestCase):
    def setUp(self):
        self.m = RAM(16, 8)
        self.c = Z80(1, self.m)
        self.c.reset() # just in case ;)
    
    def tearDown(self):
        pass

class Z80Test(BaseZ80Test):
    """base Z80 tests"""
    def test_reset(self):
        """ Z80: reset """
        self.c.reset()
        self.assertEquals(self.c.AF, 0xFFFF)
        self.assertEquals(self.c.SP, 0xFFFF)
        self.assertEquals(self.c.PC, 0x0000)
        
        self.assertEquals(self.c.I, 0x00)
        self.assertEquals(self.c.R, 0x00)
        
        #self.assertEquals(self.c.IM, Z80.IM0)
        
        self.assertEquals(self.c.IFF1, False)
        self.assertEquals(self.c.IFF2, False)
        #self.assertEquals(self.c.HALT, False)

class Z808BitLoadTest(BaseZ80Test):
    """8bit load group"""
    def test_ld_r_r(self):
        """Z80: LD r, r'"""
        for dst in range(0, 0x08):
            for src in range(0, 0x08):
                if (src not in REGS_SRC) or (dst not in REGS_SRC): continue
                op = 0x40 + (dst << 3) + src
                #print '%02X' % op
                sreg = REGS_SRC[src]
                dreg = REGS_SRC[dst]
                self.c.reset()
                setattr(self.c, sreg, 0x10)
                if sreg != dreg:
                    setattr(self.c, dreg, 0x8A)
                self.c.write(0x0000, op)
                self.c.run()
                self.assertEquals(getattr(self.c, dreg), 0x10, \
                    '0x%02X LD %s, %s: 0x%02X(exp 0x10) != 0x%02X' \
                    % (op, dreg, sreg, getattr(self.c, dreg), getattr(self.c, sreg)))
                self.assertEquals(self.c.PC, 0x0001)
                self.assertEquals(self.c.abs_T, 4)
    
    def test_ld_r_n(self):
        """Z80: LD r, n"""
        for dst in range(0, 0x08):
            if dst not in REGS_SRC: continue
            op = (dst << 3) + 0x06
            dreg = REGS_SRC[dst]
            self.c.reset()
            self.c.write(0x0000, op)
            self.c.write(0x0001, 0xA5)
            self.c.run()
            self.assertEquals(getattr(self.c, dreg), 0xA5,
                '0x%02X LD %s, 0xA5: 0x%02X != 0xA5' % (op, dreg, getattr(self.c, dreg)))
            self.assertEquals(self.c.PC, 0x0002)
            self.assertEquals(self.c.abs_T, 7)
    
    def test_ld_r_hl(self):
        """Z80: LD r, (HL)"""
        for dst in range(0, 0x08):
            if dst not in REGS_SRC: continue
            op = (dst << 3) + 0x46
            dreg = REGS_SRC[dst]
            self.c.reset()
            self.c.HL = 0x75A1
            self.c.write(self.c.HL, 0x58)
            self.c.write(0x0000, op)
            self.c.run()
            self.assertEquals(getattr(self.c, dreg), 0x58,
                '0x%02X LD %s, (HL): 0x%02X != 0x58' % (op, dreg, getattr(self.c, dreg)))
            self.assertEquals(self.c.PC, 0x0001)
            self.assertEquals(self.c.abs_T, 7)
    
    def test_ld_hl_r(self):
        """Z80: LD (HL), r"""
        for src in range(0, 0x08):
            if src not in REGS_SRC: continue
            op = src + 0x70
            sreg = REGS_SRC[src]
            self.c.reset()
            self.c.HL = 0x2146
            setattr(self.c, sreg, 0x29)
            self.c.write(0x0000, op)
            self.c.run()
            self.assertEquals(self.c.read(self.c.HL), 0x29,
                '0x%02X LD (HL), %s: 0x%02X != 0x29' % (op, sreg, self.c.read(self.c.HL)))
            self.assertEquals(self.c.PC, 0x0001)
            self.assertEquals(self.c.abs_T, 7)
    
    def test_ld_r_ixd(self):
        """Z80: LD r, (IX + d)"""
        for dst in range(0, 0x08):
            if dst not in REGS_SRC: continue
            op = (dst << 3) + 0x46
            dreg = REGS_SRC[dst]
            self.c.reset()
            self.c.IX = 0x25AF
            self.c.write(0x25C8, 0x39) # IX + 0x19
            self.c.write(0x0000, 0xDD)
            self.c.write(0x0001, op)
            self.c.write(0x0002, 0x19)
            self.c.run()
            self.assertEquals(getattr(self.c, dreg), 0x39,
                '0x%02X LD %s, (IX + 0x19): 0x%02X != 0x39' % (op, dreg, getattr(self.c, dreg)))
            self.assertEquals(self.c.PC, 0x0003)
            self.assertEquals(self.c.abs_T, 19)
        
        for dst in range(0, 0x08):
            if dst not in REGS_SRC: continue
            op = (dst << 3) + 0x46
            dreg = REGS_SRC[dst]
            self.c.reset()
            self.c.IX = 0x25AF
            self.c.write(0x2596, 0x39) # IX - 0x19
            self.c.write(0x0000, 0xDD)
            self.c.write(0x0001, op)
            self.c.write(0x0002, 0xE7)
            self.c.run()
            self.assertEquals(getattr(self.c, dreg), 0x39,
                '0x%02X LD %s, (IX - 0x19): 0x%02X != 0x39' % (op, dreg, getattr(self.c, dreg)))
            self.assertEquals(self.c.PC, 0x0003)
            self.assertEquals(self.c.abs_T, 19)
    
    def test_ld_ixd_r(self):
        """Z80: LD (IX + d), r"""
        for r in range(0, 0x08):
            if r not in REGS_SRC: continue
            op = r + 0x70
            reg = REGS_SRC[r]
            self.c.reset()
            setattr(self.c, reg, 0x1C)
            self.c.IX = 0x3100
            off = 0x06
            self.c.write(0x0000, 0xDD)
            self.c.write(0x0001, op)
            self.c.write(0x0002, off)
            self.c.run()
            self.assertEquals(self.c.read(self.IX + off), 0x1C,
                '0x%02X LD (IX + 0x06), %s: 0x%02X != 0x1C' % (op, dreg, self.c.read(self.IX + off)))
            self.assertEquals(self.c.PC, 0x0003)
            self.assertEquals(self.c.abs_T, 19)
        
        for r in range(0, 0x08):
            if r not in REGS_SRC: continue
            op = r + 0x70
            reg = REGS_SRC[r]
            self.c.reset()
            setattr(self.c, reg, 0x1C)
            self.c.IX = 0x3100
            off = -0x06
            self.c.write(0x0000, 0xDD)
            self.c.write(0x0001, op)
            self.c.write(0x0002, 0xFA) # 2'nd complement off
            self.c.run()
            self.assertEquals(self.c.read(self.IX - off), 0x1C,
                '0x%02X LD (IX - 0x06), %s: 0x%02X != 0x1C' % (op, dreg, self.c.read(self.IX + off)))
            self.assertEquals(self.c.PC, 0x0003)
            self.assertEquals(self.c.abs_T, 19)
    
    def test_ld_r_iyd(self):
        """Z80: LD r, (IY + d)"""
        for dst in range(0, 0x08):
            if dst not in REGS_SRC: continue
            op = (dst << 3) + 0x46
            dreg = REGS_SRC[dst]
            self.c.reset()
            self.c.IX = 0x25AF
            self.c.write(0x25C8, 0x39) # IY + 0x19
            self.c.write(0x0000, 0xFD)
            self.c.write(0x0001, op)
            self.c.write(0x0002, 0x19)
            self.c.run()
            self.assertEquals(getattr(self.c, dreg), 0x39,
                '0x%02X LD %s, (IY + 0x19): 0x%02X != 0x39' % (op, dreg, getattr(self.c, dreg)))
            self.assertEquals(self.c.PC, 0x0003)
            self.assertEquals(self.c.abs_T, 19)
        
        for dst in range(0, 0x08):
            if dst not in REGS_SRC: continue
            op = (dst << 3) + 0x46
            dreg = REGS_SRC[dst]
            self.c.reset()
            self.c.IX = 0x25AF
            self.c.write(0x2596, 0x39) # IY - 0x19
            self.c.write(0x0000, 0xFD)
            self.c.write(0x0001, op)
            self.c.write(0x0002, 0xE7)
            self.c.run()
            self.assertEquals(getattr(self.c, dreg), 0x39,
                '0x%02X LD %s, (IY - 0x19): 0x%02X != 0x39' % (op, dreg, getattr(self.c, dreg)))
            self.assertEquals(self.c.PC, 0x0003)
            self.assertEquals(self.c.abs_T, 19)
    
    def test_ld_iyd_r(self):
        """Z80: LD (IY + d), r"""
        for r in range(0, 0x08):
            if r not in REGS_SRC: continue
            op = r + 0x70
            reg = REGS_SRC[r]
            self.c.reset()
            setattr(self.c, reg, 0x1C)
            self.c.IY = 0x3100
            off = 0x06
            self.c.write(0x0000, 0xFD)
            self.c.write(0x0001, op)
            self.c.write(0x0002, off)
            self.c.run()
            self.assertEquals(self.c.read(self.IX + off), 0x1C,
                '0x%02X LD (IY + 0x06), %s: 0x%02X != 0x1C' % (op, dreg, self.c.read(self.IY + off)))
            self.assertEquals(self.c.PC, 0x0003)
            self.assertEquals(self.c.abs_T, 19)
        
        for r in range(0, 0x08):
            if r not in REGS_SRC: continue
            op = r + 0x70
            reg = REGS_SRC[r]
            self.c.reset()
            setattr(self.c, reg, 0x1C)
            self.c.IY = 0x3100
            off = -0x06
            self.c.write(0x0000, 0xFD)
            self.c.write(0x0001, op)
            self.c.write(0x0002, 0xFA) # 2'nd complement off
            self.c.run()
            self.assertEquals(self.c.read(self.IY - off), 0x1C,
                '0x%02X LD (IY - 0x06), %s: 0x%02X != 0x1C' % (op, dreg, self.c.read(self.IY + off)))
            self.assertEquals(self.c.PC, 0x0003)
            self.assertEquals(self.c.abs_T, 19)
    
    def test_ld_hl_n(self):
        """Z80: LD (HL), n"""
        cpu = self.c
        cpu.HL = 0x4444
        cpu.write(0x0000, 0x36)
        cpu.write(0x0001, 0x28)
        cpu.run()
        self.assertEquals(cpu.read(cpu.HL), 0x28)
        self.assertEquals(self.c.PC, 0x0002)
        self.assertEquals(self.c.abs_T, 10)
    
    def test_ld_ix_n(self):
        """Z80: LD (IX + d), n"""
        cpu = self.c
        cpu.IX = 0x219A
        # LD (IX + 0x05), 0x5A
        cpu.write(0x0000, 0xDD)
        cpu.write(0x0001, 0x36)
        cpu.write(0x0002, 0x05)
        cpu.write(0x0003, 0x5A)
        cpu.run()
        self.assertEquals(cpu.read(0x219F), 0x5A)
        self.assertEquals(self.c.PC, 0x0004)
        self.assertEquals(self.c.abs_T, 19)
    
    def test_ld_iy_n(self):
        """Z80: LD (IY + d), n"""
        cpu = self.c
        cpu.IY = 0xA940
        # LD (IY + 0x10), 0x97
        cpu.write(0x0000, 0xFD)
        cpu.write(0x0001, 0x36)
        cpu.write(0x0002, 0x10)
        cpu.write(0x0003, 0x97)
        cpu.run()
        self.assertEquals(cpu.read(0xA950), 0x97)
        self.assertEquals(self.c.PC, 0x0004)
        self.assertEquals(self.c.abs_T, 19)
    
    def test_ld_a_bc(self):
        """Z80: LD A, (BC)"""
        cpu = self.c
        cpu.BC = 0x4747
        cpu.write(cpu.BC, 0x12)
        # LD A, (BC)
        cpu.write(0x0000, 0x0A)
        cpu.run()
        self.assertEquals(cpu.A, 0x12)
        self.assertEquals(self.c.PC, 0x0001)
        self.assertEquals(self.c.abs_T, 7)
    
    def test_ld_a_de(self):
        """Z80: LD A, (DE)"""
        cpu = self.c
        cpu.DE = 0x30A2
        cpu.write(cpu.BC, 0x22)
        # LD A, (DE)
        cpu.write(0x0000, 0x1A)
        cpu.run()
        self.assertEquals(cpu.A, 0x22)
        self.assertEquals(self.c.PC, 0x0001)
        self.assertEquals(self.c.abs_T, 7)
    
    def test_ld_a_nn(self):
        """Z80: LD A, (nn)"""
        cpu = self.c
        cpu.write(0x8832, 0x04)
        # LD A, (0x8832)
        cpu.write(0x0000, 0x3A)
        cpu.write16(0x0001, 0x8832)
        cpu.run()
        self.assertEquals(cpu.A, 0x04)
        self.assertEquals(self.c.PC, 0x0003)
        self.assertEquals(self.c.abs_T, 13)
    
    def test_ld_bc_a(self):
        """Z80: LD (BC), A"""
        cpu = self.c
        cpu.BC = 0x1212
        cpu.A = 0x7A
        # LD (BC), A
        cpu.write(0x0000, 0x02)
        cpu.run()
        self.assertEquals(cpu.read(cpu.BC), cpu.A)
        self.assertEquals(self.c.PC, 0x0001)
        self.assertEquals(self.c.abs_T, 7)
    
    def test_ld_de_a(self):
        """Z80: LD (DE), A"""
        cpu = self.c
        cpu.DE = 0x1128
        cpu.A = 0xA0
        # LD (DE), A
        cpu.write(0x0000, 0x12)
        cpu.run()
        self.assertEquals(cpu.read(cpu.DE), cpu.A)
        self.assertEquals(self.c.PC, 0x0001)
        self.assertEquals(self.c.abs_T, 7)
    
    def test_ld_nn_a(self):
        """Z80: LD (nn), A"""
        cpu = self.c
        cpu.A = 0xD7
        # LD (0x3141), A
        cpu.write(0x0000, 0x32)
        cpu.write16(0x0001, 0x3141)
        cpu.run()
        self.assertEquals(cpu.read(0x3141), cpu.A)
        self.assertEquals(self.c.PC, 0x0003)
        self.assertEquals(self.c.abs_T, 13)
    
    def test_ld_a_i(self):
        """Z80: LD A, I"""
        cpu = self.c
        # LD A, I
        cpu.write(0x0000, 0xED)
        cpu.write16(0x0001, 0x57)
        cpu.run()
        self.assertEquals(self.c.PC, 0x0003)
        self.assertEquals(self.c.abs_T, 9)
        self.fail('Not implemented')
    
    def test_ld_i_a(self):
        """Z80: LD I, A"""
        cpu = self.c
        # LD I, A
        cpu.write(0x0000, 0xED)
        cpu.write16(0x0001, 0x47)
        cpu.run()
        self.assertEquals(self.c.PC, 0x0003)
        self.assertEquals(self.c.abs_T, 9)
        self.fail('Not implemented')
    
    def test_ld_a_r(self):
        """Z80: LD A, R"""
        cpu = self.c
        # LD A, R
        cpu.write(0x0000, 0xED)
        cpu.write16(0x0001, 0x5F)
        cpu.run()
        self.assertEquals(self.c.PC, 0x0003)
        self.assertEquals(self.c.abs_T, 9)
        self.fail('Not implemented')
    
    def test_ld_r_a(self):
        """Z80: LD R, A"""
        cpu = self.c
        # LD R, A
        cpu.write(0x0000, 0xED)
        cpu.write16(0x0001, 0x4F)
        cpu.run()
        self.assertEquals(self.c.PC, 0x0003)
        self.assertEquals(self.c.abs_T, 9)
        self.fail('Not implemented')


# =======
# = RUN =
# =======
if __name__ == '__main__':
    unittest.main()
