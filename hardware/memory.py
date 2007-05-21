from pydispatch.dispatcher import send, connect
from device import Device
import numpy

class RAM(Device):
    def __init__(self, adr_width, bit_width):
        self._data_width = bit_width
        self._data_mask = (2 ** bit_width) - 1
        self._size = (2 ** adr_width)
        self._adr_width = adr_width
        self._adr_mask = self._size - 1
        self._mem = numpy.empty(self._size, dtype=numpy.uint8)
        #self._mem = [0] * self._size
        super(RAM, self).__init__()

    def reset(self):
        """ reset mem to random values """
        self._mem = numpy.empty(self._size, dtype=numpy.uint8)
        #self._mem = [0] * self._size
        
    def read(self, adr):
        return self._mem[adr & self._adr_mask]

    def write(self, adr, value):
        self._mem[adr & self._adr_mask] = value #& self._data_mask
        #self._mem[adr & self._adr_mask] = value

    def __str__(self):
        return '%s object: adr %dbit, data %dbit, size: req 0x%X actual 0x%X' % (self.__class__,
            self._adr_width,
            self._data_width,
            self._size,
            len(self._mem)
        )

    def __len__(self):
        return self._size