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

from hardware.flags import Flags
from opcodes.tables import SF, ZF, YF, HF, XF, VF, NF, CF


class Z80Flags(Flags):
    def __init__(self, val=0xFF):
        self.s = False
        self.z = False
        self.y = False
        self.h = False
        self.x = False
        self.v = False
        self.n = False
        self.c = False
        super(Z80Flags, self).__init__(val)
    
    def mset(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def set(self, val):
        self.s = bool(val & SF)
        self.z = bool(val & ZF)
        self.y = bool(val & YF)
        self.h = bool(val & HF)
        self.x = bool(val & XF)
        self.v = bool(val & VF)
        self.n = bool(val & NF)
        self.c = bool(val & CF)
    
    def get(self):
        return (
              (SF if self.s else 0)
            | (ZF if self.z else 0)
            | (YF if self.y else 0)
            | (HF if self.h else 0)
            | (XF if self.x else 0)
            | (VF if self.v else 0)
            | (NF if self.n else 0)
            | (CF if self.c else 0)
            )
    
    byte = property(fget=get, fset=set)
    
    def __str__(self):
        ret = [' '] * 8
        ret[7] = 'S' if self.s else '-'
        ret[6] = 'Z' if self.z else '-'
        ret[5] = 'Y' if self.y else '-'
        ret[4] = 'H' if self.h else '-'
        ret[3] = 'X' if self.x else '-'
        ret[2] = 'P/V' if self.v else '-'
        ret[1] = 'N' if self.n else '-'
        ret[0] = 'C' if self.c else '-'
        ret.reverse()
        return ''.join(ret)