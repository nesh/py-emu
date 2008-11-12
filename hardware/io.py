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

try:
    from psyco.classes import __metaclass__
except ImportError:
    pass
# from pydispatch.dispatcher import send, connect
from device import Device

# IO events
class IORead:
    pass

class IOWrite:
    pass

class IO(Device):
    def __init__(self, adr_width, bit_width):
        self._data_width = bit_width
        self._data_mask = (2 ** bit_width) - 1
        self._adr_width = adr_width
        self._adr_mask = self._size - 1
        super(IO, self).__init__()

    def read(self, adr):
        # it will return value from the *last* event handler
        # return send(IORead, self, adr & self._adr_mask)[-1][1] & self._data_mask
        pass

    def write(self, adr, value):
        # send(IOWrite, self, adr & self._adr_mask, value & self._data_mask)
        pass