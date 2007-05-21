from pydispatch.dispatcher import send, connect
from device import Device

# IO events
class IORead:
    pass

class IOWrite:
    pass

class IO(Device):
    def __init__(self, adr_width, bit_width):
        self._data_width = bit_width
        self._data_mask = (2 ** bit_width) - 1
        self._adr_width = adr_width
        self._adr_mask = self._size - 1
        super(IO, self).__init__()

    def read(self, adr):
        # it will return value from the *last* event handler
        return send(IORead, self, adr & self._adr_mask)[-1][1] & self._data_mask

    def write(self, adr, value):
        send(IOWrite, self, adr & self._adr_mask, value & self._data_mask)