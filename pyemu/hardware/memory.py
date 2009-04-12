# Copyright 2008 Djordjevic Nebojsa <djnesh@gmail.com>
# 
# This file is part of py-emu.
# 
# py-emu is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# py-emu is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with py-emu.  If not, see <http://www.gnu.org/licenses/>.

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
    read_op = read

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