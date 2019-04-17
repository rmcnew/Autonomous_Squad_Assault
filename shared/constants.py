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

# shared constants

# coordinates
X = 'x'
Y = 'y'

# message strings
ACTION = "action"
ELECTION_NAME_DECLARE = "election_name_declare"  # also serves as ELECTION_BEGIN
ELECTION_COMPARE = "election_compare"
ELECTION_END = "election_end"
ELECTION_SLEEP_WAIT = 0.3
ELECTION_WINNER_WAIT_CYCLES = 4
FROM = "from"
GRID = "grid"
LOSER_NAME = "loser_name"
MAX_X = "max_x"
MAX_Y = "max_y"
MESSAGE_TYPE = "message_type"
MIN_X = "min_x"
MIN_Y = "min_y"
NAME = "name"
ON_TEAM_A = "on_team_a"
ON_TEAM_B = "on_team_b"
SHUTDOWN = "shutdown"
SQUAD_LEADER = "squad_leader"
TAKE_TURN = "take_turn"
TEAM_A = "team_a"
TEAM_A_LEADER = "team_a_leader"
TEAM_ASSIGNMENT = "team_assignment"
TEAM_ASSIGNMENT_SLEEP_WAIT = 0.3
TEAM_B = "team_b"
TEAM_B_LEADER = "team_b_leader"
TIMESTAMP = "timestamp"
TO = "to"
VISIBLE_MAP = "visible_map"
WARBOT_ONLINE = "warbot_online"
WINNER_NAME = "winner_name"
YOUR_LOCATION = "your_location"
YOUR_TURN = "your_turn"

# agent actions
MOVE_TO = "move_to"
FIRE_AT = "fire_at"

# Drawable prefixes
WARBOT_PREFIX = "WARBOT_"
OPFOR_PREFIX = "OPFOR_"
CIVILIAN_PREFIX = "CIV_"

# opfor generation radius away from objective
OPFOR_GENERATE_RADIUS = 6  # type: int

# opfor vision around self
OPFOR_VISION_DISTANCE = 8  # type: int

# warbot generation radius away from rally point
WARBOT_GENERATE_RADIUS = 6  # type: int

# warbot vision around self  (better than human due to high resolution camera)
WARBOT_VISION_DISTANCE = 12  # type: int
