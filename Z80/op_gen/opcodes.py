from tools import *

__all__ = ('GEN_DICT',)


REG8 = ('a', 'f', 'b', 'c', 'd', 'e', 'h', 'l', 'ixh', 'ixl', 'iyh', 'iyl')
REG16 = ('af', 'bc', 'de', 'hl', 'ix', 'iy', 'pc', 'sp')
REGANY = REG8 + REG16
REG16ALT = ('af1', 'bc1', 'de1')
REG16IND = ('(bc)', '(de)', '(hl)', '(sp)')
REGIDX = ('(ix+$)', '(iy+$)')
COND = ('c', 'z', 'm', 'pe',)
NOTCOND = ('nc', 'nz', 'p', 'po',)

# globals
GEN_DICT = {}

def nop(code, op, table=None):
    """ NOP """
    ret = std_head(code, op, table)
    return make_code(code, ret, table)
GEN_DICT['NOP'] = nop

def ld(code, op, table=None):
    """ LD """
    dst, src = [x.lower() for x in op['mn'][1]]
    do = []
    
    if dst == src:
        # ld a,a and others
        pass # no-op
    elif (dst == 'a') and (src in ('r', 'i')):
        # reading R and I changes flags!
        r = read_reg8(src)
        do += write_reg8(dst, r)
        f = read_flags()
        iff2 = state('iff2')
        do += write_flags('(%(f)s & CF) | SZXY_TABLE[%(r)s] | (VF if %(iff2)s else 0)' % locals())
    elif ((dst in REG8) or (dst in ('r', 'i'))) and (src in REG8):
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
    elif (dst in REGIDX) and (src == '#'):
        # ld (ix+o), nn
        reg = 'ix' if 'ix' in dst else 'iy'
        do.append(mem_shortcut())
        do += read_op('mem')
        do += to_signed('tmp8')
        do.append('tmp16 = ' + read_reg16(reg) + ' + tmp8')
        do += read_op('mem')
        do += write('tmp16', 'tmp8', 'mem')
        # adr = 'self.%s + as_signed(self.read_op_arg())' % reg
        # ret = 'self.write(%(adr)s, self.read_op_arg())' % locals()
    elif (dst in REG8) and (src in REGIDX):
        # ld r, (ix+o)
        reg = 'ix' if 'ix' in src else 'iy'
        do.append(mem_shortcut())
        do += read_op('mem')
        do += to_signed('tmp8')
        do += write_reg8(dst, read(read_reg16(reg) + ' + tmp8', 'mem'), False)
        # adr = 'self.%s + as_signed(self.read_op_arg())' % reg
        # ret = 'self.%(dst)s = self.read(%(adr)s)' % locals()
    elif (dst in REGIDX) and (src in REG8):
        # ld (ix+o), r
        reg = 'ix' if 'ix' in dst else 'iy'
        do.append(mem_shortcut())
        do += read_op('mem')
        do += to_signed('tmp8')
        do += write(read_reg16(reg) + ' + tmp8', read_reg8(src), 'mem')
        # adr = 'self.%s + as_signed(self.read_op_arg())' % reg
        # ret = 'self.write(%(adr)s, self.%(src)s)' % locals()
    else:
        raise SyntaxError('LD: invalid pair %s, %s' % (dst, src))
    
    ret = std_head(code, op, table)
    ret += [IDENT + x for x in do] # add commands
    return make_code(code, ret, table)
GEN_DICT['LD'] = ld
