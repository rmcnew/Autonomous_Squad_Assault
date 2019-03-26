# Autonomous Squad Assault
# Copyright (C) 2019  Richard Scott McNew.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# drawable, a base class for drawable point objects

from enum import IntFlag

from colors import Colors


class Drawable(IntFlag):
    # empty
    EMPTY = 0
    # up to 6 rifle warbots (1 SL, 2 TLs, 2 RFLMs)
    RIFLEBOT_1 = 1
    RIFLEBOT_2 = 2
    RIFLEBOT_3 = 4
    RIFLEBOT_4 = 8
    RIFLEBOT_5 = 16
    RIFLEBOT_6 = 32
    # up to 4 SAW warbots
    SAWBOT_1 = 64
    SAWBOT_2 = 128
    SAWBOT_3 = 256
    SAWBOT_4 = 512
    # up to 4 grenadier warbots
    GRENADEBOT_1 = 1024
    GRENADEBOT_2 = 2048
    GRENADEBOT_3 = 4096
    GRENADEBOT_4 = 8192
    # up to 4 UAV scouts
    UAV_1 = 16384
    UAV_2 = 32768
    UAV_3 = 65536
    UAV_4 = 131072
    # up to 9 enemies
    OPFOR_1 = 262144
    OPFOR_2 = 524288
    OPFOR_3 = 1048576
    OPFOR_4 = 2097152
    OPFOR_5 = 4194304
    OPFOR_6 = 8388608
    OPFOR_7 = 16777216
    OPFOR_8 = 33554432
    OPFOR_9 = 67108864
    # up to 20 civilians
    CIV_1 = 134217728
    CIV_2 = 268435456
    CIV_3 = 536870912
    CIV_4 = 1073741824
    CIV_5 = 2147483648
    CIV_6 = 4294967296
    CIV_7 = 8589934592
    CIV_8 = 17179869184
    CIV_9 = 34359738368
    CIV_10 = 68719476736
    CIV_11 = 137438953472
    CIV_12 = 274877906944
    CIV_13 = 549755813888
    CIV_14 = 1099511627776
    CIV_15 = 2199023255552
    CIV_16 = 4398046511104
    CIV_17 = 8796093022208
    CIV_18 = 17592186044416
    CIV_19 = 35184372088832
    CIV_20 = 70368744177664
    # weapons
    BULLET = 140737488355328
    GRENADE = 281474976710656
    FIRE = 562949953421312
    # terrain
    TREE = 1125899906842624     # slow maneuver, but provides cover and concealment
    WATER = 2251799813685248    # impassable
    ROCK = 4503599627370496     # slow maneuver, some cover
    WALL = 9007199254740992     # impassable
    DOOR = 18014398509481984    # must be opened
    MUD = 36028797018963968     # very slow maneuver, no cover
    HOLE = 72057594037927936    # impassable
    BRUSH = 144115188075855872  # concealment (no cover)
    # 288230376151711744
    # 576460752303423488
    # 1152921504606846976
    # 2305843009213693952
    
    # mission
    RALLY_POINT = 4611686018427387904
    OBJECTIVE = 9223372036854775808



    @property
    def color(self):
        if self.value == 0:
            return Colors.BLACK, Colors.BLACK
        elif self.value == 1:
            return Colors.DARK_GRAY, Colors.DARK_GRAY
        elif self.value == 2:
            return Colors.WHITE, Colors.WHITE
        elif self.value == 3:
            return Colors.PINK, Colors.PINK
        elif self.value == 4 or self.value == 18 or self.value == 22:
            return Colors.YELLOW, Colors.YELLOW
        elif self.value == 5 or self.value == 19 or self.value == 23:
            return Colors.DARK_YELLOW, Colors.DARK_YELLOW
        elif self.value == 6 or self.value == 20 or self.value == 24:
            return Colors.PALE_YELLOW, Colors.PALE_YELLOW
        elif self.value == 7 or self.value == 21 or self.value == 25:
            return Colors.DARKER_YELLOW, Colors.DARKER_YELLOW
        elif self.value == 8:
            return Colors.DARK_RED, Colors.DARK_RED
        elif self.value == 9:
            return Colors.DARK_GREEN, Colors.DARK_GREEN
        elif self.value == 10:
            return Colors.DARK_BLUE, Colors.DARK_BLUE
        elif self.value == 11:
            return Colors.DARK_VIOLET, Colors.DARK_VIOLET
        elif self.value == 12 or self.value == 26 or self.value == 30:
            return Colors.RED, Colors.RED
        elif self.value == 13 or self.value == 27 or self.value == 31:
            return Colors.GREEN, Colors.GREEN
        elif self.value == 14 or self.value == 28 or self.value == 32:
            return Colors.BLUE, Colors.BLUE
        elif self.value == 15 or self.value == 29 or self.value == 33:
            return Colors.VIOLET, Colors.VIOLET
        elif self.value == 16:
            return Colors.BROWN, Colors.BROWN
        elif self.value == 17:
            return Colors.DARK_BROWN, Colors.DARK_BROWN

