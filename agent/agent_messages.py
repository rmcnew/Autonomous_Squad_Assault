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

# messages common to all agents in the simulation

import json

from shared.constants import *
from shared.functions import timestamp


# your turn message
def your_turn_message(visible_map):
    """Message that indicates the agent needs to decide and submit a take_turn message"""
    message = {MESSAGE_TYPE: YOUR_TURN,
               VISIBLE_MAP: visible_map,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


# agent actions
def move_to(location):
    return {MOVE_TO: location.to_dict()}


def fire_at(location):
    return {FIRE_AT: location.to_dict()}


# take turn message
def take_turn_message(name, action):
    """Message that the agent sends to take a turn"""
    message = {MESSAGE_TYPE: TAKE_TURN,
               FROM: name,
               ACTION: action,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def shutdown_message():
    """Message that directs the receiver to cleanly shutdown"""
    message = {MESSAGE_TYPE: SHUTDOWN,
               TIMESTAMP: timestamp()}
    return json.dumps(message)

