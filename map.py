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

# map contains methods to create the elements that make up the simulated
# map where the autonomous infantry squad operates

# generate map:
# - generate objective building
# - put objective inside objective building
# - generate OPFOR near objective building
# - generate rally point
# - generate warbots near rally point
# - place water
# - place mud
# - place rocks
# - place trees
# - place brush
# - place holes

def generate_objective_building(grid):

def create_warbots(grid, count):
    robovacs = []
    robovac_index = 1
    while robovac_index <= count:
        charger_location = get_random_location(grid)
        robovac_location = Point(charger_location.x - 1, charger_location.y)
        if is_clean(grid, charger_location) and is_clean(grid, robovac_location):
            grid[charger_location] = Drawable["CHARGER_" + str(robovac_index)]
            grid[robovac_location] = Drawable["ROBOVAC_" + str(robovac_index)]
            robovacs.append(Robovac(robovac_location, charger_location, "ROBOVAC_" + str(robovac_index), robovac_index))
            robovac_index = robovac_index + 1
    return robovacs


def create_opfor(grid, count):
    dogs = []
    dog_index = 1
    while dog_index <= count:
        dog_location = get_random_location(grid)
        if is_clean(grid, dog_location):
            grid[dog_location] = Drawable["DOG_" + str(dog_index)]
            dogs.append(Dog(dog_location, "DOG_" + str(dog_index)))
            dog_index = dog_index + 1
    return dogs


