#!../../env/bin/python

import os
import sys
import codeop
import warnings
import shlex
from pprint import pprint

from opcodes import GEN_DICT

MYDIR = os.path.abspath(os.path.dirname(__file__))

DATA = {}

def store(tokens, data, multi_mn=False, prefix=None):
    code = tokens.pop(0)
    if '=' in code:
        code, asm = code.split('=')
    code = int(code, 0)

    if not len(tokens):
        # data[code] = None
        del data
        return

    ret = {'asm': asm, 'op': None, 'multi_mn': multi_mn}

    asm = asm.replace("'", "\\'")
    mn_parsed = []
    if multi_mn:
        asm = asm.split(',', 1)
    else:
        asm = [asm]
    for a in asm:
        mn_tmp = []
        mn = shlex.split(a)
        for m in mn:
            if ',' in m:
                m = m.split(',')
            mn_tmp.append(m)
        mn_parsed.append(mn_tmp)

    ret['mn'] = mn_parsed

    # T
    _, t = tokens.pop(0).split('=')
    if '/' in t:
        t = [int(x) for x in t.split('/')]
    else:
        t = int(t)
    ret['t'] = t

    if len(tokens):
        # RD
        _, t = tokens.pop(0).split('=')
        if ',' in t:
            t = [int(x) for x in t.split(',')]
        else:
            t = int(t)
        ret['rd'] = t

    if len(tokens):
        # WR
        _, t = tokens.pop(0).split('=')
        if ',' in t:
            t = [int(x) for x in t.split(',')]
        else:
            t = int(t)
        ret['wr'] = t

    data[code] = ret

def parse(fname, prefix=None):
    # fname = os.path.join(MYDIR, fname)
    print 'processing', fname, '...',
    if prefix:
        if prefix in (0xDDCB, 0xFDCB):
            prefix1 = (prefix & 0xFF00) >> 8
            prefix2 = (prefix & 0x00FF)
            if prefix1 not in DATA: DATA[prefix1] = {}
            root = DATA[prefix1]
            if prefix2 not in root: root[prefix2] = {}
            root = root[prefix2]
        else:
            if prefix not in DATA:
                DATA[prefix] = {}
            root = DATA[prefix]
    else:
        root = DATA

    fh = open(fname, 'rU')

    for line in fh:
        line = line.strip()
        if not line or line.startswith('#'): continue

        if prefix in (0xDD, 0xDDCB):
            line = line.replace('REGISTER', 'IX')
        elif prefix in (0xFD, 0xFDCB):
            line = line.replace('REGISTER', 'IY')

        tokens = shlex.split(line)
        # pprint(tokens)
        store(tokens, root, multi_mn=prefix in (0xDDCB, 0xFDCB))
    print 'done.'

def gen_one(code, op, table='base'):
    op['mn'] = op['mn'][0]
    gen = None
    generator = GEN_DICT.get(op['mn'][0], None)
    if generator is not None:
        gen = generator(code, op, table)
        try:
            for c in gen:
                codeop.compile_command(c, op['asm']) # check syntax
        except SyntaxError:
            print op['mn']
            print '\n'.join(gen)
            print ''
            raise
    return gen

def gen_prefix(code, data):
    prefix = code
    print 'prefix', '%02X' % prefix, '...',
    ret = [
        '# ' + '-'*70,
        '# %2X prefix start' % prefix,
        '# ' + '-'*70,
    ]
    for code, op in data.items():
        if not isinstance(op, dict): continue # skip extra data
        if op['multi_mn']: continue # not implemented for now
        gen = gen_one(code, op, table='%2x' % prefix)
        if gen:
            ret += gen
            ret.append('')
    if len(ret) == 1:
        ret = None
    else:
        ret += [
            '# ' + '-'*70,
            '# %2X prefix end' % prefix,
            '# ' + '-'*70,
        ]
    print 'done.'
    return ret

def gen():
    # pprint(DATA)
    fh = open('_opcodes.py', 'w')
    print >>fh, '''# Autogenerated, DO NOT EDIT!!!

from Z80.tables import *

JP_BASE = [None] * 0x100
JP_CB = [None] * 0x100
JP_ED = [None] * 0x100
JP_DD = [None] * 0x100
JP_FD = [None] * 0x100
JP_DDCB = [None] * 0x100
JP_FDCB = [None] * 0x100
'''
    for code, op in DATA.items():
        if op['multi_mn']: continue # not implemented for now
        if op['asm'].startswith('shift'):
            ret = gen_prefix(code, op)
        else:
            ret = gen_one(code, op)
        if ret:
            print >>fh, '\n'.join(ret)
            print >>fh,''
    fh.close()

def main():
    parse('opcodes_base.dat')
    # parse('opcodes_cb.dat', 0xCB)
    parse('opcodes_ed.dat', 0xED)
    # parse('opcodes_ddfd.dat', 0xDD)
    # parse('opcodes_ddfd.dat', 0xFD)
    # parse('opcodes_ddfdcb.dat', 0xDDCB)
    # parse('opcodes_ddfdcb.dat', 0xFDCB)
    gen()


if __name__ == '__main__':
    main()
