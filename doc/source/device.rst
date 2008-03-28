:mod:`device`
=============

.. module:: device
   :synopsis: base class for all devices.
.. moduleauthor:: Djordjevic Nebojsa <djnesh@gmail.com>

.. class:: Device()

  Base class for all devices
  
  .. method::  Device.reset()
  
    reset device
    
    :exc:`NotImplementedError`
    
  .. method::  Device.write(adr, value)
    
    write `value` to the `adr`.
    
    :exc:`NotImplementedError`
    
  .. method::  Device.read(adr)
  
    read from the `adr`
    
    :exc:`NotImplementedError`