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
    
    def gen(self, dst, src):
        if (dst in REG16) and (src in REG16):
            self.adc16(dst, src)
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
    def gen(self, dst, src):
        """ ADC A,r1"""
        if (dst in REG16) and (src in REG16):
            self._adc16(dst, src)
            return
        self.add_line('tmp16 = $A + $r1 + ($F & CF)')
        self.add_line('tmp8 = (($A & 0x88) >> 3) | (($r1 & 0x88) >> 2) | ((tmp16 & 0x88) >> 1)')
        self.add_lines(write_reg8(dst, 'tmp16'))
        self.set_flags('(CF if tmp16 & 0x100 else 0)'
                       ' | HC_ADD_TABLE[tmp8 & 0x07]'
                       ' | OV_ADD_TABLE[tmp8 >> 4]'
                       ' | SZXY_TABLE[$A]')
    
    def _adc16(self, dst, src):
        """ ADC HL,rr
        #define ADC16(hl, value)\
        {\
          Z80EX_DWORD add16temp= HL + (value) + ( F & FLAG_C ); \
          Z80EX_BYTE lookup = ( (        HL & 0x8800 ) >> 11 ) | \
                      ( (   (value) & 0x8800 ) >> 10 ) | \
                      ( ( add16temp & 0x8800 ) >>  9 );  \
          MEMPTR=hl+1; <------- WTF?
          HL = add16temp;\
          F = ( add16temp & 0x10000 ? FLAG_C : 0 )|\
              overflow_add_table[lookup >> 4] |\
              ( H & ( FLAG_3 | FLAG_5 | FLAG_S ) ) |\
              halfcarry_add_table[lookup&0x07]|\
              ( HL ? 0 : FLAG_Z );\
        }
        """
        
        self.add_line('tmp16 = $HL + $rr1 + ($F & CF)')
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
    def gen(self, dst, src):
        """ ADD r,r1 """
        if (dst in REG16) and (src in REG16):
            return self._add16(dst, src)
        self.add_line('tmp16 = $A + $r1')
        self.add_line('tmp8 = (($A & 0x88) >> 3) '
                      '| (($r1 & 0x88) >> 2) '
                      '| ((tmp16 & 0x88) >> 1)')
        self.add_lines(write_reg8(dst, 'tmp16'))
        self.set_flags('(CF if tmp16 & 0x100 else 0) '
                       '| HC_ADD_TABLE[tmp8 & 0x07] '
                       '| OV_ADD_TABLE[tmp8 >> 4] '
                       '| SZXY_TABLE[$A]')

    def _add16(self, dst, src):
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
        self.add_line('tmp16 = $rr + $rr1')
        self.add_line('tmp8 = (($rr & 0x0800) >> 11) '
                      '| (($rr1 & 0x0800) >> 10) '
                      '| ((tmp16 & 0x0800) >> 9)')
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
    """
    def gen(self, dst, src):
        bit = 0x01 << int(dst)
        self.set_flags('($F & CF)'
                       ' | HF'
                       ' | SZXY_TABLE[$r1 & 0x%(bit)02X]'
                       ' | ($r1 & 0x28)' % locals())
Bit(GEN_DICT)

class BitMPTR(GenOp):
    """
    /*BIT n,(IX+d/IY+d) and BIT n,(HL)*/
    #define BIT_MPTR( bit, value) \
    { \
      F = ( F & FLAG_C ) | FLAG_H | (sz53p_table[(value) & (0x01 << (bit))] & 0xD7) | ((MEMPTRh) & 0x28); \
    }
    """
    pass
# TBD


class Nop(GenOp):
    def gen(self, dst, src):
        pass
Nop(GEN_DICT)

class Ld(GenOp):
    def gen(self, dst, src):
        """ LD r, r1"""
        if dst == src:
            pass # no-op
        elif (dst == 'a') and (src in REG8_SPEC):
            # ld a,i/r (changes flags!)
            self.add_lines(write_reg8(dst, self.args['r']))
            self.set_flags('($F & CF) '
                           '| SZXY_TABLE[$r1] '
                           '| (VF if $IFF2 else 0)')
        elif dst in (REG8 + REG8_SPEC):
            self.add_lines(write_reg8(dst, self.args['r1'], force=False))
        elif dst in REG16:
            self.add_lines(write_reg16(dst, self.args['rr1'], force=False))
        elif dst in REG16IND:
            self.args['rr'] = read_reg16(dst[1:-1])
        else:
            raise SyntaxError('LD: invalid pair %s, %s' % (dst, src))
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
    def gen(self, dst, src):
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
    def gen(self, dst, src):
        self.add_line(mem_shortcut())
        self.add_lines(push_reg(src, 'mem'))
Push(GEN_DICT)