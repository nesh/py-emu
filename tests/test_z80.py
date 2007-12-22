#!/usr/bin/env python
# -*- coding:utf-8 

import os, sys
import unittest
import random
import zipfile, StringIO
from nose.tools import *

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from hardware.z80 import Z80, Z80Flags, CRegister16_8
from hardware.memory import RAM
from hardware.cpu import CPUException

def eqx(a, b, msg=None):
    """Shorthand for 'assert a == b, "%X != %X" % (a, b)
    """
    assert a == b, msg or "$%X != $%X" % (a, b)

class Z80FlagsTest(unittest.TestCase):
    def setUp(self):
        self.f = Z80Flags()

    def test_S(self):
        """ Z80Flags: S """
        self.f.flag.S = 1
        self.assertEquals(self.f.byte, Z80.S)

    def test_Z(self):
        """ Z80Flags: Z """
        self.f.flag.Z = 1
        self.assertEquals(self.f.byte, Z80.Z)

    def test_F5(self):
        """ Z80Flags: F5 """
        self.f.flag.F5 = 1
        self.assertEquals(self.f.byte, Z80.F5)

    def test_H(self):
        """ Z80Flags: H """
        self.f.flag.H = 1
        self.assertEquals(self.f.byte, Z80.H)

    def test_F3(self):
        """ Z80Flags: F3 """
        self.f.flag.F3 = 1
        self.assertEquals(self.f.byte, Z80.F3)

    def test_V(self):
        """ Z80Flags: V """
        self.f.flag.V = 1
        self.assertEquals(self.f.byte, Z80.V)

    def test_N(self):
        """ Z80Flags: N """
        self.f.flag.N = 1
        self.assertEquals(self.f.byte, Z80.N)

    def test_C(self):
        """ Z80Flags: C """
        self.f.flag.C = 1
        self.assertEquals(self.f.byte, Z80.C)

    def test_multiple(self):
        """ Z80Flags: multiple set/reset """
        self.f.flag.C = 1
        self.f.flag.Z = 1
        self.f.flag.N = 1
        self.assertEquals(self.f.byte, Z80.C | Z80.Z | Z80.N)
        self.f.flag.Z = 0
        self.assertEquals(self.f.byte, Z80.C | Z80.N)

    def test_multiple2(self):
        """ Z80Flags: multiple set/reset from byte """
        self.f.byte = Z80.C | Z80.Z | Z80.N
        self.assertEquals(self.f.flag.C, 1)
        self.assertEquals(self.f.flag.Z, 1)
        self.assertEquals(self.f.flag.N, 1)
        self.assertEquals(self.f.flag.F5, 0)

class Z80Test(unittest.TestCase):
    def setUp(self):
        self.m = RAM(16, 8)
        self.c = Z80(1, self.m)

    def tearDown(self):
        pass

    def test_reset(self):
        """ Z80: reset """
        self.c.reset()
        self.assertEquals(self.c.AF.word, 0xFFFF)
        self.assertEquals(self.c.SP.word, 0xFFFF)
        self.assertEquals(self.c.PC.word, 0x0000)

        self.assertEquals(self.c.I.byte, 0x00)
        self.assertEquals(self.c.R.byte, 0x00)

        self.assertEquals(self.c.IM, Z80.IM0)

        self.assertEquals(self.c.IFF1, False)
        self.assertEquals(self.c.IFF2, False)
        self.assertEquals(self.c.HALT, False)

    def test_regs_bool(self):
        """ Z80: registers boolean"""
        for reg in ('IFF1', 'IFF2','HALT'):
            r = getattr(self.c, reg)
            r = True
            self.assertEquals(r, True)

    def test_regs8(self):
        """ Z80: registers 8b"""
        for reg in ('R', 'I'):
            r = getattr(self.c, reg)
            r.byte = 0xAA11
            self.assertEquals(r.byte, 0x11)

    def test_regsAF(self):
        """ Z80: register AF"""
        r = self.c.AF
        r.word = 0x561234
        self.assertEquals(r.word, 0x1234)
        self.assertEquals(r.byte.hi, 0x12)
        self.assertEquals(r.byte.lo.byte, 0x34)

    def test_regsF(self):
        """ Z80: register F"""
        self.c.AF.word = 0x561234
        self.assertEquals(self.c.F.byte, 0x34)
        self.c.F.byte = 0x33
        self.assertEquals(self.c.AF.word, 0x1233)

    def test_regs8_16(self):
        """ Z80: registers 16/8b"""
        for reg in ('BC', 'DE', 'HL', 'AF1', 'BC1', 'DE1', 'HL1'):
            r = getattr(self.c, reg)
            r.word = 0x561234
            self.assertEquals(r.word, 0x1234)
            self.assertEquals(r.byte.hi, 0x12)
            self.assertEquals(r.byte.lo, 0x34)

    def test_regs16(self):
        """ Z80: registers 16b"""
        for reg in ('SP', 'PC'):
            r = getattr(self.c, reg)
            r.word = 0x561234
            self.assertEquals(r.word, 0x1234)

    def test_R(self):
        """ Z80: R (7bit)"""
        self.c.R.byte = 0xFF
        self.assertEqual(self.c.R.byte, 0x7F)

_testdir = os.path.join(os.path.dirname('__file__'), 'z80_test_data')
_testzip = os.path.join(os.path.dirname('__file__'), 'z80_test_data.zip')

def tohex(a):
    return int('0x%s' % a, 16)

class TestData(object):
    def __init__(self, bytes_in, bytes_out, test, code):
        super(TestData, self).__init__()
        self.bytes_in = bytes_in
        self.bytes_out = bytes_out
        self.code = code
        self.test = test
        self.test_in = self.make_in('%s.in' % test)
        self.test_out = self.make_out('%s.out' % test)

    def __repr__(self):
        return '<%s.in>' % self.test

    def make_out(self, fn):
        ret = {}
        ret['regs'] = {}

        # read MC
        fh = StringIO.StringIO(self.bytes_out)
        ln = fh.readline()
        while True:
            if ln[0] != ' ': break
            ln = ln.strip()
            ln = fh.readline()
            # TODO: read MC steps
        #

        # read regs, etc
        ln = ln.strip()

        regs = ln.split(' ')

        ret['regs']['af'] = tohex(regs[0])
        ret['regs']['bc'] = tohex(regs[1])
        ret['regs']['de'] = tohex(regs[2])
        ret['regs']['hl'] = tohex(regs[3])
        ret['regs']['af1'] = tohex(regs[4])
        ret['regs']['bc1'] = tohex(regs[5])
        ret['regs']['de1'] = tohex(regs[6])
        ret['regs']['hl1'] = tohex(regs[7])
        ret['regs']['ix'] = tohex(regs[8])
        ret['regs']['iy'] = tohex(regs[9])
        ret['regs']['sp'] = tohex(regs[10])
        ret['regs']['pc'] = tohex(regs[11])

        ln = fh.readline().strip()
        regs = ln.split()

        ret['regs']['i'] = tohex(regs[0])
        ret['regs']['r'] = tohex(regs[1])
        ret['regs']['iff1'] = tohex(regs[2]) != 0
        ret['regs']['iff2'] = tohex(regs[3]) != 0
        ret['inHalt'] = tohex(regs[4]) != 0
        ret['icount'] = int(regs[6])

        ret['mem'] = {}
        for ln in fh:
            ln = ln.strip()

            if ln == '': continue

            by = ln.split()
            adr = tohex(by[0])
            m = []
            for b in by[1:]:
                if b == '-1': break
                m.append(tohex(b))
            #
            ret['mem'][adr] = m

        fh.close()
        return ret

    def make_in(self, fn):
        ret = {}
        ret['regs'] = {}
        fh = StringIO.StringIO(self.bytes_in)

        ln = fh.readline().strip()
        if not ln: return
        regs = ln.split(' ')

        ret['regs']['af'] = tohex(regs[0])
        ret['regs']['bc'] = tohex(regs[1])
        ret['regs']['de'] = tohex(regs[2])
        ret['regs']['hl'] = tohex(regs[3])
        ret['regs']['af1'] = tohex(regs[4])
        ret['regs']['bc1'] = tohex(regs[5])
        ret['regs']['de1'] = tohex(regs[6])
        ret['regs']['hl1'] = tohex(regs[7])
        ret['regs']['ix'] = tohex(regs[8])
        ret['regs']['iy'] = tohex(regs[9])
        ret['regs']['sp'] = tohex(regs[10])
        ret['regs']['pc'] = tohex(regs[11])

        ln = fh.readline().strip()
        regs = ln.split()

        ret['regs']['i'] = tohex(regs[0])
        ret['regs']['r'] = tohex(regs[1])
        ret['regs']['iff1'] = tohex(regs[2]) != 0
        ret['regs']['iff2'] = tohex(regs[3]) != 0
        ret['inHalt'] = tohex(regs[4]) != 0

        ret['im'] = 0
        ret['icount'] = 0

        ret['mem'] = {}
        for ln in fh:
            ln = ln.strip()

            if ln == '': continue

            by = ln.split()
            adr = tohex(by[0])
            m = []
            for b in by[1:]:
                if b == '-1': break
                m.append(tohex(b))
            #
            ret['mem'][adr] = m
        # for
        fh.close()

        return ret

def _cpu_test(code, data):
    """ CPU instruction test """

    mem = RAM(16, 8)
    cpu = Z80(1, mem)
    if data.test_in:
        for a, l in data.test_in['mem'].iteritems():
            i = 0
            for c in l:
                mem.write((a + i), c)
                i += 1
            a += len(l)
    cpu.reset()
    cpu.set_state(data.test_in['regs'])

    print cpu.disassemble(0)

    try:
        cpu.run(data.test_out['icount'])
    except CPUException, err:
        print '[$%06x] %dT' % (code, data.test_out['icount'])
        raise
    # check T
    eq_(data.test_out['icount'], cpu.abs_T)
    #    raise ValueError('[$%06x] invalid T %d != %d' % (code, cpu.abs_T, data.test_out['icount']))

    # check registers
    for reg, val in data.test_out['regs'].items():
        reg = reg.upper()
        #if reg == 'AF': continue
        r = getattr(cpu, reg)
        if reg in Z80.BIT_16:
            eqx(r.word, val)
            #    raise ValueError('[$%06x] %s: $%04X != $%04X' % (code, reg, r.word, val))
        elif reg in Z80.BIT_8:
            eqx(r.byte, val)
            #    raise ValueError('[$%06x] %s: $%02X != $%02X' % (code, reg, r.byte, val))
        elif reg in Z80.BIT_1:
            eqx(r, val)
            #    raise ValueError('[$%06x] %s: $%02X != $%02X' % (code, reg, r, val))

        # test mem
        for a, l in data.test_out['mem'].iteritems():
            for b in l:
                eq_(mem.read(a), b)
                #    raise ValueError('[$%06x] memory @$%04X expected: $%02x got: $%02x' % (code, a, b, mem.read(a)))
                a += 1

def test_cpu():
    """ test cpu instruction set """
    zf = zipfile.ZipFile(_testzip, 'r')

    for name in zf.namelist():
        #if not name.endswith('.in') and not name.endswith('.out'):
        if not name.endswith('.in'):
            continue
        n, e = os.path.splitext(name)
        nn = n[:]
        if '_' in nn:
            nn = nn[:-2] # strip _x
        code = int('0x%s' % nn, 16)
        data = TestData(zf.read(name), zf.read('%s.out' % n), n, code)
        yield _cpu_test, code, data

if __name__ == '__main__':
    unittest.main()
