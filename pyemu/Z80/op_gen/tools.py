from string import Template

""" misc functions """
IDENT = ' ' * 4
HEAD = r'''def %s(z80):'''
REG8 = ('a', 'f', 'b', 'c', 'd', 'e', 'h', 'l', 'ixh', 'ixl', 'iyh', 'iyl')
REG8_SPEC = ('r', 'i',)
REG16 = ('af', 'bc', 'de', 'hl', 'ix', 'iy', 'pc', 'sp')
REGANY = REG8 + REG16
REG16ALT = ('af1', 'bc1', 'de1')
REG16IND = ('(bc)', '(de)', '(hl)', '(sp)')
REGIDX = ('(ix+$)', '(iy+$)')
COND = ('c', 'z', 'm', 'pe',)
NOTCOND = ('nc', 'nz', 'p', 'po',)
BIT_NUMBERS = [str(x) for x in range(0,9)]

def format(template, args):
    return Template(template).substitute(args)

def state(what):
    return 'z80.%s' % what

ICOUNT = r"""%s -= %%d""" % state('icount')
ITOTAL = r"""%s += %%d""" % state('itotal')

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
    ret = [
        HEAD % gen_name(code, table),
        gen_doc(code, op['asm'], table),
    ]
    if not isinstance(op['t'], (list, tuple)):
        ret += [
            '%s%s' % ((IDENT), (ICOUNT % op['t'])),
            '%s%s' % ((IDENT), (ITOTAL % op['t'])),
        ]
    return ret

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

def io_write(port, what, io=state('io')):
    return ['%(io)s.write(%(port)s, %(what)s)' % locals()]

def io_read(port, io=state('io')):
    return '%(io)s.read(%(port)s)' % locals()

def pop_reg(reg, mem=state('mem')):
    if reg in ('ix', 'iy', 'pc'):
        h = reg + 'h'
        l = reg + 'l'
    else:
        h = reg[0]
        l = reg[1]
    sp = read_reg16('sp')
    do = []
    do += write_reg8(l, read(sp, mem), force=False)
    do += write_reg16('sp', '%(sp)s + 1' % locals(), force=False)
    do += write_reg8(h, read(sp, mem), force=False)
    do += write_reg16('sp', '%(sp)s + 1' % locals())
    return do


def push_reg(reg, mem=state('mem')):
    if reg in ('ix', 'iy', 'pc'):
        h = reg + 'h'
        l = reg + 'l'
    else:
        h = reg[0]
        l = reg[1]
    h = read_reg8(h)
    l = read_reg8(l)
    sp = read_reg16('sp')
    do = []
    do += write_reg16('sp', '%(sp)s - 1' % locals(), force=False)
    do += write(sp, h, mem)
    do += write_reg16('sp', '%(sp)s - 1' % locals())
    do += write(sp, l, mem)
    return do

def read_op(mem=state('mem'), store_to='tmp8'):
    what = read_reg16('pc')
    return ['%(store_to)s = %(mem)s.read_op(%(what)s)' % locals()] \
           + write_reg16('pc', '%(what)s + 1' % locals())

def read_op16(mem=state('mem'), store_to='tmp16'):
    # what = read_reg16('pc')
    args = {
        'src': read_reg16('pc'),
        'dst': store_to,
        'mem': mem,
    }
    return [format('$dst = $mem.read_op($src) + ($mem.read_op($src + 1) * 256)', args)] \
           + write_reg16('pc', format('$src + 2', args))
    # 'tmp16 = %(mem)s.read_op(%(what)s) + (%(mem)s.read_op(%(what)s + 1) * 256)' % locals()] \
    #         + write_reg16('pc', '%(what)s + 2' % locals())

def mem_shortcut():
    return 'mem = %s # shortcut' % state('mem')


class GenOp(object):
    """ base class for code generators """
    def __init__(self, dict, name=None):
        # register class
        if name is None:
            name = self.__class__.__name__.upper()
        dict[name] = self
        
        self.args = {}
        self.do = []
        # setup base args
        for a in (REG8 + REG8_SPEC):
            self.add_arg(a.upper(), read_reg8(a))
        for a in (REG16 + REG16ALT):
            self.add_arg(a.upper(), read_reg16(a))
        self.add_arg('IFF1', state('iff1'))
        self.add_arg('IFF2', state('iff2'))
        self.add_arg('IM', state('im'))
        self.add_arg('MEMPTR', state('memptr'))
        self.add_arg('MEMPTRH', state('memptr_h'))
        self.add_arg('MEMPTRL', state('memptr_l'))
    
    def __call__(self, code, op, table=None):
        self.do = []
        
        ret = std_head(code, op, table)
        self.__param(op) # prepare operands
        
        dst, src = self.dst, self.src # shortcut
        self.setup(dst, src) # misc stuff
        self.gen(dst, src, op)
        ret += [IDENT + x for x in self.do] # add commands
        return make_code(code, ret, table)

    def arg1(self, src):
        if src in REG8:
            # r
            self.args['r'] = read_reg8(src)
        elif src in REG16:
            # rr
            self.args['rr'] = read_reg16(src)
        elif self.src in REG16IND:
            # rr
            self.args['r'] = read(read_reg16(src[1:-1]))
        elif src in REGIDX:
            # (ix+o)
            self.do.append(mem_shortcut())
            todo, r = read_idx(self.src, mem='mem')
            self.do += todo
            self.args['r'] = r
        elif src == '#':
            # n
            self.do += read_op()
            self.args['r'] = 'tmp8'
        # elif src == '@':
        #     # n
        #     self.do += read_op16()
        #     self.args['rr'] = 'tmp16'
        else:
            raise SyntaxError('%s: invalid operand %s' % (self.__class__.__name__, src))

    def arg2_16(self, dst, src):
        if (dst in REG16) and (src in REG16):
            # rr,rr1
            self.args['rr'] = read_reg16(dst)
            self.args['rr1'] = read_reg16(src)
        else:
            raise SyntaxError('%s: invalid pair %s, %s' % (self.__class__.__name__, dst, src))

    def arg2(self, dst, src):
        if (dst in (REG8 + REG8_SPEC)) and (src in REG8):
            # r,r1
            self.args['r'] = read_reg8(dst)
            self.args['r1'] = read_reg8(src)
        elif (dst in REG8) and (src in (REG8 + REG8_SPEC)):
            # r,r1
            self.args['r'] = read_reg8(dst)
            self.args['r1'] = read_reg8(src)
        elif (dst in REG8) and (src in REG16IND):
            # r, (rr)
            self.args['r'] = read_reg8(dst)
            self.args['r1'] = read(read_reg16(src[1:-1]))
        elif (dst in REG8) and (src in REGIDX):
            # r,(ix+o)
            self.args['r'] = read_reg8(dst)
            self.add_line(mem_shortcut())
            todo, r = read_idx(src, mem='mem')
            self.add_lines(todo)
            self.add_line('tmp8 = %(r)s' % locals())
            self.args['r1'] = 'tmp8'
        elif (dst in REG8) and (src == '#'):
            # r,n
            self.args['r'] = read_reg8(dst)
            self.add_lines(read_op())
            self.args['r1'] = 'tmp8'
        else:
            raise SyntaxError('%s: invalid pair %s, %s' % (self.__class__.__name__, dst, src))
    
    
    def arg_bit(self, dst, src):
        if (dst in BIT_NUMBERS) and (src in REG8):
            # [0-8],n
            self.args['r'] = dst
            self.args['r1'] = read_reg8(src)
        elif (dst in BIT_NUMBERS) and (src in REG16IND):
            # [0-8], (rr)
            self.args['r'] = dst
            self.args['r1'] = read(read_reg16(src[1:-1]))
        else:
            raise SyntaxError('%s: invalid pair %s, %s' % (self.__class__.__name__, dst, src))
        
    def add_t(self, t, ident=1):
        self.add_lines([
            ICOUNT % t,
            ITOTAL % t,
        ], ident)

    # def __call__(self, code, op, table=None):
    #     self.do = []
    #     
    #     ret = std_head(code, op, table)
    #     self.__param(op) # prepare operands
    #     
    #     dst, src = self.dst, self.src # shortcut
    #     self.setup(dst, src) # misc stuff
    #     skip_gen = False
    #     
    #     # the big bad switch^2 ;)
    #     if (dst is None) and (src is None):
    #         pass # no operands
    #     elif dst is None:
    #         # 1 operand
    #         if src in REG8:
    #             # r
    #             self.args['r'] = read_reg8(src)
    #         elif src in REG16:
    #             # rr
    #             self.args['rr'] = read_reg16(src)
    #         elif self.src in REG16IND:
    #             # rr
    #             self.args['r'] = read(read_reg16(src[1:-1]))
    #         elif src in REGIDX:
    #             # (ix+o)
    #             self.do.append(mem_shortcut())
    #             todo, r = read_idx(self.src, mem='mem')
    #             self.do += todo
    #             self.args['r'] = r
    #         elif src == '#':
    #             # n
    #             self.do += read_op()
    #             self.args['r'] = 'tmp8'
    #         else:
    #             raise SyntaxError('%s: invalid operand %s' % (self.__class__.__name__, src))
    #     else:
    #         # 2 operands
    #         if (dst in (REG8 + REG8_SPEC)) and (src in REG8):
    #             # r,r1
    #             self.args['r'] = read_reg8(dst)
    #             self.args['r1'] = read_reg8(src)
    #         elif (dst in REG8) and (src in (REG8 + REG8_SPEC)):
    #             # r,r1
    #             self.args['r'] = read_reg8(dst)
    #             self.args['r1'] = read_reg8(src)
    #         elif (dst in REG8) and (src in REG16IND):
    #             # r, (rr)
    #             self.args['r'] = read_reg8(dst)
    #             # self.add_line('tmp8 = %s' % read(read_reg16(src[1:-1])))
    #             self.args['r1'] = read(read_reg16(src[1:-1]))
    #         elif (dst in REG8) and (src in REGIDX):
    #             # r,(ix+o)
    #             self.args['r'] = read_reg8(dst)
    #             self.add_line(mem_shortcut())
    #             todo, r = read_idx(src, mem='mem')
    #             self.add_lines(todo)
    #             self.add_line('tmp8 = %(r)s' % locals())
    #             self.args['r1'] = 'tmp8'
    #         elif (dst in REG8) and (src == '#'):
    #             # r,n
    #             self.args['r'] = read_reg8(dst)
    #             self.add_lines(read_op(store_to=self.args['r']))
    #             self.args['r1'] = 'tmp8'
    #             # self.gen(dst, src)
    #             skip_gen = True
    #         elif (dst in BIT_NUMBERS) and (src in REG8):
    #             # [0-8],n
    #             self.args['r'] = dst
    #             self.args['r1'] = read_reg8(src)
    #         elif (dst in BIT_NUMBERS) and (src in REG16IND):
    #             # [0-8], (rr)
    #             self.args['r'] = dst
    #             # self.add_line('tmp8 = %s' % read(read_reg16(src[1:-1])))
    #             self.args['r1'] = read(read_reg16(src[1:-1]))
    #         elif (dst in REG16) and (src in REG16):
    #             # rr,rr1
    #             self.args['rr'] = read_reg16(dst)
    #             self.args['rr1'] = read_reg16(src)
    #         elif (dst in REG16) and (src == '@'):
    #             # rr,nnnn
    #             self.add_line(mem_shortcut())
    #             self.add_lines(read_op16(mem='mem', store_to=read_reg16(dst)))
    #             self.args['rr1'] = 'tmp16'
    #             # self.gen(dst, src)
    #             skip_gen = True
    #         elif (dst in REG16) and (src == '(@)'):
    #             # rr, (nnnn)
    #             self.add_line(mem_shortcut())
    #             self.add_lines(read_op16('mem'))
    #             self.args['rr'] = read_reg16(dst)
    #             self.args['rr1'] = read16('tmp16')
    #         elif (dst in REG16IND) and (src in REG8):
    #             # (rr), r
    #             self.args['r1'] = read_reg8(src)
    #             self.gen(dst, src)
    #             skip_gen = True
    #             self.add_lines(write(self.args['rr'], self.args['r1']))
    #         elif (dst in REG16IND) and (src == '#'):
    #             # (rr), nn
    #             self.add_line(mem_shortcut())
    #             self.add_lines(read_op('mem'))
    #             self.args['r1'] = 'tmp8'
    #             self.gen(dst, src)
    #             skip_gen = True
    #             self.add_lines(write(self.args['rr'], 'tmp8', 'mem'))
    #         elif (dst == '(@)') and (src in REG16):
    #             # (nnnn), rr
    #             self.add_line(mem_shortcut())
    #             self.add_lines(read_op16('mem'))
    #             self.args['rr1'] = read_reg16(src)
    #             self.args['rr'] = 'tmp16'
    #             # self.gen(dst, src)
    #             skip_gen = True
    #             self.add_lines(write16(self.args['rr'], self.args['rr1'], 'mem'))
    #         elif (dst == '(@)') and (src in REG8):
    #             # (nnnn), r
    #             self.add_line(mem_shortcut())
    #             self.add_lines(read_op16('mem'))
    #             self.add_lines(write('tmp16', read_reg8(src), 'mem'))
    #             skip_gen = True
    #         elif (dst in REG8) and (src == '(@)'):
    #             # r, (nnnn)
    #             self.add_lines(read_op16())
    #             self.args['r'] = read_reg8(dst)
    #             self.args['r1'] = read('tmp16')
    #         elif (dst in REGIDX) and (src == '#'):
    #             # (ix+o), nn
    #             self.args['r1'] = 'tmp8'
    #             reg = 'ix' if 'ix' in dst else 'iy'
    #             self.add_line(mem_shortcut())
    #             self.add_lines(read_op('mem') + to_signed('tmp8'))
    #             self.add_line('tmp16 = ' + read_reg16(reg) + ' + tmp8')
    #             self.add_lines(read_op('mem'))
    #             skip_gen = True
    #             self.add_lines(write('tmp16', 'tmp8', 'mem'))
    #         elif (dst in REG8) and (src in REGIDX):
    #             # r, (ix+o)
    #             self.add_line(mem_shortcut())
    #             todo, r = read_idx(src, mem='mem')
    #             self.add_lines(todo)
    #             # self.gen(dst, src)
    #             skip_gen = True
    #             self.add_lines(write_reg8(dst, r, False))
    #         elif (dst in REGIDX) and (src in REG8):
    #             # (ix+o), r
    #             self.add_line(mem_shortcut())
    #             self.add_lines(write_idx(dst, read_reg8(src), 'mem'))
    #             skip_gen = True
    #         else:
    #             raise SyntaxError('%s: invalid pair %s, %s' % (self.__class__.__name__, dst, src))
    #     
    #     if not skip_gen:
    #         self.gen(dst, src)
    #     ret += [IDENT + x for x in self.do] # add commands
    #     return make_code(code, ret, table)
    
    def add_line(self, line, ident=1):
        assert isinstance(line, basestring)
        if ident == 1:
            self.do.append(self.format(line))
        else:
            ident -= 1
            self.do.append('%s%s' % (IDENT*ident, self.format(line)))
    
    def add_lines(self, lines, ident=1):
        assert isinstance(lines, (list, tuple))
        if ident == 1:
            self.do += lines
        else:
            ident -= 1
            self.do += ['%s%s' % (IDENT*ident, l) for l in lines]
    
    def add_arg(self, arg, val):
        self.args[arg] = val
    
    def setup(self, dst, src):
        pass
    
    def __param(self, op):
        if len(op['mn']) == 1: # no operands
            self.dst = self.src = None
        elif isinstance(op['mn'][1], basestring): # 1 operand
            self.dst = None
            self.src = op['mn'][1].lower()
        elif len(op['mn'][1]) == 2: # two operands
            self.dst, self.src = [x.lower() for x in op['mn'][1]]
        else:
            raise SyntaxError('%s: too many parameters %r' % (self.__class__.__name__, op['mn'][1]))
    
    def format(self, template):
        return format(template, self.args)
    
    def set_flags(self, line):
        self.add_lines(write_flags(self.format(line)))
