import sys
from ctypes import *

from hardware.cpu import CPUTrapInvalidOP

_Z80 = CDLL("z80_core.so")

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
F5_FLAG = Y_FLAG = 0x20 # 5
H_FLAG  = 0x10 # 4
F3_FLAG = X_FLAG = 0x08 # 3
V_FLAG = P_FLAG  = 0x04 # 2
N_FLAG  = 0x02 # 1
C_FLAG  = 0x01 # 0

# Bits in IFF flip-flops
IFF_1 = 0x01        # IFF1 flip-flop
IFF_IM1 = 0x02      # 1: IM1 mode
IFF_IM2 = 0x04      # 1: IM2 mode
IFF_2 = 0x08        # IFF2 flip-flop
IFF_EI = 0x20       # 1: EI pending
IFF_HALT = 0x80     # 1: CPU HALTed

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
        
        ('write', c_void_p),
        ('read', c_void_p),
        ('read_op', c_void_p),
        
        ('io_write', c_void_p),
        ('io_read', c_void_p),
        
        ('patch', c_void_p),
        ('jump', c_void_p),
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
def _exec_z80_handle(val):
    if val == 0: # OK
        return val
    elif val == -1:
        raise CPUTrapInvalidOP()
    else:
        raise CPUException(val)
_Z80.ExecZ80.argtypes = (Z80StateP, c_int)
_Z80.ExecZ80.restype = _exec_z80_handle

# /** IntZ80() *************************************************/
# /** This function will generate interrupt of given vector.  **/
# /*************************************************************/
# void IntZ80(register Z80 *R,register word Vector);
_Z80.IntZ80.argtypes = (Z80StateP, word)
_Z80.IntZ80.restype = None
