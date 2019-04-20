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
from random import randint

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

    def get_random_location_near_point(self, point, radius):
        while True:
            random_direction = Direction.get_random()
            random_radius = randint(2, radius + 1)
            scaled_vector = random_direction.to_scaled_vector(random_radius)
            random_point = point.plus_vector(scaled_vector)
            if self.on_map(random_point):
                return random_point

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
        if self.on_map(objective):
            return objective
        for x in range(self.grid.width):
            current_point = self.offset_point(Point(x, 0))
            current_distance = distance(objective, current_point)
            if current_distance < closest_distance:
                closest_point = current_point
                closest_distance = current_distance
        return closest_point

    def find_closest_left_point(self, waypoint):
        closest_point = None
        closest_distance = inf  # infinity
        if self.on_map(waypoint):
            return waypoint
        for y in range(self.grid.height):
            current_point = self.offset_point(Point(0, y))
            current_distance = distance(waypoint, current_point)
            if current_distance < closest_distance:
                closest_point = current_point
                closest_distance = current_distance
        return closest_point

    def find_closest_right_point(self, waypoint):
        closest_point = None
        closest_distance = inf  # infinity
        if self.on_map(waypoint):
            return waypoint
        for y in range(self.grid.height):
            current_point = self.offset_point(Point(self.grid.width - 1, y))
            current_distance = distance(waypoint, current_point)
            if current_distance < closest_distance:
                closest_point = current_point
                closest_distance = current_distance
        return closest_point

    def is_left_of_me(self, point_of_interest, my_location):
        return point_of_interest.x < my_location.x

    def is_right_of_me(self, point_of_interest, my_location):
        return point_of_interest.x > my_location.x

    def get_line_position(self, team_leader_position, my_position):
        return Point(my_position.x, team_leader_position.y)

    def find_flanking_waypoint(self, objective_location, my_location):
        left_candidate = objective_location.plus_vector(Direction.WEST.to_scaled_vector(WARBOT_VISION_DISTANCE - 4))
        left_candidate_waypoint = Point(left_candidate.x, my_location.y)
        logging.debug("left_candidate is: {}, left_candidate_waypoint is: {}"
                      .format(left_candidate, left_candidate_waypoint))
        right_candidate = objective_location.plus_vector(Direction.EAST.to_scaled_vector(WARBOT_VISION_DISTANCE - 4))
        right_candidate_waypoint = Point(right_candidate.x, my_location.y)
        logging.debug("right_candidate is: {}, right_candidate_waypoint is: {}"
                      .format(right_candidate, right_candidate_waypoint))
        left_waypoint_navigable = self.can_enter_route_plan(left_candidate_waypoint)
        logging.debug("left_waypoint_navigable is: {}".format(left_waypoint_navigable))
        right_waypoint_navigable = self.can_enter_route_plan(right_candidate_waypoint)
        logging.debug("right_waypoint_navigable is: {}".format(right_waypoint_navigable))
        left_distance = inf  # infinity
        right_distance = inf
        if left_waypoint_navigable:
            logging.debug("Calculating left_distance . . .")
            left_distance = distance(my_location, left_candidate_waypoint)
            logging.debug("left_distance: {}".format(left_distance))
        if right_waypoint_navigable:
            logging.debug("Calculating right_path and right_distance . . .")
            right_distance = distance(my_location, right_candidate_waypoint)
            logging.debug("right_distance: {}".format(right_distance))
        if left_distance < right_distance:
            logging.debug("Selecting left flanking candidate")
            return left_candidate, left_candidate_waypoint
        else:
            logging.debug("Selecting right flanking candidate")
            return right_candidate, right_candidate_waypoint

    def find_flanking_path(self, objective_location, my_location):
        preferred_candidate = Point(my_location.x, objective_location.y)
        candidate = preferred_candidate
        logging.debug("candidate is: {}".format(candidate))
        navigable = self.can_enter_route_plan(candidate)
        logging.debug("navigable is: {}".format(navigable))
        while not navigable:
            logging.debug("candidate is not navigable, selecting alternate point")
            candidate = self.get_random_location_near_point(preferred_candidate, 3)
            logging.debug("alternate candidate is: {}".format(candidate))
            navigable = self.can_enter_route_plan(candidate)
            logging.debug("alternate navigable is: {}".format(navigable))
        logging.debug("Calculating path . . .")
        path = find_path(self, my_location, candidate)
        logging.debug("path is: {}".format(path))
        return candidate, path

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
