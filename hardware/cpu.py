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
        
        self._op = {}
        
        self.current_op = None
        
        # register handler
        connect(_add_cycles, cpu_inc_t, sender=self.__class__)
        
        self.adr_modes = {}
    
    def _dummy_read(self):
        return None
    
    def _cycles(self, op):
        raise NotImplementedError('%s._cycles() is not implemented' % self.__class__)
    
    def _bytes(self, op):
        raise NotImplementedError('%s._bytes() is not implemented' % self.__class__)
    
    def _mnemonic(self, op):
        raise NotImplementedError('%s._mnemonic() is not implemented' % self.__class__)
    
    def add_op(self, opcode, handler, adr_mode, override=False):
        """
            0 cycles
            1 handler
            2 address handler
        """
        
        if opcode in self._op and not override:
            raise KeyError('Duplicated opcode $%02X' % opcode)
        self._op[opcode] = (
            self._cycles(opcode),
            handler,
            self.adr_modes[adr_mode][0],
        )
    
    def register_opcodes(self):
        raise NotImplementedError('%s.register_opcodes() is not implemented' % self.__class__)
    
    def read_op(self):
        raise NotImplementedError('%s.read_op() is not implemented' % self.__class__)
    
    def run(self, cycles=None):
        if cycles is None:
            # run one inst
            self.current_op = self.read_op()
            t, handler, read_op = self._op[self.current_op]
            handler(*read_op())
            self.abs_T += t
            self.T -= t
            return
        
        # run until we spend all cycles
        self.T += cycles
        while self.T >= 0:
            self.current_op = self.read_op()
            t, handler, read_op = self._op[self.current_op]
            handler(*read_op())
            self.abs_T += t
            self.T -= t
    
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