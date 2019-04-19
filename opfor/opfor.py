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
import logging

from agent.agent import Agent
from agent.agent_messages import *


class Opfor(Agent):

    def __init__(self, to_me_queue, from_me_queue, initial_location, initial_visible_map, name):
        Agent.__init__(self, to_me_queue, from_me_queue, initial_location,
                       initial_visible_map, OPFOR_VISION_DISTANCE, name)
        self.action_queue = []
        self.path = []

    def run(self):
        run_simulation = True
        while run_simulation:
            # get message from to_me_queue
            message = self.get_sim_message()
            if message is not None:
                if message[MESSAGE_TYPE] == SHUTDOWN:
                    run_simulation = False
                logging.debug("{}: Received sim message with type: {}".format(self.name, message[MESSAGE_TYPE]))
                if message[MESSAGE_TYPE] == YOUR_TURN:
                    do_nothing_response = take_turn_do_nothing_message(self.name)
                    self.put_sim_message(do_nothing_response)
                    logging.debug("{}: Sent do nothing message: {}".format(self.name, do_nothing_response))
