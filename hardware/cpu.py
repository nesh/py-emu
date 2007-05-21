from pydispatch.dispatcher import send, connect
from device import Device

# errors
class CPUException(Exception):
    pass

class CPUTrapInvalidOP(CPUException):
    pass

# Events
class CPUIncT:
    pass

class CPUReset:
    pass

class CPUIRQ:
    pass

class CPUNMI:
    pass

class CPU(Device):
    def __init__(self, break_after, mem, io=None):
        self.T = 0
        self.abs_T = 0
        self.mem = mem
        self.io = io
        self.break_after = break_after

        super(CPU, self).__init__()
        
        self._op = self._opcodes()
        # register handler
        connect(self.add_cycles, CPUIncT, weak=False)
    
    def _opcodes(self):
        """
            0 cycles
            1 len
            2 handler
            3 address handler
            4 mnemo
        """
        raise NotImplementedError('%s._opcodes() is not implemented' % self.__class__)
        
    def add_cycles(self, num):
        self.T -= num
        self.abs_T += num
        
    def run(self, cycles=None):
        raise NotImplementedError('%s.run() is not implemented' % self.__class__)
        
    def _invalid_op(self, code, *args, **kwargs):
        raise CPUTrapInvalidOP('$%X' % code)

    def get_state(self):
        """get cpu state

           return hash with current cpu state
        """
        raise NotImplementedError('%s.get_state() is not implemented' % self.__class__)

    def set_state(self, state):
        """set cpu state

           set current cpu state
        """
        raise NotImplementedError('%s.set_state() is not implemented' % self.__class__)
        
    def disassemble(self, address, instruction_count=1, dump_adr=True, dump_hex=True):
        raise NotImplementedError('%s.disassemble() is not implemented' % self.__class__)