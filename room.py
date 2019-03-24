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
from robovac import Robovac
from dog import Dog

# room contains methods to create the elements that make up the simulated 
# room where the robovacs operate


# fill a wall block
def fill_wall_block(block, grid):
    start_x = block.x * int(grid.width / 4)
    stop_x = (block.x + 1) * int(grid.width / 4)
    start_y = block.y * int(grid.height / 4)
    stop_y = (block.y + 1) * int(grid.height / 4)
    for x in range(start_x, stop_x):
        for y in range(start_y, stop_y):
            grid.array[x][y] = Drawable.WALL.value


# create the walls
def create_walls(grid):
    # create a border wall so robovacs stay inside the window
    for x in range(0, grid.width):
        grid.array[x][0] = Drawable.WALL.value
        grid.array[x][grid.height - 1] = Drawable.WALL.value
    for y in range(0, grid.height):
        grid.array[0][y] = Drawable.WALL.value
        grid.array[grid.width - 1][y] = Drawable.WALL.value
    # randomly generate some wall sections to give the room an unusual shape:
    # 1) divide the room into a 4 x 4 grid
    # 2) randomly choose two blocks and fill them with wall
    first_block = get_random_block()
    # print("first block: {}".format(first_block))
    second_block = get_random_block()
    while (first_block.x == second_block.x and first_block.y == second_block.y) or \
            (fabs(first_block.x - second_block.x) == 1 and fabs(first_block.y - second_block.y) == 1):
        second_block = get_random_block()
    # print("second_block: {}".format(second_block))
    fill_wall_block(first_block, grid)
    fill_wall_block(second_block, grid)


# fill a dropoff block
def fill_dropoff_block(grid):
    block = get_random_location(grid)
    start_x = block.x
    start_y = block.y
    stop_x = min(block.x + DROPOFF_SIZE, grid.width)
    stop_y = min(block.y + DROPOFF_SIZE, grid.height)
    clear = True
    for x in range(start_x, stop_x):
        for y in range(start_y, stop_y):
            if x <= grid.width and y <= grid.height and grid.array[x][y] != Drawable.CLEAN.value:
                clear = False
    if clear:
        for x in range(start_x, stop_x):
            for y in range(start_y, stop_y):
                grid.array[x][y] = Drawable.DROPOFF.value
    return clear


# create the dropoffs
def create_dropoffs(grid):
    dropoffs_left = DROPOFF_COUNT
    while dropoffs_left > 0:
        if fill_dropoff_block(grid):
            dropoffs_left = dropoffs_left - 1


# fill a furniture block
def fill_furniture_block(grid):
    block = get_random_location(grid)
    start_x = block.x
    start_y = block.y
    stop_x = min(block.x + FURNITURE_SIZE, grid.width)
    stop_y = min(block.y + FURNITURE_SIZE, grid.height)
    clear = True
    for x in range(start_x, stop_x):
        for y in range(start_y, stop_y):
            if x <= grid.width and y <= grid.height and grid.array[x][y] != Drawable.CLEAN.value:
                clear = False
    if clear:
        for x in range(start_x, stop_x):
            for y in range(start_y, stop_y):
                grid.array[x][y] = Drawable.FURNITURE.value
    return clear


# create the furniture
def create_furniture(grid):
    furniture_left = FURNITURE_COUNT
    while furniture_left > 0:
        if fill_furniture_block(grid):
            furniture_left = furniture_left - 1


# create robovacs and chargers
def create_robovacs(grid, count):
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


def create_dogs(grid, count):
    dogs = []
    dog_index = 1
    while dog_index <= count:
        dog_location = get_random_location(grid)
        if is_clean(grid, dog_location):
            grid[dog_location] = Drawable["DOG_" + str(dog_index)]
            dogs.append(Dog(dog_location, "DOG_" + str(dog_index)))
            dog_index = dog_index + 1
    return dogs


def create_dirt(grid, dirty, filthy):
    dirt = []
    filth = []
    dirt_index = 1
    dirt_count = dirty
    while dirt_index <= dirt_count:
        dirt_location = get_random_location(grid)
        if is_clean(grid, dirt_location):
            grid[dirt_location] = Drawable["DIRTY"]
            dirt.append(dirt_location)
            dirt_index = dirt_index + 1
    filth_index = 1
    filth_count = filthy
    while filth_index <= filth_count:
        filth_location = get_random_location(grid)
        if is_clean(grid, filth_location):
            grid[filth_location] = Drawable["FILTHY"]
            filth.append(filth_location)
            filth_index = filth_index + 1
    return dirt, filth
