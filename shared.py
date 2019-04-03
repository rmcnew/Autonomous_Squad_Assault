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


# shared constants and functions
import random
from colors import Colors
from drawable import Drawable

# frames per second
from point import Point

FPS = 30
SECONDS_PER_MINUTE = 60

# game window
TOP_BUFFER = 0
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 960
BOTTOM_BUFFER = 100

# cell size and game grid
CELL_SIZE = 10
assert WINDOW_WIDTH % CELL_SIZE == 0, "Window width must be a multiple of cell size."
assert WINDOW_HEIGHT % CELL_SIZE == 0, "Window height must be a multiple of cell size."

# background color
BG_COLOR = Colors.BLACK

# game title
AUTO_ASSAULT = 'Autonomous Squad Assault'

# game font
SANS_FONT = 'freesansbold.ttf'

# coordinates
X = 'x'
Y = 'y'

# opfor generation radius away from objective
OPFOR_GENERATE_RADIUS = 6

# warbot generation radius away from rally point
WARBOT_GENERATE_RADIUS = 6

# legend scale factor
LEGEND_SCALE = 19


