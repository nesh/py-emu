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

# #define AND(value)\
# {\
#   A &= (value);\
#   F = FLAG_H | sz53p_table[A];\
# }

def and_(code, op, table=None):
    """ AND """
    src = op['mn'][1].lower()
    do = []
    a = read_reg8('a')
    
    if src in REG8:
        # and r
        r = read_reg8(src)
    elif src in REG16IND:
        # and (rr)
        r = read(read_reg16(src[1:-1]))
    elif src in REGIDX:
        # and (ix+o)
        do.append(mem_shortcut())
        todo, r = read_idx(src, mem='mem')
        do += todo
    elif src == '#':
        # and n
        do += read_op()
        r = 'tmp8'
    else:
        raise SyntaxError('AND invalid source %s' % src)
    do += write_reg8('a', '%(a)s & %(r)s' % locals(), force=False)
    
    do += write_flags('HF | SZ53P_TABLE[%(a)s]' % locals())
        
    ret = std_head(code, op, table)
    ret += [IDENT + x for x in do] # add commands
    return make_code(code, ret, table)
GEN_DICT['AND'] = and_

# #define ADC(a, value)\
# {\
#   Z80EX_WORD adctemp = A + (value) + ( F & FLAG_C ); \
#   Z80EX_BYTE lookup = ( (       A & 0x88 ) >> 3 ) | \
#               ( ( (value) & 0x88 ) >> 2 ) | \
#               ( ( adctemp & 0x88 ) >> 1 );  \
#   A=adctemp;\
#   F = ( adctemp & 0x100 ? FLAG_C : 0 ) |\
#       halfcarry_add_table[lookup & 0x07] | overflow_add_table[lookup >> 4] |\
#       sz53_table[A];\
# }

def adc(code, op, table=None):
    """ ADC A"""
    dst, src = [x.lower() for x in op['mn'][1]]
    if dst == 'hl':
        return adc16(code, op, table=None)
    do = []
    a = read_reg8(dst)
    f = read_reg8('f')
    
    if src in REG8:
        # adc a,r
        r = read_reg8(src)
    elif src in REG16IND:
        # adc a,(rr)
        # do.append(mem_shortcut())
        do.append('tmp8 = %s' % read(read_reg16(src[1:-1])))
        r = 'tmp8'
    elif src in REGIDX:
        # adc a,(ix+o)
        do.append(mem_shortcut())
        todo, r = read_idx(src, mem='mem')
        do += todo
        do.append('tmp8 = %(r)s' % locals())
        r = 'tmp8'
    elif src == '#':
        # adc a,n
        do += read_op()
        r = 'tmp8'
    else:
        raise SyntaxError('ADC invalid pair %s,%s' % (dst, src))    
    do.append('tmp16 = %(a)s + %(r)s + (%(f)s & CF)' % locals())
    do.append('tmp8 = ((%(a)s & 0x88) >> 3) | ((%(r)s & 0x88) >> 2) | ((tmp16 & 0x88) >> 1)' % locals())
    do += write_reg8(dst, 'tmp16')
    
    do += write_flags('(CF if tmp16 & 0x100 else 0) '
                      '| HALFCARRY_ADD_TABLE[tmp8 & 0x07] '
                      '| OVERFLOW_ADD_TABLE[tmp8 >> 4] '
                      '| SZ53_TABLE[%(a)s]' % locals())
        
    ret = std_head(code, op, table)
    ret += [IDENT + x for x in do] # add commands
    return make_code(code, ret, table)
GEN_DICT['ADC'] = adc

# #define ADC16(hl, value)\
# {\
#   Z80EX_DWORD add16temp= HL + (value) + ( F & FLAG_C ); \
#   Z80EX_BYTE lookup = ( (        HL & 0x8800 ) >> 11 ) | \
#               ( (   (value) & 0x8800 ) >> 10 ) | \
#               ( ( add16temp & 0x8800 ) >>  9 );  \
#   MEMPTR=hl+1;\
#   HL = add16temp;\
#   F = ( add16temp & 0x10000 ? FLAG_C : 0 )|\
#       overflow_add_table[lookup >> 4] |\
#       ( H & ( FLAG_3 | FLAG_5 | FLAG_S ) ) |\
#       halfcarry_add_table[lookup&0x07]|\
#       ( HL ? 0 : FLAG_Z );\
# }

def adc16(code, op, table=None):
    """ ADC HL"""
    dst, src = [x.lower() for x in op['mn'][1]]
    do = []
    hl = read_reg16(dst)
    h = read_reg8('h')
    l = read_reg8('l')
    f = read_reg8('f')
    
    if src in REG16:
        # adc hl,rr
        r = read_reg16(src)
    else:
        raise SyntaxError('ADC16 invalid pair %s,%s' % (dst, src))    
    do.append('tmp16 = %(hl)s + %(r)s + (%(f)s & CF)' % locals())
    do.append('tmp8 = ((%(hl)s & 0x8800) >> 11) | ((%(r)s & 0x8800) >> 10) | ((tmp16 & 0x8800) >> 9)' % locals())
    do += write_reg16(dst, 'tmp16')
    
    do += write_flags('(CF if tmp16 & 0x10000 else 0) '
                      '| OVERFLOW_ADD_TABLE[tmp8 >> 4] '
                      '| (%(h)s & XYSF) '
                      '| HALFCARRY_ADD_TABLE[tmp8 & 0x07] '
                      '| 0 if %(hl)s else ZF' % locals())
        
    ret = std_head(code, op, table)
    ret += [IDENT + x for x in do] # add commands
    return make_code(code, ret, table)


# #define ADD(a, value)\
# {\
#   Z80EX_WORD addtemp = A + (value); \
#   Z80EX_BYTE lookup = ( (       A & 0x88 ) >> 3 ) | \
#               ( ( (value) & 0x88 ) >> 2 ) | \
#               ( ( addtemp & 0x88 ) >> 1 );  \
#   A=addtemp;\
#   F = ( addtemp & 0x100 ? FLAG_C : 0 ) |\
#       halfcarry_add_table[lookup & 0x07] | overflow_add_table[lookup >> 4] |\
#       sz53_table[A];\
# }

def add(code, op, table=None):
    """ ADD"""
    dst, src = [x.lower() for x in op['mn'][1]]
    if dst in REG16:
        return add16(code, op, table=None)
    do = []
    a = read_reg8(dst)
    f = read_reg8('f')
    
    if src in REG8:
        # add a,r
        r = read_reg8(src)
    elif src in REG16IND:
        # add a,(rr)
        # do.append(mem_shortcut())
        do.append('tmp8 = %s' % read(read_reg16(src[1:-1])))
        r = 'tmp8'
    elif src in REGIDX:
        # add a,(ix+o)
        do.append(mem_shortcut())
        todo, r = read_idx(src, mem='mem')
        do += todo
        do.append('tmp8 = %(r)s' % locals())
        r = 'tmp8'
    elif src == '#':
        # add a,n
        do += read_op()
        r = 'tmp8'
    else:
        raise SyntaxError('ADD invalid pair %s,%s' % (dst, src))    
    do.append('tmp16 = %(a)s + %(r)s' % locals())
    do.append('tmp8 = ((%(a)s & 0x88) >> 3) | ((%(r)s & 0x88) >> 2) | ((tmp16 & 0x88) >> 1)' % locals())
    do += write_reg8(dst, 'tmp16')
    
    do += write_flags('(CF if tmp16 & 0x100 else 0) '
                      '| HALFCARRY_ADD_TABLE[tmp8 & 0x07] '
                      '| OVERFLOW_ADD_TABLE[tmp8 >> 4] '
                      '| SZ53_TABLE[%(a)s]' % locals())
        
    ret = std_head(code, op, table)
    ret += [IDENT + x for x in do] # add commands
    return make_code(code, ret, table)
GEN_DICT['ADD'] = add


# #define ADD16(value1,value2)\
# {\
#   Z80EX_DWORD add16temp = (value1) + (value2); \
#   Z80EX_BYTE lookup = ( (  (value1) & 0x0800 ) >> 11 ) | \
#               ( (  (value2) & 0x0800 ) >> 10 ) | \
#               ( ( add16temp & 0x0800 ) >>  9 );  \
#   MEMPTR=value1+1;\
#   (value1) = add16temp;\
#   F = ( F & ( FLAG_V | FLAG_Z | FLAG_S ) ) |\
#       ( add16temp & 0x10000 ? FLAG_C : 0 )|\
#       ( ( add16temp >> 8 ) & ( FLAG_3 | FLAG_5 ) ) |\
#       halfcarry_add_table[lookup];\
# }

def add16(code, op, table=None):
    """ ADC HL"""
    dst, src = [x.lower() for x in op['mn'][1]]
    do = []
    hl = read_reg16(dst)
    f = read_reg8('f')
    
    if src in REG16:
        # add rr,rr
        r = read_reg16(src)
    else:
        raise SyntaxError('ADD16 invalid pair %s,%s' % (dst, src))    
    do.append('tmp16 = %(hl)s + %(r)s' % locals())
    do.append('tmp8 = ((%(hl)s & 0x0800) >> 11) | ((%(r)s & 0x0800) >> 10) | ((tmp16 & 0x0800) >> 9)' % locals())
    do += write_reg16(dst, 'tmp16')
    
    do += write_flags('(%(f)s & VZSF) '
                      '| (CF if tmp16 & 0x10000 else 0) '
                      '| ((tmp16 >> 8) & XYF) '
                      '| HALFCARRY_ADD_TABLE[tmp8] ' % locals())
        
    ret = std_head(code, op, table)
    ret += [IDENT + x for x in do] # add commands
    return make_code(code, ret, table)


# #define BIT( bit, value ) \
# { \
#   F = ( F & FLAG_C ) | FLAG_H | sz53p_table[(value) & (0x01 << (bit))] | ((value) & 0x28); \
# }

def bit(code, op, table=None):
    """ BIT """
    bit, src = [x.lower() for x in op['mn'][1]]
    f = read_reg8('f')
    do = []
    bit = 0x01 << int(bit)
    
    if src in REG8:
        # bit n,r
        r = read_reg8(src)
    elif src in REG16IND:
        # bit n,(rr)
        do.append('tmp8 = %s' % read(read_reg16(src[1:-1])))
        r = 'tmp8'
    else:
        raise SyntaxError('BIT invalid source %s' % src)
    
    do += write_flags('(%(f)s & CF) | HF | SZ53_TABLE[%(r)s & 0x%(bit)02X] | (%(r)s & 0x28)' % locals())
        
    ret = std_head(code, op, table)
    ret += [IDENT + x for x in do] # add commands
    return make_code(code, ret, table)
GEN_DICT['BIT'] = bit


# /*BIT n,(IX+d/IY+d) and BIT n,(HL)*/
# #define BIT_MPTR( bit, value) \
# { \
#   F = ( F & FLAG_C ) | FLAG_H | (sz53p_table[(value) & (0x01 << (bit))] & 0xD7) | ((MEMPTRh) & 0x28); \
# }

# TODO bit_mptr

# #define CALL(addr, wr1, wr2) \
# {\
#   PUSH(PC,wr1,wr2); \
#   PC=addr; \
#   MEMPTR=addr;\
# }



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
        do.append(mem_shortcut())
        todo, r = read_idx(src, mem='mem')
        do += todo
        do += write_reg8(dst, r, False)
    elif (dst in REGIDX) and (src in REG8):
        # ld (ix+o), r
        # reg = 'ix' if 'ix' in dst else 'iy'
        do.append(mem_shortcut())
        do += write_idx(dst, read_reg8(src), 'mem')
        # do += read_op('mem')
        # do += to_signed('tmp8')
        # do += write(read_reg16(reg) + ' + tmp8', read_reg8(src), 'mem')
        # adr = 'self.%s + as_signed(self.read_op_arg())' % reg
        # ret = 'self.write(%(adr)s, self.%(src)s)' % locals()
    else:
        raise SyntaxError('LD: invalid pair %s, %s' % (dst, src))
    
    ret = std_head(code, op, table)
    ret += [IDENT + x for x in do] # add commands
    return make_code(code, ret, table)
GEN_DICT['LD'] = ld


# #define POP(rp, rd1, rd2) \
# {\
#   regpair tmp; \
#   READ_MEM(tmp.b.l,SP++,rd1);\
#   READ_MEM(tmp.b.h,SP++,rd2);\
#   rp=tmp.w;\
# }

def pop(code, op, table=None):
    """ POP """
    src = op['mn'][1].lower()
    do = []
    
    do.append(mem_shortcut())
    if src in REG16:
        # push rr
        do += pop_reg(src, 'mem')
    else:
        raise SyntaxError('POP invalid source %s' % src)
    
    ret = std_head(code, op, table)
    ret += [IDENT + x for x in do] # add commands
    return make_code(code, ret, table)
GEN_DICT['POP'] = pop


# /*wr1=t-states before first byte, wr2=t-states before second*/
# #define PUSH(rp, wr1, wr2) \
# {\
#   regpair tmp; \
#   tmp.w=rp; \
#   WRITE_MEM(--SP, tmp.b.h, wr1); \
#   WRITE_MEM(--SP, tmp.b.l, wr2); \
# }

def push(code, op, table=None):
    """ PUSH """
    src = op['mn'][1].lower()
    do = []
    
    do.append(mem_shortcut())
    if src in REG16:
        # push rr
        do += push_reg(src, 'mem')
    else:
        raise SyntaxError('PUSH invalid source %s' % src)
    
    ret = std_head(code, op, table)
    ret += [IDENT + x for x in do] # add commands
    return make_code(code, ret, table)
GEN_DICT['PUSH'] = push
