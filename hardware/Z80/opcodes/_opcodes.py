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
            'self.f = (self.f & (PF | ZF | SF)) | (a & (CF | XF | YF))',
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

# ===============
# = for testing =
# ===============
if __name__ == '__main__':
    import genop
    genop.main()