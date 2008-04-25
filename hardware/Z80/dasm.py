from dasmtab import *
from tools import as_signed

__all__ = ('dasm',)

def dasm(adr, read):
    """ This function will disassemble a single command and
        return the number of bytes disassembled.
    """
    
    pos = adr
    b = read(pos)
    pos += 1
    j = False

    if b == 0xCB:
        b = read(pos)
        pos += 1
        t = MNEMONICS_CB[b]
    elif b == 0xED:
        b = read(pos)
        pos += 1
        t = MNEMONICS_ED[b]
    elif b == 0xDD:
        c = 'X'
        b = read(pos)
        pos += 1
        if b != 0xCB:
            t = MNEMONICS_XX[b]
        else:
            offset = read(pos)
            pos += 1
            j = True
            b = read(pos)
            pos += 1
            t = MNEMONICS_XCB[b]
    elif b == 0xFD:
        c = 'Y'
        b = read(pos)
        pos += 1
        if b != 0xCB:
            t = MNEMONICS_XX[b]
        else:
            offset = read(pos)
            pos += 1
            j = True
            b = read(pos)
            pos += 1
            t = MNEMONICS_XCB[b]
    else:
        t = MNEMONICS[b]
    
    if '^' in t:
        op = as_signed(read(pos))
        pos += 1
        op = '%+d' % op
        t = t.replace('^', op)
    if '%' in t:
        t = t.replace('%', c)
    if '*' in t:
        op = read(pos)
        pos += 1
        op = '%02Xh' % op
        t = t.replace('*', op)
    else:
        if '@' in t:
            if not j:
                offset = read(pos)
                pos += 1
            j = '%+d' % as_signed(offset)
            t = t.replace('@', j)
        else:
            if '#' in t:
                lo = read(pos)
                pos += 1
                hi = read(pos)
                pos += 1
                t = t.replace('#', '%04Xh' % (lo + 256 * hi))
    return t, pos - adr