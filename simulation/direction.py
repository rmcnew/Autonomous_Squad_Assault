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
import logging
from enum import Enum
from random import choice

from shared.functions import distance


class Direction(Enum):
    SOUTH = (0, 1)
    SOUTHEAST = (1, 1)
    EAST = (1, 0)
    NORTHEAST = (1, -1)
    NORTH = (0, -1)
    NORTHWEST = (-1, -1)
    WEST = (-1, 0)
    SOUTHWEST = (-1, 1)

    def to_unit_vector(self):
        return self.value

    def to_scaled_vector(self, scalar):
        return self.value[0] * scalar, self.value[1] * scalar

    def to_str(self):
        return self.name

    @classmethod
    def from_str(cls, str):
        return cls[str]

    @classmethod
    def get_random(cls):
        return cls[choice(list(cls.__members__))]

    @classmethod
    def points_to_direction(cls, from_point, to_point):
        logging.debug("points_to_direction: from_point: {}, to_point: {}".format(from_point, to_point))
        x_difference = to_point.x - from_point.x
        y_difference = to_point.y - from_point.y
        magnitude = distance(from_point, to_point)
        logging.debug("x_difference: {}, y_difference: {}, magnitude: {}".format(x_difference, y_difference, magnitude))
        x_scaled = int(round(x_difference / magnitude))
        y_scaled = int(round(y_difference / magnitude))
        logging.debug("x_scaled: {}, y_scaled: {}".format(x_scaled, y_scaled))
        return Direction((x_scaled, y_scaled))
