import warnings

IDENT = ' '*4
ADD_T = 'self.icount -= %d; self.itotal += %d'
#READ_OP = 'self.read(self.pc); self.pc = (self.pc + 1) & 0xFFFF'
READ_OP = 'self.read_op_arg()'
CMDS = {}
# XXX unfold read_*?

_REG8 = ('a', 'f', 'b', 'c', 'd', 'e', 'h', 'l', 'r', 'i', 'ixh', 'ixl', 'iyh', 'iyl')
_REG16 = ('af', 'bc', 'de', 'hl', 'ix', 'iy', 'pc', 'sp', 'af1')
_REG16IND = ('(bc)', '(de)', '(hl)', '(sp)')
_REGIDX = ('(ix+$)', '(iy+$)')
_COND = ('c', 'z', )
_NOTCOND = ('nc', 'nz', )


class _OpBase(object):
    def parse_bits(self, bits):
        self.opcode = bits[0]
        if len(bits) > 1:
            args = bits[1].split(',')
            
            self.dst = args[0].lower()
            if len(args) > 1:
                self.src = args[1].lower()
    
    def __call__(self, type_, code, op, tstates, bits):
        self.parse_bits(bits)
        self.name = ' '.join(bits)
        self.type = type_
        self.code = code
        self.op = op
        self.tstates = tstates
        return self.parse()


class NOP(_OpBase):
    def parse(self):
        return ['pass']
CMDS['NOP'] = NOP()

class LD(_OpBase):
    def parse(self):
        opcode, dst, src = self.opcode, self.dst, self.src
        if dst == src:
            ret = 'pass'
        elif (dst == 'a') and (src == 'r'):
            # A=(R&0x7f) | (R7&0x80);\
            # F = ( F & FLAG_C ) | sz53_table[A] | ( IFF2 ? FLAG_V : 0 );\
            return [
                'self.a = self.r',
                'self.f = (self.f & CF) | SZXY_TABLE[self.a] | (VF if self.iff2 else 0)'
            ]
        elif (dst == 'a') and (src == 'i'):
            # A=I;\
            # F = ( F & FLAG_C ) | sz53_table[A] | ( IFF2 ? FLAG_V : 0 );\
            return [
                'self.a = self.i',
                'self.f = (self.f & CF) | SZXY_TABLE[self.a] | (VF if self.iff2 else 0)'
            ]
        elif (src == 'a') and (dst == 'r'):
            ret = 'self.r = self.r7 = self.a'
        elif ((dst in _REG8) and (src in _REG8)) or ((dst in _REG16) and (src in _REG16)):
            ret = 'self.%(dst)s = self.%(src)s' % locals()
        elif (dst in _REG16) and (src == '@'):
            ret = 'self.%(dst)s = self.read_op_arg16()' % locals()
        elif (dst in _REG8) and (src == '#'):
            ret = 'self.%(dst)s = self.read_op()' % locals()
        elif (dst in _REG16IND) and (src in _REG8):
            dst = dst[1:-1] # strip ()
            ret = 'self.write(self.%(dst)s, self.%(src)s)' % locals()
        elif (dst in _REG16IND) and (src == '#'):
            dst = dst[1:-1] # strip ()
            ret = 'self.write(self.%(dst)s, self.read_op_arg())' % locals()
        elif (dst in _REG8) and (src in _REG16IND):
            src = src[1:-1] # strip ()
            ret = 'self.%(dst)s = self.read(self.%(src)s)' % locals()
        elif (dst == '(@)') and (src in _REG16):
            ret = 'self.write16(self.read_op_arg16(), self.%(src)s)' % locals()
        elif (dst in _REG16) and (src == '(@)'):
            ret = 'self.%(dst)s = self.read16(self.read_op_arg16())' % locals()
        elif (dst == '(@)') and (src in _REG8):
            ret = 'self.write(self.read_op_arg16(), self.%(src)s)' % locals()
        elif (dst in _REG8) and (src == '(@)'):
            ret = 'self.%(dst)s = self.read(self.read_op_arg16())' % locals()
        elif (dst in _REGIDX) and (src == '#'):
            reg = 'ix' if 'ix' in dst else 'iy'
            adr = 'self.%s + as_signed(self.read_op_arg())' % reg
            ret = 'self.write(%(adr)s, self.read_op_arg())' % locals()
        elif (dst in _REG8) and (src in _REGIDX):
            reg = 'ix' if 'ix' in src else 'iy'
            adr = 'self.%s + as_signed(self.read_op_arg())' % reg
            ret = 'self.%(dst)s = self.read(%(adr)s)' % locals()
        elif (dst in _REGIDX) and (src in _REG8):
            reg = 'ix' if 'ix' in dst else 'iy'
            adr = 'self.%s + as_signed(self.read_op_arg())' % reg
            ret = 'self.write(%(adr)s, self.%(src)s)' % locals()
        elif ('rr' in src) or ('rl' in src) or ('sla' in src) or ('sra' in src) or ('sll' in src) or ('srl' in src) or ('res' in src) or ('set' in src):
            # TODO remove as shift/bit operations are implemented
            warnings.warn('skipping %s' % self.name)
            return []
        else:
            raise ValueError('unhandled pair %(opcode)s: %(dst)s, %(src)s' % locals())
        return [ret]
CMDS['LD'] = LD()

class INC(_OpBase):
    def parse(self):
        opcode, dst = self.opcode, self.dst
        
        # (value)++;\
        # F = ( F & FLAG_C ) | ( (value)==0x80 ? FLAG_V : 0 ) |\
        #   ( (value)&0x0f ? 0 : FLAG_H ) | sz53_table[(value)];\
        flags8 = 'self.f = (self.f & CF) | (VF if v == 0x80 else 0) ' \
                 '| (0 if v & 0x0F else HF) | SZXY_TABLE[v]'
        
        if dst in _REG16IND:
            dst = dst[1:-1]
            ret = [
                'v = self.read(self.%(dst)s)' % locals(),
                'v = (v + 1) & 0xFF',
                'self.write(self.%(dst)s, v)' % locals(),
                flags8,
            ]
        elif dst in _REG16:
            ret = [
                'self.%(dst)s = (self.%(dst)s + 1) & 0xFFFF' % locals()
            ]
        elif dst in _REG8:
            ret = [
                'v = self.%(dst)s' % locals(),
                'v = (v + 1) & 0xFF',
                'self.%(dst)s = v' % locals(),
                flags8,
            ]
        elif dst in _REGIDX:
            reg = 'ix' if 'ix' in dst else 'iy'
            adr = 'self.%s + as_signed(self.read_op_arg())' % reg
            ret = [
                'ptr = %(adr)s' % locals(),
                'v = self.read(ptr)',
                'v = (v + 1) & 0xFF',
                'self.write(ptr, v)',
                flags8,
            ]
        else:
            raise ValueError('unhandled pair %(opcode)s: %(dst)s' % locals())
        return ret
CMDS['INC'] = INC()


class DEC(_OpBase):
    def parse(self):
        opcode, dst = self.opcode, self.dst
        
        # F = ( F & FLAG_C ) | ( (value)&0x0f ? 0 : FLAG_H ) | FLAG_N;\
        # (value)--;\
        # F |= ( (value)==0x7f ? FLAG_V : 0 ) | sz53_table[value];\
        flags1 = 'self.f = (self.f & CF) | (0 if v & 0x0F else HF) | NF'
        flags2 = 'self.f |= (VF if v == 0x7F else 0) | SZXY_TABLE[v]'
        if dst in _REG16IND:
            dst = dst[1:-1]
            ret = [
                'v = self.read(self.%(dst)s)' % locals(),
                flags1,
                'v = (v - 1) & 0xFF',
                'self.write(self.%(dst)s, v)' % locals(),
                flags2,
            ]
        elif dst in _REG16:
            ret = [
                'self.%(dst)s = (self.%(dst)s - 1) & 0xFFFF' % locals()
            ]
        elif dst in _REG8:
            ret = [
                'v = self.%(dst)s' % locals(),
                flags1,
                'v = (v - 1) & 0xFF',
                'self.%(dst)s = v' % locals(),
                flags2,
            ]
        elif dst in _REGIDX:
            reg = 'ix' if 'ix' in dst else 'iy'
            adr = 'self.%s + as_signed(self.read_op_arg())' % reg
            ret = [
                'ptr = %(adr)s' % locals(),
                'v = self.read(ptr)',
                flags1,
                'v = (v - 1) & 0xFF',
                'self.write(ptr, v)',
                flags2,
            ]
        else:
            raise ValueError('unhandled pair %(opcode)s: %(dst)s' % locals())
        return ret
CMDS['DEC'] = DEC()


class RLCA(_OpBase):
    def parse(self):
        # A = ( A << 1 ) | ( A >> 7 );\
        # F = ( F & ( FLAG_P | FLAG_Z | FLAG_S ) ) |\
        #   ( A & ( FLAG_C | FLAG_3 | FLAG_5 ) );\
        return [
            'a = self.a',
            'a = (a << 1) | (a >> 7)',
            'self.f = (self.f & PZSF) | (a & CXYF)',
            'self.a = a & 0xFF'
        ]
CMDS['RLCA'] = RLCA()


class EX(_OpBase):
    def parse(self):
        opcode, dst, src = self.opcode, self.dst, self.src
        if (dst in _REG16) and (src in _REG16):
            return [
                'self.%(dst)s, self.%(src)s = self.%(src)s, self.%(dst)s' % locals()
            ]
        if (dst in _REG16IND) and (src in _REG16):
            dst = dst[1:-1]
            return [
                'tmp = self.%(src)s' % locals(),
                'self.%(src)s = self.read16(self.%(dst)s)' % locals(),
                'self.write16(self.%(dst)s, tmp)' % locals(),
            ]
        else:
            raise ValueError('unhandled pair %(opcode)s: %(dst)s, %(src)s' % locals())
        return ret
CMDS['EX'] = EX()


class ADD(_OpBase):
    def parse(self):
        opcode, dst, src = self.opcode, self.dst, self.src
        if dst == 'a':
            ret = []
            if src in _REG8: # r, r
                # 8bit
                # Z80EX_WORD addtemp = A + (value); \
                # Z80EX_BYTE lookup = ( (       A & 0x88 ) >> 3 ) | \
                #           ( ( (value) & 0x88 ) >> 2 ) | \
                #           ( ( addtemp & 0x88 ) >> 1 );  \
                # A=addtemp;\
                # F = ( addtemp & 0x100 ? FLAG_C : 0 ) |\
                #   halfcarry_add_table[lookup & 0x07] | overflow_add_table[lookup >> 4] |\
                #   sz53_table[A];\
                arg = 'self.%(src)s' % locals()
            elif src in _REG16IND: # r, (rr)
                src = src[1:-1]
                arg = 'self.read(self.%(src)s)' % locals()
            elif (dst in _REG8) and (src == '#'): # r, n
                arg = 'self.read_op_arg()'
            elif (dst in _REG8) and (src in _REGIDX): # r, (idx+d)
                reg = 'ix' if 'ix' in src else 'iy'
                adr = 'self.%s + as_signed(self.read_op_arg())' % reg
                arg = 'self.read(%(adr)s)' % locals()
            ret += [
                    'd = %(arg)s' % locals(),
                    'tmp = self.a + d',
                    'lookup = ((d & 0x88) >> 3) | ((self.a & 0x88) >> 2) | ((tmp & 0x88) >> 1)',
                    'self.a = tmp & 0xFF',
                    'self.f = (CF if tmp & 0x100 else 0) | HC_ADD_TABLE[lookup & 0x07] | OV_ADD_TABLE[lookup >> 4] | SZXY_TABLE[self.a]',
            ]
        elif (dst in _REG16) and (src in _REG16): # rr, rr
            # Z80EX_DWORD add16temp = (value1) + (value2); \
            # Z80EX_BYTE lookup = ( (  (value1) & 0x0800 ) >> 11 ) | \
            #           ( (  (value2) & 0x0800 ) >> 10 ) | \
            #           ( ( add16temp & 0x0800 ) >>  9 );  \
            # MEMPTR=value1+1;\
            # (value1) = add16temp;\
            # F = ( F & ( FLAG_V | FLAG_Z | FLAG_S ) ) |\
            #   ( add16temp & 0x10000 ? FLAG_C : 0 )|\
            #   ( ( add16temp >> 8 ) & ( FLAG_3 | FLAG_5 ) ) |\
            #   halfcarry_add_table[lookup];\
            ret = [
                'v1 = self.%(dst)s' % locals(),
                'v2 = self.%(src)s' % locals(),
                'tmp = v1 + v2',
                'lookup = ((v1 & 0x0800) >> 11) | ((v2 & 0x0800) >> 10) | ((tmp & 0x0800) >> 9)',
                'self.%(dst)s = tmp & 0xFFFF' % locals(),
                'self.f = (self.f & VZSF) | (CF if tmp & 0x10000 else 0) | ((tmp >> 8) & XYF) | HC_ADD_TABLE[lookup]',
            ]
        else:
            raise ValueError('unhandled pair %(opcode)s: %(dst)s, %(src)s' % locals())
        return ret
CMDS['ADD'] = ADD()


class RRCA(_OpBase):
    def parse(self):
        # F = ( F & ( FLAG_P | FLAG_Z | FLAG_S ) ) | ( A & FLAG_C );\
        # A = ( A >> 1) | ( A << 7 );\
        # F |= ( A & ( FLAG_3 | FLAG_5 ) );\
        return [
            'a = self.a',
            'self.f = (self.f & PZSF) | (a & CF)',
            'a = (a >> 1) | (a << 7)',
            'self.f |= (a & XYF)',
            'self.a = a & 0xFF'
        ]
CMDS['RRCA'] = RRCA()


class DJNZ(_OpBase):
    def parse(self):
        return [
            'offset = as_signed(self.read_op_arg())',
            'self.b = (self.b - 1) & 0xFF',
            'if self.b:',
            '%(IDENT)sself.pc = (self.pc + offset) & 0xFFFF' % globals(),
            '%s%s' % (IDENT, (ADD_T % (5, 5))),
        ]
CMDS['DJNZ'] = DJNZ()


class RLA(_OpBase):
    def parse(self):
        # Z80EX_BYTE bytetemp = A;\
        # A = ( A << 1 ) | ( F & FLAG_C );\
        # F = ( F & ( FLAG_P | FLAG_Z | FLAG_S ) ) |\
        #   ( A & ( FLAG_3 | FLAG_5 ) ) | ( bytetemp >> 7 );\
        return [
            'a = self.a',
            'a = (a << 1) | (self.f & CF)',
            'self.f = (self.f & PZSF) | (a & XYF) | (self.a >> 7)',
            'self.a = a & 0xFF'
        ]
CMDS['RLA'] = RLA()


class JR(_OpBase):
    def parse(self):
        opcode, flag = self.opcode, self.dst
        ret = ['offset = as_signed(self.read_op_arg())']
        if flag == '%':
            ret += ['self.pc = (self.pc + offset) & 0xFFFF']
        elif flag in _COND:
            ret += [
                'if self.f & %sF:' % flag.upper(),
                '%(IDENT)sself.pc = (self.pc + offset) & 0xFFFF' % globals(),
                '%s%s' % (IDENT, (ADD_T % (5, 5))),
            ]
        elif flag in _NOTCOND:
            ret += [
                'if not (self.f & %sF):' % flag[1].upper(),
                '%(IDENT)sself.pc = (self.pc + offset) & 0xFFFF' % globals(),
                '%s%s' % (IDENT, (ADD_T % (5, 5))),
            ]
        else:
            raise ValueError('unhandled flag %(opcode)s: %(flag)s' % locals())
        return ret
CMDS['JR'] = JR()


class RRA(_OpBase):
    def parse(self):
        # Z80EX_BYTE bytetemp = A;\
        # A = ( A >> 1 ) | ( F << 7 );\
        # F = ( F & ( FLAG_P | FLAG_Z | FLAG_S ) ) |\
        #   ( A & ( FLAG_3 | FLAG_5 ) ) | ( bytetemp & FLAG_C ) ;\
        return [
            'a = self.a',
            'a = (a >> 1) | (self.f << 7)',
            'self.f = (self.f & PZSF) | (a & XYF) | (self.a & CF)',
            'self.a = a & 0xFF'
        ]
CMDS['RRA'] = RRA()


class DAA(_OpBase):
    def parse(self):
        # const Z80EX_BYTE *tdaa = (daatab+(A+0x100*((F & 3) + ((F >> 2) & 4)))*2);\
        # F = *tdaa; A = *(tdaa + 1);\
        return [
            'idx = (self.a + 0x100 * ((self.f & 3) + ((self.f >> 2) & 4))) * 2',
            'self.f = DAA_TABLE[idx]',
            'self.a = DAA_TABLE[idx + 1]',
        ]
CMDS['DAA'] = DAA()


class CPL(_OpBase):
    def parse(self):
        # A ^= 0xff;\
        # F = ( F & ( FLAG_C | FLAG_P | FLAG_Z | FLAG_S ) ) |\
        #   ( A & ( FLAG_3 | FLAG_5 ) ) | ( FLAG_N | FLAG_H );\
        return [
            'self.a ^= 0xFF',
            'self.f = (self.f & CPZSF) | (self.a & XYF) | NHF'
        ]
CMDS['CPL'] = CPL()


class SCF(_OpBase):
    def parse(self):
        # F = ( F & ( FLAG_P | FLAG_Z | FLAG_S ) ) |\
        #   ( A & ( FLAG_3 | FLAG_5          ) ) |\
        #   FLAG_C;\
        return [
            'self.f = (self.f & PZSF) | (self.a & XYF) | CF'
        ]
CMDS['SCF'] = SCF()


class CCF(_OpBase):
    def parse(self):
        # F = ( F & ( FLAG_P | FLAG_Z | FLAG_S ) ) |\
        #   ( ( F & FLAG_C ) ? FLAG_H : FLAG_C ) | ( A & ( FLAG_3 | FLAG_5 ) );\
        return [
            'self.f = (self.f & PZSF) | (HF if self.f & CF else CF) | (self.a & XYF)'
        ]
CMDS['CCF'] = CCF()


class HALT(_OpBase):
    def parse(self):
        # cpu->halted=1;\
        # PC--;\
        return [
            'self.in_halt = True',
            'self.pc = (self.pc - 1) & 0xFFFF'
        ]
CMDS['HALT'] = HALT()


class ADC(_OpBase):
    def parse(self):
        opcode, dst, src = self.opcode, self.dst, self.src
        if dst == 'a':
            ret = []
            if src in _REG8: # r, r
                # Z80EX_WORD adctemp = A + (value) + ( F & FLAG_C ); \
                # Z80EX_BYTE lookup = ( (       A & 0x88 ) >> 3 ) | \
                #           ( ( (value) & 0x88 ) >> 2 ) | \
                #           ( ( adctemp & 0x88 ) >> 1 );  \
                # A=adctemp;\
                # F = ( adctemp & 0x100 ? FLAG_C : 0 ) |\
                #   halfcarry_add_table[lookup & 0x07] | overflow_add_table[lookup >> 4] |\
                #   sz53_table[A];\
                arg = 'self.%(src)s' % locals()
            elif src in _REG16IND: # r, (rr)
                src = src[1:-1]
                arg = 'self.read(self.%(src)s)' % locals()
            elif (dst in _REG8) and (src == '#'): # r, n
                arg = 'self.read_op_arg()'
            elif (dst in _REG8) and (src in _REGIDX): # r, (idx+d)
                reg = 'ix' if 'ix' in src else 'iy'
                adr = 'self.%s + as_signed(self.read_op_arg())' % reg
                arg = 'self.read(%(adr)s)' % locals()
            ret += [
                    'd = %(arg)s' % locals(),
                    'tmp = self.a + d + (1 if self.f & CF else 0)',
                    'lookup = ((self.a & 0x88) >> 3) | ((d & 0x88) >> 2) | ((tmp & 0x88) >> 1)',
                    'self.a = tmp & 0xFF',
                    'self.f = (CF if tmp & 0x100 else 0) | HC_ADD_TABLE[lookup & 0x07] | OV_ADD_TABLE[lookup >> 4] | SZXY_TABLE[self.a]',
            ]
        elif (dst in _REG16) and (src in _REG16): # rr, rr
            # Z80EX_DWORD add16temp= HL + (value) + ( F & FLAG_C ); \
            # Z80EX_BYTE lookup = ( (        HL & 0x8800 ) >> 11 ) | \
            #           ( (   (value) & 0x8800 ) >> 10 ) | \
            #           ( ( add16temp & 0x8800 ) >>  9 );  \
            # MEMPTR=hl+1;\
            # HL = add16temp;\
            # F = ( add16temp & 0x10000 ? FLAG_C : 0 )|\
            #   overflow_add_table[lookup >> 4] |\
            #   ( H & ( FLAG_3 | FLAG_5 | FLAG_S ) ) |\
            #   halfcarry_add_table[lookup&0x07]|\
            #   ( HL ? 0 : FLAG_Z );\
            ret = [
                'v1 = self.hl',
                'v2 = self.%(src)s' % locals(),
                'tmp = v1 + v2 + (1 if self.f & CF else 0)',
                'lookup = ((v1 & 0x8800) >> 11) | ((v2 & 0x8800) >> 10) | ((tmp & 0x8800) >> 9)',
                'self.hl = tmp & 0xFFFF',
                'self.f = (CF if tmp & 0x10000 else 0) | OV_ADD_TABLE[lookup >> 4] | (self.h & XYSF) | HC_ADD_TABLE[lookup & 0x07] | (0 if v1 else ZF)',
            ]
        else:
            raise ValueError('unhandled pair %(opcode)s: %(dst)s, %(src)s' % locals())
        return ret
CMDS['ADC'] = ADC()


class SUB(_OpBase):
    def parse(self):
        opcode, dst, src = self.opcode, self.dst, 'a'
        if dst in _REG8: # r, r
            # 8bit
            # Z80EX_WORD subtemp = A - (value); \
            # Z80EX_BYTE lookup = ( (       A & 0x88 ) >> 3 ) | \
            #           ( ( (value) & 0x88 ) >> 2 ) | \
            #           (  (subtemp & 0x88 ) >> 1 );  \
            # A=subtemp;\
            # F = ( subtemp & 0x100 ? FLAG_C : 0 ) | FLAG_N |\
            # halfcarry_sub_table[lookup & 0x07] | overflow_sub_table[lookup >> 4] |\
            # sz53_table[A];\
            arg = 'self.%(dst)s' % locals()
        elif dst in _REG16IND: # r, (rr)
            dst = dst[1:-1]
            arg = 'self.read(self.%(dst)s)' % locals()
        elif dst == '#': # r, n
            arg = 'self.read_op_arg()'
        elif dst in _REGIDX: # r, (idx+d)
            reg = 'ix' if 'ix' in dst else 'iy'
            adr = 'self.%s + as_signed(self.read_op_arg())' % reg
            arg = 'self.read(%(adr)s)' % locals()
        else:
            raise ValueError('unhandled pair %(opcode)s: %(dst)s' % locals())
        ret = [
                'd = %(arg)s' % locals(),
                'tmp = self.a - d',
                'lookup = ((self.a & 0x88) >> 3) | ((d & 0x88) >> 2) | ((tmp & 0x88) >> 1)',
                'self.a = tmp & 0xFF',
                'self.f = (CF if tmp & 0x100 else 0) | NF | HC_SUB_TABLE[lookup & 0x07] | OV_SUB_TABLE[lookup >> 4] | SZXY_TABLE[self.a]',
        ]
        return ret
CMDS['SUB'] = SUB()


class SBC(_OpBase):
    def parse(self):
        opcode, dst, src = self.opcode, self.dst, self.src
        if dst == 'a':
            ret = []
            if src in _REG8: # r, r
                # Z80EX_WORD sbctemp = A - (value) - ( F & FLAG_C ); \
                # Z80EX_BYTE lookup = ( (       A & 0x88 ) >> 3 ) | \
                #           ( ( (value) & 0x88 ) >> 2 ) | \
                #           ( ( sbctemp & 0x88 ) >> 1 );  \
                # A=sbctemp;\
                # F = ( sbctemp & 0x100 ? FLAG_C : 0 ) | FLAG_N |\
                # halfcarry_sub_table[lookup & 0x07] | overflow_sub_table[lookup >> 4] |\
                # sz53_table[A];\
                arg = 'self.%(src)s' % locals()
            elif src in _REG16IND: # r, (rr)
                src = src[1:-1]
                arg = 'self.read(self.%(src)s)' % locals()
            elif (dst in _REG8) and (src == '#'): # r, n
                arg = 'self.read_op_arg()'
            elif (dst in _REG8) and (src in _REGIDX): # r, (idx+d)
                reg = 'ix' if 'ix' in src else 'iy'
                adr = 'self.%s + as_signed(self.read_op_arg())' % reg
                arg = 'self.read(%(adr)s)' % locals()
            ret += [
                    'd = %(arg)s' % locals(),
                    'tmp = self.a - d - (1 if self.f & CF else 0)',
                    'lookup = ((self.a & 0x88) >> 3) | ((d & 0x88) >> 2) | ((tmp & 0x88) >> 1)',
                    'self.a = tmp & 0xFF',
                    'self.f = (CF if tmp & 0x100 else 0) | NF | HC_SUB_TABLE[lookup & 0x07] | OV_SUB_TABLE[lookup >> 4] | SZXY_TABLE[self.a]',
            ]
        elif (dst in _REG16) and (src in _REG16): # rr, rr
            # Z80EX_DWORD sub16temp = HL - (value) - (F & FLAG_C); \
            # Z80EX_BYTE lookup = ( (        HL & 0x8800 ) >> 11 ) | \
            #           ( (   (value) & 0x8800 ) >> 10 ) | \
            #           ( ( sub16temp & 0x8800 ) >>  9 );  \
            # MEMPTR=hl+1;\
            # HL = sub16temp;\
            # F = ( sub16temp & 0x10000 ? FLAG_C : 0 ) |\
            # FLAG_N | overflow_sub_table[lookup >> 4] |\
            # ( H & ( FLAG_3 | FLAG_5 | FLAG_S ) ) |\
            # halfcarry_sub_table[lookup&0x07] |\
            # ( HL ? 0 : FLAG_Z) ;\
            ret = [
                'v1 = self.hl',
                'v2 = self.%(src)s' % locals(),
                'tmp = v1 - v2 - (1 if self.f & CF else 0)',
                'lookup = ((v1 & 0x8800) >> 11) | ((v2 & 0x8800) >> 10) | ((tmp & 0x8800) >> 9)',
                'self.hl = tmp & 0xFFFF',
                'self.f = (CF if tmp & 0x10000 else 0) | NF | (self.h & XYSF) | OV_SUB_TABLE[lookup >> 4] | HC_SUB_TABLE[lookup & 0x07] | (0 if v1 else ZF)',
            ]
        else:
            raise ValueError('unhandled pair %(opcode)s: %(dst)s, %(src)s' % locals())
        return ret
CMDS['SBC'] = SBC()


class AND(_OpBase):
    def parse(self):
        opcode, src = self.opcode, self.dst
        # A &= (value);\
        # F = FLAG_H | sz53p_table[A];\
        if src == '#':
            src = 'self.read_op_arg()'
        elif src in _REG16IND: # r, (rr)
            src = src[1:-1]
            src = 'self.read(self.%(src)s)' % locals()
        elif (src in _REGIDX): # r, (idx+d)
            reg = 'ix' if 'ix' in src else 'iy'
            adr = 'self.%s + as_signed(self.read_op_arg())' % reg
            src = 'self.read(%(adr)s)' % locals()
        else:
            src = 'self.%(src)s' % locals()
        return [
            'self.a &= %(src)s' % locals(),
            'self.f = HF | SZXYP_TABLE[self.a]'
        ]
CMDS['AND'] = AND()

class XOR(_OpBase):
    def parse(self):
        opcode, src = self.opcode, self.dst
        # A ^= (value);\
        # F = sz53p_table[A];\
        if src == '#':
            src = 'self.read_op_arg()'
        elif src in _REG16IND: # r, (rr)
            src = src[1:-1]
            src = 'self.read(self.%(src)s)' % locals()
        elif (src in _REGIDX): # r, (idx+d)
            reg = 'ix' if 'ix' in src else 'iy'
            adr = 'self.%s + as_signed(self.read_op_arg())' % reg
            src = 'self.read(%(adr)s)' % locals()
        else:
            src = 'self.%(src)s' % locals()
        return [
            'self.a ^= %(src)s' % locals(),
            'self.f = SZXYP_TABLE[self.a]'
        ]
CMDS['XOR'] = XOR()


class OR(_OpBase):
    def parse(self):
        opcode, src = self.opcode, self.dst
        # A ^= (value);\
        # F = sz53p_table[A];\
        if src == '#':
            src = 'self.read_op_arg()'
        elif src in _REG16IND: # r, (rr)
            src = src[1:-1]
            src = 'self.read(self.%(src)s)' % locals()
        elif (src in _REGIDX): # r, (idx+d)
            reg = 'ix' if 'ix' in src else 'iy'
            adr = 'self.%s + as_signed(self.read_op_arg())' % reg
            src = 'self.read(%(adr)s)' % locals()
        else:
            src = 'self.%(src)s' % locals()
        return [
            'self.a |= %(src)s' % locals(),
            'self.f = SZXYP_TABLE[self.a]'
        ]
CMDS['OR'] = OR()
# ===============
# = for testing =
# ===============
if __name__ == '__main__':
    import genop
    genop.main()