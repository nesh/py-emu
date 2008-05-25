import sys
import os
from ctypes import *

LIB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'clibs', 'build', 'Release'))

libz80 = CDLL(os.path.join(LIB_DIR, "libz80.dylib"))

byte = c_uint8
sbyte = c_int8
word = c_uint16
c_func_ptr = c_void_p # better?

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
        ('b', B),
        ('w', c_uint16),
    )

S_FLAG  = 0x80 # 7
Z_FLAG  = 0x40 # 6
F5_FLAG = Y_FLAG = 0x20 # 5
H_FLAG  = 0x10 # 4
F3_FLAG = X_FLAG = 0x08 # 3
V_FLAG = P_FLAG  = 0x04 # 2
N_FLAG  = 0x02 # 1
C_FLAG  = 0x01 # 0

# ============
# = IM modes =
# ============
IM0, IM1, IM2 = range(0, 3)

# =============
# = registers =
# =============
regAF, regBC, regDE, regHL, regAF_, regBC_, regDE_, regHL_, regIX, regIY, regPC, regSP, regI, regR, regR7, regIM, regIFF1, regIFF2 = range(0, 18)

class Z80State(Structure):
    _fields_ = (
        ('af', pair),
        ('bc', pair),
        ('de', pair),
        ('hl', pair),
        ('af_', pair),
        ('bc_', pair),
        ('de_', pair),
        ('hl_', pair),
        ('ix', pair),
        ('iy', pair),
        ('i', byte),
        ('r', word),
        ('r7', byte),
        ('sp', pair),
        ('pc', pair),
        ('iff1', byte),
        ('iff2', byte),
        ('memptr', pair),
        ('im', byte),
        ('halted', c_int),
        ('tstate', c_ulong),
        ('op_tstate', byte),
        ('noint_once', c_int),
        ('doing_opcode', c_int),
        ('int_vector_req', c_char),
        ('prefix', byte),
        # callbacks
        ('tstate_c', c_func_ptr), # z80ex_tstate_cb
        ('tstate_cb_user_data', c_void_p),
        ('pread_cb', c_func_ptr), # z80ex_pread_cb
        ('pread_cb_user_data', c_void_p),
        ('pwrite_cb', c_func_ptr), # z80ex_pwrite_cb
        ('pwrite_cb_user_data', c_void_p),
        ('mread_cb', c_func_ptr), # z80ex_mread_cb
        ('mread_cb_user_data', c_void_p),
        ('mwrite_cb', c_func_ptr), # z80ex_mwrite_cb
        ('mwrite_cb_user_data', c_void_p),
        ('intread_cb', c_func_ptr), # z80ex_intread_cb
        ('intread_cb_user_data', c_void_p),
        # misc
        ('tmpword', pair),
        ('tmpadr', pair),
        ('tmpbyte', byte),
        ('tmpbyte_s', sbyte),
    )


Z80StateP = POINTER(Z80State)
UserDataP = c_void_p

# =============
# = callbacks =
# =============

# called on each T-State [optional]
# void (*z80ex_tstate_cb)(Z80EX_CONTEXT *cpu, void *user_data)
z80ex_tstate_cb = CFUNCTYPE(None, Z80StateP, UserDataP)

# read byte from memory <addr> -- called when RD & MREQ goes active.
# m1_state will be 1 if M1 signal is active
# Z80EX_BYTE (*z80ex_mread_cb)(Z80EX_CONTEXT *cpu, Z80EX_WORD addr, int m1_state, void *user_data);
z80ex_mread_cb = CFUNCTYPE(byte, Z80StateP, word, c_int, UserDataP)

# write <value> to memory <addr> -- called when WR & MREQ goes active
# typedef void (*z80ex_mwrite_cb)(Z80EX_CONTEXT *cpu, Z80EX_WORD addr, Z80EX_BYTE value, void *user_data);
z80ex_mwrite_cb = CFUNCTYPE(None, Z80StateP, word, byte, UserDataP)

# read byte from <port> -- called when RD & IORQ goes active
# Z80EX_BYTE (*z80ex_pread_cb)(Z80EX_CONTEXT *cpu, Z80EX_WORD port, void *user_data);
z80ex_pread_cb = CFUNCTYPE(byte, Z80StateP, word, UserDataP)

# write <value> to <port> -- called when WR & IORQ goes active
# void (*z80ex_pwrite_cb)(Z80EX_CONTEXT *cpu, Z80EX_WORD port, Z80EX_BYTE value, void *user_data);
z80ex_pwrite_cb = CFUNCTYPE(None, Z80StateP, word, byte, UserDataP)

# read byte of interrupt vector -- called when M1 and IORQ goes active
# Z80EX_BYTE (*z80ex_intread_cb)(Z80EX_CONTEXT *cpu, void *user_data);
z80ex_intread_cb = CFUNCTYPE(byte, Z80StateP, UserDataP)

# void (*z80ex_opcode_fn) (Z80EX_CONTEXT *cpu);
z80ex_opcode_fn = CFUNCTYPE(None, Z80StateP)

# =============
# = Functions =
# =============
def _handle_boolean(val):
    """ convert int to boolean """
    return val != 0

# create and initialize CPU
# Z80EX_CONTEXT *z80ex_create(z80ex_mread_cb mrcb_fn, void *mrcb_data,
#   z80ex_mwrite_cb mwcb_fn, void *mwcb_data,
#   z80ex_pread_cb prcb_fn, void *prcb_data,
#   z80ex_pwrite_cb pwcb_fn, void *pwcb_data,
#   z80ex_intread_cb ircb_fn, void *ircb_data);
libz80.z80ex_create.argtypes = (c_func_ptr, c_void_p,
                                 c_func_ptr, c_void_p,
                                 c_func_ptr, c_void_p,
                                 c_func_ptr, c_void_p,
                                 c_func_ptr, c_void_p,
                                )
libz80.z80ex_create.restype = Z80StateP

# destroy CPU
# void z80ex_destroy(Z80EX_CONTEXT *cpu);
libz80.z80ex_destroy.argtypes = (Z80StateP,)
libz80.z80ex_destroy.restype = None

# do next opcode (instruction or prefix), return number of T-states eaten
# int z80ex_step(Z80EX_CONTEXT *cpu);
libz80.z80ex_step.argtypes = (Z80StateP,)
libz80.z80ex_step.restype = c_int

# run cpu until tstates expire, return remainder (can be negative)
# int z80ex_run(Z80EX_CONTEXT *cpu, int tstates);
libz80.z80ex_run.argtypes = (Z80StateP, c_int)
libz80.z80ex_run.restype = c_int

# return type of last opcode, processed with z80ex_step.
# type will be 0 for complete instruction, or prefix value for dd/fd/cb/ed prefixes
# Z80EX_BYTE z80ex_last_op_type(Z80EX_CONTEXT *cpu);
libz80.z80ex_last_op_type.argtypes = (Z80StateP,)
libz80.z80ex_last_op_type.restype = byte

# set T-state callback
# void z80ex_set_tstate_callback(Z80EX_CONTEXT *cpu, z80ex_tstate_cb cb_fn, void *user_data);
libz80.z80ex_set_tstate_callback.argtypes = (Z80StateP, c_func_ptr, c_void_p)
libz80.z80ex_set_tstate_callback.restype = None

# maskable interrupt
# returns number of t-states if interrupt was accepted, or 0
# int z80ex_int(Z80EX_CONTEXT *cpu);
libz80.z80ex_int.argtypes = (Z80StateP,)
libz80.z80ex_int.restype = c_int

# non-maskable interrupt
# returns number of t-states(11 if interrupt taken, 0 if processor
# doing an instruction just now)
# int z80ex_nmi(Z80EX_CONTEXT *cpu);
libz80.z80ex_nmi.argtypes = (Z80StateP,)
libz80.z80ex_nmi.restype = c_int

# reset CPU
# void z80ex_reset(Z80EX_CONTEXT *cpu);
libz80.z80ex_reset.argtypes = (Z80StateP,)
libz80.z80ex_reset.restype = None

# getting register value
# Z80EX_WORD z80ex_get_reg(Z80EX_CONTEXT *cpu, Z80_REG_T reg);
libz80.z80ex_get_reg.argtypes = (Z80StateP, byte)
libz80.z80ex_get_reg.restype = word

# setting register value (for 1-byte registers, lower byte of <value> will be used)
# void z80ex_set_reg(Z80EX_CONTEXT *cpu, Z80_REG_T reg, Z80EX_WORD value);
libz80.z80ex_set_reg.argtypes = (Z80StateP, byte, word)
libz80.z80ex_set_reg.restype = None

# returns 1 if CPU doing HALT instruction now
# int z80ex_doing_halt(Z80EX_CONTEXT *cpu);
libz80.z80ex_doing_halt.argtypes = (Z80StateP,)
libz80.z80ex_doing_halt.restype = _handle_boolean

# when called from callbacks, returns current T-state of executing opcode
# (instruction or prefix),
# else returns t-states taken by last opcode executed
# int z80ex_op_tstate(Z80EX_CONTEXT *cpu);
libz80.z80ex_op_tstate.argtypes = (Z80StateP,)
libz80.z80ex_op_tstate.restype = c_int

# generate <w_states> Wait-states. (T-state callback will be called for each of them).
# must be used in t-state callback or I/O callbacks to simulate WAIT signal
# or disabled CLK
# void z80ex_w_states(Z80EX_CONTEXT *cpu, unsigned w_states);
libz80.z80ex_w_states.argtypes = (Z80StateP, c_uint)
libz80.z80ex_w_states.restype = None

# spend one T-state doing nothing (often IO devices don't handle data request on
# the first T-state, at which RD/WR goes active).
# for use in I/O callbacks
# void z80ex_next_t_state(Z80EX_CONTEXT *cpu);
libz80.z80ex_next_t_state.argtypes = (Z80StateP,)
libz80.z80ex_next_t_state.restype = None



# def _exec_z80_handle(val):
#     if val == 0: # OK
#         return val
#     elif val == -1:
#         raise CPUTrapInvalidOP()
#     else:
#         raise CPUException(val)
# _Z80.ExecZ80.argtypes = (Z80StateP, c_int)
# _Z80.ExecZ80.restype = _exec_z80_handle