import unittest

from hardware.Z80.z80 import Z80, Z80Flags
from hardware.memory import RAM

REGS_SRC = {
    0x07: 'A',
    0x00: 'B',
    0x01: 'C',
    0x02: 'D',
    0x03: 'E',
    0x04: 'H',
    0x05: 'L',
}

REG_8B = ('A', 'B', 'C', 'D', 'E', 'H', 'L')
RP = ('BC', 'DE', 'HL', 'SP')
RP2 = ('BC', 'DE', 'HL', 'AF')

def make_cpu():
    m = RAM(16, 8)
    c = Z80(1, m)
    c.reset()
    c.F.byte = 0x00 # reset flags
    return c

# class BaseZ80Test(unittest.TestCase):
#     def setUp(self):
#         self.m = RAM(16, 8)
#         self.c = Z80(1, self.m)
#         self.c.reset() # just in case ;)
#         self.c.F.byte = 0x00 # reset flags
#     
#     def tearDown(self):
#         pass
#     
#     def err(self, msg='FAIL', start=0x0000, len_=1):
#         return '%s: %s' % (self.c.disassemble(start), msg)
#     
#     def eq(self, op1, op2, msg='FAIL', start=0x0000, len_=1):
#         msg = '%s: %s != %s' % (msg, op1, op2)
#         self.assertEquals(op1, op2, self.err(msg, start, len_))
#     
#     def eq_8b(self, op1, op2, msg='FAIL', start=0x0000, len_=1):
#         msg = '%s: %02Xh != %02Xh' % (msg, op1, op2)
#         self.assertEquals(op1, op2, self.err(msg, start, len_))
#     
#     def eq_16b(self, op1, op2, msg='FAIL', start=0x0000, len_=1):
#         msg = '%s: %02Xh != %02Xh' % (msg, op1, op2)
#         self.assertEquals(op1, op2, self.err(msg, start, len_))
#     
#     def check_pc(self, val, start=0x0000, len_=1):
#         msg = 'INVALID PC: %04Xh != %04Xh' % (self.c.PC, val)
#         self.assertEquals(self.c.PC, val, self.err(msg, start, len_))
#     
#     def check_t(self, val, start=0x0000, len_=1):
#         msg = 'INVALID T: %d != %d' % (self.c.abs_T, val)
#         self.assertEquals(self.c.abs_T, val, self.err(msg, start, len_))
#     
#     def check_f(self, f, start=0x0000, len_=1):
#         msg = 'INVALID F: %02Xh != %02Xh' % (self.c.F.byte, f)
#         self.assertEquals(self.c.F.byte, f, self.err(msg, start, len_))


def test_reset():
    """ Z80: reset """
    m = RAM(16, 8)
    cpu = Z80(1, m)
    cpu.reset()

    assert cpu.AF == 0x0000
    assert cpu.SP == 0xF000
    assert cpu.PC == 0x0000

    assert cpu.I == 0x00
    assert cpu.R == 0x00

    assert cpu.IM == Z80.IM0

    assert cpu.IFF1 == False
    assert cpu.IFF2 == False
    assert cpu.HALT == False
