def as_signed(val):
    """ convert value to the signed one """
    if val & 0x80:
        return -(256 - val)
    else:
        return val
