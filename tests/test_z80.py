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

from hardware.Z80.z80 import Z80
from hardware.Z80.z80core import F5_FLAG, F3_FLAG
from hardware.memory import RAM
from hardware.cpu import CPUException

_testdir = os.path.join(os.path.dirname(__file__), '..', 'private', 'z80_test_data')
_testzip = os.path.join(os.path.dirname(__file__), 'z80_test_data.zip')

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
    
    def dasm(self):
        mem = RAM(16, 8)
        io = RAM(16, 8)
        cpu = Z80(1, mem, io)
        if self.test_in:
            for a, l in self.test_in['mem'].iteritems():
                i = 0
                for c in l:
                    cpu.write((a + i), c)
                    i += 1
                a += len(l)
        cpu.reset()
        if self.test_in:
            cpu.set_state(self.test_in['regs'])
        return cpu.disassemble(0, dump_adr=False, dump_hex=False)



mem = RAM(16, 8)
io = RAM(16, 8)
cpu = Z80(1, mem, io)

def _cpu_test(code, data):
    """ CPU instruction test """
    
    if data.test_in:
        for a, l in data.test_in['mem'].iteritems():
            i = 0
            for c in l:
                cpu.write((a + i), c)
                i += 1
            a += len(l)

    cpu.reset()    
    cpu.set_state(data.test_in['regs'])
    start_pc = cpu.PC
    try:
        # print 'running from %04X' % cpu.PC
        cpu.run(data.test_out['icount'] - 1)
        assert cpu._cpu.Trap == 0, 'invalid op @%04X' % cpu._cpu.Trap
        # check T
        assert data.test_out['icount'] == cpu.icount, '%d != %d' % (data.test_out['icount'], cpu.icount)
        
        # check registers
        for reg, val in data.test_out['regs'].items():
            reg = reg.upper()
            r = getattr(cpu, reg)
            if reg == 'R': continue # ignore R for now
            if reg == 'AF':
                # reset 5 & 3 for now
                r &= ~(F5_FLAG | F3_FLAG)
                val &= ~(F5_FLAG | F3_FLAG)
                assert r == val, '%s(%04X) != %04X (F: %s)' % \
                    (reg, r, val, cpu.flags_as_str(val & 0xFF))
            else:
                assert r == val, '%s(%04X) != %04X' % (reg, r, val)
        # test mem
        for a, l in data.test_out['mem'].iteritems():
            for b in l:
                assert cpu.read(a) == b
                a += 1
    except Exception, err:
        # print len(data.test_in['mem']), data.test_in['mem']
        print cpu.disassemble(0, bytes=len(data.test_in['mem'][start_pc]))
        print '='*50
        print 'Test: %X' % code
        print cpu
        raise

def xtest_cpu():
    """ test cpu instruction set (dir)"""
    for root, dirs, files in os.walk(_testdir):
        for name in files:
            #if not name.endswith('.in') and not name.endswith('.out'):
            if not name.endswith('.in'):
                continue
            n, e = os.path.splitext(name)
            nn = n[:]
            if '_' in nn:
                nn = nn[:-2] # strip _x
            code = int('0x%s' % nn, 16)
            inf = open(os.path.join(root, name))
            outf = open(os.path.join(root, '%s.out' % n))
            data = TestData(inf.read(), outf.read(), n, code)
            _cpu_test.description = 'test %s' % name
            yield _cpu_test, code, data

def test_cpu_zip():
    """ test cpu instruction set (zip)"""
    zf = zipfile.ZipFile(_testzip, 'r')
    
    for name in zf.namelist():
        if not name.endswith('.in'):
            continue
        n, e = os.path.splitext(name)
        nn = n[:]
        if '_' in nn:
            nn = nn[:-2] # strip _x
        code = int('0x%s' % nn, 16)
        data = TestData(zf.read(name), zf.read('%s.out' % n), n, code)
        yield _cpu_test, code, data
        _cpu_test.description = 'test %s' % name

if __name__ == '__main__':
    import nose
    nose.main()
