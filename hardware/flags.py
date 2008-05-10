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

class Flags(object):
    def __init__(self, val=0):
        self.set(val)

    def set(self, val):
        raise NotImplementedError('%s.set()s not implemented' % self.__class__)

    def mset(self, **kwargs):
        raise NotImplementedError('%s.mset()s not implemented' % self.__class__)

    def get(self):
        raise NotImplementedError('%s.get()s not implemented' % self.__class__)

    def __int__(self):
        """ slower than get!! """
        return self.get()

    def __str__(self):
        raise NotImplementedError('%s.__str__()s not implemented' % self.__class__)

    def __hex__(self):
        return hex(self.get())
