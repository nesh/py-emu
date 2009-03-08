def state(what):
    return 'state[\'%s\']' % what

def state_ind(what):
    return state(what[1:-1])

STATE_REG8 = ('a', 'f', 'b', 'c', 'd', 'e', 'r')

# 16b regs stored as 2 * 8b
STATE_REG8_16 = ('af', 'bc', 'de')
STATE_REG8_16_HI = ('a', 'b', 'd')
STATE_REG8_16_LO = ('f', 'c', 'e')

# 8b regs stored as pairs
STATE_REG16 = ('hl', 'ix', 'iy', 'pc', 'sp')
#STATE_REG16_8_HI = ('h', 'ixh', 'iyh')
#STATE_REG16_8_LO = ('l', 'ixl', 'iyl')
STATE_REG16_8 = {
    'h': 'hl',
    'l': 'hl',
    'ixh': 'ix',
    'ixl': 'ix',
    'iyh': 'iy',
    'iyl': 'iy',
}


def read_reg8(what):
    assert what in STATE_REG8 or what in STATE_REG16_8, '%s' % where
    if what in STATE_REG8:
        return '(%s)' % state(what)
    r16 = STATE_REG16_8[what]
    r16r = state(r16)
    if what == r16[0]: # hi
        return '((%(r16r)s & 0xFF00) / 256)' % locals()
    else: # lo
        return '(%(r16r)s & 0xFF)' % locals()

def write_flags(what):
    f = state['f']
    return ['%(f) = (%(what)s & 0xFF)' % locals]

def read_flags():
    return state['f']

def write_reg8(where, what, force=True):
    assert where in STATE_REG8 or where in STATE_REG16_8, '%s' % where

    if force:
        what = '((%s) & 0xFF)' % what

    if where in STATE_REG8:
        where = state(where)
        return ['%(where)s = %(what)s' % locals()]

    r16 = STATE_REG16_8[where]
    r16r = state(r16)
    if where == r16[0]: # hi
        return [
            '# %(where)s write' % locals(),
            '%(r16r)s = (%(r16r)s & 0xFF) + ((%(what)s) * 256)' % locals(),
        ]
    else:
        return [
            '# %(where)s write' % locals(),
            '%(r16r)s = (%(what)s) + (%(r16r)s & 0xFF00)' % locals(),
        ]
    assert False, '%s' % where

def read_reg16(what):
    assert what in STATE_REG16 or what in STATE_REG8_16, '%s' % what
    if what in STATE_REG16:
        return state(what)
    lo = state(what[1])
    hi = state(what[0])
    return '((%(hi)s * 256) + %(lo)s)' % locals()

def write_reg16(where, what, force=True):
    assert where in STATE_REG16 or where in STATE_REG8_16, '%s' % where
    if force:
        what = '((%s) & 0xFFFF)' % what

    if where in STATE_REG16:
        where = state(where)
        return ['%(where)s = %(what)s' % locals()]
    # reg 8
    lo = state(where[1])
    hi = state(where[0])
    return [
        '# %(where)s write' % locals(),
        '%(lo)s = (%(what)s) & 0xFF' % locals(),
        '%(hi)s = (%(what)s) / 256' % locals()
    ]

def read(what, mem=state('mem')):
    return '%(mem)s.read(%(what)s)' % locals()

def read16(what, mem=state('mem')):
    return '(%(mem)s.read(%(what)s) + (%(mem)s.read((%(what)s) + 1) * 256))' % locals()

def write(where, what, mem=state('mem')):
    return ['%(mem)s.write(%(where)s, %(what)s)' % locals()]

def write16(where, what, mem=state('mem')):
    return [
        '%(mem)s.write(%(where)s, %(what)s)' % locals(), # no need for & 0xFF, memory will do this
        '%(mem)s.write((%(where)s) + 1, %(what)s / 256)' % locals()
    ]

def read_op(mem=state('mem')):
    what = read_reg16('pc')
    return ['tmp8 = %(mem)s.read_op(%(what)s)' % locals()] \
           + write_reg16('pc', '%(what)s + 1' % locals())

def read_op16(mem=state('mem')):
    what = read_reg16('pc')
    return ['tmp16 = %(mem)s.read_op(%(what)s) + (%(mem)s.read_op(%(what)s + 1) * 256)' % locals()] \
            + write_reg16('pc', '%(what)s + 2' % locals())

def mem_shortcut():
    return 'mem = %s # shortcut' % state('mem')
