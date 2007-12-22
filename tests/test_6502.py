#!/usr/bin/env python
# -*- coding:utf-8

import os, sys
import unittest
import random
import zipfile, StringIO

import config

from hardware.MOS65xx.MOS6502 import MOS6502, MOS6502Flags
from hardware.memory import RAM
from hardware.cpu import CPUException

def eqx(a, b, msg=None):
    """Shorthand for 'assert a == b, "%X != %X" % (a, b)
    """
    assert a == b, msg or "$%X != $%X" % (a, b)

class MOS6502FlagsTest(unittest.TestCase):
    def setUp(self):
        self.f = MOS6502Flags(0)
    
    def test_multiple(self):
        """ MOS6502Flags: multiple set/reset """
        self.f.c = True
        self.f.z = True
        self.f.d = True
        self.assertEquals(int(self.f), MOS6502Flags.C | MOS6502Flags.Z | MOS6502Flags.D)
        self.f.z = False
        self.assertEquals(self.f.get(), MOS6502Flags.C | MOS6502Flags.D)
    
    def test_multiple2(self):
        """ MOS6502Flags: multiple set/reset from byte """
        self.f.set(MOS6502Flags.C | MOS6502Flags.Z | MOS6502Flags.D)
        self.assertEquals(self.f.c, True)
        self.assertEquals(self.f.z, True)
        self.assertEquals(self.f.d, True)
        self.assertEquals(self.f.f5, False)
    
    def test_str(self):
        """ MOS6502Flags: test __str__ """
        self.f.set(0xFF)
        self.assertEquals(str(self.f), 'SVUBDIZC')


class MOS6502Test(unittest.TestCase):
    def setUp(self):
        self.m = RAM(16, 8)
        self.c = MOS6502(1, self.m)
    
    def tearDown(self):
        pass
    
    def test_bo(self):
        """ MOS6502: test byteorder r/w """
        self.m.write(0x215F, 0x76)
        self.m.write(0x2160, 0x30)
        self.assertEquals(self.c.read_word(0x215F), 0x3076)
        
        self.c.write_word(0x215F, 0x3076)
        self.assertEquals(self.c.read_word(0x215F), 0x3076)
    
    def test_reset(self):
        """ MOS6502: reset """
        self.m.write(MOS6502.RESET_VECTOR, 0x76)
        self.m.write(MOS6502.RESET_VECTOR + 1, 0x30)
        
        self.c.reset()
        self.assertEquals(self.c.A, 0)
        self.assertEquals(self.c.X, 0)
        self.assertEquals(self.c.Y, 0)
        
        self.assertEquals(self.c.S, 0xFF)
        self.assertEquals(self.c.P.get(), 0x20)
        self.assertEquals(self.c.PC, 0x3076)
    
    def test_am_1(self):
        """ MOS6502: AM -- Immediate """
        self.c.PC = 0x215F
        self.m.write(0x215F, 0x0A)
        
        self.assertEquals(self.c._read_immediate(), 0x0A)
        self.assertEquals(self.c.PC, 0x215F + 1)
    
    def test_am_2(self):
        """ MOS6502: AM -- Absolute """
        self.c.PC = 0x215F
        self.c.write_word(0x215F, 0x31F6)
        self.m.write(0x31F6, 0xAA)
        
        self.assertEquals(self.c._read_absolute(), 0xAA)
        self.assertEquals(self.c.PC, 0x215F + 2)
    
    def test_am_3(self):
        """ MOS6502: AM -- Absolute zero page """
        self.c.PC = 0x215F
        self.c.write_word(0x215F, 0x31)
        self.m.write(0x31, 0xAA)
        
        self.assertEquals(self.c._read_zero_page(), 0xAA)
        self.assertEquals(self.c.PC, 0x215F + 1)
    
    def test_am_6(self):
        """ MOS6502: AM -- Absolute indexed X/Y """
        self.c.PC = 0x215F
        self.c.write_word(0x215F, 0x31F6)
        self.c.X = 0x10
        self.m.write(0x31F6 + self.c.X, 0xAA)
        
        self.assertEquals(self.c._read_indexed_x(), 0xAA)
        self.assertEquals(self.c.PC, 0x215F + 2)
        
        self.c.PC = 0x215F
        self.c.Y = 0x10
        self.m.write(0x31F6 + self.c.Y, 0xBB)
        
        self.assertEquals(self.c._read_indexed_y(), 0xBB)
        self.assertEquals(self.c.PC, 0x215F + 2)
    
    def test_am_6a(self):
        """ MOS6502: AM -- Absolute indexed X/Y page crossed"""
        # TODO: 1T increase at page crossing
        pass
    
    def test_am_8(self):
        """ MOS6502: AM -- Indirect """
        self.c.PC = 0x0000
        self.c.write_word(0x0000, 0x215F)
        self.c.write_word(0x215F, 0x3076)
        
        self.assertEquals(self.c._read_indirect(), 0x3076)
        self.assertEquals(self.c.PC, 2)
    
    def test_am_9(self):
        """ MOS6502: AM -- Pre-indexed indirect X """
        self.c.X = 0x05
        self.c.PC = 0x0042
        self.m.write(0x0042, 0x3E)
        self.c.write_word(0x0043, 0x2415)
        self.m.write(0x2415, 0x6E)
        
        self.assertEquals(self.c._read_pre_indirect(), 0x6E)
        self.assertEquals(self.c.PC, 0x43)
        
        self.c.X = 0x05
        self.c.PC = 0x0042
        self.m.write(0x0042, 0xFF)
        self.c.write_word(0x0004, 0x2416) # 0xFF + 0x05
        self.m.write(0x2416, 0x6E)
        
        self.assertEquals(self.c._read_pre_indirect(), 0x6E)
        self.assertEquals(self.c.PC, 0x43)
    
    
    def test_am_10(self):
        """ MOS6502: AM -- Post-indexed indirect Y """
        self.c.Y = 0x05
        self.c.PC = 0x0042
        self.m.write(0x0042, 0x4C)
        self.c.write_word(0x004C, 0x2100)
        self.m.write(0x2105, 0x6D)
        
        self.assertEquals(self.c._read_post_indirect(), 0x6D)
        self.assertEquals(self.c.PC, 0x43)
    
    def test_am_11_f(self):
        """ MOS6502: AM -- Relative """
        
        # forward
        self.c.PC = 0x1121
        self.m.write(self.c.PC, 0x27)
        
        self.assertEquals(self.c._read_relative(), 0x1149) # 0x1122 + 0x27 (0xA7 = 39)
        self.assertEquals(self.c.PC, 0x1122)
        
        self.c.PC = 0xFFFF
        self.m.write(self.c.PC, 0x27)
        
        self.assertEquals(self.c._read_relative(), 0x0027)
        self.assertEquals(self.c.PC, 0x0000)
        
        # back
        self.c.PC = 0x1121
        self.m.write(self.c.PC, 0xA7)
        
        self.assertEquals(self.c._read_relative(), 0x10FB) # 0x1122 + 0xA7 (0xA7 = -39)
        self.assertEquals(self.c.PC, 0x1122)
        
        self.c.PC = 0x0000
        self.m.write(self.c.PC, 0xA7)
        
        self.assertEquals(self.c._read_relative(), 0xFFDA)
        self.assertEquals(self.c.PC, 0x0001)
        

class MOS6502_ADC(unittest.TestCase):
    def setUp(self):
        self.m = RAM(16, 8)
        self.c = MOS6502(1, self.m)
        self.c.PC = 0x0000
        self.c.A = 10
        self.c.P.c = False
        self.c.abs_T = self.c.T = 0
    
    def tearDown(self):
        pass
    
    def test_adc_base(self):
        self.m[0x00] = 0x69
        self.m[0x01] = 20
        self.c.run()
        self.assertEquals(self.c.A, 30)
        self.assertEquals(self.c.P.c, False)
        self.assertEquals(self.c.PC, 0x0002)
        self.assertEquals(self.c.abs_T, 2)

    def test_adc_c(self):
        self.m[0x00] = 0x69
        self.m[0x01] = 20
        self.c.P.c = True
        self.c.run()
        self.assertEquals(self.c.A, 31)
        self.assertEquals(self.c.P.c, False)

    def test_adc_ovf(self):
        self.m[0x00] = 0x69
        self.m[0x01] = 0xFF
        self.c.run()
        self.assertEquals(self.c.A, 9)
        self.assertEquals(self.c.P.c, True)

    def test_adc_z(self):
        self.m[0x00] = 0x69
        self.c.A = 0x10
        self.m[0x01] = 0xF0
        self.c.run()
        self.assertEquals(self.c.A, 0)
        self.assertEquals(self.c.P.z, True)

# -------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
