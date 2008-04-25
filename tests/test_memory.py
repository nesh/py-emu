#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys
import unittest
import random

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from hardware.memory import RAM

class MemoryTest(unittest.TestCase):
    def setUp(self):
        self.m = RAM(16, 8)
        self.values = [random.randint(0, 0xFF) for x in range(0x10000)]
        assert len(self.values) == 0x10000
        for i in range(0x10000):
            self.m.write(i, self.values[i])

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
                self.m.write(x, val)
                self.assertEquals(
                    self.m.read(x),
                    val & 0xFF,
                    '$%04X: $%02X != $%02X' % (x, self.m.read(x), val & 0xFF)
                )

    def test_rw_arr(self):
        """ memory: read/write as array """
        values = [random.randint(0, 0x10000) for x in range(10)]
        for x in range(0x1000):
            for val in values:
                self.m[x] = val
                self.assertEquals(
                    self.m[x],
                    val & 0xFF,
                    '$%04X: $%02X != $%02X' % (x, self.m[x], val & 0xFF)
                )
    
    def test_big_addr(self):
        """ memory: test big addresses """
        self.m.write(0x10100, 0xAA)
        self.assertEquals(self.m.read(0x10100), 0xAA)
        self.assertEquals(self.m.read(0x0100), 0xAA)

    def test_big_addr_a(self):
        """ memory: test big addresses array access """
        self.m[0x10100] = 0x11A
        self.assertEquals(self.m[0x10100], 0x1A)
        self.assertEquals(self.m[0x0100], 0x1A)

    def test_iter(self):
        """ memory: test __iter__ """
        i = 0
        for x in self.m:
            self.assertEquals(x, self.values[i], '$%04X: %r != %r' % (i, x, self.values[i]))
            i += 1


if __name__ == '__main__':
    unittest.main()
