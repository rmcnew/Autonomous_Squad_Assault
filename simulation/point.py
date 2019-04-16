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
from shared.constants import X, Y

class Point:
    """Represents a point on the grid"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "Point({}, {})".format(self.x, self.y)

    def __repr__(self):
        return "Point({}, {})".format(self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def to_dict(self):
        return {X: self.x, Y: self.y}

    def plus_direction(self, direction):
        return Point(self.x + direction.value[0], self.y + direction.value[1])

    def minus_direction(self, direction):
        return Point(self.x - direction.value[0], self.y - direction.value[1])

    def plus_vector(self, vector):
        return Point(self.x + vector[0], self.y + vector[1])

    def minus_vector(self, vector):
        return Point(self.x - vector[0], self.y - vector[1])
