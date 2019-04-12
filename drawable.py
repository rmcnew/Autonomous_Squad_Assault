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

from enum import Enum

from colors import Colors


class Drawable(Enum):
    # empty
    EMPTY = 0
    # up to 11 warbots (1 SL, 2 TLs, 8 RFLMs)
    WARBOT_1 = 1
    WARBOT_2 = 2
    WARBOT_3 = 4
    WARBOT_4 = 8
    WARBOT_5 = 16
    WARBOT_6 = 32
    WARBOT_7 = 64
    WARBOT_8 = 128
    WARBOT_9 = 256
    WARBOT_10 = 512
    WARBOT_11 = 1024
    # up to 11 enemies
    OPFOR_1 = 2048
    OPFOR_2 = 4096
    OPFOR_3 = 8192
    OPFOR_4 = 16384
    OPFOR_5 = 32768
    OPFOR_6 = 65536
    OPFOR_7 = 131072
    OPFOR_8 = 262144
    OPFOR_9 = 524288
    OPFOR_10 = 1048576
    OPFOR_11 = 2097152
    # up to 20 civilians
    CIV_1 = 4194304
    CIV_2 = 8388608
    CIV_3 = 16777216
    CIV_4 = 33554432
    CIV_5 = 67108864
    CIV_6 = 134217728
    CIV_7 = 268435456
    CIV_8 = 536870912
    CIV_9 = 1073741824
    CIV_10 = 2147483648
    CIV_11 = 4294967296
    CIV_12 = 8589934592
    CIV_13 = 17179869184
    CIV_14 = 34359738368
    CIV_15 = 68719476736
    CIV_16 = 137438953472
    CIV_17 = 274877906944
    CIV_18 = 549755813888
    CIV_19 = 1099511627776
    CIV_20 = 2199023255552
    # weapons
    BULLET = 4398046511104
    GRENADE = 8796093022208
    FIRE = 17592186044416
    # terrain
    WATER = 35184372088832
    MUD = 70368744177664
    DIRT = 140737488355328
    GRASS = 281474976710656
    TREE = 562949953421312
    ROCK = 1125899906842624
    DOOR = 2251799813685248
    WALL = 4503599627370496
    # Not used
    # 9007199254740992
    # 18014398509481984
    # 36028797018963968
    # 72057594037927936
    # 144115188075855872
    # 288230376151711744
    # 576460752303423488
    # 1152921504606846976
    # 2305843009213693952

    # mission
    RALLY_POINT = 4611686018427387904
    OBJECTIVE = 9223372036854775808

    @property
    def color(self):
        if self.name == "EMPTY":
            return Colors.BLACK, Colors.BLACK
        elif self.name.startswith("WARBOT"):
            return Colors.PURPLE, Colors.PURPLE
        elif self.name.startswith("OPFOR"):
            return Colors.RED, Colors.RED
        elif self.name.startswith("CIV"):
            return Colors.PINK, Colors.PINK
        elif self.name == "BULLET":
            return Colors.PALE_ORANGE, Colors.PALE_ORANGE
        elif self.name == "GRENADE":
            return Colors.ORANGE, Colors.ORANGE
        elif self.name == "FIRE":
            return Colors.DARK_RED, Colors.DARK_RED
        elif self.name == "TREE":
            return Colors.FOREST_GREEN, Colors.FOREST_GREEN
        elif self.name == "WATER":
            return Colors.BLUE, Colors.BLUE
        elif self.name == "ROCK":
            return Colors.DARK_GRAY, Colors.DARK_GRAY
        elif self.name == "WALL":
            return Colors.GRAY, Colors.GRAY
        elif self.name == "DOOR":
            return Colors.WHITE, Colors.WHITE
        elif self.name == "DIRT":
            return Colors.BROWN, Colors.BROWN
        elif self.name == "MUD":
            return Colors.DARK_BROWN, Colors.DARK_BROWN
        elif self.name == "GRASS":
            return Colors.BRUSH_GREEN, Colors.BRUSH_GREEN
        elif self.name == "RALLY_POINT":
            return Colors.GOLD, Colors.GOLD
        elif self.name == "OBJECTIVE":
            return Colors.VIOLET, Colors.VIOLET

