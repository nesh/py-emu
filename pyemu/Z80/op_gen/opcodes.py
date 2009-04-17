""" opcode generator for Z80, based on macros from Z80~Ex by boo_boo(^at^)inbox.ru """

from tools import *

__all__ = ('GEN_DICT',)


# globals
GEN_DICT = {}

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
        self.add_line('adctemp = $A + $r1 + ($F & CF)')
        self.add_line('lookup = (($A & 0x88) >> 3) | (($r1 & 0x88) >> 2) | ((adctemp & 0x88) >> 1)')
        self.add_lines(write_reg8(dst, 'adctemp'))
        self.set_flags('(CF if adctemp & 0x100 else 0)'
                       ' | HC_ADD_TABLE[lookup & 0x07]'
                       ' | OV_ADD_TABLE[lookup >> 4]'
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
        self.add_line('add16temp = $HL + $rr1 + ($F & CF)')
        self.add_line('$MEMPTR = $HL + 1')
        self.add_line('lookup = (($HL & 0x8800) >> 11) '
                      '| (($rr1 & 0x8800) >> 10) '
                      '| ((add16temp & 0x8800) >> 9)')
        self.add_lines(write_reg16(dst, 'add16temp'))
        self.set_flags('(CF if add16temp & 0x10000 else 0) '
                       '| OV_ADD_TABLE[lookup >> 4] '
                       '| ($H & XYSF) '
                       '| HC_ADD_TABLE[lookup & 0x07] '
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
        self.add_line('addtemp = $A + $r1')
        self.add_line('lookup = (($A & 0x88) >> 3) '
                      '| (($r1 & 0x88) >> 2) '
                      '| ((addtemp & 0x88) >> 1)')
        self.add_lines(write_reg8(dst, 'addtemp'))
        self.set_flags('(CF if addtemp & 0x100 else 0) '
                       '| HC_ADD_TABLE[lookup & 0x07] '
                       '| OV_ADD_TABLE[lookup >> 4] '
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
        self.add_line('add16temp = $rr + $rr1')
        self.add_line('lookup = (($rr & 0x0800) >> 11) '
                      '| (($rr1 & 0x0800) >> 10) '
                      '| ((add16temp & 0x0800) >> 9)')
        self.add_line('$MEMPTR = $rr + 1')
        self.add_lines(write_reg16(dst, 'add16temp'))
        self.set_flags('($F & VZSF) '
                       '| (CF if add16temp & 0x10000 else 0) '
                       '| ((add16temp >> 8) & XYF) '
                       '| HC_ADD_TABLE[lookup]')
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


class Cp(GenOp):
    """ CP
    
    #define CP(value)\
    {\
    	Z80EX_WORD cptemp = A - value; \
    	Z80EX_BYTE lookup = ( (       A & 0x88 ) >> 3 ) | \
    			    ( ( (value) & 0x88 ) >> 2 ) | \
    			    ( (  cptemp & 0x88 ) >> 1 );  \
    	F = ( cptemp & 0x100 ? FLAG_C : ( cptemp ? 0 : FLAG_Z ) ) | FLAG_N |\
    		halfcarry_sub_table[lookup & 0x07] |\
    			overflow_sub_table[lookup >> 4] |\
    			( value & ( FLAG_3 | FLAG_5 ) ) |\
    			( cptemp & FLAG_S );\
    }
    """
    def gen(self, dst, src, op):
        self.arg1(src)
        self.add_line('cptemp = $A - $r')
        self.add_line('lookup = (($A & 0x88) >> 3)'
                      ' | (($r & 0x88) >> 2)'
                      ' | ((cptemp & 0x88) >> 1)'
                      )
        self.set_flags('(CF if cptemp & 0x100 else 0)'
                       ' | NF'
                       ' | HC_SUB_TABLE[lookup & 0x07]'
                       ' | OV_SUB_TABLE[lookup >> 4]'
                       ' | SZ_TABLE[cptemp]'
                       ' | ($r & XYF)'
                      )
Cp(GEN_DICT)


class Dec(GenOp):
    """ 
    #define DEC(value)\
    {\
    	F = ( F & FLAG_C ) | ( (value)&0x0f ? 0 : FLAG_H ) | FLAG_N;\
    	(value)--;\
    	F |= ( (value)==0x7f ? FLAG_V : 0 ) | sz53_table[value];\
    }
    """
    def _flags1(self, val):
        self.set_flags('($F & CF)'
                       ' | (0 if %(val)s & 0x0F else HF)'
                       ' | NF' % locals()
                      )

    def _flags2(self, val):
        self.add_line('$F |= (VF if %(val)s == 0x7F else 0)'
                       ' | SZXY_TABLE[%(val)s]' % locals()
                      )
        
    def gen(self, dst, src, op):
        self.arg1(src)
        if src in REG8:
            self._flags1(read_reg8(src))
            self.add_lines(write_reg8(src, '%s - 1' % read_reg8(src)))
            self._flags2(read_reg8(src))
        elif src in REG16IND:
            reg = read_reg8(src[1:-1])
            self.add_line(mem_shortcut())
            self.add_line('tmp8 = %s' % read(reg, 'mem'))
            self._flags1('tmp8')
            self.add_line('tmp8 = (tmp8 - 1) & 0xFF')
            self._flags2('tmp8')
            self.add_lines(write(reg, 'tmp8', 'mem'))
        elif src in REGIDX:
            reg = 'ix' if 'ix' in src else 'iy'
            self.add_line('tmp16 = ' + read_reg16(reg) + ' + tmp8')
            self.add_line('tmp8 = %s' % read('tmp16', 'mem'))
            self._flags1('tmp8')
            self.add_line('tmp8 = (tmp8 - 1) & 0xFF')
            self._flags2('tmp8')
            self.add_lines(write('tmp16', 'tmp8', 'mem'))
        else:
            self.add_lines(write_reg16(src, '%s - 1' % read_reg16(src)))
Dec(GEN_DICT)


class Inc(GenOp):
    """ 
    #define INC(value)\
    {\
    	(value)++;\
    	F = ( F & FLAG_C ) | ( (value)==0x80 ? FLAG_V : 0 ) |\
    		( (value)&0x0f ? 0 : FLAG_H ) | sz53_table[(value)];\
    }
    """
    def _flags(self, val):
        self.set_flags('($F & CF)'
                       ' | (VF if %(val)s == 0x80 else 0)'
                       ' | (0 if %(val)s & 0x0F else HF)'
                       ' | SZXY_TABLE[%(val)s]' % locals()
                      )

        
    def gen(self, dst, src, op):
        self.arg1(src)
        if src in REG8:
            self.add_lines(write_reg8(src, '%s + 1' % read_reg8(src)))
            self._flags(read_reg8(src))
        elif src in REG16IND:
            reg = read_reg8(src[1:-1])
            self.add_line(mem_shortcut())
            self.add_line('tmp8 = %s' % read(reg, 'mem'))
            self.add_line('tmp8 = (tmp8 + 1) & 0xFF')
            self._flags('tmp8')
            self.add_lines(write(reg, 'tmp8', 'mem'))
        elif src in REGIDX:
            reg = 'ix' if 'ix' in src else 'iy'
            self.add_line('tmp16 = ' + read_reg16(reg) + ' + tmp8')
            self.add_line('tmp8 = %s' % read('tmp16', 'mem'))
            self.add_line('tmp8 = (tmp8 + 1) & 0xFF')
            self._flags('tmp8')
            self.add_lines(write('tmp16', 'tmp8', 'mem'))
        else:
            self.add_lines(write_reg16(src, '%s + 1' % read_reg16(src)))
Inc(GEN_DICT)


class Ld(GenOp):
    def gen(self, dst, src, op):
        """ LD r, r1"""
        if dst == src:
            # ld a,a and others
            pass # no-op
        elif (dst == 'a') and (src in ('r', 'i')):
            # reading R and I changes flags!
            r = read_reg8(src)
            self.add_lines(write_reg8(dst, r))
            f = read_flags()
            self.set_flags('($F & CF)'
                           ' | SZXY_TABLE[%(r)s]'
                           ' | (VF if $IFF2 else 0)' % locals())
        elif ((dst in REG8) or (dst in ('r', 'i'))) and (src in REG8):
            # ld r,r1
            self.add_lines(write_reg8(dst, read_reg8(src), False))
        elif (dst in REG16) and (src in REG16):
            # ld rr,rr1
            self.add_lines(write_reg16(dst, read_reg16(src), False))
        elif (dst in REG16) and (src == '@'):
            # ld rr,nnnn
            self.add_line(mem_shortcut())
            self.add_lines(read_op16('mem') + write_reg16(dst, 'tmp16', False))
        elif (dst in REG8) and (src == '#'):
            # ld r, n
            self.add_lines(read_op() + write_reg8(dst, 'tmp8', False))
        elif (dst in REG16IND) and (src in REG8):
            # ld (rr), r
            self.add_lines(write(read_reg16(dst[1:-1]), read_reg8(src)))
            # memptr
            self.add_line('$MEMPTRH = %s' % read_reg8(src))
            self.add_line('$MEMPTRL = %s + 1' % read_reg16(dst[1:-1]))
        elif (dst in REG16IND) and (src == '#'):
            # ld (rr), nn
            self.add_line(mem_shortcut())
            self.add_lines(read_op('mem') + write(read_reg16(dst[1:-1]), 'tmp8', 'mem'))
        elif (dst in REG8) and (src in REG16IND):
            # ld r, (rr)
            self.add_lines(write_reg8(dst, read(read_reg16(src[1:-1])), False))
            # memptr
            self.add_line('$MEMPTR = (%s + 1) & 0xFFFF' % read_reg16(src[1:-1]))
        elif (dst == '(@)') and (src in REG16):
            # ld (nnnn), rr
            self.add_line(mem_shortcut())
            self.add_lines(read_op16('mem') + write16('tmp16', read_reg16(src), 'mem'))
            # memptr
            self.add_line('$MEMPTR = (tmp16 + 1) & 0xFFFF')
        elif (dst in REG16) and (src == '(@)'):
            # ld rr, (nnnn)
            self.add_line(mem_shortcut())
            self.add_lines(read_op16('mem') + write_reg16(dst, read16('tmp16', 'mem'), False))
            # memptr
            self.add_line('$MEMPTR = (%s + 1) & 0xFFFF' % read_reg16(dst))
        elif (dst == '(@)') and (src in REG8):
            # ld (nnnn), r
            self.add_line(mem_shortcut())
            self.add_lines(read_op16('mem') + write('tmp16', read_reg8(src), 'mem'))
        elif (dst in REG8) and (src == '(@)'):
            # ld r, (nnnn)
            self.add_line(mem_shortcut())
            self.add_lines(read_op16('mem') + write_reg8(dst, read('tmp16', 'mem')))
        elif (dst in REGIDX) and (src == '#'):
            # ld (ix+o), nn
            reg = 'ix' if 'ix' in dst else 'iy'
            self.add_line(mem_shortcut())
            self.add_lines(read_op('mem'))
            self.add_lines(to_signed('tmp8'))
            self.add_line('tmp16 = ' + read_reg16(reg) + ' + tmp8')
            self.add_lines(read_op('mem') + write('tmp16', 'tmp8', 'mem'))
        elif (dst in REG8) and (src in REGIDX):
            # ld r, (ix+o)
            self.add_line(mem_shortcut())
            todo, r = read_idx(src, mem='mem')
            self.add_lines(todo + write_reg8(dst, r, False))
        elif (dst in REGIDX) and (src in REG8):
            # ld (ix+o), r
            self.add_line(mem_shortcut())
            self.add_lines(write_idx(dst, read_reg8(src), 'mem'))
        else:
            raise SyntaxError('LD: invalid pair %s, %s' % (dst, src))
Ld(GEN_DICT)


class Jp(GenOp):
    """ 
	PC=addr; \
	MEMPTR=addr;\
    """
    def gen(self, cond, src, op):
        self.add_line(mem_shortcut())
        # where to jump
        if src == '@':
            self.add_lines(read_op16('mem'))
        elif src in REG16:
            self.add_line('tmp16 = %s' % read_reg16(src))
        else:
            raise SyntaxError('CALL: invald address %s' % src)
        if cond is None:
            self.add_line('$PC = tmp16')
            if src == '@': self.add_line('$MEMPTR = tmp16')
        else:
            # cond call
            if cond not in COND:
                raise SyntaxError('CALL: invald condition %s' % cond)
            self.add_line('if %s:' % COND[cond])
            self.add_line('# taken', 2)
            self.add_line('$PC = tmp16', 2)
            if src == '@': self.add_line('$MEMPTR = tmp16', 2)
            self.add_t(op['t'][1], 2)
            self.add_line('else:')
            self.add_line('# not taken', 2)
            self.add_t(op['t'][0], 2)
Jp(GEN_DICT)


class Jr(GenOp):
    """ 
	PC+=offset; \
	MEMPTR=PC;\
    """
    def gen(self, cond, src, op):
        self.add_line(mem_shortcut())
        self.add_lines(read_op('mem'))
        self.add_lines(to_signed('tmp8'))
        if cond is None:
            self.add_line('$MEMPTR = ($PC + tmp8) & 0xFFFF')
            self.add_line('$PC = $MEMPTR')
        else:
            # cond call
            if cond not in COND:
                raise SyntaxError('CALL: invald condition %s' % cond)
            self.add_line('if %s:' % COND[cond])
            self.add_line('# taken', 2)
            self.add_line('$MEMPTR = ($PC + tmp8) & 0xFFFF', 2)
            self.add_line('$PC = $MEMPTR', 2)
            self.add_t(op['t'][1], 2)
            self.add_line('else:')
            self.add_line('# not taken', 2)
            self.add_t(op['t'][0], 2)
Jr(GEN_DICT)


class Or(GenOp):
    """
    #define OR(value)\
    {\
    	A |= (value);\
    	F = sz53p_table[A];\
    }
    """
    def gen(self, dst, src, op):
        self.arg1(src)
        self.add_line('$A |= $r')
        self.set_flags('SZXYP_TABLE[$A]')
Or(GEN_DICT)


class Out(GenOp):
    """
    #define OUT(port,reg, wr) \
    {\
    	WRITE_PORT(port,reg,wr); \
    	MEMPTR=port+1;\
    }
    """
    def gen(self, dst, src, op):
        port = dst[1:-1]
        reg = read_reg8(src)
        if (port == '#') and (src in REG8):
            self.add_lines(read_op())
            port = self.format('tmp8 + ($A * 256)')
            self.add_line('$MEMPTRL = %s + 1' % port)
            self.add_line('$MEMPTRH = $A')
        elif (port == 'c') and (src in REG8):
            port = read_reg16('bc')
            self.add_line('$MEMPTR = (%s + 1) & 0xFFFF' % port)
        elif (port == 'c') and (src == '0'):
            port = read_reg16('bc')
            reg = '0x00'
            self.add_line('$MEMPTR = (%s + 1) & 0xFFFF' % port)
        else:
            raise SyntaxError('OUT: invald pair %s,%s' % (dst, src))
        self.add_lines(io_write(port, reg))
Out(GEN_DICT)


class In(GenOp):
    """
    	READ_PORT(reg,port,rd); \
    	F = ( F & FLAG_C) | sz53p_table[(reg)];\
    	MEMPTR=port+1;\
    """
    def gen(self, dst, src, op):
        port = src[1:-1]
        reg = read_reg8(dst)
        if (port == '#') and (dst in REG8):
            self.add_lines(read_op())
            port = self.format('tmp8 + ($A * 256)')
            self.add_line('$MEMPTRL = %s + 1' % port)
            self.add_line('$MEMPTRH = $A')
            self.add_lines(write_reg8(dst, io_read(port), False))
        elif (port == 'c') and (dst in REG8):
            port = read_reg16('bc')
            self.add_line('$MEMPTR = (%s + 1) & 0xFFFF' % port)
            self.add_lines(write_reg8(dst, io_read(port), False))
            self.set_flags('($F & CF) | SZXYP_TABLE[%s]' % reg)
        elif (port == 'c') and (dst is None):
            # IN (C)
            port = read_reg16('bc')
            self.add_line('$MEMPTR = (%s + 1) & 0xFFFF' % port)
            self.set_flags('($F & CF) | SZXYP_TABLE[%s]' % io_read(port))
        else:
            raise SyntaxError('IN: invald pair %s,%s' % (dst, src))
In(GEN_DICT)


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


class Ret(GenOp):
    """ 
    #define RET(rd1, rd2) \
    {\
    	POP(PC, rd1, rd2);\
    	MEMPTR=PC;\
    }
    """
    def gen(self, dst, cond, op):
        if cond is None:
            self.add_lines(pop_reg('pc'))
            self.add_line('$MEMPTR = $PC')
        else:
            # cond call
            if cond not in COND:
                raise SyntaxError('RET: invald condition %s' % cond)
            self.add_line('if %s:' % COND[cond])
            self.add_line('# taken', 2)
            self.add_lines(pop_reg('pc'), 2)
            self.add_line('$MEMPTR = $PC', 2)
            self.add_t(op['t'][1], 2)
            self.add_line('else:')
            self.add_line('# not taken', 2)
            self.add_t(op['t'][0], 2)
Ret(GEN_DICT)
