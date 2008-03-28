#!/usr/bin/env python
# -*- coding:utf-8

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from z80.base import *
from z80.ld8 import *

# =======
# = RUN =
# =======
if __name__ == '__main__':
    unittest.main()
