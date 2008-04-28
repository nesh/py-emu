import random
try:
    from psyco.classes import __metaclass__
except ImportError:
    pass

from device import Device


class RAM(Device):
    def __init__(self, adr_width, bit_width):
        self.size = (2 ** adr_width)
        self.data_size = (2 ** bit_width)
        self.data_width = bit_width
        self.data_mask = self.data_size - 1
        self.adr_width = adr_width
        self.adr_mask = self.size - 1
        self.sign = 1 << (self.data_width - 1)
        self.mem = [0xDEADBEEF] * self.size
        super(RAM, self).__init__()
    
    def reset(self):
        pass
    
    def read(self, adr):
        return self.mem[adr & self.adr_mask]
    
    def write(self, adr, value):
        self.mem[adr & self.adr_mask] = value & self.data_mask
    
    def __str__(self):
        return '%s object: adr %dbit, data %dbit, size: req 0x%X actual 0x%X' % (self.__class__,
            self.adr_width,
            self.data_width,
            self.size,
            len(self.mem)
        )
    
    def __len__(self):
        return len(self.mem)
    
    def __getitem__(self, k):
        # if isinstance(k, slice):
        #     start = k.start & self.adr_mask
        #     stop =  k.stop & self.adr_mask
        #     return self.mem[start:stop]
        # else:
        return self.mem[k & self.adr_mask]
    
    def __setitem__(self, k, value):
        # if isinstance(k, slice):
        #     start = k.start & self.adr_mask
        #     stop =  k.stop & self.adr_mask
        #     if isinstance(value, (list, tuple)):
        #         self.mem[start:stop] = [v & self.data_mask for v in value]
        #     else:
        #         self.mem[start:stop] = value & self.data_mask
        # else:
        self.mem[k & self.adr_mask] = value & self.data_mask
    
    def __contains__(self, v):
        return (v & self.data_mask) in self.mem