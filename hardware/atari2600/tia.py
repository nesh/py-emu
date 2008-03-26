from pyglet import image

from hardware.device import Device
from tia_tables import *

P0_BIT = 0x01 # Bit for Player 0
M0_BIT = 0x02 # Bit for Missle 0
P1_BIT = 0x04 # Bit for Player 1
M1_BIT = 0x08 # Bit for Missle 1
BL_BIT = 0x10 # Bit for Ball
PF_BIT = 0x20 # Bit for Playfield
SCORE_BIT = 0x40 # Bit for Playfield score mode
PRIORITY_BIT = 0x080 # Bit for Playfield priority
HBLANK = 68

class TIA(Device):
    def __init__(self):
        super(TIA, self).__init__()
        self.regs = [0] * 0x3D
        self.bit_enabled = [True] * 6
        self.disabled_mask_table = [0] * 640

        # init tables
        self._init_tables()

        # Init stats counters
        self.framecounter = 0

        self.AUDV0 = 0
        self.AUDV1 = 0
        self.AUDF0 = 0
        self.AUDF1 = 0
        self.AUDC0 = 0
        self.AUDC1 = 0

    def reset(self):
        self.regs = [0] * 0x3D # clear regs
        self.frame_reset()

    def frame_reset(self):
        pass

    def _init_tables(self):
        self.compute_ball_mask_table()
        self.compute_collision_table()
        self.compute_missile_mask_table()
        self.compute_player_mask_table()
        self.compute_player_position_reset_when_table()
        self.compute_player_reflect_table()
        self.compute_playfield_mask_table()

    def compute_player_position_reset_when_table(self):
        self.player_position_reset_when_table = [[[0] * 160] * 160] * 8 #[8][160][160]

        for mode in range(8):
            for oldx in range(160):
                # Set everything to 0 for non-delay/non-display section
                #for newx in range(160):
                #    ourPlayerPositionResetWhenTable[mode][oldx][newx] = 0
                # Now, we'll set the entries for non-delay/non-display section
                for newx in range(160 + 72 + 5):
                    if mode == 0x00:
                        if (newx >= oldx) & (newx < (oldx + 4)):
                            ourPlayerPositionResetWhenTable[mode][oldx][newx % 160] = -1
                        if (newx >= oldx + 4) & (newx < (oldx + 4 + 8)):
                            ourPlayerPositionResetWhenTable[mode][oldx][newx % 160] = 1
                    elif mode == 0x01:
                        if (newx >= oldx) & (newx < (oldx + 4)):
                            ourPlayerPositionResetWhenTable[mode][oldx][newx % 160] = -1
                        elif (newx >= (oldx + 16)) & (newx < (oldx + 16 + 4)):
                            ourPlayerPositionResetWhenTable[mode][oldx][newx % 160] = -1
                        if (newx >= oldx + 4) & (newx < (oldx + 4 + 8)):
                            ourPlayerPositionResetWhenTable[mode][oldx][newx % 160] = 1
                        elif (newx >= oldx + 16 + 4) & (newx < (oldx + 16 + 4 + 8)):
                            ourPlayerPositionResetWhenTable[mode][oldx][newx % 160] = 1

    def compute_player_mask_table(self):
        self.player_mask_table = [[[[0x00] * 320] * 8] * 2] * 4 #[4][2][8][320]

        for enable in range(2):
            for mode in range(8):
                for x in range(160 + 72):
                    if mode == 0x00:
                        if (enable == 0) and (x >= 0) and (x < 8):
                            self.player_mask_table[0][enable][mode][x % 160] = 0x80 >> x
                    elif mode == 0x01:
                        if (enable == 0) and (x >= 0) and (x < 8):
                            self.player_mask_table[0][enable][mode][x % 160] = 0x80 >> x
                        elif ((x - 16) >= 0) and ((x - 16) < 8):
                            self.player_mask_table[0][enable][mode][x % 160] = 0x80 >> (x - 16)
                    elif mode == 0x02:
                        if (enable == 0) and (x >= 0) and (x < 8):
                            self.player_mask_table[0][enable][mode][x % 160] = 0x80 >> x
                        elif ((x - 32) >= 0) and ((x - 32) < 8):
                            self.player_mask_table[0][enable][mode][x % 160] = 0x80 >> (x - 32)
                    elif mode == 0x03:
                        if (enable == 0) and (x >= 0) and (x < 8):
                            self.player_mask_table[0][enable][mode][x % 160] = 0x80 >> x
                        elif ((x - 16) >= 0) and ((x - 16) < 8):
                            self.player_mask_table[0][enable][mode][x % 160] = 0x80 >> (x - 16)
                        elif ((x - 32) >= 0) and ((x - 32) < 8):
                            self.player_mask_table[0][enable][mode][x % 160] = 0x80 >> (x - 32)
                    elif mode == 0x04:
                        if (enable == 0) and (x >= 0) and (x < 8):
                            self.player_mask_table[0][enable][mode][x % 160] = 0x80 >> x
                        elif ((x - 64) >= 0) and ((x - 64) < 8):
                            self.player_mask_table[0][enable][mode][x % 160] = 0x80 >> (x - 64)
                    elif mode == 0x05:
                        # For some reason in double size mode the player's output
                        # is delayed by one pixel thus we use > instead of >=
                        if (enable == 0) and (x > 0) and (x <= 16):
                                self.player_mask_table[0][enable][mode][x % 160] = 0x80 >> ((x - 1)/2)
                    elif mode == 0x06:
                        if (enable == 0) and (x >= 0) and (x < 8):
                            self.player_mask_table[0][enable][mode][x % 160] = 0x80 >> x
                        elif ((x - 32) >= 0) and ((x - 32) < 8):
                            self.player_mask_table[0][enable][mode][x % 160] = 0x80 >> (x - 32)
                        elif ((x - 64) >= 0) and ((x - 64) < 8):
                            self.player_mask_table[0][enable][mode][x % 160] = 0x80 >> (x - 64)
                    elif mode == 0x07:
                        # For some reason in quad size mode the player's output
                        # is delayed by one pixel thus we use > instead of >=
                        if (enable == 0) and (x > 0) and (x <= 32):
                            self.player_mask_table[0][enable][mode][x % 160] = 0x80 >> ((x - 1)/4)
                # Copy data into wrap-around area
                for x in range(160):
                    self.player_mask_table[0][enable][mode][x + 160] = \
                    self.player_mask_table[0][enable][mode][x]
        # Now, copy data for alignments of 1, 2 and 3
        for align in range(1, 4):
            for enable in range(2):
                for mode in range(8):
                    for x in range(320):
                        self.player_mask_table[align][enable][mode][x] = \
                        self.player_mask_table[0][enable][mode][(x + 320 - align) % 320];


    def compute_missile_mask_table(self):
        self.missile_mask_table = [[[[False] * 320] * 4] * 8] * 4 #[4][8][4][320]

        for number in range(8):
            for size in range(4):
                for x in range(160 + 72):
                    # Only one copy of the missile
                    if number in (0x00, 0x05, 0x07): #(number == 0x00) or (number == 0x05) or (number == 0x07):
                        if (x >= 0) and (x < (1 << size)):
                            self.missile_mask_table[0][number][size][x % 160] = True
                    # Two copies - close
                    elif number == 0x01:
                        if (x >= 0) and (x < (1 << size)):
                            self.missile_mask_table[0][number][size][x % 160] = True
                        elif ((x - 16) >= 0) and ((x - 16) < (1 << size)):
                            self.missile_mask_table[0][number][size][x % 160] = True
                    # Two copies - medium
                    elif number == 0x02:
                        if (x >= 0) and (x < (1 << size)):
                            self.missile_mask_table[0][number][size][x % 160] = True
                        elif ((x - 32) >= 0) and ((x - 32) < (1 << size)):
                            self.missile_mask_table[0][number][size][x % 160] = True
                    # Three copies - close
                    elif number == 0x03:
                        if (x >= 0) and (x < (1 << size)):
                            self.missile_mask_table[0][number][size][x % 160] = True
                        elif ((x - 16) >= 0) and ((x - 16) < (1 << size)):
                            self.missile_mask_table[0][number][size][x % 160] = True
                        elif ((x - 32) >= 0) and ((x - 32) < (1 << size)):
                            self.missile_mask_table[0][number][size][x % 160] = True
                    # Two copies - wide
                    elif number == 0x04:
                        if (x >= 0) and (x < (1 << size)):
                            self.missile_mask_table[0][number][size][x % 160] = True
                        elif ((x - 64) >= 0) and ((x - 64) < (1 << size)):
                            self.missile_mask_table[0][number][size][x % 160] = True
                    # Three copies - medium
                    elif number == 0x06:
                        if (x >= 0) and (x < (1 << size)):
                            self.missile_mask_table[0][number][size][x % 160] = True
                        elif ((x - 32) >= 0) and ((x - 32) < (1 << size)):
                            self.missile_mask_table[0][number][size][x % 160] = True
                        elif ((x - 64) >= 0) and ((x - 64) < (1 << size)):
                            self.missile_mask_table[0][number][size][x % 160] = True

                # Copy data into wrap-around area
                for x in range(160):
                    self.missile_mask_table[0][number][size][x + 160] = \
                    self.missile_mask_table[0][number][size][x]

        # Now, copy data for alignments of 1, 2 and 3
        for align in range(1, 4):
            for number in range(8):
                for size in range(4):
                    for x in range(320):
                        self.missile_mask_table[align][number][size][x] = \
                        self.missile_mask_table[0][number][size][(x + 320 - align) % 320]

    def compute_collision_table(self):
        self.collision_table = [0] * 64

        for i in range(64):
            if (i & M0_BIT) and (i & P1_BIT):    # M0-P1
                self.collision_table[i] |= 0x0001

            if (i & M0_BIT) and (i & P0_BIT):    # M0-P0
                self.collision_table[i] |= 0x0002

            if (i & M1_BIT) and (i & P0_BIT):    # M1-P0
                self.collision_table[i] |= 0x0004

            if (i & M1_BIT) and (i & P1_BIT):   # M1-P1
                self.collision_table[i] |= 0x0008

            if (i & P0_BIT) and (i & PF_BIT):   # P0-PF
                self.collision_table[i] |= 0x0010

            if (i & P0_BIT) and (i & BL_BIT):   # P0-BL
                self.collision_table[i] |= 0x0020

            if (i & P1_BIT) and (i & PF_BIT):   # P1-PF
                self.collision_table[i] |= 0x0040

            if (i & P1_BIT) and (i & BL_BIT):   # P1-BL
                self.collision_table[i] |= 0x0080

            if (i & M0_BIT) and (i & PF_BIT):   # M0-PF
                self.collision_table[i] |= 0x0100

            if (i & M0_BIT) and (i & BL_BIT):   # M0-BL
                self.collision_table[i] |= 0x0200

            if (i & M1_BIT) and (i & PF_BIT):   # M1-PF
                self.collision_table[i] |= 0x0400

            if (i & M1_BIT) and (i & BL_BIT):   # M1-BL
                self.collision_table[i] |= 0x0800

            if (i & BL_BIT) and (i & PF_BIT):   # BL-PF
                self.collision_table[i] |= 0x1000

            if (i & P0_BIT) and (i & P1_BIT):   # P0-P1
                self.collision_table[i] |= 0x2000

            if (i & M0_BIT) and (i & M1_BIT):   # M0-M1
                self.collision_table[i] |= 0x4000
        self.collision_table = tuple(self.collision_table)

    def compute_ball_mask_table(self):
        self.ball_mask_table = [[[False] * 320] * 4] * 4 #[4][4][320]
        for size in range(4):
            for x in range(160):
                self.ball_mask_table[0][size][x % 160] = False
            for x in range(160 + 8):
                if (x >= 0) and (x < (1 << size)):
                    self.ball_mask_table[0][size][x + 160] = self.ball_mask_table[0][size][x]
        for align in range(1, 4):
            for size in range(4):
                for x in range(320):
                    self.ball_mask_table[align][size][x] = self.ball_mask_table[0][size][(x + 320 - align) % 320]
        # convert all to touples (RO)
        for size in range(4):
            for align in range(4):
                self.ball_mask_table[size][align] = tuple(self.ball_mask_table[size][align])
        for size in range(4):
            self.ball_mask_table[size] = tuple(self.ball_mask_table[size])
        self.ball_mask_table = tuple(self.ball_mask_table)
