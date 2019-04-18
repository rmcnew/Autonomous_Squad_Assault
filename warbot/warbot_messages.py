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

# messages common to warbots in the simulation

import json

from shared.constants import *
from shared.functions import timestamp


def warbot_online_message(name):
    """Message to notify other warbots that this warbot is operational"""
    message = {MESSAGE_TYPE: WARBOT_ONLINE,
               FROM: name,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def election_name_declare_message(name):
    """Message that implicitly starts the leader election and gives name for comparison"""
    message = {MESSAGE_TYPE: ELECTION_NAME_DECLARE,
               NAME: name,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def election_compare_message(my_name, their_name):
    """Message that indicates a warbot won an name comparison against another warbot"""
    message = {MESSAGE_TYPE: ELECTION_COMPARE,
               WINNER_NAME: my_name,
               LOSER_NAME: their_name,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def election_end_message(my_name):
    """Message that indicates a warbot has defeated all challengers and
       not received additional challenges before the timeout"""
    message = {MESSAGE_TYPE: ELECTION_END,
               WINNER_NAME: my_name,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def team_assignment_message(squad_leader, team_a, team_b_leader, team_b):
    """Message sent by leader that assigns warbots to teams"""
    message = {MESSAGE_TYPE: TEAM_ASSIGNMENT,
               SQUAD_LEADER: squad_leader,
               TEAM_A: team_a,
               TEAM_B_LEADER: team_b_leader,
               TEAM_B: team_b,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def forming_squad_column_wedge_message(name):
    """Message sent by warbots that are moving to form squad column wedge"""
    message = {MESSAGE_TYPE: FORMING_SQUAD_COLUMN_WEDGE,
               FROM: name,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def ready_for_movement_message(name):
    """Message sent by warbot that is in position and ready for movement"""
    message = {MESSAGE_TYPE: READY_FOR_MOVEMENT,
               FROM: name,
               TIMESTAMP: timestamp()}
    return json.dumps(message)
