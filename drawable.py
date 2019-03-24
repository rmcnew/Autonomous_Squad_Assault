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
    CLEAN = 0
    WALL = 1
    DROPOFF = 2
    FURNITURE = 3
    DOG_1 = 4
    DOG_2 = 5
    DOG_3 = 6
    DOG_4 = 7
    CHARGER_1 = 8
    CHARGER_2 = 9
    CHARGER_3 = 10
    CHARGER_4 = 11
    ROBOVAC_1 = 12
    ROBOVAC_2 = 13
    ROBOVAC_3 = 14
    ROBOVAC_4 = 15
    DIRTY = 16
    FILTHY = 17
    DOG_1_AND_DIRTY = 18
    DOG_2_AND_DIRTY = 19
    DOG_3_AND_DIRTY = 20
    DOG_4_AND_DIRTY = 21
    DOG_1_AND_FILTHY = 22
    DOG_2_AND_FILTHY = 23
    DOG_3_AND_FILTHY = 24
    DOG_4_AND_FILTHY = 25
    ROBOVAC_1_AND_DIRTY = 26
    ROBOVAC_2_AND_DIRTY = 27
    ROBOVAC_3_AND_DIRTY = 28
    ROBOVAC_4_AND_DIRTY = 29
    ROBOVAC_1_AND_FILTHY = 30
    ROBOVAC_2_AND_FILTHY = 31
    ROBOVAC_3_AND_FILTHY = 32
    ROBOVAC_4_AND_FILTHY = 33

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

