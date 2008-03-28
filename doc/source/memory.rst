:mod:`memory`
=============

.. module:: memory
   :synopsis: base class for all memory based devices.
.. moduleauthor:: Djordjevic Nebojsa <djnesh@gmail.com>

.. class:: RAM(adr_width, bit_width)

  extends :class:`~device.Device`
  
  **R**\ andom\ **A**\ ccess\ **M**\ emory

  .. method:: RAM.reset()
    
    resets memory to random values.

  .. method:: RAM.reset()
    
    resets memory to random values.

  .. method:: RAM.write(adr, value)
    
    write `value` to the `adr`.
    
  .. method:: RAM.read(adr)
  
    read from the `adr`
