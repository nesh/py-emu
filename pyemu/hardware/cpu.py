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

class CPUException(Exception):
    pass

class CPUTrapInvalidOP(CPUException):
    pass

class _CpuInvalidCommand(object):
    def __call__(self, *args, **kwargs):
        raise CPUTrapInvalidOP('%r, %r' % (args, kwargs))

# used to mark invalid operations
InvalidOp = _CpuInvalidCommand()

class CPU(Device):
    def __init__(self, mem, io=None):
        self.mem = mem
        self.io = io
        super(CPU, self).__init__()
    
    def reset(self):
        self.icount = 0
        self.itotal = 0
    
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