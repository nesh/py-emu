from pydispatch.dispatcher import send, connect
from device import Device

# errors
class CPUException(Exception):
    pass

class CPUTrapInvalidOP(CPUException):
    pass

# signals
cpu_inc_t = object()
cpu_reset = object()
cpu_irq = object()
cpu_nmi = object()

def _add_cycles(instance=None, num=0):
    instance.T -= num
    instance.abs_T += num

class CPU(Device):
    def __init__(self, break_after, mem, io=None):
        self.T = 0
        self.abs_T = 0
        self.mem = mem
        self.io = io
        self.break_after = break_after

        super(CPU, self).__init__()
        
        self._op = self._opcodes()
        self.current_op = None
        
        # register handler
        connect(_add_cycles, cpu_inc_t, sender=self.__class__)
    
    def _opcodes(self):
        """
            0 cycles
            1 len
            2 handler
            3 address handler
            4 mnemo
        """
        # main table
        ret = []
        for x in range(0x100):
            ret.append((0, 1, self._invalid_op, None, 'BUG $%02X' % x))
        return ret
    
    def _read_op(self):
        raise NotImplementedError('%s._read_op() is not implemented' % self.__class__)

    def run(self, cycles=None):
        if cycles is None:
            # run one inst
            self.current_op = self._read_op()
            op = self._op[self.current_op]
            op[2](op[3])
            self.abs_T += op[0]
            self.T -= op[0]
            return

        # run until we spend all cycles
        self.T += cycles
        while self.T >= 0:
            self.current_op = self._read_op()
            op = self._op[self.current_op]
            op[2](op[3])
            self.abs_T += op[0]
            self.T -= op[0]
        
    def _invalid_op(self, read):
        raise CPUTrapInvalidOP('$%X' % self.current_op)

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