from memory import RAM

class IO(RAM):
    def __init__(self, adr_width, bit_width):
        self.size = (2 ** adr_width)
        self.data_size = (2 ** bit_width)
        self.data_width = bit_width
        self.data_mask = self.data_size - 1
        self.adr_width = adr_width
        self.adr_mask = self.size - 1
        self.sign = 1 << (self.data_width - 1)
        super(IO, self).__init__()

    def reset(self):
        raise NotImplementedError('%s.reset() is not implemented' % self.__class__)
    
    def write(self, adr, value):
        raise NotImplementedError('%s.write() is not implemented' % self.__class__)
    
    def read(self, adr):
        raise NotImplementedError('%s.read() is not implemented' % self.__class__)
