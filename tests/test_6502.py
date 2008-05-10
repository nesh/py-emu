#!/usr/bin/env python
# -*- coding:utf-8

# Copyright 2008 Djordjevic Nebojsa <djnesh@gmail.com>
# 
# This file is part of py-emu.
# 
# py-emu is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# py-emu is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with py-emu.  If not, see <http://www.gnu.org/licenses/>.

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
    
    def test_base(self):
        """ MOS6502: base test """
        for x in range(0x100):
            #print 'check code %02X -- %s' % (x, self.c._mnemonic(x))
            self.assert_(x in self.c._op, 'missing code %02X' % x)
    
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
