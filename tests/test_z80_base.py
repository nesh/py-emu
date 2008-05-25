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
from nose.tools import *

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from hardware.Z80.z80 import Z80
from hardware.memory import RAM
from hardware.io import IO
from hardware.cpu import CPUException

_testzip = os.path.join(os.path.dirname(__file__), 'z80_test_data.zip')

class TIO(RAM):
    def __init__(self, adr_width, bit_width):
        super(TIO, self).__init__(adr_width, bit_width)
        self.mem = [0xFF] * self.size


mem = RAM(16, 8)
io = TIO(16, 8)
cpu = Z80(mem, io)

def test_reset():
    """ Z80: reset state """
    cpu.reset()
    assert cpu.pc == 0x0000
    assert not cpu.iff1
    assert not cpu.iff2
    assert cpu.im == 0
    for r in ('af', 'sp', 'bc', 'de', 'hl', 'af1', 'bc1', 'de1', 'hl1', 'ix', 'iy'):
        assert getattr(cpu, r) == 0xFFFF, 'invalid after reset value for %s' % r

def test_af():
    """ Z80: test af """
    cpu.af = 0x1234
    assert cpu.a == 0x12
    assert cpu.f == 0x34
    cpu.a = 0xAA
    cpu.f = 0xFF
    assert cpu.af == 0xAAFF
    
def test_bc():
    """ Z80: test bc """
    cpu.bc = 0x1234
    assert cpu.b == 0x12
    assert cpu.c == 0x34
    cpu.b = 0xBB
    cpu.c = 0xCC
    assert cpu.bc == 0xBBCC

def test_de():
    """ Z80: test de """
    cpu.de = 0x1234
    assert cpu.d == 0x12
    assert cpu.e == 0x34
    cpu.d = 0xDD
    cpu.e = 0xEE
    assert cpu.de == 0xDDEE

def test_hl():
    """ Z80: test hl """
    cpu.hl = 0x1234
    assert cpu.h == 0x12
    assert cpu.l == 0x34
    cpu.h = 0x11
    cpu.l = 0x22
    assert cpu.hl == 0x1122

def test_ix():
    """ Z80: test ix """
    cpu.ix = 0x1234
    assert cpu.ixh == 0x12
    assert cpu.ixl == 0x34
    cpu.ixh = 0x32
    cpu.ixl = 0x23
    assert cpu.ix == 0x3223

def test_iy():
    """ Z80: test iy """
    cpu.iy = 0x1234
    assert cpu.iyh == 0x12
    assert cpu.iyl == 0x34
    cpu.iyh = 0x21
    cpu.iyl = 0x32
    assert cpu.iy == 0x2132

if __name__ == '__main__':
    import nose
    try:
        import psyco
        #psyco.full()
        psyco.log()
        psyco.profile(0.05)
        psyco.runonly()
    except ImportError:
        pass
    nose.main()
