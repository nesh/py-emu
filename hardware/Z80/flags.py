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