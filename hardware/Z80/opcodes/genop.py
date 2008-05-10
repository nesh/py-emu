#!/usr/bin/env python2.5

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

MYDIR = os.path.abspath(os.path.dirname(__file__))

IDENT = ' '*4
ADD_T = 'self.icount -= %d; self.itotal += %d'
#READ_OP = 'self.read(self.pc); self.pc = (self.pc + 1) & 0xFFFF'
READ_OP = 'self.read_op_arg()'
CMDS = {}
# XXX unfold read_*?


def addr_mode(a, delays):
    if a == '@':
        # if 'rd' in delays:
        #     return 'self.read_op16(%s)' % ', '.join([str(n) for n in delays['rd']])
        # else:
        return 'self.read_op_arg16()'
    elif a == '#':
        # if 'rd' in delays:
        #     return 'self.read_op(%s)' % ', '.join([str(n) for n in delays['rd']])
        # else:
        return READ_OP
    elif '(' in a: # ind
        return 'self.read(self.%s)' % a.lower()[1:-1]
    else:
        return 'self.%s' % a.lower()


def nop(type_, code, op, tstates, delays, bits):
    return []
CMDS['NOP'] = nop


def ld(type_, code, op, tstates, delays, bits):
    opcode = bits[0]
    args = bits[1].split(',')
    
    if '(' in args[0]:
        args[0] = args[0].strip('(').strip(')')
        return ['self.write(self.%s, %s)' % (
            args[0].lower(),
            addr_mode(args[1], delays),
        )]
    else:
        return ['self.%s = %s' % (args[0].lower(), addr_mode(args[1], delays))]
CMDS['LD'] = ld


def rlca(type_, code, op, tstates, delays, bits):
    return [
        'a = self.a # shortcut',
        'a = ((a << 1) & 0xFF) | ((a >> 7) & 0xFF)',
        'self.f = (self.f & (PF | ZF | SF)) | (a & (CF | XF | YF))',
        'self.a = a'
    ]
CMDS['RLCA'] = rlca


def ex(type_, code, op, tstates, delays, bits):
    opcode = bits[0]
    args = bits[1].split(',')
    a0 = args[0].lower()
    a1 = args[1].lower()
    return [
        'self.%(a0)s, self.%(a1)s = self.%(a1)s, self.%(a0)s' % locals(),
    ]
CMDS['EX'] = ex


def add(type_, code, op, tstates, delays, bits):
    opcode = bits[0]
    args = bits[1].split(',')
    a0 = args[0].lower()
    
    if len(args) == 1: # 8bit
        return [
            'a = self.a # shortcut' % locals(),
            'value = self.%(a0)s' % locals(),
            'tmp = a + value',
            'lookup = ((a & 0x88) >> 3) | ((value & 0x88) >> 2) | ((tmp & 0x88) >> 1)',
            'self.a = tmp & 0xFF',
            'self.f = (CF if tmp & 0x100 else 0) | HF_ADD_TABLE[lookup & 0x07] | OW_ADD_TABLE[lookup >> 4] | SZXY_TABLE[self.a]'
        ]
    # 16bit
    a1 = args[1].lower()
    return [
        '%(a0)s = self.%(a0)s # shortcut' % locals(),
        '%(a1)s = self.%(a1)s # shortcut' % locals(),
        'tmp = %(a0)s + %(a1)s' % locals(),
        'lookup = ((%(a0)s & 0x0800) >> 11) | ((%(a1)s & 0x0800 >> 10) | ((tmp & 0x0800) >> 9)' % locals(),
        'self.%(a0)s = tmp & 0xFFFF' % locals(),
        'self.f = (self.f & (VF | ZF | SF)) | (CF if tmp & 0x10000 else 0) | ((tmp >> 8) & (XF | YF)) | HF_ADD_TABLE[lookup]'
    ]
CMDS['ADD'] = add


def inc(type_, code, op, tstates, delays, bits):
    opcode = bits[0]
    args = bits[1].split(',')
    args[0] = args[0].lower()
    
    if len(args[0]) > 1:
        m = '0xFFFF'
    else:
        m = '0xFF'
    ret = [
        'value = self.%s # shortcut' % args[0],
        'value = (value + 1) & %s' % m
    ]
    
    if len(args[0]) == 1:
        ret.append('self.f = (self.f & CF) | (VF if value == 0x80 else 0) | (0 if value & 0xF else HF) | SZXY_TABLE[value]')
    
    ret.append('self.%s = value' % args[0])
    return ret
CMDS['INC'] = inc


def dec(type_, code, op, tstates, delays, bits):
    opcode = bits[0]
    args = bits[1].split(',')
    args[0] = args[0].lower()
    
    if len(args[0]) > 1:
        m = '0xFFFF'
    else:
        m = '0xFF'
    ret = [
        'value = self.%s # shortcut' % args[0],
        'value = (value - 1) & %s' % m
    ]
    
    if len(args[0]) == 1:
        ret.insert(1, 'self.f = (self.f & CF) | (0 if value & 0xF else HF) | NF')
        # F |= ( (value)==0x7f ? FLAG_V : 0 ) | sz53_table[value];\
        ret.append('self.f |= (VF if value == 0x7f else 0) | SZXY_TABLE[value]')
    
    ret.append('self.%s = value' % args[0])
    return ret
CMDS['DEC'] = dec


def and_(type_, code, op, tstates, delays, bits):
    opcode = bits[0]
    args = bits[1].split(',')
    a0 = args[0].lower()
    return [
        'self.a &= %s' % addr_mode(a0, delays),
        'self.f = HF | SZXY_TABLE[value]'
    ]
CMDS['AND'] = and_


def convert_to_table(out, type_, table):
    print >>out, '%sdef _init_%s(self):' % (IDENT, type_.lower())
    print >>out, '%s""" init tables """' % (IDENT*2)
    print >>out, '%sself._%s = (' % (IDENT*3, type_.lower())
    
    for code, op in table:
        if type_ == 'base':
            fnname = 'op_%02X' % code
        else:
            fnname = 'op_%s_%02X' % (type_.upper(), code)
        #print 'creating', fnname
        print >>out, '%sself.%s, # %s' % (IDENT*4, fnname, op)
    print >>out, '%s) # %s' % (IDENT*3, type_.lower())



def convert_to_py(out, type_, code, op, tstates, delays):
    bits = op.split()
    opcode = bits[0].upper()
    if opcode not in CMDS: return
    
    if type_ == 'base':
        fnname = 'op_%02X' % code
    else:
        fnmame = 'op_%s_%02X' % (type_.upper(), code)
    
    # for prefixed ops: min. time used to fetch the prefix (4) must be substracted
    for d in delays.keys():
        if type_ != 'base':
            delays[d] = [t - 4 for t in delays[d]]
    if type_ != 'base':
        tstates = [t - 4 for t in tstates]
    
    print >>out, '%sdef %s(self):' % (IDENT, fnname)
    print >>out, '%s""" %s """' % (IDENT*2, op)
    
    print >>out, '%sself.prefix = 0x%02X' % (IDENT*2, code)
    
    ret = CMDS[opcode](type_, code, op, tstates, delays, [b.replace("'", '1') for b in bits])
    print >>out, '%s# %s' % (IDENT*2, opcode)
    for l in ret:
        print >>out, '%s%s' % (IDENT*2, l.rstrip())
    # end
    print >>out, '%s# end' % (IDENT*2)
    print >>out, '%s%s' % (IDENT*2, (ADD_T % (tstates[0], tstates[0])))
    print >>out, '%s' % IDENT


def process_ofile(fname, name, dasm_fh):
    print 'Processing %s (%s)' % (fname, name)
    print '='*72
    
    fh = open(fname, 'rU')
    fout = open(fname.replace('.dat', '.py'), 'w') #sys.stdout
    
    print >>fout, '# autogenerated from %s, do not edit\n\n' % fname
    print >>fout, 'from tables import *\n\n'
    print >>fout, 'class Z80Mixin%s(object):' % name.upper()
    
    table = []
    
    for line in fh:
        try:
            line = line.strip()
            if not line or line.startswith('#'): continue
            
            if name.lower() in ('dd', 'ddcb'):
                line = line.replace('REGISTER', 'IX')
            elif name.lower() in ('fd', 'fdcb'):
                line = line.replace('REGISTER', 'IY')
            
            bits = [s.strip() for s in line.split('\t')]
            
            if len(bits) < 2: continue
            
            # parse line
            
            # code="OP"
            code, op = bits[0].split('=')
            code = int(code, 16)
            op = op.strip('"')
            table.append((code, op))
            
            # t="T1[,T2]"
            dummy, b = bits[1].split('=')
            if dummy != 't': raise ValueError('syntax error, expected "t"')
            b = b.strip('"')
            if '/' in b:
                t = [int(s) for s in b.split('/')]
            else:
                t = [int(b)]
            
            # delays
            delays = {}
            for bit in bits[2:]:
                dummy, b = bit.split('=')
                b = b.strip('"')
                if (dummy != 'rd') and (dummy != 'wr'):
                    raise ValueError('syntax error, expected "rd/wr"')
                if ',' in b:
                    delays[dummy] = [int(s) for s in b.split(',')]
                else:
                    delays[dummy] = [int(b)]
            
            convert_to_py(fout, name, code, op, t, delays)
        except Exception, err:
            print >>sys.stderr, line
            print >>sys.stderr, bits
            raise
    convert_to_table(fout, name, table)


def main():
    dasm_fh = open('dasmtab.py', 'w')
    
    process_ofile('opcodes_base.dat', 'base', dasm_fh)
    # process_ofile('opcodes_cb.dat', 'cb', dasm_fh)
    # process_ofile('opcodes_ed.dat', 'ed', dasm_fh)
    # process_ofile('opcodes_ddfd.dat', 'dd', dasm_fh)
    # process_ofile('opcodes_ddfd.dat', 'fd', dasm_fh)
    # process_ofile('opcodes_ddfdcb.dat', 'ddcb', dasm_fh)
    # process_ofile('opcodes_ddfdcb.dat', 'fdcb', dasm_fh)
    
    dasm_fh.close()

if __name__ == '__main__':
    main()