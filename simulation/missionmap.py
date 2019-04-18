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

from noise import pnoise3

# map contains methods to create the elements that make up the simulated
# map where the autonomous infantry squad operates
from shared.constants import *
from simulation.abstract_map import AbstractMap
from simulation.direction import Direction
from simulation.drawable import Drawable
from simulation.point import Point


class MissionMap(AbstractMap):
    def __init__(self, args):
        AbstractMap.__init__(self)
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
        self.warbot_locations = {}
        warbot_index = 1
        while warbot_index <= warbot_count:
            # put bots near rally point
            random_point = self.get_random_unoccupied_location_near_point(
                self.rally_point_location,
                WARBOT_GENERATE_RADIUS)
            warbot_name = WARBOT_PREFIX + str(warbot_index)
            self.grid[random_point] = [Drawable[warbot_name], Drawable.DIRT]
            self.warbot_locations[warbot_name] = random_point
            warbot_index = warbot_index + 1

    def generate_opfor_locations(self, opfor_count):
        self.opfor_locations = {}
        opfor_index = 1
        while opfor_index <= opfor_count:
            # put opfor near objective
            random_point = self.get_random_unoccupied_location_near_point(
                self.objective_location,
                OPFOR_GENERATE_RADIUS)
            # print ("random_point: {} for drawable: {}".format(random_point, Drawable["OPFOR_" + str(opfor_index)]))
            opfor_name = OPFOR_PREFIX + str(opfor_index)
            self.grid[random_point] = [Drawable[opfor_name], Drawable.DIRT]
            self.opfor_locations[opfor_name] = random_point
            opfor_index = opfor_index + 1

    def generate_civilian_locations(self, civilian_count):
        self.civilian_locations = {}
        civilian_index = 1
        while civilian_index <= civilian_count:
            random_point = self.get_random_unoccupied_location()
            civilian_name = CIVILIAN_PREFIX + str(civilian_index)
            self.grid[random_point] = [Drawable[civilian_name], Drawable.DIRT]
            self.civilian_locations[civilian_name] = random_point
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

    def get_visible_map_around_point(self, point, distance):
        minus = self.normalize_point(point.plus_vector(Direction.SOUTHWEST.to_scaled_vector(distance)))
        plus = self.normalize_point(point.plus_vector(Direction.NORTHEAST.to_scaled_vector(distance)))
        # print("minus is {}, plus is {}".format(minus, plus))
        return {YOUR_LOCATION: point.to_dict(),
                GRID: self.grid.array[minus.x:plus.x+1, minus.y:plus.y+1].tolist(),
                MIN_X: minus.x,
                MIN_Y: minus.y}

    def move_agent(self, agent_name, new_location):
        logging.debug("Moving {} to new location: {}".format(agent_name, new_location))
        if agent_name.startswith(WARBOT_PREFIX):
            agent_location = self.warbot_locations[agent_name]
            logging.debug("{} current location is {}".format(agent_name, agent_location))
            if not self.is_occupied(new_location):
                self.warbot_locations[agent_name] = new_location
                # get the current location and remove the warbot
                logging.debug("{} currently contains: {}".format(agent_location, self.grid[agent_location]))
                drawables_at_agent_location = self.grid[agent_location]
                drawables_at_agent_location.remove(Drawable[agent_name])
                self.grid[agent_location] = drawables_at_agent_location
                logging.debug("{} now contains: {}".format(agent_location, self.grid[agent_location]))
                # get the new location and add the warbot
                logging.debug("{} currently contains: {}".format(new_location, self.grid[new_location]))
                drawables_at_new_location = self.grid[new_location]
                drawables_at_new_location.insert(0, Drawable[agent_name])
                self.grid[new_location] = drawables_at_new_location
                logging.debug("{} now contains: {}".format(new_location, self.grid[new_location]))

        elif agent_name.startswith(OPFOR_PREFIX):
            agent_location = self.opfor_locations[agent_name]
            if not self.is_occupied(new_location):
                self.opfor_locations[agent_name] = new_location
                drawables_at_agent_location = self.grid[agent_location]
                if len(drawables_at_agent_location) > 0:
                    drawables_at_agent_location.remove(Drawable[agent_name])
                self.grid[new_location] = self.grid[new_location].append(Drawable[agent_name])
