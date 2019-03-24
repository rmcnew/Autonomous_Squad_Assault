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

# A* path finding
from math import fabs

from direction import Direction
from shared import *


# shared constants and functions
def manhattan_distance(from_location, to_location):
    return fabs(from_location.x - to_location.x) + fabs(from_location.y - to_location.y)


START = None
END = None


def get_enterable_adjacent_locations(grid, location):
    locations = []
    for direction in Direction:
        candidate = location.plus(direction)
        if can_enter(grid, candidate):
            locations.append(candidate)
    return locations


# use A* algorithm to find a path 
def find_path(grid, from_location, to_location):
    from_node = Node(from_location, 0, 0, START)
    to_node = Node(to_location, 0, 0, END)

    # open_list would be better as a priority queue, but
    # python's heapq does not easily work with Node objects
    open_list = []
    closed_list = []

    open_list.append(from_node)

    while len(open_list) > 0:
        current_node = open_list[0]
        current_index = 0
        # find the lowest cost node in open_list
        for index, node in enumerate(open_list):
            if node.cost < current_node.cost:
                current_node = node
                current_index = index

        # move lowest cost node from open list to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # if we have reached the goal, return the path
        if current_node == to_node:
            path = []
            current = current_node
            while current is not START:
                path.append(current.location)
                current = current.parent
            return path[::-1]  # reverse the path

        # otherwise, get adjacent locations
        adjacent_locations = get_enterable_adjacent_locations(grid, current_node.location)

        # create nodes for the adjacent locations
        for adjacent_location in adjacent_locations:
            adjacent_node = Node(adjacent_location,
                                 current_node.movement_cost + 1,
                                 manhattan_distance(adjacent_location, to_location),
                                 current_node)

            # selectively add the adjacent nodes to the open list
            if adjacent_node in closed_list:
                continue
            for open_node in open_list:
                if adjacent_node == open_node and adjacent_node.cost > open_node.cost:
                    continue
            open_list.append(adjacent_node)


class Node(object):
    def __init__(self, location, movement_cost, heuristic_cost, parent):
        self.location = location
        self.movement_cost = movement_cost
        self.heuristic_cost = heuristic_cost
        self.cost = self.movement_cost + self.heuristic_cost
        self.parent = parent

    def __eq__(self, node):
        return self.location.x == node.location.x and self.location.y == node.location.y
