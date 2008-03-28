import random

from hardware.flags import Flags
from tables import *

class Z80Flags(Flags):
    S  = S_FLAG # 7
    Z  = Z_FLAG # 6
    F5 = F5_FLAG # 5
    H  = H_FLAG # 4
    F3  = F3_FLAG # 3
    V  = V_FLAG # 2
    N  = N_FLAG # 1
    C  = C_FLAG # 0
    
    def __init__(self, val=None):
        self.s = False
        self.z = False
        self.f5 = False
        self.h = False
        self.f3 = False
        self.v = False
        self.n = False
        self.c = False
        
        if val is None:
            val = random.randint(0, 0xFF)
        super(Z80Flags, self).__init__(val)
    
    def mset(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def set(self, val):
        self.s = bool(val & S_FLAG)
        self.z = bool(val & Z_FLAG)
        self.f5 = bool(val & F5_FLAG)
        self.h = bool(val & H_FLAG)
        self.f3 = bool(val & F3_FLAG)
        self.v = bool(val & V_FLAG)
        self.n = bool(val & N_FLAG)
        self.c = bool(val & C_FLAG)
    
    def get(self):
        return (
            (S_FLAG if self.s else 0)
            | (Z_FLAG if self.z else 0)
            | (F5_FLAG if self.f5 else 0)
            | (H_FLAG if self.h else 0)
            | (F3_FLAG if self.f3 else 0)
            | (V_FLAG if self.v else 0)
            | (N_FLAG if self.n else 0)
            | (C_FLAG if self.c else 0)
            )
    
    byte = property(fget=get, fset=set)
    
    def __str__(self):
        ret = ['-'] * 8
        ret[7] = 'S' if self.s else '-'
        ret[6] = 'Z' if self.z else '-'
        ret[5] = '5' if self.f5 else '-'
        ret[4] = 'H' if self.h else '-'
        ret[3] = '3' if self.f3 else '-'
        ret[2] = 'V' if self.v else '-'
        ret[1] = 'N' if self.n else '-'
        ret[0] = 'C' if self.c else '-'
        ret.reverse()
        return ''.join(ret)