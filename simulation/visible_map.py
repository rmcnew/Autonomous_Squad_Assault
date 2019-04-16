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
from shared.constants import *
from simulation.abstract_map import AbstractMap
from simulation.drawable import Drawable
from simulation.point import Point


class VisibleMap(AbstractMap):
    def __init__(self, array, x_offset, y_offset):
        AbstractMap.__init__(self)
        self.grid.import_array(array)
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.opfor_locations = []
        self.warbot_locations = []
        self.civilian_locations = []

    def scan(self):
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                current_point = Point(x, y)
                drawables = self.grid[current_point]
                for drawable in drawables:
                    if drawable.value == Drawable.OBJECTIVE:
                        self.objective_location = current_point
                    elif drawable.value == Drawable.RALLY_POINT:
                        self.rally_point_location = current_point
                    elif drawable.name.startswith(WARBOT_PREFIX):
                        self.warbot_locations.append(current_point)
                    elif drawable.name.startswith(OPFOR_PREFIX):
                        self.opfor_locations.append(current_point)
                    elif drawable.name.startswith(CIVILIAN_PREFIX):
                        self.civilian_locations.append(current_point)
