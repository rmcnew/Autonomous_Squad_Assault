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

from shared.constants import *
from shared.functions import timestamp
import json


def warbot_online_message(name):
    """Message to notify other warbots that this warbot is operational"""
    message = {MESSAGE_TYPE: WARBOT_ONLINE,
               FROM: name,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def election_begin_message():
    """Message that indicates an election is starting"""
    message = {MESSAGE_TYPE: ELECTION_BEGIN,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def election_id_declare_message(name):
    """Message that gives process ID for comparison"""
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