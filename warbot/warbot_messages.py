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


def start_movement_message():
    """Message sent by leader to start movement to objective"""
    message = {MESSAGE_TYPE: START_MOVEMENT,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def squad_leader_waypoint_message(waypoint):
    """Message sent by squad leader giving a waypoint for movement toward the objective"""
    message = {MESSAGE_TYPE: SQUAD_LEADER_WAYPOINT,
               WAYPOINT: waypoint.to_dict(),
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def opfor_contact_message():
    """Message that indicates contact with OPFOR and transition to direct attack"""
    message = {MESSAGE_TYPE: OPFOR_CONTACT,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def suppressive_fire_position_message(suppressive_fire_position):
    """Message sent by A Team Leader that gives the suppressive fire position"""
    message = {MESSAGE_TYPE: SUPPRESSIVE_FIRE_POSITION,
               LOCATION: suppressive_fire_position.to_dict(),
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def flanking_position_message(flanking_position_waypoint, flanking_position):
    """Message sent by B Team Leader that gives the flanking position waypoint and the flanking position"""
    message = {MESSAGE_TYPE: FLANKING_POSITION,
               FLANKING_POSITION_WAYPOINT: flanking_position_waypoint.to_dict(),
               FLANKING_POSITION: flanking_position.to_dict(),
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def ready_to_flank_message(name):
    """Message sent by Team B to Squad Leader indicating ready to flank OPFOR"""
    message = {MESSAGE_TYPE: READY_TO_FLANK,
               NAME: name,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def lift_and_shift_fire_message():
    """Message sent by Squad Leader to direct lift and shift fire for Team A and assault for Team B"""
    message = {MESSAGE_TYPE: LIFT_AND_SHIFT_FIRE,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def limit_of_advance_message(name):
    """Message sent by Team B indicating limit of advance reached"""
    message = {MESSAGE_TYPE: LIMIT_OF_ADVANCE,
               NAME: name,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def secure_objective_message():
    """Message sent by squad leader to form security perimeter around objective"""
    message = {MESSAGE_TYPE: SECURE_OBJECTIVE,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def in_security_perimeter_position_message(name):
    """Message sent to squad leader to establish security perimeter"""
    message = {MESSAGE_TYPE: IN_SECURITY_PERIMETER_POSITION,
               NAME: name,
               TIMESTAMP: timestamp()}
    return json.dumps(message)
