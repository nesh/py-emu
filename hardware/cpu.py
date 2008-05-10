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

from device import Device

# errors
class CPUException(Exception):
    pass

class CPUTrapInvalidOP(CPUException):
    pass

class CPU(Device):
    def __init__(self, mem, io=None, use_tstate_cb=False):
        self.mem = mem
        self.io = io
        # callbacks
        self.use_tstate_cb = use_tstate_cb
        super(CPU, self).__init__()
    
    def reset(self):
        self.tstate = 0
        self.op_tstate = 0
        self.icount = 0
        self.itotal = 0
        self.doing_opcode = False
        self.prefix = 0
    
    def run(self, cycles=None):
        raise NotImplementedError('%s.run() is not implemented' % self.__class__)
    
    def get_state(self):
        """get cpu state
           
           return dict with current cpu state
        """
        raise NotImplementedError('%s.get_state() is not implemented' % self.__class__)
    
    def set_state(self, state):
        """set cpu state
           
           set current cpu state with state dict
        """
        raise NotImplementedError('%s.set_state() is not implemented' % self.__class__)
    
    def disassemble(self, address, instruction_count=1, dump_adr=True, dump_hex=True):
        raise NotImplementedError('%s.disassemble() is not implemented' % self.__class__)
    
    # ===============
    # = z80mx based =
    # ===============
    def step(self):
        """ do next opcode (instruction or prefix),
            return number of T-states eaten
        """
        raise NotImplementedError('%s.step() is not implemented' % self.__class__)
    
    def last_op_type(self):
        """ Return type of last opcode, processed with `step`.
            
            Type will be 0 for complete instruction, or prefix value
            for dd/fd/cb/ed prefixes.
        """
        raise NotImplementedError('%s.last_op_type() is not implemented' % self.__class__)
    
    def irq(self):
        """ maskable interrupt.
            
            returns number of t-states if interrupt was accepted, or 0.
        """
        raise NotImplementedError('%s.irq() is not implemented' % self.__class__)
    
    def nmi(self):
        """ non-maskable interrupt.
            
            returns number of t-states(11 if interrupt taken, 0 if processor
            doing an instruction just now)
        """
        raise NotImplementedError('%s.nmi() is not implemented' % self.__class__)
    
    def op_tstate(self):
        """ when called from callbacks, returns current T-state
            of executing opcode (instruction or prefix),
            else returns t-states taken by last opcode executed
        """
        raise NotImplementedError('%s.op_tstate() is not implemented' % self.__class__)
    
    def w_states(self):
        """ generate <w_states> Wait-states.
            (T-state callback will be called for each of them).
            must be used in t-state callback or I/O callbacks
            to simulate WAIT signal or disabled CLK
        """
        raise NotImplementedError('%s.w_states() is not implemented' % self.__class__)
    
    def next_tstate(self):
        """ spend one T-state doing nothing
            (often IO devices don't handle data request on
            the first T-state, at which RD/WR goes active).
            for use in I/O callbacks
        """
        raise NotImplementedError('%s.next_tstate() is not implemented' % self.__class__)
    
    # ==================
    # = Read/Write mem =
    # ==================
    def int_read(self):
        """ read opcode argument """
        raise NotImplementedError('%s.read_op_arg() is not implemented' % self.__class__)

    def read_op(self):
        """ read opcode """
        if self.int_vector_req:
            return self.int_read()
        ret = self.mem.read(self.pc) # state = 1
        self.pc = (self.pc + 1) & 0xFFFF
        return ret
    
    def read_op_arg(self):
        """ read opcode argument """
        if self.int_vector_req:
            return self.int_read()
        ret = self.mem.read(self.pc) # state=0
        self.pc = (self.pc + 1) & 0xFFFF
        return ret
    
    def read(self, addr, wait=0):
        """ read memory """
        if wait: self._wait_until(wait)
        return self.mem.read(addr) # state = 0
    
    def write(self, addr, value, wait=0, state=None):
        """ write memory """
        if wait: self._wait_until(wait)
        self.mem.write(addr, value)
    
    # ========
    # = Sync =
    # ========
    def _wait_until(self, t):
        """ wait until end of opcode-tstate given (to be used on opcode execution) """
        if not self.use_tstate_cb:
            self.op_tstate += t
            self.tstate += t
            return
        for x in xrange(self.op_tstate, t):
            self.op_tstate += 1
            self.tstate += 1
            self.tstate_cb(self)
    
    def tstates(self, amount):
        """ spend <amount> t-states (not affecting opcode-tstate counter,
            for using outside of certain opcode execution) """
        if not self.use_tstate_cb:
            self.tstate += amount
            return
        for x in xrange(0, amount):
            self.tstate += 1
            self.tstate_cb(self)