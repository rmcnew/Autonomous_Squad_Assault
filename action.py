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
from enum import Enum


class Action(Enum):
    TURN_NORTH = "turn_north"
    TURN_NORTHEAST = "turn_northeast"
    TURN_EAST = "turn_east"
    TURN_SOUTHEAST = "turn_southeast"
    TURN_SOUTH = "turn_south"
    TURN_SOUTHWEST = "turn_southwest"
    TURN_WEST = "turn_west"
    TURN_NORTHWEST = "turn_northwest"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    MOVE_FORWARD = "move_forward"
    MOVE_BACKWARD = "move_backward"
