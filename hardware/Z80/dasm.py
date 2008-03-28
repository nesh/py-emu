# =================
# = opcode tables =
# =================
OP_R = ('B', 'C', 'D', 'E', 'H', 'L', '(HL)', 'A')
OP_R_A = ('B', 'C', 'D', 'E', 'H', 'L', 'HL_ind', 'A')
OP_RP = ('BC', 'DE', 'HL', 'SP')
OP_RP2 = ('BC', 'DE', 'HL', 'AF')
OP_CC = ('NZ', 'Z', 'NC', 'C', 'PO', 'PE', 'P', 'M')
OP_ALU = ('ADD A', 'ADC A', 'SUB', 'SBC A', 'AND', 'XOR', 'OR', 'CP')
OP_ROT = ('RLC', 'RRC', 'RL', 'RR', 'SLA', 'SRA', 'SLL', 'SRL')
OP_IM = ('0' '0/1', '1', '2', '0', '0/1', '1', '2')
OP_BLI = (
    ('LDI', 'CPI', 'INI', 'OUTI'),    # 4
    ('LDD', 'CPD', 'IND', 'OUTD'),    # 5
    ('LDIR', 'CPIR', 'INIR', 'OTIR'), # 6
    ('LDDR', 'CPDR', 'INDR', 'OTDR')  # 7
)
OP_ACC_F = ('RLCA', 'RRCA', 'RLA', 'RRA', 'DAA', 'CPL', 'SCF', 'CCF')
OP_POP_VAR = ('RET', 'EXX', 'JP HL', 'LD SP, HL')
OP_ASS = {
    4: 'EX (SP), HL',
    5: 'EX DE, HL',
    6: 'DI',
    7: 'EI'
}
OP_ASS2 = ('LD I, A', 'LD R, A', 'LD A, I', 'LD A, R', 'RRD', 'RLD', 'NOP', 'NOP')

IDX = ('IX', 'IY') # index reg's
IX, IY = range(1, 3)

# ====================
# = opcode breakdown =
# ====================
class OpCode(object):
    X_MASK = 0xC0
    Y_MASK = 0x38
    Z_MASK = 0x07
    P_MASK = 0x30
    Q_MASK = 0x08
    
    def __init__(self, val):
        self.val = val
    
    def _x(self):
        return (self.val & OpCode.X_MASK) >> 6
    x = property(fget=_x)

    def _y(self):
        return (self.val & OpCode.Y_MASK) >> 3
    y = property(fget=_y)

    def _z(self):
        return (self.val & OpCode.Z_MASK)
    z = property(fget=_z)

    def _p(self):
        return (self.val & OpCode.P_MASK) >> 4
    p = property(fget=_p)

    def _q(self):
        return (self.val & OpCode.Q_MASK) >> 3
    q = property(fget=_q)


def break_opcode(val):
    op = OpCode(val)
    return op.x, op.y, op.z, op.p, op.q

def as_signed(val):
    """ convert value to the signed one """
    if val & 0x80:
        return -(val & (0x80 - 1))
    else:
        return val
        

class DasmMixin(object):
    def dasm_xd(self, op):
        self.last_prefix = IX if op == 0xDD else IY

        rdop = self.read_op # shortcut
        rdop16 = self.read_op16 # shortcut
        byte = self.read(self.PC) # peek next byte
        # shortcuts
        x, y, z, p, q = break_opcode(byte)
        
        if byte in (0xDD, 0xFD, 0xED):
            return 'NONI'
        
        # get opcode
        byte = rdop()
        
        if byte == 0xCB:
            return self.dasm_xxcb()
        raise NotImplementedError('xD')
        
    def dasm_dd(self):
        return self.dasm_xd(0xDD)

    def dasm_fd(self):
        return self.dasm_xd(0xFD)

    def dasm_xxcb(self):
        # DD/FD CB
        rdop = self.read_op # shortcut
        rdop16 = self.read_op16 # shortcut
        d = as_signed(rdop())
        byte = rdop()
        # shortcuts
        x, y, z, p, q = break_opcode(byte)
        
        idx = '(%s%+d)'% (IDX[self.last_prefix], d)
        
        if x == 0:
            if z != 6:
                return 'LD %s, %s %s' % (OP_R[z], OP_ROT[y], idx)
            else:
                return '%s %s' % (OP_ROT[y], idx)
        elif x == 1:
            return 'BIT %d, %s' % (y, OP_R[z])
        elif x == 2:
            if z != 6:
                return 'LD %s, RES %d, %s' % (OP_R[z], y, idx)
            else:
                return 'RES %d, %s' % (y, idx)
        else:
            if z != 6:
                return 'LD %s, SET %d, %s' % (OP_R[z], y, idx)
            else:
                return 'SET %d, %s' % (y, idx)

    def dasm_cb(self):
        rdop = self.read_op # shortcut
        rdop16 = self.read_op16 # shortcut
        byte = rdop()
        # shortcuts
        x, y, z, p, q = break_opcode(byte)
        
        if x == 0:
            return '%s %s' % (OP_ROT[y], OP_R[z])
        elif x == 1:
            return 'BIT %s, %s' % (y, OP_R[z])
        elif x == 2:
            return 'RES %s, %s' % (y, OP_R[z])
        else:
            return 'SET %s, %s' % (y, OP_R[z])

    def dasm_ed(self):
        rdop = self.read_op # shortcut
        rdop16 = self.read_op16 # shortcut
        byte = rdop()
        # shortcuts
        x, y, z, p, q = break_opcode(byte)
        
        if x == 0 or x == 3:
            return 'NONI NOP'
        elif x == 1:
            if z == 0:
                if y != 6:
                    return 'IN %s, (C)' % OP_R[y]
                else:
                    return 'IN (C)'
            elif z == 1:
                if y != 6:
                    return 'OUT (C), %s' % OP_R[y]
                else:
                    return 'OUT (C), 0'
            elif z == 2:
                if q:
                    return 'ADC HL, %s' % OP_RP[p]
                else:
                    return 'SBC HL, %s' % OP_RP[p]
            elif z == 3:
                nn = rdop16()
                if q:
                    return 'LD %s, (%04Xh)' % (OP_RP[p], nn)
                else:
                    return 'LD (%04Xh), %s' % (nn, OP_RP[p])
            elif z == 4:
                return 'NEG'
            elif z == 5:
                if y == 1:
                    return 'RETI'
                else:
                    return 'RETN'
            elif z == 6:
                return 'IM %s' % OP_IM[y]
            else:
                return OP_ASS2[y]
        elif x == 2:
            if z <= 3 and y >= 4:
                return OP_BLI[y][z]
            else:
                return 'NONI NOP'

    def dasm(self, addr):
        old_pc = self.PC
        self.PC = addr
        
        ret = []

        rdop = self.read_op # shortcut
        rdop16 = self.read_op16 # shortcut
        byte = rdop()
        # shortcuts
        rd = self.read
        wr = self.write
        x, y, z, p, q = break_opcode(byte)
    
        if x == 0:
            if z == 0:
                if y == 0:
                    ret.append('NOP')
                elif y == 1:
                    ret.append('EX AF, AF\'')
                elif y == 2:
                    ret.append('DJNZ')
                    ret.append('%d' % as_signed(rdop()))
                elif y == 3:
                    ret.append('JR')
                    ret.append('%d' % as_signed(rdop()))
                else:
                    ret.append('JR %s' % OP_CC[y - 4])
                    ret.append('%d' % as_signed(rdop()))
            elif z == 1:
                if q:
                    ret.append('ADD HL, %s' % OP_RP[p])
                else:
                    nn = rdop16()
                    ret.append('LD %s, %04Xh' % (OP_RP[p], nn))
            elif z == 2:
                if q:
                    if p == 0:
                        ret.append('LD A, (BC)')
                    elif p == 1:
                        ret.append('LD A, (DE)')
                    elif p == 2:
                        nn = rdop16()
                        ret.append('LD HL, (%04Xh)' % nn)
                    else:
                        nn = rdop16()
                        ret.append('LD A, (%04Xh)' % nn)
                else:
                    if p == 0:
                        ret.append('LD (BC), A')
                    elif p == 1:
                        ret.append('LD (DE), A')
                    elif p == 2:
                        nn = rdop16()
                        ret.append('LD (%04Xh), HL' % nn)
                    else:
                        nn = rdop16()
                        ret.append('LD (%04Xh), A' % nn)
            elif z == 3:
                if q:
                    ret.append('DEC %s' % OP_RP[p])
                else:
                    ret.append('INC %s' % OP_RP[p])
            elif z == 4:
                ret.append('INC %s' % OP_R[y])
            elif z == 5:
                ret.append('DEC %s' % OP_R[y])
            elif z == 6:
                n = rdop()
                ret.append('LD %s, %02Xh' % (OP_R[y], n))
            else:
                ret.append(OP_ACC_F[y])
        elif x == 1:
            if (z == 6) and (y == 6):
                ret.append('HALT') # special case, replaces LD (HL), (HL)
            else:
                ret.append('LD %s, %s' % (OP_R[y], OP_R[z]))
        elif x == 2:
            ret.append('%s %s' % (OP_ALU[y], OP_R[z]))
        elif x == 3:
            if z == 0:
                ret.append('RET %s' % OP_CC[y])
            elif z == 1:
                if q:
                    ret.append(OP_POP_VAR[p])
                else:
                    ret.append('POP %s' % OP_RP2[p])
            elif z == 2:
                nn = rdop16()
                ret.append('JP %s, %04Xh' % (OP_CC[y], nn))
            elif z == 3:
                if y == 0:
                    nn = rdop16()
                    ret.append('JP %04Xh' % nn)
                elif y == 1:
                    ret.append(self.dasm_cb()) # CB prefixed
                elif y == 2:
                    n = rdop()
                    ret.append('OUT (%02Xh), A' % n)
                elif y == 3:
                    n = rdop()
                    ret.append('IN A, (%02Xh)' % n)
                else:
                    ret.append(OP_ASS[y])
            elif z == 4:
                nn = rdop16()
                ret.append('CALL %s, %04Xh' % (OP_CC[y], nn))
            elif z == 5:
                if q:
                    if p == 0:
                        nn = rdop16()
                        ret.append('CALL %04Xh' % nn)
                    elif p == 1:
                        ret.append(self.dasm_dd()) # DD prefixed
                    elif p == 2:
                        ret.append(self.dasm_ed()) # ED prefixed
                    else:
                        ret.append(self.dasm_fd()) # FD prefixed
                else:
                    ret.append('PUSH %s' % OP_RP2[p])
            elif z == 6:
                n = rdop()
                ret.append('%s %02Xh' % (OP_ALU[y], n))
            else:
                ret.append('RST %02Xh' % (y * 8))

        off = self.PC - addr # used bytes
        self.PC = old_pc # restore PC

        if not ret:
            for o in range(off):
                ret.append('%02X' % rd(addr + o))
            return ''.join(ret), off
        else:
            return ' '.join(ret), off