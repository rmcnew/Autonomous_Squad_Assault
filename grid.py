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
from shared import WINDOW_HEIGHT, WINDOW_WIDTH, CELL_SIZE
from drawable import Drawable


class Grid:
    def __init__(self):
        self.width = int(WINDOW_WIDTH / CELL_SIZE)
        self.height = int(WINDOW_HEIGHT / CELL_SIZE)
        # create grid
        self.array = numpy.zeros((self.width, self.height), numpy.int8)

    def __getitem__(self, point):  # point must be a Point; returned value is a list of Drawable
        drawables_present = []
        raw_value = self.array[point.x][point.y]
        print("{} raw value is {}".format(point, raw_value))
        for draw in Drawable:
            if (draw.value & raw_value) > 0:
                drawables_present.append(draw)
        return drawables_present

    def __setitem__(self, point, drawables_list):  # point must be a Point, drawables_list must be a list of Drawable
        raw_value = 0
        for draw in drawables_list:
            raw_value = raw_value | draw.value
        print("Setting {} to {}".format(point, raw_value))
        self.array[point.x][point.y] = raw_value

