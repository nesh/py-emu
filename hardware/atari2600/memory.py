from hardware.memory import RAM
#from tia import TIA

__all__ = ('A2600Mem',)

CV_SIG = (
     '\x9D\xFF\xF3',  # STA $F3FF
     '\x99\x00\xF4'   # STA $F400
)

def memcmp(buf, buf1, ln):
    x = 0
    for b in buf[:ln]:
        if b != buf1[x]:
            return False
        x += 1
    return True

def is_probably_cv(image):
    return CV_SIG[0] in image or CV_SIG[1] in image

def detect_type(image):
    """ cartrige factory """

    size = len(image)
    if (size % 8448) == 0:
        return 'AR'
    elif (size == 2048) or ((size == 4096) and memcmp(image, image[2048:], 2048)):
        if is_probably_cv(image):
            return 'CV'
        else:
            return Cartridge2K(image)


class Cartridge(RAM):
    def __init__(self, adr_width, bit_width):
        self._bank_locked = False
        self.tia = None #TIA()
        super(Cartridge, self).__init__(adr_width, bit_width)

    def lock_bank(self):
        self._bank_locked = True

    def unlock_bank(self):
        self._bank_locked = False

    def save(self, fname):
        raise NotImplementedError('%s.save() is not implemented' % self.__class__)

    def load(self, fname):
        raise NotImplementedError('%s.load() is not implemented' % self.__class__)

    def set_bank(self, no):
        raise NotImplementedError('%s.set_bank() is not implemented' % self.__class__)

    def get_bank(self):
        raise NotImplementedError('%s.get_bank() is not implemented' % self.__class__)

    def bank_count(self):
        raise NotImplementedError('%s.bank_count() is not implemented' % self.__class__)

    def patch(self, adr, val):
        raise NotImplementedError('%s.patch() is not implemented' % self.__class__)


class Cartridge2K(Cartridge):
    def __init__(self, image):
        super(Cartridge2K, self).__init__(11, 8)

        assert len(image) == (2 * 1024)

        a = 0
        for b in image:
            super(Cartridge2K, self).write(a, ord(b))
            a += 1
        self._mem = tuple(self._mem) # mem is RO

    def __str__(self):
        return '2K cartrige'

    def bank_count(self):
        return 1

    def set_bank(self, no):
        return

    def get_bank(self):
        return 0

    def patch(self, adr, val):
        self.write(adr, val)

    def write(self, adr, value):
        return

class A2600Mem(RAM):
    TIA_WRITE = set(range(0, 0x002C))
    TIA_READ = set(range(0x0000, 0x000D) + range(0x0030, 0x003D))
    PIA_RAM = set(range(0x0080, 0x00FF))
    PIA_PORTS_TIMER = set(range(0x0280, 0x0297))

    def __init__(self, fname):
        fh = open(fname, 'rb')
        image = fh.read()
        fh.close()
        self.cart = detect_type(image)
        print 'loaded %s (%s)' % (fname, self.cart)
        super(A2600Mem, self).__init__(13, 8)


    def read(self, adr):
        if adr & 0x1000:
            return self.cart.read(adr)
        return self._mem[adr & self._adr_mask]

    def write(self, adr, value):
        if adr & 0x1000:
            return self.cart.write(adr, value)
        self._mem[adr & self._adr_mask] = value & self._data_mask
