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
ELECTION_BEGIN = "election_begin"
ELECTION_ID_DECLARE = "election_id_declare"
ELECTION_COMPARE = "election_compare"
ELECTION_END = "election_end"
ELECTION_WINNER_WAIT_CYCLES = 4
ID = "id"
FROM = "from"
LOSER_ID = "loser_id"
MESSAGE_TYPE = "message_type"
SHUTDOWN = "shutdown"
TAKE_TURN = "take_turn"
TIMESTAMP = "timestamp"
WINNER_ID = "winner_id"
YOUR_TURN = "your_turn"

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