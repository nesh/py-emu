import sys, ctypes
import random
try:
    from psyco import compact
    from psyco.classes import __metaclass__
except ImportError:
    class compact(object):
        pass

if sys.byteorder == "little":
    class _Reg16(ctypes.Structure):
        """Structure with little endian byte order"""
        _fields_ = (
            ('lo', ctypes.c_uint8),
            ('hi', ctypes.c_uint8),
        )
elif sys.byteorder == "big":
    class _Reg16(ctypes.Structure):
        """Structure with big endian byte order"""
        _fields_ = (
            ('hi', ctypes.c_uint8),
            ('lo', ctypes.c_uint8),
        )
else:
    raise RuntimeError("Invalid byteorder")

class CRegister16_8(ctypes.Union):
    _fields_ = (
        ('word', ctypes.c_uint16),
        ('byte', _Reg16)
    )

class CRegister16(ctypes.Structure):
    _fields_ = (
        ('word', ctypes.c_uint16),
    )

class CRegister8(ctypes.Structure):
    _fields_ = (
        ('byte', ctypes.c_uint8),
    )

class Register16_8(compact):
    def __init__(self, val=random.randint(0, 0xFFFF)):
        self._value = val
    
    def _get(self):
        return self._value
    def _set(self, val):
        self._value = val & 0xFFFF
    value = property(fget=_get, fset=_set)

    def _get_hi(self):
        return (self._value & 0xFF00) >> 8
    def _set_hi(self, val):
        self._value = (self._value & 0x00FF) | ((val & 0xFF) << 8)
    hi = property(fget=_get_hi, fset=_set_hi)

    def _get_lo(self):
        return (self._value & 0x00FF)
    def _set_lo(self, val):
        self._value = (self._value & 0xFF00) | (val & 0xFF)
    lo = property(fget=_get_lo, fset=_set_lo)
    