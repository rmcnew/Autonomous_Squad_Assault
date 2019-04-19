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

# map contains methods to create the elements that make up the simulated
# map where the autonomous infantry squad operates
from simulation.drawable import Drawable
from simulation.grid import Grid


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



