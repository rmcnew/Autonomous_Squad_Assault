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
import numpy
from pygame_constants import WINDOW_HEIGHT, WINDOW_WIDTH, CELL_SIZE
from drawable import Drawable


class Grid:
    def __init__(self):
        self.all_drawables = list(Drawable.__members__)
        self.width = None
        self.height = None
        self.array = None

    def default_grid(self):
        """create the default grid used for the simulation"""
        self.width = int(WINDOW_WIDTH / CELL_SIZE)
        self.height = int(WINDOW_HEIGHT / CELL_SIZE)
        # create grid
        self.array = numpy.zeros((self.width, self.height), numpy.uint64)

    def import_array(self, array):
        """import an array to represent a portion of the map visible to a warbot or opfor"""
        self.array = array
        self.width = array.shape[0]
        self.height = array.shape[1]

    def __getitem__(self, point):  # point must be a Point; returned value is a list of Drawable
        drawables_present = []
        raw_value = int(self.array[point.x][point.y])
        # print("{} raw value is {}".format(point, raw_value))
        for draw in self.all_drawables:
            if (Drawable[draw].value & raw_value) > 0:
                drawables_present.append(Drawable[draw])
        return drawables_present

    def __setitem__(self, point, drawables_list):  # point must be a Point, drawables_list must be a list of Drawable
        raw_value = 0
        for draw in drawables_list:
            raw_value = raw_value | draw.value
            # print("raw_value is {}".format(raw_value))
        # print("Setting {} to {}".format(point, raw_value))
        self.array[point.x][point.y] = raw_value

