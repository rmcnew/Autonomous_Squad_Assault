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
TOP_BUFFER = 50
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


# legend scale factor
LEGEND_SCALE = 19


def get_random_location(grid):
    return Point(random.randint(0, grid.width - 1), random.randint(0, grid.height - 1))


def get_random_upper_location(grid):
    return Point(random.randint(0, grid.width - 1), random.randint((grid.height/2), (3/4 * grid.height)))


def get_random_lower_location(grid):
    return Point(random.randint(0, grid.width - 1), random.randint(0, (grid.height/2) - 1))


def get_random_block():
    return Point(random.randint(0, 3), random.randint(0, 3))


def on_grid(grid, point):
    return 0 <= point.x <= grid.width and 0 <= point.y <= grid.height


def can_enter(grid, point):
    return on_grid(grid, point)
    # other checks go here