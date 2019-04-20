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
from math import inf

from shared.constants import *
from shared.functions import distance
from simulation.a_star import find_path
from simulation.abstract_map import AbstractMap
from simulation.direction import Direction
from simulation.drawable import Drawable
from simulation.point import Point


class VisibleMap(AbstractMap):
    def __init__(self, array, x_offset, y_offset):
        AbstractMap.__init__(self)
        self.grid.import_array(array)
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.opfor_locations = {}
        self.warbot_locations = {}
        self.civilian_locations = {}

    def unoffset_point(self, point):
        # logging.debug("Underlying grid dimensions: width={}, height={}. x_offset={}, y_offset={}. Requested point: {}"
        #              .format(self.grid.width, self.grid.height, self.x_offset, self.y_offset, point))
        adjusted_point = point.minus_vector((self.x_offset, self.y_offset))
        # logging.debug("adjusted_point is {}".format(adjusted_point))
        return adjusted_point

    def offset_point(self, point):
        return point.plus_vector((self.x_offset, self.y_offset))

    def is_occupied(self, point):
        adjusted_point = self.unoffset_point(point)
        for drawable in self.grid[adjusted_point]:
            if drawable in AbstractMap.occupied:
                return True
        return False

    def is_navigable(self, point):
        adjusted_point = self.unoffset_point(point)
        drawables = self.grid[adjusted_point]
        return Drawable.WATER not in drawables

    def get_random_location_one_away(self, location):
        return location.plus_direction(Direction.get_random())

    def on_map(self, point):
        adjusted_point = self.unoffset_point(point)
        return 0 <= adjusted_point.x < self.grid.width and 0 <= adjusted_point.y < self.grid.height

    def can_enter(self, point):
        return self.on_map(point) and not self.is_occupied(point)

    def can_enter_route_plan(self, point):
        return self.on_map(point) and self.is_navigable(point)

    def find_closest_top_point(self, objective):
        closest_point = None
        closest_distance = inf  # infinity
        for x in range(self.grid.width):
            current_point = self.offset_point(Point(x, 0))
            current_distance = distance(objective, current_point)
            if current_distance < closest_distance:
                closest_point = current_point
                closest_distance = current_distance
        return closest_point

    def get_line_position(self, team_leader_position, my_position):
        return Point(my_position.x, team_leader_position.y)

    def find_flanking_path(self, objective_location, my_location):
        left_candidate = objective_location.plus_vector(Direction.WEST.to_scaled_vector(WARBOT_VISION_DISTANCE - 2))
        right_candidate = objective_location.plus_vector(Direction.EAST.to_scaled_vector(WARBOT_VISION_DISTANCE - 2))
        left_navigable = self.is_navigable(left_candidate)
        right_navigable = self.is_navigable(right_candidate)
        left_distance = inf  # infinity
        right_distance = inf
        left_path = None
        right_path = None
        if left_navigable:
            left_path = find_path(self, my_location, left_candidate)
            left_distance = len(left_path)
        if right_navigable:
            right_path = find_path(self, my_location, right_candidate)
            right_distance = len(right_path)
        if left_distance < right_distance:
            return left_candidate, left_path
        else:
            return right_candidate, right_path


    def scan(self):
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                current_point = Point(x, y)
                drawables = self.grid[current_point]
                for drawable in drawables:
                    if drawable is Drawable.OBJECTIVE:
                        self.objective_location = self.offset_point(current_point)
                    elif drawable is Drawable.RALLY_POINT:
                        self.rally_point_location = self.offset_point(current_point)
                    elif drawable.name.startswith(WARBOT_PREFIX):
                        self.warbot_locations[drawable.name] = self.offset_point(current_point)
                    elif drawable.name.startswith(OPFOR_PREFIX):
                        self.opfor_locations[drawable.name] = self.offset_point(current_point)
                    elif drawable.name.startswith(CIVILIAN_PREFIX):
                        self.civilian_locations[drawable.name] = self.offset_point(current_point)
