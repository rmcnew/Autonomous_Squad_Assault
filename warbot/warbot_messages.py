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


def election_begin_message():
    """Message that indicates an election is starting"""
    message = {MESSAGE_TYPE: ELECTION_BEGIN,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def election_id_declare_message(my_id):
    """Message that gives process ID for comparison"""
    message = {MESSAGE_TYPE: ELECTION_ID_DECLARE,
               ID: my_id,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def election_compare_message(my_id, their_id):
    """Message that indicates a process won an ID comparison against another process"""
    message = {MESSAGE_TYPE: ELECTION_COMPARE,
               WINNER_ID: my_id,
               LOSER_ID: their_id,
               TIMESTAMP: timestamp()}
    return json.dumps(message)


def election_end_message(my_id):
    """Message that indicates a process has defeated all challengers and
       not received additional challenges before the timeout"""
    message = {MESSAGE_TYPE: ELECTION_END,
               WINNER_ID: my_id,
               TIMESTAMP: timestamp()}
    return json.dumps(message)