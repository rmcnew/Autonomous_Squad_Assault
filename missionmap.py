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

from math import fabs

from shared import *
from drawable import Drawable
from direction import Direction
from random import randint
# map contains methods to create the elements that make up the simulated
# map where the autonomous infantry squad operates


class MissionMap:

    def __init__(self, grid, args):
        self.grid = grid
        self.objective_location = self.generate_objective()
        self.opfor = self.generate_opfor(args.e)
        self.rally_point_location = self.generate_rally_point()
        self.warbots = self.generate_warbots(args.r, args.s, args.g, args.u)
        # - place water
        # - place mud
        # - place rocks
        # - place trees
        # - place brush
        # - place holes
        # - place civilians

    def generate_objective(self):
        objective_location = self.get_random_upper_location()
        self.grid[objective_location] = [Drawable.OBJECTIVE]
        return objective_location

    def generate_rally_point(self):
        rally_point_location = self.get_random_lower_location()
        self.grid[rally_point_location] = [Drawable.RALLY_POINT]
        return rally_point_location

    def generate_warbots(self, riflebot_count, sawbot_count, grenadebot_count, scoutbot_count):
        warbots = []
        warbot_index = 1
        while warbot_index <= riflebot_count:
            # put warbot near rally point
            warbot_index = warbot_index + 1
        return warbots

    def generate_opfor(self, count):
        opfor = []
        opfor_index = 1
        while opfor_index <= count:
            # put opfor near objective
            random_point = self.get_random_location_near_point(self.objective_location, OPFOR_GENERATE_RADIUS)
            # print ("random_point: {} for drawable: {}".format(random_point, Drawable["OPFOR_" + str(opfor_index)]))
            self.grid[random_point] = [Drawable["OPFOR_" + str(opfor_index)]]
            opfor_index = opfor_index + 1
        return opfor

    def get_random_location(self):
        return Point(randint(0, self.grid.width - 1), randint(0, self.grid.height - 1))

    def get_random_upper_location(self):
        return Point(randint(0, self.grid.width - 1), randint(0, (0.25 * self.grid.height) - 1))

    def get_random_lower_location(self):
        return Point(randint(0, self.grid.width - 1), randint((0.75 * self.grid.height),  self.grid.height - 1))

    def get_random_location_near_point(self, point, radius):
        while True:
            random_direction = Direction.get_random()
            random_radius = randint(2, radius + 1)
            scaled_vector = random_direction.to_scaled_vector(random_radius)
            random_point = point.plus_vector(scaled_vector)
            if self.on_map(random_point):
                return random_point

    def get_random_block(self):
        return Point(randint(0, 3), randint(0, 3))

    def on_map(self, point):
        return 0 <= point.x <= self.grid.width and 0 <= point.y <= self.grid.height

    def can_enter(self, point):
        return self.on_map(point)
        # other checks go here
