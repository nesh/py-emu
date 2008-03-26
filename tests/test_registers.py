#!/usr/bin/env python
# -*- coding:utf-8

import os, sys
import unittest
import random

""" register test """
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from hardware.register import *

class RegisterTest(unittest.TestCase):
    """ registers -- pyre python """
    def setUp(self):
        self.reg = Register16_8(0x1234)

    def tearDown(self):
        pass

    def test_r16(self):
        """ register: 16b """
        self.assertEquals(self.reg.value, 0x1234)

    def test_r16_out(self):
        """ register: 16b overflow """
        self.reg.value = 0x123456
        self.assertEquals(self.reg.value, 0x3456)

    def test_r8(self):
        """ register: 8b hi/low """
        self.assertEquals(self.reg.hi, 0x12)
        self.assertEquals(self.reg.lo, 0x34)
        self.reg.lo = 0x11
        self.reg.hi = 0x22
        self.assertEquals(self.reg.hi, 0x22)
        self.assertEquals(self.reg.lo, 0x11)
        self.assertEquals(self.reg.value, 0x2211)

    def test_r8_out(self):
        """ register: 8b overflow """
        self.reg.lo = 0x1001
        self.reg.hi = 0x1002
        self.assertEquals(self.reg.hi, 0x02)
        self.assertEquals(self.reg.lo, 0x01)
        self.assertEquals(self.reg.value, 0x0201)

class CRegisterTest(unittest.TestCase):
    """ registers -- ctypes """
    def setUp(self):
        self.reg = CRegister16_8(0x1234)

    def tearDown(self):
        pass

    def test_r16(self):
        """ cregister: 16b """
        ret = 0x1234
        self.assertEquals(self.reg.word, ret, '$%04X != $%04X' % (self.reg.word, ret))

    def test_r8_single(self):
        """ cregister: 8bit """
        reg = CRegister8(0x1234)
        ret = 0x34
        self.assertEquals(reg.byte, ret, '$%02X != $%02X' % (reg.byte, ret))

    def test_r16_single(self):
        """ cregister: 16bit """
        reg = CRegister16(0xAA1234)
        ret = 0x1234
        self.assertEquals(reg.word, ret, '$%04X != $%04X' % (reg.word, ret))

    def test_r16_out(self):
        """ cregister: 16b overflow """
        self.reg.word = 0x123456
        self.assertEquals(self.reg.word, 0x3456)

    def test_r8(self):
        """ cregister: 8b hi/low """
        hi = 0x12
        lo = 0x34
        self.assertEquals(self.reg.byte.hi, hi, '$%02X != $%02X' % (self.reg.byte.hi, hi))
        self.assertEquals(self.reg.byte.lo, lo, '$%02X != $%02X' % (self.reg.byte.lo, lo))

        hi = 0x22
        lo = 0x11
        ret = 0x2211
        self.reg.byte.lo = lo
        self.reg.byte.hi = hi
        self.assertEquals(self.reg.byte.hi, hi, '$%02X != $%02X' % (self.reg.byte.hi, hi))
        self.assertEquals(self.reg.byte.lo, lo, '$%02X != $%02X' % (self.reg.byte.lo, lo))
        self.assertEquals(self.reg.word, ret, '$%04X != $%04X' % (self.reg.word, ret))

    def test_r8_out(self):
        """ cregister: 8b overflow """
        hi = 0x02
        lo = 0x01
        ret = 0x0201

        self.reg.byte.lo = 0x1001
        self.reg.byte.hi = 0x1002
        self.assertEquals(self.reg.byte.hi, hi, '$%02X != $%02X' % (self.reg.byte.hi, hi))
        self.assertEquals(self.reg.byte.lo, lo, '$%02X != $%02X' % (self.reg.byte.lo, lo))
        self.assertEquals(self.reg.word, ret, '$%04X != $%04X' % (self.reg.word, ret))

if __name__ == '__main__':
    unittest.main()
