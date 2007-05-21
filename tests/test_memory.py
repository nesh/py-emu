#!/usr/bin/env python
# encoding: utf-8

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

    def test_out(self):
        """ memory: out of bounds """
        val = 0x1F
        
        self.m.write(0x10001, val)
        
        self.assertEquals(self.m.read(0x10001), self.m.read(0x01))
        self.assertEquals(self.m.read(0x10001), self.m.read(0x01))
        self.assertEquals(self.m.read(0x10001), val)
        self.assertEquals(self.m.read(0x01), val)


if __name__ == '__main__':
    unittest.main()
