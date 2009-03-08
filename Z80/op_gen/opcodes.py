from rw import *

__all__ = ('GEN_DICT',)


IDENT = ' ' * 4
REG8 = ('a', 'f', 'b', 'c', 'd', 'e', 'h', 'l', 'ixh', 'ixl', 'iyh', 'iyl')
REG16 = ('af', 'bc', 'de', 'hl', 'ix', 'iy', 'pc', 'sp')
REGANY = REG8 + REG16
REG16ALT = ('af1', 'bc1', 'de1')
REG16IND = ('(bc)', '(de)', '(hl)', '(sp)')
REGIDX = ('(ix+$)', '(iy+$)')
COND = ('c', 'z', 'm', 'pe',)
NOTCOND = ('nc', 'nz', 'p', 'po',)
ICOUNT = r"""%s -= %%d""" % state('icount') # TODO: what's faster a['foo'] or a.foo?
HEAD = r'''def %s(z80):'''

# globals
GEN_DICT = {}

def nop(code, op, table='base'):
    name = 'opcode_%s_%02X' % (table, code)
    ret = [
        HEAD % name,
        '%s"""0x%02X: %s"""' % ((IDENT), code, op['asm']),
        '%s%s' % ((IDENT), (ICOUNT % op['t'])),
    ]
    return ('\n'.join(ret), 'JP_%s[0x%02X] = %s' % (table.upper(), code, name))
GEN_DICT['NOP'] = nop

def ld(code, op, table='base'):
    dst, src = [x.lower() for x in op['mn'][1]]
    name = 'opcode_%s_%02X' % (table, code)

    do = []

    if dst == src:
        do.append('pass # no-op')
    elif (dst == 'a') and (src in ('r', 'i')):
        # reading R and I changes flags!
        r = read_reg8(src)
        do += write_reg8(dst, r)
        f = read_flags()
        iff2 = state['iff2']
        do += write_flags('(%(f)s & CF) | SZXY_TABLE[%(r)s] | (VF if %(iff2)s else 0)' % locals())
    elif (dst in REG8) and (src in REG8):
        # ld r,r1
        do += write_reg8(dst, read_reg8(src), False)
    elif (dst in REG16) and (src in REG16):
        # ld rr,rr1
        do += write_reg16(dst, read_reg16(src), False)
    elif (dst in REG16) and (src == '@'):
        # ld rr,nnnn
        do.append(mem_shortcut())
        do += read_op16('mem')
        do += write_reg16(dst, 'tmp16', False)
    elif (dst in REG8) and (src == '#'):
        # ld r, n
        do += read_op()
        do += write_reg8(dst, 'tmp8', False)
    elif (dst in REG16IND) and (src in REG8):
        # ld (rr), r
        do += write(read_reg16(dst[1:-1]), read_reg8(src))
    elif (dst in REG16IND) and (src == '#'):
        # ld (rr), nn
        do.append(mem_shortcut())
        do += read_op('mem')
        do += write(read_reg16(dst[1:-1]), 'tmp8', 'mem')
    elif (dst in REG8) and (src in REG16IND):
        # ld r, (rr)
        do += write_reg8(dst, read(read_reg16(src[1:-1])), False)
    elif (dst == '(@)') and (src in REG16):
        # ld (nnnn), rr
        do.append(mem_shortcut())
        do += read_op16('mem')
        do += write16('tmp16', read_reg16(src), 'mem')
    elif (dst in REG16) and (src == '(@)'):
        # ld rr, (nnnn)
        do.append(mem_shortcut())
        do += read_op16('mem')
        do += write_reg16(dst, 'tmp16', False)
    elif (dst == '(@)') and (src in REG8):
        # ld (nnnn), r
        do.append(mem_shortcut())
        do += read_op16('mem')
        do += write('tmp16', read_reg8(src), 'mem')
    elif (dst in REG8) and (src == '(@)'):
        # ld r, (nnnn)
        do += read_op()
        do += write_reg8(dst, 'tmp8')
    else:
        raise KeyError('LD: invalid pair %s, %s' % (dst, src))

    ret = [
        HEAD % name,
        '%s"""0x%02X: %s"""' % ((IDENT), code, op['asm']),
    ]
    ret += [IDENT + x for x in do] # add commands

    return ('\n'.join(ret), 'JP_%s[0x%02X] = %s' % (table.upper(), code, name))
GEN_DICT['LD'] = ld
