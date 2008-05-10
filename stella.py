#!/usr/bin/env python
# encoding: utf-8

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

"""
py-emu.py

Created by  on 2007-12-26.
Copyright (c) 2007 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from optparse import OptionParser

from pyglet import font
from pyglet import clock
from pyglet import window
from pyglet.gl import *
from pyglet.window import key

import settings
from hardware.atari2600.memory import A2600Mem
from hardware.MOS65xx.MOS6502 import MOS6502


ROOT = os.path.abspath(os.path.dirname(__file__))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


parser = OptionParser()
parser.add_option("-p", "--pal", dest="system", action='store_const', const='PAL',
                  help="emulate PAL system", default='PAL')
parser.add_option("-n", "--ntsc", dest="system", action='store_const', const='NTSC',
                  help="emulate NTSC system")
parser.add_option("-f", "--fps",
                  action="store_true", dest="fps", default=False,
                  help="show fps")
parser.add_option("-d", "--d",
                  action="store_true", dest="debug", default=False,
                  help="debug mode")
parser.add_option("", "--profile",
                  action="store_true", dest="profile", default=False,
                  help="profile code")
(options, args) = parser.parse_args()

SYSTEMS = {'PAL': (160, 228, 50), 'NTSC': (160, 192, 60)}


class MainWindow(window.Window):
    def __init__(self):
        self.sys_width, self.sys_height, self.hz = SYSTEMS[options.system]
        self.fps = self.hz / 2
        super(MainWindow, self).__init__(self.sys_width * 2, self.sys_height * 2, visible=False)
        self.show_fps = options.fps
        self.show_cpu = options.debug
        self.font = font.load('Monaco', 10)
        self.fps_display = clock.ClockDisplay(
            font=self.font,
            color=(0, 0.5, 0, 0.5),
            interval=1,
            format='%(fps)d',
        )

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.set_visible()

        self.setup_emu()

    #def draw(self):
    #    self.text.draw()

    def run(self):
        clock.set_fps_limit(self.fps)

        while not self.has_exit:
            self.dispatch_events()
            # run emu for one frame
            self.cpu.run(cycles=25000)
            self.clear()
            if self.show_fps: self.fps_display.draw() # show FPS
            if self.show_cpu: # cpu debug info
                text = font.Text(self.font, '%s %02X' % (self.cpu, self.cpu.current_op))
                text.draw()
            # housekeeping
            dt = clock.tick()
            # show frame
            self.flip()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.has_exit = True # EXIT
        elif symbol == key.F10:
            self.show_fps = not self.show_fps # Toggle FPS
        elif symbol == key.F11:
            self.show_cpu = not self.show_cpu # Toggle CPU

    def on_key_release(self, symbol, modifiers):
        pass

    def setup_emu(self, cpu_mhz=1.19):
        t_per_frame = int((cpu_mhz * 1e6) / self.hz)
        self.mem = A2600Mem(os.path.join(ROOT, 'private', 'data', '3d_tic.bin'))
        self.cpu = MOS6502(t_per_frame, self.mem)
        self.cpu.reset()

def main(options):
    if options.debug:
        options.fps = True # force fps display in debug mode

    win = MainWindow()

    if options.profile:
        import cProfile
        import pstats
        cProfile.run('win.run()', 'stella.prof')
        stats = pstats.Stats('stella.prof')
        stats.strip_dirs()
        stats.sort_stats('cumulative', 'calls')
        stats.print_stats(20)
    else:
        win.run()
    return 0


if __name__ == "__main__":
    # if not options.profile:
    #     # no psyco if profiling
    #     try:
    #         import psyco
    #         psyco.full()
    #         # psyco.log()
    #         # psyco.profile(0.05)
    #         # psyco.runonly()
    #     except ImportError:
    #         pass
    sys.exit(main(options))
