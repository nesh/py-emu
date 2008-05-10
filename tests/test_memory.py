#!/usr/bin/env python
# -*- coding:utf-8 -*-

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

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from hardware.memory import RAM

ram =  RAM(16, 8)
class MemoryTest(unittest.TestCase):
    def setUp(self):
        self.m = ram

    def tearDown(self):
        pass

    def test_size(self):
        """ memory: size """
        self.assertEquals(len(self.m), 0x10000)

    def test_rw(self):
        """ memory: read/write """
        values = [random.randint(0, 0x10000) for x in range(10)]
        for x in range(0x1000):
            for val in values:
                self.m[x] = val
                self.assertEquals(
                    self.m[x],
                    val & 0xFF,
                    '$%04X: $%02X != $%02X' % (x, self.m[x], val & 0xFF)
                )

    # def test_slice_addr(self):
    #     """ memory: test slice addresses """
    #     ret = [0, 1, 2]
    #     self.m[0:3] = ret
    #     self.assertEquals(self.m[0:3], ret)
    # 
    #     ret = [2, 1, 0]
    #     self.m[0x10000:0x10003] = ret
    #     self.assertEquals(self.m[0x10000:0x10003], ret)

    def test_big_addr(self):
        """ memory: test big addresses """
        self.m[0x10100] = 0xAA
        self.assertEquals(self.m[0x10100], 0xAA)
        self.assertEquals(self.m[0x0100], 0xAA)


if __name__ == '__main__':
    import nose
    nose.main()