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

try:
    from psyco.classes import __metaclass__
except ImportError:
    pass

from settings import logging

class Device(object):
    def __init__(self):
        super(Device, self).__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)
    
    def reset(self):
        raise NotImplementedError('%s.reset() is not implemented' % self.__class__)
    
    def write(self, adr, value):
        raise NotImplementedError('%s.write() is not implemented' % self.__class__)
    
    def read(self, adr):
        raise NotImplementedError('%s.read() is not implemented' % self.__class__)
