""" misc functions """
IDENT = ' ' * 4
HEAD = r'''def %s(z80):'''

def state(what):
    return 'z80.%s' % what

ICOUNT = r"""%s -= %%d""" % state('icount') # TODO: what's faster a['foo'] or a.foo?

def gen_name(code, table):
    if table:
        return 'opcode_%s%02x' % (table, code)
    else:
        return 'opcode_%02x' % code

def gen_doc(code, asm, prefix=None):
    if not prefix:
        return '%s"""0x%02X: %s"""' % (IDENT, code, asm)
    else:
        return '%s"""0x%s%02X: %s"""' % (IDENT, prefix.upper(), code, asm)

def gen_jp(table=None):
    if table:
        return 'JP_%s' % table.upper()
    else:
        return 'JP_BASE'

def std_head(code, op, table):
    return [
        HEAD % gen_name(code, table),
        gen_doc(code, op['asm'], table),
        '%s%s' % ((IDENT), (ICOUNT % op['t'])),
    ]

def make_code(code, data, table):
    return ('\n'.join(data), '%s[0x%02X] = %s' % (gen_jp(table), code, gen_name(code, table)))

# keep API separated
read_reg8 = read_reg16 = state

def read_flags():
    return state('f')

def to_signed(what):
    i = IDENT
    return [
        'if %(what)s & 0x80: # convert to signed' % locals(),
            '%(i)s%(what)s = -(256 - %(what)s)' % locals(),
    ]

def read_idx(src, mem=state('mem')):
    reg = 'ix' if 'ix' in src else 'iy'
    do = []
    do += read_op(mem)
    do += to_signed('tmp8')
    ret = read(read_reg16(reg) + ' + tmp8', mem)
    return do, ret

def write_idx(dst, src, mem=state('mem')):
    reg = 'ix' if 'ix' in dst else 'iy'
    do = []
    do += read_op(mem)
    do += to_signed('tmp8')
    do += write(read_reg16(reg) + ' + tmp8', src, mem)
    return do

def write_flags(what, force=False):
    f = state('f')
    if force:
        return ['%(f)s = (%(what)s) & 0xFF' % locals()]
    else:
        return ['%(f)s = %(what)s' % locals()]

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
