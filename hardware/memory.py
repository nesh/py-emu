import random
import ctypes

from device import Device


class RAM(Device):
    def __init__(self, adr_width, bit_width):
        self._data_width = bit_width
        self._data_mask = (2 ** bit_width) - 1
        self._size = (2 ** adr_width)
        self._adr_width = adr_width
        self._adr_mask = self._size - 1
        self._sign = 1 << (self._data_width - 1)
        self._mem = [0] * self._size
        super(RAM, self).__init__()
    
    def as_signed(self, val):
        """ convert value to the signed one """
        if val & self._sign:
            return -(val & (self._sign - 1))
        else:
            return val
    
    def reset(self):
        """ reset mem to random values """
        self._mem = [0] * self._size
    
    def read(self, adr):
        # don't enforce data width on read because is already enforced on write!
        return self._mem[adr & self._adr_mask]
    
    def write(self, adr, value):
        self._mem[adr & self._adr_mask] = value & self._data_mask
    
    def __str__(self):
        return '%s object: adr %dbit, data %dbit, size: req 0x%X actual 0x%X' % (self.__class__,
            self._adr_width,
            self._data_width,
            self._size,
            len(self._mem)
        )
    
    def __len__(self):
        return len(self._mem)
    
    def __getitem__(self, k):
        """ slicing is NOT supported """
        return self._mem[k & self._adr_mask]
    
    def __setitem__(self, k, value):
        """ slicing is NOT supported """
        self._mem[k & self._adr_mask] = value & self._data_mask
    
    def __iter__(self):
        return iter(self._mem)
    
    def __contains__(self, v):
        return v in self._mem