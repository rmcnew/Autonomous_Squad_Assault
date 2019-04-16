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

from random import randint

from math import pow, sqrt
from noise import pnoise3

# map contains methods to create the elements that make up the simulated
# map where the autonomous infantry squad operates
from shared.constants import *
from simulation.direction import Direction
from simulation.drawable import Drawable
from simulation.grid import Grid
from simulation.point import Point


class MissionMap:
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

    def __init__(self, grid=Grid()):
        self.grid = grid
        self.objective_location = None
        self.opfor_locations = None
        self.rally_point_location = None
        self.warbot_locations = None
        self.civilian_locations = None

    def populate_map(self, args):
        # initialize the default grid
        self.grid.default_grid()
        # randomly generate terrain
        self.generate_terrain(randint(100, 1000))
        # generate objective and opfor
        self.generate_objective_location()
        self.generate_opfor_locations(args.e)
        # generate rally point and warbots
        self.generate_rally_point_location()
        self.generate_warbot_locations(args.r)
        # generate civilians
        self.generate_civilian_locations(args.c)

    def generate_objective_location(self):
        self.objective_location = self.get_random_upper_location_on_dirt()
        self.grid[self.objective_location] = [Drawable.OBJECTIVE]

    def generate_rally_point_location(self):
        self.rally_point_location = self.get_random_lower_location_on_dirt()
        self.grid[self.rally_point_location] = [Drawable.RALLY_POINT]

    def generate_warbot_locations(self, warbot_count):
        self.warbot_locations = []
        warbot_index = 1
        while warbot_index <= warbot_count:
            # put bots near rally point
            random_point = self.get_random_unoccupied_location_near_point(
                self.rally_point_location,
                WARBOT_GENERATE_RADIUS)
            self.grid[random_point] = [Drawable[WARBOT_PREFIX + str(warbot_index)]]
            self.warbot_locations.append(random_point)
            warbot_index = warbot_index + 1

    def generate_opfor_locations(self, opfor_count):
        self.opfor_locations = []
        opfor_index = 1
        while opfor_index <= opfor_count:
            # put opfor near objective
            random_point = self.get_random_unoccupied_location_near_point(
                self.objective_location,
                OPFOR_GENERATE_RADIUS)
            # print ("random_point: {} for drawable: {}".format(random_point, Drawable["OPFOR_" + str(opfor_index)]))
            self.grid[random_point] = [Drawable[OPFOR_PREFIX + str(opfor_index)]]
            self.opfor_locations.append(random_point)
            opfor_index = opfor_index + 1

    def generate_civilian_locations(self, civilian_count):
        self.civilian_locations = []
        civilian_index = 1
        while civilian_index <= civilian_count:
            random_point = self.get_random_unoccupied_location()
            self.grid[random_point] = [Drawable[CIVILIAN_PREFIX + str(civilian_index)]]
            self.civilian_locations.append(random_point)
            civilian_index = civilian_index + 1

    def generate_terrain(self, seed):
        scale = 100.0
        octaves = 6
        persistence = 0.5
        lacunarity = 2.0
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                current_point = Point(x, y)
                noise = pnoise3(
                    x/scale,
                    y/scale,
                    seed/scale,
                    octaves=octaves,
                    persistence=persistence,
                    lacunarity=lacunarity,
                    repeatx=self.grid.width,
                    repeaty=self.grid.height,
                    base=0)
                if noise < -0.35:
                    self.grid[current_point] = [Drawable.WATER]
                elif noise < -0.20:
                    self.grid[current_point] = [Drawable.MUD]
                elif noise < 0.1:
                    self.grid[current_point] = [Drawable.DIRT]
                elif noise < 0.45:
                    self.grid[current_point] = [Drawable.GRASS]
                elif noise < 0.75:
                    self.grid[current_point] = [Drawable.TREE]
                else:
                    self.grid[current_point] = [Drawable.ROCK]

    def get_random_location(self):
        return Point(randint(0, self.grid.width - 1), randint(0, self.grid.height - 1))

    def get_random_upper_location_on_dirt(self):
        while True:
            random_point = self.get_random_upper_location()
            if Drawable.DIRT in self.grid[random_point]:
                return random_point

    def get_random_upper_location(self):
        return Point(randint(0, self.grid.width - 1), randint(0, (0.25 * self.grid.height) - 1))

    def get_random_lower_location_on_dirt(self):
        while True:
            random_point = self.get_random_lower_location()
            if Drawable.DIRT in self.grid[random_point]:
                return random_point

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

    def get_random_unoccupied_location_near_point(self, point, radius):
        while True:
            random_point = self.get_random_location_near_point(point, radius)
            if not self.is_occupied(random_point):
                return random_point

    def get_random_unoccupied_location(self):
        while True:
            random_point = self.get_random_location()
            if not self.is_occupied(random_point):
                return random_point

    def is_occupied(self, point):
        for drawable in self.grid[point]:
            if drawable in MissionMap.occupied:
                return True
        return False

    def on_map(self, point):
        return 0 <= point.x < self.grid.width and 0 <= point.y < self.grid.height

    def empty(self, point):
        return len(self.grid[point]) == 0

    def distance(self, point_a, point_b):
        return sqrt(pow(point_a.x - point_b.x, 2) + pow(point_a.y - point_b.y, 2))

    def can_enter(self, point):
        return self.on_map(point) and not self.is_occupied(point)

    def normalize_point(self, point):
        point_x = point.x
        if point_x < 0:
            point_x = 0
        elif point_x >= self.grid.width:
            point_x = self.grid.width - 1

        point_y = point.y
        if point_y < 0:
            point_y = 0
        elif point_y >= self.grid.height:
            point_y = self.grid.height - 1
        # only create a new point if needed
        if point_x == point.x and point_y == point.y:
            return point
        else:  # otherwise return the existing point
            return Point(point_x, point_y)

    def get_visible_map_around_point(self, point, distance):
        minus = self.normalize_point(point.plus_vector(Direction.SOUTHWEST.to_scaled_vector(distance)))
        plus = self.normalize_point(point.plus_vector(Direction.NORTHEAST.to_scaled_vector(distance)))
        # print("minus is {}, plus is {}".format(minus, plus))
        return {YOUR_LOCATION: point.to_dict(),
                GRID: self.grid.array[minus.x:plus.x+1, minus.y:plus.y+1].tolist(),
                MIN_X: minus.x,
                MAX_X: (plus.x + 1),
                MIN_Y: minus.y,
                MAX_Y: (plus.y + 1)}

    def get_named_drawable_at_location(self, location, prefix):
        if self.on_map(location):
            for drawable in self.grid[location]:
                if drawable.name.startswith(prefix):
                    return drawable.name
        else:
            return None
