import warnings

IDENT = ' '*4
ADD_T = 'self.icount -= %d; self.itotal += %d'
#READ_OP = 'self.read(self.pc); self.pc = (self.pc + 1) & 0xFFFF'
READ_OP = 'self.read_op_arg()'
CMDS = {}
# XXX unfold read_*?

_REG8 = ('a', 'f', 'b', 'c', 'd', 'e', 'h', 'l', 'r', 'i', 'ixh', 'ixl', 'iyh', 'iyl')
_REG16 = ('af', 'bc', 'de', 'hl', 'ix', 'iy', 'pc', 'sp')
_REG16IND = ('(bc)', '(de)', '(hl)', '(sp)')
_REGIDX = ('(ix+$)', '(iy+$)')

def _parse_bits(bits):
    opcode = bits[0]
    args = bits[1].split(',')
    
    dst = args[0].lower()
    src = args[1].lower()
    return opcode, dst, src

def nop(type_, code, op, tstates, bits):
    return ['pass']
CMDS['NOP'] = nop

def ld(type_, code, op, tstates, bits):
    opcode, dst, src = _parse_bits(bits)
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
        ret = 'self.%(dst)s = self.read(self.%(dst)s)' % locals()
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
        warnings.warn('skipping %s' % ' '.join(bits))
        return []
    else:
        raise ValueError('unhandled pair %(opcode)s: %(dst)s, %(src)s' % locals())
    return [ret]
CMDS['LD'] = ld

# ===============
# = for testing =
# ===============
if __name__ == '__main__':
    import genop
    genop.main()