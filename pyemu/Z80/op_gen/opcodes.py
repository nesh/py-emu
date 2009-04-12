""" opcode generator for Z80, based on macros from Z80~Ex by boo_boo(^at^)inbox.ru """

from tools import *

__all__ = ('GEN_DICT',)


# globals
GEN_DICT = {}


class And(GenOp):
    """ AND
    
    #define AND(value)\
    {\
      A &= (value);\
      F = FLAG_H | sz53p_table[A];\
    }
    """
    def gen(self, dst, src, op):
        self.arg1(src)
        self.add_line('$A &= $r')
        self.set_flags('HF | SZXYP_TABLE[$A]')
And(GEN_DICT)


class Adc(GenOp):
    """ ADC
    #define ADC(a, value)\
    {\
      Z80EX_WORD adctemp = A + (value) + ( F & FLAG_C ); \
      Z80EX_BYTE lookup = ( (       A & 0x88 ) >> 3 ) | \
                  ( ( (value) & 0x88 ) >> 2 ) | \
                  ( ( adctemp & 0x88 ) >> 1 );  \
      A=adctemp;\
      F = ( adctemp & 0x100 ? FLAG_C : 0 ) |\
          halfcarry_add_table[lookup & 0x07] | overflow_add_table[lookup >> 4] |\
          sz53_table[A];\
    }
    """
    def gen(self, dst, src, op):
        """ ADC A,r1"""
        if (dst in REG16) and (src in REG16):
            return self._adc16(dst, src, op)
        self.arg2(dst, src)
        self.add_line('tmp16 = $A + $r1 + ($F & CF)')
        self.add_line('tmp8 = (($A & 0x88) >> 3) | (($r1 & 0x88) >> 2) | ((tmp16 & 0x88) >> 1)')
        self.add_lines(write_reg8(dst, 'tmp16'))
        self.set_flags('(CF if tmp16 & 0x100 else 0)'
                       ' | HC_ADD_TABLE[tmp8 & 0x07]'
                       ' | OV_ADD_TABLE[tmp8 >> 4]'
                       ' | SZXY_TABLE[$A]')
    
    def _adc16(self, dst, src, op):
        """ ADC HL,rr
        #define ADC16(hl, value)\
        {\
          Z80EX_DWORD add16temp= HL + (value) + ( F & FLAG_C ); \
          Z80EX_BYTE lookup = ( (        HL & 0x8800 ) >> 11 ) | \
                      ( (   (value) & 0x8800 ) >> 10 ) | \
                      ( ( add16temp & 0x8800 ) >>  9 );  \
          MEMPTR=hl+1;
          HL = add16temp;\
          F = ( add16temp & 0x10000 ? FLAG_C : 0 )|\
              overflow_add_table[lookup >> 4] |\
              ( H & ( FLAG_3 | FLAG_5 | FLAG_S ) ) |\
              halfcarry_add_table[lookup&0x07]|\
              ( HL ? 0 : FLAG_Z );\
        }
        """
        
        self.arg2_16(dst, src)
        self.add_line('tmp16 = $HL + $rr1 + ($F & CF)')
        self.add_line('$MEMPTR = $HL + 1')
        self.add_line('tmp8 = (($HL & 0x8800) >> 11) '
                      '| (($rr1 & 0x8800) >> 10) '
                      '| ((tmp16 & 0x8800) >> 9)')
        self.add_lines(write_reg16(dst, 'tmp16'))
        self.set_flags('(CF if tmp16 & 0x10000 else 0) '
                       '| OV_ADD_TABLE[tmp8 >> 4] '
                       '| ($H & XYSF) '
                       '| HC_ADD_TABLE[tmp8 & 0x07] '
                       '| 0 if $H else ZF')
Adc(GEN_DICT)

class Add(GenOp):
    """
    #define ADD(a, value)\
    {\
      Z80EX_WORD addtemp = A + (value); \
      Z80EX_BYTE lookup = ( (       A & 0x88 ) >> 3 ) | \
                  ( ( (value) & 0x88 ) >> 2 ) | \
                  ( ( addtemp & 0x88 ) >> 1 );  \
      A=addtemp;\
      F = ( addtemp & 0x100 ? FLAG_C : 0 ) |\
          halfcarry_add_table[lookup & 0x07] | overflow_add_table[lookup >> 4] |\
          sz53_table[A];\
    }
    """
    def gen(self, dst, src, op):
        """ ADD r,r1 """
        if (dst in REG16) and (src in REG16):
            return self._add16(dst, src, op)
        self.arg2(dst, src)
        self.add_line('tmp16 = $A + $r1')
        self.add_line('tmp8 = (($A & 0x88) >> 3) '
                      '| (($r1 & 0x88) >> 2) '
                      '| ((tmp16 & 0x88) >> 1)')
        self.add_lines(write_reg8(dst, 'tmp16'))
        self.set_flags('(CF if tmp16 & 0x100 else 0) '
                       '| HC_ADD_TABLE[tmp8 & 0x07] '
                       '| OV_ADD_TABLE[tmp8 >> 4] '
                       '| SZXY_TABLE[$A]')

    def _add16(self, dst, src, op):
        """ ADD rr,rr1
        #define ADD16(value1,value2)\
        {\
          Z80EX_DWORD add16temp = (value1) + (value2); \
          Z80EX_BYTE lookup = ( (  (value1) & 0x0800 ) >> 11 ) | \
                      ( (  (value2) & 0x0800 ) >> 10 ) | \
                      ( ( add16temp & 0x0800 ) >>  9 );  \
          MEMPTR=value1+1;\
          (value1) = add16temp;\
          F = ( F & ( FLAG_V | FLAG_Z | FLAG_S ) ) |\
              ( add16temp & 0x10000 ? FLAG_C : 0 )|\
              ( ( add16temp >> 8 ) & ( FLAG_3 | FLAG_5 ) ) |\
              halfcarry_add_table[lookup];\
        }
        """
        self.arg2_16(dst, src)
        self.add_line('tmp16 = $rr + $rr1')
        self.add_line('tmp8 = (($rr & 0x0800) >> 11) '
                      '| (($rr1 & 0x0800) >> 10) '
                      '| ((tmp16 & 0x0800) >> 9)')
        self.add_line('$MEMPTR = $rr + 1')
        self.add_lines(write_reg16(dst, 'tmp16'))
        self.set_flags('($F & VZSF) '
                       '| (CF if tmp16 & 0x10000 else 0) '
                       '| ((tmp16 >> 8) & XYF) '
                       '| HC_ADD_TABLE[tmp8]')
Add(GEN_DICT)

class Bit(GenOp):
    """ BIT n,r
        #define BIT( bit, value ) \
        { \
          F = ( F & FLAG_C ) | FLAG_H | sz53p_table[(value) & (0x01 << (bit))] | ((value) & 0x28); \
        }

        /*BIT n,(IX+d/IY+d) and BIT n,(HL)*/ -- TODO???
        #define BIT_MPTR( bit, value) \
        { \
          F = ( F & FLAG_C ) | FLAG_H | (sz53p_table[(value) & (0x01 << (bit))] & 0xD7) | ((MEMPTRh) & 0x28); \
        }
    """
    def gen(self, dst, src, op):
        self.arg_bit(dst, src)
        bit = 0x01 << int(dst)
        self.set_flags('($F & CF)'
                       ' | HF'
                       ' | SZXYP_TABLE[$r1 & 0x%(bit)02X]' % locals())
                       # ' | ($r1 & 0x28)' % locals())
Bit(GEN_DICT)


class Nop(GenOp):
    def gen(self, dst, src, op):
        pass
Nop(GEN_DICT)

COND = {
    'c': '$F & CF',
    'nc': 'not ($F & CF)',
    'nz': 'not ($F & ZF)',
    'z': '$F & ZF',
    'pe': '$F & PF',
    'po': 'not ($F & PF)',
    'p': 'not ($F & SF)',
    'm': '$F & SF',
}

class Call(GenOp):
    """ CALL
    
	PUSH(PC,wr1,wr2); \
	PC=addr; \
	MEMPTR=addr;\
    """
    def gen(self, cond, src, op):
        self.add_line(mem_shortcut())
        self.add_lines(read_op16('mem'))
        if cond is None:
            self.add_lines(push_reg('pc', 'mem'))
            self.add_line('$PC = tmp16')
            return
        # cond call
        if cond not in COND:
            raise SyntaxError('CALL: invald condition %s' % cond)
        self.add_line('if %s:' % COND[cond])
        self.add_line('# taken', 2)
        self.add_lines(push_reg('pc', 'mem'), 2)
        self.add_line('$PC = tmp16', 2)
        self.add_t(op['t'][1], 2)
        self.add_line('else:')
        self.add_line('# not taken', 2)
        self.add_t(op['t'][0], 2)
Call(GEN_DICT)


class Ld(GenOp):
    def gen(self, dst, src, op):
        """ LD r, r1"""
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
            do += write_reg16(dst, read16('tmp16', 'mem'), False)
        elif (dst == '(@)') and (src in REG8):
            # ld (nnnn), r
            do.append(mem_shortcut())
            do += read_op16('mem')
            do += write('tmp16', read_reg8(src), 'mem')
        elif (dst in REG8) and (src == '(@)'):
            # ld r, (nnnn)
            do.append(mem_shortcut())
            do += read_op16('mem')
            do += write_reg8(dst, read('tmp16', 'mem'))
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
        self.do = do
Ld(GEN_DICT)


class Pop(GenOp):
    """
    #define POP(rp, rd1, rd2) \
    {\
      regpair tmp; \
      READ_MEM(tmp.b.l,SP++,rd1);\
      READ_MEM(tmp.b.h,SP++,rd2);\
      rp=tmp.w;\
    }
    """
    def gen(self, dst, src, op):
        self.add_line(mem_shortcut())
        self.add_lines(pop_reg(src, 'mem'))
Pop(GEN_DICT)

class Push(GenOp):
    """
        /*wr1=t-states before first byte, wr2=t-states before second*/
        #define PUSH(rp, wr1, wr2) \
        {\
          regpair tmp; \
          tmp.w=rp; \
          WRITE_MEM(--SP, tmp.b.h, wr1); \
          WRITE_MEM(--SP, tmp.b.l, wr2); \
        }
    """
    def gen(self, dst, src, op):
        self.add_line(mem_shortcut())
        self.add_lines(push_reg(src, 'mem'))
Push(GEN_DICT)