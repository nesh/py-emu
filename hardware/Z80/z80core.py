import sys
from ctypes import *

_Z80 = CDLL("Z80_core.so")

byte = c_uint8
word = c_uint16

if sys.byteorder == "little":
    class B(Structure):
        """Structure with little endian byte order"""
        _fields_ = (
            ('l', c_uint8),
            ('h', c_uint8),
        )
elif sys.byteorder == "big":
    class B(Structure):
        """Structure with big endian byte order"""
        _fields_ = (
            ('h', c_uint8),
            ('l', c_uint8),
        )
else:
    raise RuntimeError("Invalid byteorder")

class pair(Union):
    _fields_ = (
        ('B', B),
        ('W', c_uint16),
    )

S_FLAG  = 0x80 # 7
Z_FLAG  = 0x40 # 6
F5_FLAG = 0x20 # 5
H_FLAG  = 0x10 # 4
F3_FLAG  = 0x08 # 3
V_FLAG = P_FLAG  = 0x04 # 2
N_FLAG  = 0x02 # 1
C_FLAG  = 0x01 # 0

class Z80State(Structure):
    _fields_ = (
        ('AF', pair),
        ('BC', pair),
        ('DE', pair),
        ('HL', pair),
        ('IX', pair),
        ('IY', pair),
        ('PC', pair),
        ('SP', pair),
        ('AF1', pair),
        ('BC1', pair),
        ('DE1', pair),
        ('HL1', pair),
        ('IFF', byte),
        ('I', c_uint8),
        ('R', byte),
        ('IPeriod', c_int),
        ('ICount', c_int),
        ('ITotal', c_int),
        ('IBackup', c_int),
        ('IRequest', word),
        ('IAutoReset', byte),
        ('TrapBadOps', byte),
        ('Trap', word),
        ('Trace', byte),
        
        ('write', c_void_p),
        ('read', c_void_p),
        ('read_op', c_void_p),
        
        ('io_write', c_void_p),
        ('io_read', c_void_p),
        
        ('patch', c_void_p),
        ('loop', c_void_p),
        ('jump', c_void_p),
        
        ('User', c_void_p),
    )
Z80StateP = POINTER(Z80State)
PBYTE = POINTER(byte)
PWORD = POINTER(word)
READ = CFUNCTYPE(byte, word)
WRITE = CFUNCTYPE(None, word, byte)
PATCH = CFUNCTYPE(None, Z80StateP)
LOOP = CFUNCTYPE(word, Z80StateP)

# Func spec
# /** ResetZ80() ***********************************************/
# /** This function can be used to reset the registers before **/
# /** starting execution with RunZ80(). It sets registers to  **/
# /** their initial values.                                   **/
# /*************************************************************/
# void ResetZ80(register Z80 *R);
_Z80.ResetZ80.argtypes = (Z80StateP,)
_Z80.ResetZ80.restype = None

# /** ExecZ80() ************************************************/
# /** This function will execute given number of Z80 cycles.  **/
# /** It will then return the number of cycles left, possibly **/
# /** negative, and current register values in R.             **/
# /*************************************************************/
# #ifdef EXECZ80
# int ExecZ80(register Z80 *R,register int RunCycles);
# #endif
_Z80.ExecZ80.argtypes = (Z80StateP, c_int)
_Z80.ExecZ80.restype = c_int

# /** IntZ80() *************************************************/
# /** This function will generate interrupt of given vector.  **/
# /*************************************************************/
# void IntZ80(register Z80 *R,register word Vector);
_Z80.IntZ80.argtypes = (Z80StateP, word)
_Z80.IntZ80.restype = None
