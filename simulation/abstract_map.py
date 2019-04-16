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

from math import pow, sqrt

# map contains methods to create the elements that make up the simulated
# map where the autonomous infantry squad operates
from simulation.drawable import Drawable
from simulation.grid import Grid
from simulation.point import Point


class AbstractMap:
    # hash for quick lookup of occupied grid squares
    occupied = {
        Drawable.WARBOT_1: True,
        Drawable.WARBOT_2: True,
        Drawable.WARBOT_3: True,
        Drawable.WARBOT_4: True,
        Drawable.WARBOT_5: True,
        Drawable.WARBOT_6: True,
        Drawable.WARBOT_7: True,
        Drawable.WARBOT_8: True,
        Drawable.WARBOT_9: True,
        Drawable.WARBOT_10: True,
        Drawable.WARBOT_11: True,
        Drawable.OPFOR_1: True,
        Drawable.OPFOR_2: True,
        Drawable.OPFOR_3: True,
        Drawable.OPFOR_4: True,
        Drawable.OPFOR_5: True,
        Drawable.OPFOR_6: True,
        Drawable.OPFOR_7: True,
        Drawable.OPFOR_8: True,
        Drawable.OPFOR_9: True,
        Drawable.OPFOR_10: True,
        Drawable.OPFOR_11: True,
        Drawable.CIV_1: True,
        Drawable.CIV_2: True,
        Drawable.CIV_3: True,
        Drawable.CIV_4: True,
        Drawable.CIV_5: True,
        Drawable.CIV_6: True,
        Drawable.CIV_7: True,
        Drawable.CIV_8: True,
        Drawable.CIV_9: True,
        Drawable.CIV_10: True,
        Drawable.CIV_11: True,
        Drawable.CIV_12: True,
        Drawable.CIV_13: True,
        Drawable.CIV_14: True,
        Drawable.CIV_15: True,
        Drawable.CIV_16: True,
        Drawable.CIV_17: True,
        Drawable.CIV_18: True,
        Drawable.CIV_19: True,
        Drawable.CIV_20: True,
        Drawable.WATER: True
    }

    def __init__(self):
        self.grid = Grid()
        self.objective_location = None
        self.opfor_locations = None
        self.rally_point_location = None
        self.warbot_locations = None
        self.civilian_locations = None
        self.x_offset = 0
        self.y_offset = 0

    def unoffset_point(self, point):
        return point.minus_vector((self.x_offset, self.y_offset))

    def offset_point(self, point):
        return point.plus_vector((self.x_offset, self.y_offset))

    def is_occupied(self, point):
        adjusted_point = self.unoffset_point(point)
        for drawable in self.grid[adjusted_point]:
            if drawable in AbstractMap.occupied:
                return True
        return False

    def on_map(self, point):
        adjusted_point = self.unoffset_point(point)
        return 0 <= adjusted_point.x < self.grid.width and 0 <= adjusted_point.y < self.grid.height

    def empty(self, point):
        adjusted_point = self.unoffset_point(point)
        return len(self.grid[adjusted_point]) == 0

    def distance(self, point_a, point_b):
        return sqrt(pow(point_a.x - point_b.x, 2) + pow(point_a.y - point_b.y, 2))

    def can_enter(self, point):
        adjusted_point = self.unoffset_point(point)
        return self.on_map(adjusted_point) and not self.is_occupied(adjusted_point)

    def normalize_point(self, point):
        adjusted_point = self.unoffset_point(point)
        point_x = adjusted_point.x
        if point_x < 0:
            point_x = 0
        elif point_x >= self.grid.width:
            point_x = self.grid.width - 1

        point_y = adjusted_point.y
        if point_y < 0:
            point_y = 0
        elif point_y >= self.grid.height:
            point_y = self.grid.height - 1
        # only create a new point if needed
        if point_x == adjusted_point.x and point_y == adjusted_point.y:
            return point
        else:  # otherwise return the existing point
            return self.offset_point(Point(point_x, point_y))

    def get_named_drawable_at_location(self, location, prefix):
        adjusted_location = self.unoffset_point(location)
        if self.on_map(adjusted_location):
            for drawable in self.grid[adjusted_location]:
                if drawable.name.startswith(prefix):
                    return drawable.name
        else:
            return None
