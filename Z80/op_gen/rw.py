def state(what):
    return 'z80.%s' % what

def state_ind(what):
    return state(what[1:-1])

# keep API separated
read_reg8 = read_flags = read_reg16 = state

def write_flags(what):
    f = state['f']
    return ['%(f) = (%(what)s & 0xFF)' % locals]

def write_reg8(where, what, force=True):
    if force:
        what = '((%s) & 0xFF)' % what
    where = state(where)
    return ['%(where)s = %(what)s' % locals()]

def write_reg16(where, what, force=True):
    if force:
        what = '((%s) & 0xFFFF)' % what
    where = state(where)
    return ['%(where)s = %(what)s' % locals()]

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
