#!../../../env/bin/python

import os
import sys
import codeop
import warnings
import shlex
from pprint import pprint

from tools import gen_name, gen_jp, IDENT, state, ICOUNT, ITOTAL
from opcodes import GEN_DICT, read_op

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

def gen_one(code, op, table=None):
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

def gen_prefix(code, data, parent=None):
    if parent:
        prefix = (parent << 8) | code
    else:
        prefix = code
    fname = 'prefix_%2x' % prefix
    print 'prefix', '%02X' % prefix, '...',
    table = '%2x' % prefix
    ret = [
        '# ' + '='*70,
        '# %2X prefix start' % prefix,
        '# ' + '='*70,
        '',
        'def %s(z80):' % fname,
    ]
    ret += [IDENT + x for x in read_op()]
    # if code in (0xDD, 0xFD, 0xED):
    ret.append('%s%s' % (IDENT, (ICOUNT % 4)))
    ret.append('%s%s' % (IDENT, (ITOTAL % 4)))
    ret += [
        '%(i)s%(r)s += 1' % {'i': IDENT, 'r': state('_r')},
        '%(i)s%(jp)s[tmp8](z80)' % {'i': IDENT, 'jp': gen_jp(table), 'op': read_op()},
        '%s[0x%02X] = %s' % (gen_jp('%2x' % parent if parent else None), code, fname),
        '# ' + '-'*70,
        ''
    ]
    for code, op in data.items():
        if not isinstance(op, dict): continue # skip extra data
        if op['multi_mn']: continue # not implemented for now
        # for prefixed ops: min. time used to fetch the prefix (4) must be substracted
        if isinstance(op['t'], list):
            op['t'] = [t - 4 for t in op['t']]
        else:
            op['t'] -= 4
        if op['asm'].startswith('shift'):
            gen = gen_prefix(code, op, parent=prefix)
        else:
            gen = gen_one(code, op, table='%2x' % prefix)
        if gen:
            ret += gen
            ret.append('')
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

from pyemu.Z80.tables import *
from pyemu.hardware.cpu import CPUTrapInvalidOP

__all__ = ('JP_BASE',)

def invalid_op(z80):
    raise CPUTrapInvalidOP('%04X' % z80.pc)

JP_BASE = [invalid_op] * 0x100
JP_CB = [invalid_op] * 0x100
JP_ED = [invalid_op] * 0x100
JP_DD = [invalid_op] * 0x100
JP_FD = [invalid_op] * 0x100
JP_DDCB = [invalid_op] * 0x100
JP_FDCB = [invalid_op] * 0x100


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
    # add code to fill FD & DD tables
    print >>fh, """
# fill fd & dd blank spots
for i in range(0, 0x100):
    if JP_DD[i] == invalid_op: JP_DD[i] = JP_BASE[i]
    if JP_FD[i] == invalid_op: JP_FD[i] = JP_BASE[i]
"""
    fh.close()

def main():
    parse('opcodes_base.dat')
    parse('opcodes_cb.dat', 0xCB)
    parse('opcodes_ed.dat', 0xED)
    parse('opcodes_ddfd.dat', 0xDD)
    parse('opcodes_ddfd.dat', 0xFD)
    parse('opcodes_ddfdcb.dat', 0xDDCB)
    parse('opcodes_ddfdcb.dat', 0xFDCB)
    gen()


if __name__ == '__main__':
    main()